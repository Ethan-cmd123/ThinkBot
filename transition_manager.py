import time
import math

class TransitionManager:
    def __init__(self):
        self.transition_duration = 1.0  # Slower overall movement
        self.start_time = None
        self.start_pos = None
        self.target_pos = None
        self.current_easing = self._ease_out_elastic  # Default easing
        
    def start_transition(self, start_pos, target_pos):
        self.start_time = time.time()
        self.start_pos = start_pos
        self.target_pos = target_pos
        
    def get_current_position(self):
        if not all([self.start_time, self.start_pos, self.target_pos]):
            return None
            
        elapsed = time.time() - self.start_time
        progress = min(elapsed / self.transition_duration, 1.0)
        
        # Use acceleration/deceleration easing
        progress = self._ease_in_out_cubic(progress)
        
        x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * progress
        y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * progress
        
        return (x, y)
        
    def _ease_out_cubic(self, x):
        return 1 - pow(1 - x, 3)
        
    def _ease_out_elastic(self, x):
        c4 = (2 * math.pi) / 8  # Much slower elastic effect
        if x == 0 or x == 1:
            return x
        return pow(2, -10 * x) * math.sin((x * 5 - 0.75) * c4) + 1  # Reduced frequency
        
    def _ease_out_bounce(self, x):
        n1 = 7.5625
        d1 = 2.75
        if x < 1 / d1:
            return n1 * x * x
        elif x < 2 / d1:
            x -= 1.5 / d1
            return n1 * x * x + 0.75
        elif x < 2.5 / d1:
            x -= 2.25 / d1
            return n1 * x * x + 0.9375
        else:
            x -= 2.625 / d1
            return n1 * x * x + 0.984375
            
    def _ease_in_out_cubic(self, x):
        """Smooth acceleration and deceleration"""
        if x < 0.5:
            return 4 * x * x * x
        else:
            return 1 - pow(-2 * x + 2, 3) / 2
            
    def set_easing(self, easing_type):
        """Change easing function: 'elastic', 'bounce', 'cubic'"""
        easing_functions = {
            'elastic': self._ease_out_elastic,
            'bounce': self._ease_out_bounce,
            'cubic': self._ease_in_out_cubic  # Use new easing as default
        }
        self.current_easing = easing_functions.get(easing_type, self._ease_in_out_cubic)
