import time
import threading
from datetime import datetime

class Timer:
    def __init__(self):
        self.running = False
        self.start_time = 0
        self.end_time = None
        self.timer_thread = None
        self.callback = None
        self.timer_type = None  # "stopwatch", "timer", or "alarm"
        self.display_text = ""
        self.force_display = False  # Add this flag
        self.alarm_time = None
        self.split_times = []
        self.laps = []
        
    def start_stopwatch(self):
        self.timer_type = "stopwatch"
        self.start_time = time.time()
        self.running = True
        self.force_display = True  # Force display when starting
        self.timer_thread = threading.Thread(target=self._run_stopwatch, daemon=True)
        self.timer_thread.start()
        
    def start_timer(self, minutes):
        self.timer_type = "timer"
        self.start_time = time.time()
        self.end_time = self.start_time + (minutes * 60)
        self.running = True
        self.force_display = True  # Force display when starting
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()
        
    def lap(self):
        """Record lap time for stopwatch"""
        if self.timer_type == "stopwatch" and self.running:
            elapsed = time.time() - self.start_time
            self.laps.append(elapsed)
            lap_num = len(self.laps)
            self.display_text = f"Lap {lap_num}: {int(elapsed//60):02d}:{int(elapsed%60):02d}"
            return len(self.laps)
            
    def split(self):
        """Record split time"""
        if self.timer_type == "stopwatch" and self.running:
            split = time.time() - self.start_time
            self.split_times.append(split)
            return f"{int(split//60):02d}:{int(split%60):02d}"
            
    def set_alarm(self, hour, minute):
        """Set alarm for specific time"""
        now = datetime.now()
        alarm_time = now.replace(hour=hour, minute=minute, second=0)
        if alarm_time < now:
            alarm_time = alarm_time.replace(day=alarm_time.day + 1)
        self.alarm_time = alarm_time.timestamp()
        self.timer_type = "alarm"
        self.running = True
        self.force_display = True
        self.timer_thread = threading.Thread(target=self._run_alarm, daemon=True)
        self.timer_thread.start()
        
    def _run_stopwatch(self):
        while self.running:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.display_text = f"Stopwatch: {minutes:02d}:{seconds:02d}"
            time.sleep(0.1)
            
    def _run_timer(self):
        while self.running and time.time() < self.end_time:
            remaining = self.end_time - time.time()
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            self.display_text = f"Timer: {minutes:02d}:{seconds:02d}"
            if remaining <= 0:
                self.display_text = "Timer Complete!"
                if self.callback:
                    self.callback()
                break
            time.sleep(0.1)
            
    def _run_alarm(self):
        """Run alarm countdown"""
        while self.running and time.time() < self.alarm_time:
            remaining = self.alarm_time - time.time()
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            seconds = int(remaining % 60)
            self.display_text = f"Alarm in: {hours:02d}:{minutes:02d}:{seconds:02d}"
            time.sleep(0.1)
            
        if self.running:
            self.display_text = "ALARM!"
            if self.callback:
                self.callback()
            
    def stop(self):
        self.running = False
        self.force_display = False  # Stop forcing display
        if self.timer_thread:
            self.timer_thread.join()
        self.display_text = ""
