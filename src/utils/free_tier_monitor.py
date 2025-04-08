import logging
from datetime import datetime, date

class FreeTierMonitor:
    def __init__(self):
        self._daily_ops = 0
        self._last_reset_date = date.today()
        self.DAILY_OPS_LIMIT = 4500  # Safe limit for free tier
        self.STORAGE_LIMIT_GB = 4.5  # 90% of 5GB free tier
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def reset_if_new_day(self):
        today = date.today()
        if today > self._last_reset_date:
            self._daily_ops = 0
            self._last_reset_date = today
            self.logger.info("Reset daily operation counter")
    
    def can_perform_operation(self):
        self.reset_if_new_day()
        can_perform = self._daily_ops < self.DAILY_OPS_LIMIT
        if not can_perform:
            self.logger.warning("Daily operation limit reached")
        return can_perform
    
    def increment_ops(self):
        self.reset_if_new_day()
        self._daily_ops += 1
        if self._daily_ops % 100 == 0:  # Log every 100 operations
            self.logger.info(f"Operation count: {self._daily_ops}")
        return self._daily_ops

    def get_current_ops(self):
        return self._daily_ops