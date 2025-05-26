import os
import queue
import threading
import time
from datetime import date

lock = threading.RLock()

# Buffer for unpublished messages

class QueueManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.counts_history_queue = queue.Queue()
        self.entities_queue = queue.Queue()
        self.session_day = date.today()


    def get_counts_history(self):
        counts_history = []
        with self.lock:
            while not self.counts_history_queue.empty():
                counts = self.counts_history_queue.get()
                counts_history.append(counts)
        return counts_history
    
    def get_entities(self):
        entities = []
        with self.lock:
            while not self.entities_queue.empty():
                entity = self.entities_queue.get()
                entities.append(entity)
        return entities

    def save_counts(self, counts):
        with self.lock:
            self.counts_history_queue.put(counts)
            print(f"Counts in queue: {self.counts_history_queue.qsize()}")

    def get_counts_queue_size(self):
        with self.lock: 
            return self.counts_history_queue.qsize()


    def is_queue_empty(self):
        return self.counts_history_queue.empty()
    
    def is_entities_queue_empty(self):
        return self.entities_queue.empty()
        

