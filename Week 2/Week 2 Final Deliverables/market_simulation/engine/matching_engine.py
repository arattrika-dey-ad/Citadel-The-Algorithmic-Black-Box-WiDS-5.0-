"""
Matching Engine - Core order book and trade matching logic
"""
import heapq
from collections import defaultdict, deque
import uuid

class OrderBook:
    """Limit order book with FIFO matching"""
    
    def __init__(self):
        """Initialize empty order book"""
        # Bids: price level -> deque of orders (max-heap, so store negative prices)
        self.bids = defaultdict(deque)
        self.bid_prices = []  # Max-heap (store negative prices)
        
        # Asks: price level -> deque of orders (min-heap)
        self.asks = defaultdict(deque)
        self.ask_prices = []  # Min-heap
        
        # Order lookup by ID
        self.orders = {}
        
        # Trade history
        self.trades = []
        
    def add_order(self, order):
        """
        Add a new order to the book
        
        Args:
            order: Order dictionary with side, price, quantity
            
        Returns:
            List of trades resulting from this order
        """
        order_id = str(uuid.uuid4())[:8]
        order['id'] = order_id
        order['remaining'] = order['quantity']
        order['status'] = 'active'
        
        self.orders[order_id] = order
        trades = []
        
        # Try to match immediately
        if order['side'] == 'buy':
            trades = self._match_buy_order(order)
        else:  # sell
            trades = self._match_sell_order(order)
        
        # If order not fully filled and is limit order, add to book
        if order['remaining'] > 0 and order['order_type'] == 'limit':
            self._add_to_book(order)
        
        return trades
    
    def _match_buy_order(self, order):
        """Match a buy order against existing asks"""
        trades = []
        
        while (order['remaining'] > 0 and self.asks and 
               (order['order_type'] == 'market' or 
                (order['order_type'] == 'limit' and 
                 order['price'] >= self._best_ask()))):
            
            best_ask = self._best_ask()
            if order['order_type'] == 'limit' and order['price'] < best_ask:
                break
            
            price_level = self.asks[best_ask]
            
            while price_level and order['remaining'] > 0:
                resting_order = price_level[0]
                
                # Determine trade price
                if order['order_type'] == 'market':
                    trade_price = best_ask
                else:
                    trade_price = min(order['price'], best_ask)
                
                # Determine trade quantity
                trade_qty = min(order['remaining'], resting_order['remaining'])
                
                # Execute trade
                trades.append({
                    'buyer': order['agent_id'],
                    'seller': resting_order['agent_id'],
                    'price': trade_price,
                    'quantity': trade_qty,
                    'timestamp': order['timestamp'],
                    'aggressor': 'buy'
                })
                
                # Update order quantities
                order['remaining'] -= trade_qty
                resting_order['remaining'] -= trade_qty
                
                # Remove resting order if fully filled
                if resting_order['remaining'] == 0:
                    price_level.popleft()
                    self.orders[resting_order['id']]['status'] = 'filled'
                    
            # Remove empty price level
            if not price_level:
                del self.asks[best_ask]
                # Rebuild ask heap
                self.ask_prices = list(self.asks.keys())
                heapq.heapify(self.ask_prices)
        
        return trades
    
    def _match_sell_order(self, order):
        """Match a sell order against existing bids"""
        trades = []
        
        while (order['remaining'] > 0 and self.bids and 
               (order['order_type'] == 'market' or 
                (order['order_type'] == 'limit' and 
                 order['price'] <= self._best_bid()))):
            
            best_bid = self._best_bid()
            if order['order_type'] == 'limit' and order['price'] > best_bid:
                break
            
            price_level = self.bids[best_bid]
            
            while price_level and order['remaining'] > 0:
                resting_order = price_level[0]
                
                # Determine trade price
                if order['order_type'] == 'market':
                    trade_price = best_bid
                else:
                    trade_price = max(order['price'], best_bid)
                
                # Determine trade quantity
                trade_qty = min(order['remaining'], resting_order['remaining'])
                
                # Execute trade
                trades.append({
                    'buyer': resting_order['agent_id'],
                    'seller': order['agent_id'],
                    'price': trade_price,
                    'quantity': trade_qty,
                    'timestamp': order['timestamp'],
                    'aggressor': 'sell'
                })
                
                # Update order quantities
                order['remaining'] -= trade_qty
                resting_order['remaining'] -= trade_qty
                
                # Remove resting order if fully filled
                if resting_order['remaining'] == 0:
                    price_level.popleft()
                    self.orders[resting_order['id']]['status'] = 'filled'
                    
            # Remove empty price level
            if not price_level:
                del self.bids[best_bid]
                # Rebuild bid heap
                self.bid_prices = [-p for p in self.bids.keys()]
                heapq.heapify(self.bid_prices)
        
        return trades
    
    def _add_to_book(self, order):
        """Add resting order to the book"""
        price = order['price']
        
        if order['side'] == 'buy':
            if price not in self.bids:
                self.bids[price] = deque()
                heapq.heappush(self.bid_prices, -price)  # Negative for max-heap
            self.bids[price].append(order)
        else:  # sell
            if price not in self.asks:
                self.asks[price] = deque()
                heapq.heappush(self.ask_prices, price)
            self.asks[price].append(order)
    
    def cancel_order(self, order_id):
        """
        Cancel an existing order
        
        Args:
            order_id: ID of order to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order['status'] != 'active':
            return False
        
        # Remove from price level
        price = order['price']
        if order['side'] == 'buy' and price in self.bids:
            price_level = self.bids[price]
            # Find and remove the order
            for i, o in enumerate(price_level):
                if o['id'] == order_id:
                    price_level.remove(o)
                    break
            # Remove empty price level
            if not price_level:
                del self.bids[price]
                # Rebuild heap
                self.bid_prices = [-p for p in self.bids.keys()]
                heapq.heapify(self.bid_prices)
        elif order['side'] == 'sell' and price in self.asks:
            price_level = self.asks[price]
            # Find and remove the order
            for i, o in enumerate(price_level):
                if o['id'] == order_id:
                    price_level.remove(o)
                    break
            # Remove empty price level
            if not price_level:
                del self.asks[price]
                # Rebuild heap
                self.ask_prices = list(self.asks.keys())
                heapq.heapify(self.ask_prices)
        
        order['status'] = 'cancelled'
        return True
    
    def _best_bid(self):
        """Get best (highest) bid price"""
        if not self.bid_prices:
            return 0
        return -self.bid_prices[0]  # Convert back from negative
    
    def _best_ask(self):
        """Get best (lowest) ask price"""
        if not self.ask_prices:
            return float('inf')
        return self.ask_prices[0]
    
    def get_bbo(self):
        """
        Get best bid and offer
        
        Returns:
            Tuple of (best_bid, best_ask, spread)
        """
        best_bid = self._best_bid()
        best_ask = self._best_ask() if self.ask_prices else float('inf')
        
        if best_bid == 0 or best_ask == float('inf'):
            spread = float('inf')
        else:
            spread = best_ask - best_bid
        
        return best_bid, best_ask, spread
    
    def get_mid_price(self):
        """Calculate mid price from best bid/ask"""
        best_bid, best_ask, _ = self.get_bbo()
        if best_bid == 0 or best_ask == float('inf'):
            return 100.0  # Default starting price
        return (best_bid + best_ask) / 2
    
    def get_order_book_depth(self, levels=5):
        """Get order book depth"""
        bids = []
        asks = []
        
        # Get top N bid levels
        bid_prices_sorted = sorted(self.bids.keys(), reverse=True)[:levels]
        for price in bid_prices_sorted:
            total_qty = sum(order['remaining'] for order in self.bids[price])
            bids.append((price, total_qty))
        
        # Get top N ask levels
        ask_prices_sorted = sorted(self.asks.keys())[:levels]
        for price in ask_prices_sorted:
            total_qty = sum(order['remaining'] for order in self.asks[price])
            asks.append((price, total_qty))
        
        return bids, asks
    
    def get_stats(self):
        """Get order book statistics"""
        total_bid_volume = sum(
            sum(order['remaining'] for order in orders)
            for orders in self.bids.values()
        )
        total_ask_volume = sum(
            sum(order['remaining'] for order in orders)
            for orders in self.asks.values()
        )
        
        return {
            'num_bid_levels': len(self.bids),
            'num_ask_levels': len(self.asks),
            'total_bid_volume': total_bid_volume,
            'total_ask_volume': total_ask_volume,
            'num_orders': len([o for o in self.orders.values() if o['status'] == 'active']),
            'num_trades': len(self.trades)
        }