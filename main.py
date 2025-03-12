import pyttsx3
from eye_tracker import EyeTracker
from groqAi import ThinkBot, BotStatus
import threading
from transition_manager import TransitionManager
from time import *
import time

def initialize_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 0.9)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Use female voice
    return engine

# Initialize components
tts_engine = initialize_tts()
api_key = "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"
thinkbot = ThinkBot(api_key)
thinkbot.engine = tts_engine

# Create eye tracker first and pass to ThinkBot
eye_tracker = EyeTracker()
eye_tracker.set_animation_state(True)
eye_tracker.transition_manager = TransitionManager()  # Add transition manager
thinkbot.eye_tracker = eye_tracker  # Set eye tracker before starting thread

# Create a thread for thinkbot
def thinkbot_thread():
    while True:
        thinkbot.run()

# Start thinkbot thread
thinkbot_thread = threading.Thread(target=thinkbot_thread, daemon=True)
thinkbot_thread.start()

last_status = None
while True:
    current_status = thinkbot.status
    
    # Handle status changes with smoother transitions
    if current_status != last_status:
        try:
            if current_status == BotStatus.WAKE_DETECTED.value:
                eye_tracker.set_animation_state(False)
                eye_tracker.slide_to_position(0, 0, easing='elastic')  # Center eyes
                eye_tracker.set_eye_color((144, 238, 144))  # Ensure green color is set
                eye_tracker.target_color = [144, 238, 144]  # Explicitly set target color
                if hasattr(eye_tracker, 'set_emotion'):
                    eye_tracker.set_emotion('happy', smooth=True)
            elif current_status == BotStatus.LISTENING_COMMAND.value:
                if hasattr(eye_tracker, 'set_emotion'):
                    eye_tracker.set_emotion('curious', smooth=True)
                if hasattr(eye_tracker, 'set_talking'):
                    eye_tracker.set_talking(True)
            elif current_status == BotStatus.PROCESSING_COMMAND.value:
                if hasattr(eye_tracker, 'set_emotion'):
                    eye_tracker.set_emotion('focused', smooth=True)
            else:
                eye_tracker.set_eye_color((0, 191, 255))  # Set back to blue
                eye_tracker.target_color = [0, 191, 255]  # Explicitly set target color
                eye_tracker.set_animation_state(True)  # Resume idle movements
                eye_tracker.current_emotion = 'happy'  # Force happy emotion
                eye_tracker.emotion_timer = time.time()  # Reset emotion timer
                    
        except Exception as e:
            print(f"Error handling status change: {e}")
            
        last_status = current_status

    # Run the eye tracker loop
    if not eye_tracker.run():
        break

eye_tracker.cleanup()