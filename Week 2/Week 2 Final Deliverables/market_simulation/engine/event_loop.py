"""
Event Loop - Discrete event simulation scheduler
"""
import heapq
import time
from typing import List, Tuple, Callable, Any
import uuid

class Event:
    """Base event class"""
    def __init__(self, timestamp: float, event_type: str, data: Any = None):
        self.timestamp = timestamp
        self.event_type = event_type
        self.data = data
        self.sequence_id = time.time_ns()  # Ensure total ordering
        
    def __lt__(self, other):
        """Comparison for heap ordering"""
        if self.timestamp == other.timestamp:
            return self.sequence_id < other.sequence_id
        return self.timestamp < other.timestamp
    
    def __repr__(self):
        return f"Event({self.timestamp:.2f}, {self.event_type}, {self.data})"

class EventLoop:
    """Discrete event simulation scheduler using heapq"""
    
    def __init__(self, start_time: float = 0.0):
        """
        Initialize event loop
        
        Args:
            start_time: Initial simulation time
        """
        self.time = start_time
        self.event_queue = []
        self.handlers = {}
        self.running = False
        self.event_count = 0
        
    def schedule_event(self, delay: float, event_type: str, data: Any = None):
        """
        Schedule an event to occur after delay
        
        Args:
            delay: Time from now until event
            event_type: Type of event
            data: Event data
        """
        event = Event(self.time + delay, event_type, data)
        heapq.heappush(self.event_queue, event)
        self.event_count += 1
        
    def register_handler(self, event_type: str, handler: Callable):
        """
        Register handler for event type
        
        Args:
            event_type: Event type to handle
            handler: Function to call when event occurs
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        
    def process_next_event(self) -> bool:
        """
        Process the next event in queue
        
        Returns:
            True if event processed, False if queue empty
        """
        if not self.event_queue:
            return False
            
        event = heapq.heappop(self.event_queue)
        
        # Advance simulation time
        self.time = event.timestamp
        
        # Call handlers for this event type
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                handler(event)
        
        return True
    
    def run(self, max_events: int = None, max_time: float = None):
        """
        Run event loop
        
        Args:
            max_events: Maximum number of events to process
            max_time: Maximum simulation time
        """
        self.running = True
        events_processed = 0
        
        while self.running and self.event_queue:
            if max_events and events_processed >= max_events:
                break
            if max_time and self.time >= max_time:
                break
                
            self.process_next_event()
            events_processed += 1
            
        self.running = False
        
    def stop(self):
        """Stop event loop"""
        self.running = False
        
    def clear(self):
        """Clear all pending events"""
        self.event_queue.clear()
        
    def get_next_event_time(self) -> float:
        """Get timestamp of next event"""
        if self.event_queue:
            return self.event_queue[0].timestamp
        return float('inf')
    
    def get_stats(self) -> dict:
        """Get event loop statistics"""
        return {
            'current_time': self.time,
            'events_pending': len(self.event_queue),
            'events_processed': self.event_count - len(self.event_queue),
            'total_events': self.event_count
        }