#include <iostream>
#include <vector>
#include <queue>
#include <map>
#include <unordered_map>
#include <string>
#include <chrono>
#include <memory>
#include <iomanip>
#include <cassert>
#include <algorithm>

// ==================== Data Structures & Enums ====================

enum class OrderType {
    MARKET,
    LIMIT
};

enum class Side {
    BUY,
    SELL
};

struct Order {
    uint64_t id;
    Side side;
    OrderType type;
    uint32_t quantity;
    double price;  // For MARKET orders, price is ignored for matching
    uint64_t timestamp;
    std::string trader_id;
    
    // For partial fills
    uint32_t filled_quantity = 0;
    uint32_t remaining_quantity() const { return quantity - filled_quantity; }
    
    Order(uint64_t id, Side side, OrderType type, uint32_t qty, double price, 
          const std::string& trader_id, uint64_t timestamp)
        : id(id), side(side), type(type), quantity(qty), price(price),
          trader_id(trader_id), timestamp(timestamp) {}
};

struct Trade {
    uint64_t trade_id;
    double price;
    uint32_t quantity;
    std::string buyer_id;
    std::string seller_id;
    uint64_t timestamp;
    uint64_t buy_order_id;
    uint64_t sell_order_id;
    
    Trade(uint64_t trade_id, double price, uint32_t qty, 
          const std::string& buyer, const std::string& seller,
          uint64_t timestamp, uint64_t buy_id, uint64_t sell_id)
        : trade_id(trade_id), price(price), quantity(qty),
          buyer_id(buyer), seller_id(seller), timestamp(timestamp),
          buy_order_id(buy_id), sell_order_id(sell_id) {}
    
    void print() const {
        std::cout << "Trade " << trade_id << ": "
                  << quantity << " @ " << std::fixed << std::setprecision(2) << price
                  << " | Buyer: " << buyer_id << " | Seller: " << seller_id << "\n";
    }
};

// ==================== Price Level Implementation ====================

class PriceLevel {
private:
    std::queue<std::shared_ptr<Order>> orders;
    uint32_t total_quantity = 0;
    double price;
    
public:
    PriceLevel(double price) : price(price) {}
    
    void add_order(const std::shared_ptr<Order>& order) {
        orders.push(order);
        total_quantity += order->remaining_quantity();
    }
    
    // Match against an incoming order
    uint32_t match(std::shared_ptr<Order>& incoming_order, 
                   std::vector<Trade>& trades,
                   uint64_t& trade_counter,
                   uint64_t timestamp) {
        
        uint32_t matched_qty = 0;
        
        while (!orders.empty() && incoming_order->remaining_quantity() > 0) {
            auto& resting_order = orders.front();
            
            uint32_t exec_qty = std::min(
                incoming_order->remaining_quantity(),
                resting_order->remaining_quantity()
            );
            
            // Determine buyer and seller based on sides
            std::string buyer_id, seller_id;
            uint64_t buy_order_id, sell_order_id;
            
            if (incoming_order->side == Side::BUY) {
                buyer_id = incoming_order->trader_id;
                seller_id = resting_order->trader_id;
                buy_order_id = incoming_order->id;
                sell_order_id = resting_order->id;
            } else {
                buyer_id = resting_order->trader_id;
                seller_id = incoming_order->trader_id;
                buy_order_id = resting_order->id;
                sell_order_id = incoming_order->id;
            }
            
            // Record trade
            trades.emplace_back(
                ++trade_counter,
                price,  // Execution price is the resting order's price
                exec_qty,
                buyer_id,
                seller_id,
                timestamp,
                buy_order_id,
                sell_order_id
            );
            
            // Update quantities
            incoming_order->filled_quantity += exec_qty;
            resting_order->filled_quantity += exec_qty;
            total_quantity -= exec_qty;
            matched_qty += exec_qty;
            
            // Remove fully filled resting order
            if (resting_order->remaining_quantity() == 0) {
                orders.pop();
            } else {
                // Partial fill, break to maintain FIFO
                break;
            }
        }
        
        return matched_qty;
    }
    
    bool empty() const { return orders.empty(); }
    uint32_t get_total_quantity() const { return total_quantity; }
    double get_price() const { return price; }
    
    void print() const {
        std::cout << "  Price " << std::fixed << std::setprecision(2) << price 
                  << ": " << total_quantity << " total, " 
                  << orders.size() << " orders\n";
    }
};

// ==================== Order Book Implementation ====================

class OrderBook {
private:
    // Bids: highest price first (descending)
    std::map<double, PriceLevel, std::greater<double>> bids;
    
    // Asks: lowest price first (ascending)
    std::map<double, PriceLevel> asks;
    
    std::vector<Trade> trades;
    uint64_t order_counter = 0;
    uint64_t trade_counter = 0;
    
