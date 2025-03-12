from enum import Enum
import random
import time

class Emotion:
    def __init__(self, name, intensity=0.5, color=(0, 191, 255)):
        self.name = name
        self.intensity = intensity
        self.color = color

class EmotionSynthesizer:
    def __init__(self):
        # Base emotions with their colors
        self.emotions = {
            'happy': Emotion('happy', 0.5, (144, 238, 144)),  # Light green
            'sad': Emotion('sad', 0.5, (70, 130, 180)),      # Steel blue
            'angry': Emotion('angry', 0.5, (255, 0, 0)),     # Red
            'calm': Emotion('calm', 0.5, (0, 191, 255)),     # Deep sky blue
            'excited': Emotion('excited', 0.5, (255, 215, 0)), # Gold
            'worried': Emotion('worried', 0.5, (147, 112, 219)) # Medium purple
        }
        self.current_emotion = self.emotions['calm']
        self.secondary_emotion = None
        self.curiosity_level = 0.5  # Add curiosity tracking
        self.last_emotion_change = time.time()
        self.emotion_duration = random.uniform(30, 120)  # Emotions last 30-120 seconds
        
    def update_emotion(self, emotion_name, intensity=0.5):
        if emotion_name in self.emotions:
            old_emotion = self.current_emotion
            self.secondary_emotion = old_emotion
            self.current_emotion = self.emotions[emotion_name]
            self.current_emotion.intensity = intensity
            return self.blend_emotions()
            
    def blend_emotions(self):
        if not self.secondary_emotion:
            return self.current_emotion.color
            
        # Blend colors based on intensities
        blend_ratio = self.current_emotion.intensity
        c1 = self.current_emotion.color
        c2 = self.secondary_emotion.color
        
        blended_color = (
            int(c1[0] * blend_ratio + c2[0] * (1 - blend_ratio)),
            int(c1[1] * blend_ratio + c2[1] * (1 - blend_ratio)),
            int(c1[2] * blend_ratio + c2[2] * (1 - blend_ratio))
        )
        return blended_color
        
    def get_current_emotion_str(self):
        if self.secondary_emotion:
            return f"feeling {self.current_emotion.name} with a hint of {self.secondary_emotion.name}"
        return f"feeling {self.current_emotion.name}"
        
    def update_emotions(self):
        """Naturally evolve emotions over time"""
        current_time = time.time()
        if current_time - self.last_emotion_change > self.emotion_duration:
            # Randomly shift emotions
            self.curiosity_level = min(1.0, max(0.0, self.curiosity_level + random.uniform(-0.2, 0.2)))
            
            # More likely to be curious when calm or happy
            if self.current_emotion.name in ['calm', 'happy']:
                self.curiosity_level = min(1.0, self.curiosity_level + 0.1)
            
            # Update emotion duration
            self.emotion_duration = random.uniform(30, 120)
            self.last_emotion_change = current_time
