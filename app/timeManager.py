import time 
class TimeManager:
    def __init__(self):
        self.TOTAL_TIME_START = time.time()

        self.transactions_update_start_time = time.time()

        self.report_time_start = time.time()

        self.API_ALLOWED_CALL_TIME = 2.01


    def is_transactions_update_time(self):
        t = time.time() - self.transactions_update_start_time
        if t >= 300:
            self.transactions_update_start_time = time.time()
            return True 
        return False

    def is_report_time(self):
        t = time.time() - self.report_time_start
        if t > 900:
            self.report_time_start = time.time()
            return True
        return False
        

    def api_call_delay(self, x):
        for i in range(x):
            time.sleep(self.API_ALLOWED_CALL_TIME)

    def main_cycle_delay(self, algtime):
        if algtime<self.API_ALLOWED_CALL_TIME:
            time.sleep(self.API_ALLOWED_CALL_TIME-algtime)