    // Track orders by ID for cancellation/modification
    std::unordered_map<uint64_t, std::shared_ptr<Order>> orders_by_id;
    
    // Price-time priority matching
    void match_limit_order(std::shared_ptr<Order>& order, uint64_t timestamp);
    void match_market_order(std::shared_ptr<Order>& order, uint64_t timestamp);
    
public:
    OrderBook() = default;
    
    // Core matching function
    void match(std::shared_ptr<Order>& order, uint64_t timestamp) {
        if (order->type == OrderType::MARKET) {
            match_market_order(order, timestamp);
        } else {
            match_limit_order(order, timestamp);
        }
    }
    
    // Public interface to submit orders
    uint64_t submit_order(Side side, OrderType type, uint32_t quantity, 
                         double price, const std::string& trader_id) {
        uint64_t timestamp = std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::system_clock::now().time_since_epoch()
        ).count();
        
        auto order = std::make_shared<Order>(
            ++order_counter, side, type, quantity, price, trader_id, timestamp
        );
        
        orders_by_id[order->id] = order;
        
        // Try to match immediately
        match(order, timestamp);
        
        // If not fully filled and it's a limit order, add to book
        if (order->remaining_quantity() > 0 && type == OrderType::LIMIT) {
            add_to_book(order);
        }
        
        return order->id;
    }
    
    // Add resting order to book
    void add_to_book(const std::shared_ptr<Order>& order) {
        if (order->side == Side::BUY) {
            auto it = bids.find(order->price);
            if (it == bids.end()) {
                it = bids.emplace(order->price, PriceLevel(order->price)).first;
            }
            it->second.add_order(order);
        } else {
            auto it = asks.find(order->price);
            if (it == asks.end()) {
                it = asks.emplace(order->price, PriceLevel(order->price)).first;
            }
            it->second.add_order(order);
        }
    }
    
    // Getters for validation
    const std::vector<Trade>& get_trades() const { return trades; }
    const std::map<double, PriceLevel, std::greater<double>>& get_bids() const { return bids; }
    const std::map<double, PriceLevel>& get_asks() const { return asks; }
    
    void print_book() const {
        std::cout << "\n========== ORDER BOOK ==========\n";
        std::cout << "BIDS (Highest to Lowest):\n";
        for (const auto& [price, level] : bids) {
            level.print();
        }
        
        std::cout << "\nASKS (Lowest to Highest):\n";
        for (const auto& [price, level] : asks) {
            level.print();
        }
        std::cout << "===============================\n";
    }
    
    void print_trades() const {
        std::cout << "\n========== TRADE LOG ==========\n";
        for (const auto& trade : trades) {
            trade.print();
        }
        std::cout << "===============================\n";
    }
};

// ==================== Matching Algorithm Implementation ====================

void OrderBook::match_limit_order(std::shared_ptr<Order>& order, uint64_t timestamp) {
    // For BUY limit order: match against ASK side
    if (order->side == Side::BUY) {
        while (!asks.empty() && order->remaining_quantity() > 0) {
            auto best_ask = asks.begin();
            
            // Check if we can cross the spread
            if (order->price < best_ask->first) {
                break;  // No match possible
            }
            
            // Match at this price level
            best_ask->second.match(order, trades, trade_counter, timestamp);
            
            // Remove empty price levels
            if (best_ask->second.empty()) {
                asks.erase(best_ask);
            }
        }
    } 
    // For SELL limit order: match against BID side
    else {
        while (!bids.empty() && order->remaining_quantity() > 0) {
            auto best_bid = bids.begin();
            
            // Check if we can cross the spread
            if (order->price > best_bid->first) {
                break;  // No match possible
            }
            
            // Match at this price level
            best_bid->second.match(order, trades, trade_counter, timestamp);
            
            // Remove empty price levels
            if (best_bid->second.empty()) {
                bids.erase(best_bid);
            }
        }
    }
}

void OrderBook::match_market_order(std::shared_ptr<Order>& order, uint64_t timestamp) {
    // For MARKET BUY: take best asks regardless of price
    if (order->side == Side::BUY) {
        while (!asks.empty() && order->remaining_quantity() > 0) {
            auto best_ask = asks.begin();
            
            // Match at this price level
            best_ask->second.match(order, trades, trade_counter, timestamp);
            
            // Remove empty price levels
            if (best_ask->second.empty()) {
                asks.erase(best_ask);
            }
        }
    } 
    // For MARKET SELL: take best bids regardless of price
    else {
        while (!bids.empty() && order->remaining_quantity() > 0) {
            auto best_bid = bids.begin();
            
            // Match at this price level
            best_bid->second.match(order, trades, trade_counter, timestamp);
            
            // Remove empty price levels
            if (best_bid->second.empty()) {
                bids.erase(best_bid);
            }
        }
    }
}

// ==================== Test Suite ====================

