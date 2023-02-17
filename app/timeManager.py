import time 
class TimeManager:
    def __init__(self):
        self.transactions_update_start_time = time.time()

    def is_transactions_update_time(self):
        t = time.time() - self.transactions_update_start_time
        if t >= 300:
            self.transactions_update_start_time = time.time()
            return True 
        return False