class OrderBookTest {
private:
    OrderBook book;
    
public:
    void run_validation_test() {
        std::cout << "\n================ VALIDATION TEST ================\n";
        std::cout << "Testing: Massive MARKET BUY clearing entire ASK side\n\n";
        
        // Step 1: Build ASK ladder
        std::cout << "1. Submitting ASK ladder:\n";
        std::cout << "   - ASK 10 @ 101.00\n";
        std::cout << "   - ASK 20 @ 102.00\n";
        std::cout << "   - ASK 30 @ 103.00\n";
        
        book.submit_order(Side::SELL, OrderType::LIMIT, 10, 101.00, "Seller1");
        book.submit_order(Side::SELL, OrderType::LIMIT, 20, 102.00, "Seller2");
        book.submit_order(Side::SELL, OrderType::LIMIT, 30, 103.00, "Seller3");
        
        book.print_book();
        
        // Step 2: Submit massive MARKET BUY
        std::cout << "\n2. Submitting MARKET BUY for 60 shares:\n";
        book.submit_order(Side::BUY, OrderType::MARKET, 60, 0.0, "BigBuyer");
        
        // Step 3: Verify results
        std::cout << "\n3. Results:\n";
        book.print_trades();
        book.print_book();
        
        // Step 4: Assertions
        verify_results();
    }
    
    void verify_results() {
        const auto& trades = book.get_trades();
        const auto& asks = book.get_asks();
        
        std::cout << "\n4. Verification:\n";
        
        // Check that ASK side is empty
        if (asks.empty()) {
            std::cout << "   ✓ ASK side is completely cleared (PASS)\n";
        } else {
            std::cout << "   ✗ ASK side not empty (FAIL)\n";
            std::cout << "     Remaining asks: " << asks.size() << " price levels\n";
        }
        
        // Check trade count
        if (trades.size() == 3) {
            std::cout << "   ✓ Correct number of trades: 3 (PASS)\n";
        } else {
            std::cout << "   ✗ Wrong number of trades: " << trades.size() << " (FAIL)\n";
        }
        
        // Check trade prices and quantities
        double expected_prices[] = {101.00, 102.00, 103.00};
        uint32_t expected_quantities[] = {10, 20, 30};
        bool price_check = true;
        bool qty_check = true;
        
        for (size_t i = 0; i < trades.size() && i < 3; i++) {
            if (std::abs(trades[i].price - expected_prices[i]) > 0.001) {
                price_check = false;
                std::cout << "   ✗ Trade " << i+1 << " wrong price: " 
                          << trades[i].price << " vs " << expected_prices[i] << "\n";
            }
            if (trades[i].quantity != expected_quantities[i]) {
                qty_check = false;
                std::cout << "   ✗ Trade " << i+1 << " wrong quantity: " 
                          << trades[i].quantity << " vs " << expected_quantities[i] << "\n";
            }
        }
        
        if (price_check) std::cout << "   ✓ All trade prices correct (PASS)\n";
        if (qty_check) std::cout << "   ✓ All trade quantities correct (PASS)\n";
        
        // Check total filled quantity
        uint32_t total_filled = 0;
        for (const auto& trade : trades) {
            total_filled += trade.quantity;
        }
        
        if (total_filled == 60) {
            std::cout << "   ✓ Total filled quantity: 60 (PASS)\n";
        } else {
            std::cout << "   ✗ Total filled quantity: " << total_filled << " (FAIL)\n";
        }
        
        std::cout << "\n================================================\n";
    }
    
    void run_additional_tests() {
        std::cout << "\n\n================ ADDITIONAL TESTS ================\n";
        
        // Test 1: Partial fill
        std::cout << "\nTest 1: Partial fill\n";
        OrderBook book2;
        book2.submit_order(Side::SELL, OrderType::LIMIT, 100, 100.0, "S1");
        book2.submit_order(Side::BUY, OrderType::LIMIT, 150, 100.0, "B1");
        book2.print_book();
        book2.print_trades();
        
        // Test 2: Price-time priority
        std::cout << "\nTest 2: Price-time priority\n";
        OrderBook book3;
        book3.submit_order(Side::BUY, OrderType::LIMIT, 50, 99.0, "B1");
        book3.submit_order(Side::BUY, OrderType::LIMIT, 100, 100.0, "B2");
        book3.submit_order(Side::BUY, OrderType::LIMIT, 75, 100.0, "B3");
        book3.submit_order(Side::SELL, OrderType::MARKET, 125, 0.0, "S1");
        book3.print_trades();
    }
};

// ==================== Main Execution ====================

int main() {
    std::cout << "ORDER BOOK MATCHING ENGINE IMPLEMENTATION\n";
    std::cout << "=========================================\n";
    
    OrderBookTest tester;
    
    // Run the required validation test
    tester.run_validation_test();
    
    // Run additional tests
    tester.run_additional_tests();
    
    return 0;
}
