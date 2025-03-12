import os
import pyttsx3
import speech_recognition as sr
from groq import Groq
import logging
from botBase import BotStatus
from emotionSynthesizer import EmotionSynthesizer
import random
import time
import threading
import pygame  # Add pygame import
from aiLearningSupervisor import *
from aiTeachingScript import AITeacher
from speechHandler import *
from timerHandler import *


class ThinkBot:
    def __init__(self, api_key):
        print("Initializing ThinkBot...")
        self.base_voice_rate = 175  # Move this to top of init
        self.client = Groq(api_key=api_key)
        self.speech_lock = threading.Lock()  # Add lock for speech synchronization
        self.engine = pyttsx3.init()
        self.setup_voice()  # Call setup_voice after setting base_voice_rate
        self._original_say = self.engine.say  # Store original say method
        self.engine.say = self.enhanced_say  # Replace with our enhanced version
        self.recognizer = sr.Recognizer()
        self.set_voice("female")
        logging.basicConfig(level=logging.INFO)
        self._status = BotStatus.IDLE
        self.awaiting_learning_input = False  # Add this line
        self.learning_mode = False
        self.current_command = None  # Add this line
        self.emotion_synth = EmotionSynthesizer()
        self.learning_response = None  # Add this line
        self.current_step = 0
        self.steps = []
        self.in_steps = False
        self.confirmation_words = [
            'continue', 'yes', 'yeah', 'sure', 'okay', 'ok', 'alright', 
            'right', 'good', 'go', 'next', 'proceed', 'carry on', 'yep', 
            'move on', 'ready'
        ]
        self.recognizer.pause_threshold = 0.5  # Increased from 0.3
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.4  # Increased from 0.3
        self.operation_timeout = None  # Remove timeout restriction
        self.previous_command = None
        self.awaiting_step_confirmation = False
        self.step_trigger_phrases = [
            "how to cook", "how to make", "how to build",
            "steps for", "instructions for", "guide for",
            "teach me to", "show me to", "process of",
            "how do i", "method for", "recipe for"
        ]
        self.simple_queries = [
            "what is", "who is", "where is", "when",
            "why", "can you", "do you", "tell me",
            "what time", "what day", "weather", "hello"
        ]
        self.person_greetings = [
            "Hello, good to see you!",
            "Welcome back!",
            "Greetings, how are you today?",
            "Master, it's nice to see you!",
        ]
        self.person_goodbyes = [
            "Goodbye, until next time!",
            "Take care!",
            "See you soon!",
            "Have a great time!",
        ]
        self.last_greeting_time = 0
        self.greeting_cooldown = 5  # Cooldown in seconds
        self.wake_word_cooldown = time.time()
        self.wake_word_delay = 0.0  # 3 seconds between wake word checks
        self.listening_timeout = 0.0  # 10 seconds listening timeout
        self.listening_start_time = 0
        self.consecutive_wakes = 0
        self.max_consecutive_wakes = 3
        self.last_spontaneous_time = time.time()
        self.eye_tracker = None  # Will be set from main.py
        self.speech_handler = SpeechHandler()
        self.last_command_time = 0
        self.command_cooldown = 0.5  # 500ms cooldown between commands
        self.last_wake_time = 0
        self.wake_cooldown = 2.0  # Increased from 1.5 to 2.0 seconds
        self.is_active = False
        self.processing_timeout = 2.0  # Timeout for processing animation
        self.is_speaking = False
        self.speech_cooldown = 2.0  # Increased to 2.0 seconds
        self.current_caption = ""
        self.last_caption_update = time.time()
        self.caption_timeout = 5  # Seconds to show caption
        self.response_cooldown = 0.5  # Add cooldown after response
        self.can_listen = True  # Add new flag to control listening state
        self.name = "thinkbot"
        self.last_activity_time = time.time()
        self.idle_timeout = 30.0  # Seconds before sleep mode
        self.timer = Timer()
        self.last_response_time = 0
        self.response_cooldown = 1.0  # 1 second between responses
        self.speak_cooldown = 0.5  # Time to wait after speaking

    def setup_voice(self):
        """Configure voice settings for more natural speech"""
        try:
            self.engine.setProperty('rate', self.base_voice_rate)
            self.engine.setProperty('volume', 0.9)
            voices = self.engine.getProperty('voices')
            
            selected_voice = None
            for voice in voices:
                if "zira" in voice.id.lower():
                    selected_voice = voice
                    break
                elif "david" in voice.id.lower():
                    selected_voice = voice
                    break
            
            if not selected_voice and voices:
                selected_voice = voices[1] if len(voices) > 1 else voices[0]
                
            if selected_voice:
                self.engine.setProperty('voice', selected_voice.id)
                
        except Exception as e:
            print(f"Voice setup error: {e}")
            # Set fallback defaults if error occurs
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 0.9)

    def enhanced_say(self, text):
        """Enhanced speaking function with better prosody"""
        # Add subtle pauses for more natural speech
        text = text.replace(',', ', ')
        text = text.replace('.', '. ')
        text = text.replace('?', '? ')
        text = text.replace('!', '! ')
        
        self._original_say(text)  # Use stored original method

    def say(self, text):
        """Enhanced speaking function with better prosody"""
        # Add subtle pauses for more natural speech
        text = text.replace(',', ', <break time="100ms"/>')
        text = text.replace('.', '. <break time="200ms"/>')
        text = text.replace('?', '? <break time="200ms"/>')
        text = text.replace('!', '! <break time="200ms"/>')
        
        self.engine.say(text)
        self.engine.runAndWait()

    @property
    def status(self):
        return self._status.value

    def _update_status(self, new_status: BotStatus):
        self._status = new_status
        logging.info(f"Status: {self._status.value}")

    def set_voice(self, gender):
        voices = self.engine.getProperty('voices')
        if gender == "female":
            self.engine.setProperty('voice', voices[1].id)
        else:
            self.engine.setProperty('voice', voices[1].id)

    def get_chat_response(self, user_input):
        self._update_status(BotStatus.PROCESSING_COMMAND)

        # Add max token limit and conciseness to prompt
        custom_prompt = (
            "DO NOT USE EMOJIS. You are ThinkBot. Keep responses VERY SHORT - max 2 sentences. "
            "Never refer to yourself as AI. Address user. "
            f"Current emotional state: {self.emotion_synth.get_current_emotion_str()}. "
            "IMPORTANT: Be extremely concise. Don't explain or elaborate unless asked."
        )

        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": custom_prompt + user_input}],
            model="llama3-8b-8192",
            max_tokens=50  # Limit response length
        )
        
        response = chat_completion.choices[0].message.content
        # Clean up response to be more concise
        response = response.split(".")[0].strip() + "."  # Keep only first sentence
        return response.replace('*', '')

    def listen_for_wake_word(self):
        """Listen for wake word with improved controls"""
        self._update_status(BotStatus.LISTENING_WAKE)
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.wake_word_cooldown < self.wake_word_delay:
            return False
            
        # Check consecutive wake limit
        if self.consecutive_wakes >= self.max_consecutive_wakes:
            time.sleep(2)  # Force pause
            self.consecutive_wakes = 0
            return False
            
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            try:
                print("Listening for wake word...")
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                text = self.recognizer.recognize_google(audio).lower()
                
                if "hello" in text or "hi" in text:
                    self._update_status(BotStatus.WAKE_DETECTED)
                    self.wake_word_cooldown = current_time
                    self.consecutive_wakes += 1
                    self.listening_start_time = current_time
                    return True
                else:
                    self.consecutive_wakes = 0
                    return False
                    
            except sr.UnknownValueError:
                self.consecutive_wakes = 0
                return False
            except sr.WaitTimeoutError:
                return False
            except sr.RequestError as e:
                logging.error(f"Could not request results; {e}")
                return False

    def enter_learning_mode(self):
        """Handle entering learning mode"""
        self._update_status(BotStatus.LEARNING_MODE)
        self.learning_mode = True
        self.awaiting_learning_input = True
        self.learning_status = "Entered learning mode"
        
        print("\n=== LEARNING MODE ACTIVATED ===")
        self.safe_say("Entering learning mode, master. What would you like me to learn?")
        
        # Only quit pygame if it's initialized
        if pygame.get_init():
            pygame.quit()
            
        # Wait for learning input
        while self.learning_mode and not self.learning_response:
            time.sleep(0.1)
            
        if self.learning_response:
            return self.teach(self.learning_response)
        return False

    def exit_learning_mode(self):
        self._update_status(BotStatus.IDLE)
        self.learning_mode = False
        print("Exiting learning mode, master.")
        self.safe_say("Exiting learning mode, master.")

    def teach(self, task):
        """Process learning request"""
        print(f"\n[LEARNING] Starting to learn: {task}")
        print("[LEARNING] Analyzing task requirements...")
        self.learning_status = f"Learning: {task}"
        
        try:
            # Initialize teaching components
            teacher = AITeacher(self.client.api_key)
            supervisor = AILearningSupervior()
            
            # Backup current version
            supervisor.backup_working_version()
            
            # Generate and implement new code
            if teacher.teach(task):
                if supervisor.validate_new_code():
                    self.learning_status = "Successfully learned new capability!"
                    print("\n[LEARNING] ✓ Successfully learned new task")
                    self.safe_say("I have successfully learned the new task, master.")
                    return True
                    
            self.learning_status = "Failed to learn task"
            print("\n[LEARNING] ✗ Failed to learn task")
            self.safe_say("I'm sorry master, I failed to learn that properly.")
            return False
            
        except Exception as e:
            self.learning_status = f"Error during learning: {str(e)}"
            print(f"\n[LEARNING] ✗ Error: {e}")
            self.safe_say("I encountered an error while trying to learn, master.")
            return False
        finally:
            # Reset learning state
            self.learning_response = None
            self.learning_mode = False
            self._update_status(BotStatus.IDLE)

    def listen_for_command(self):
        """Enhanced command listening with Vosk"""
        self._update_status(BotStatus.LISTENING_COMMAND)
        
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return None
            
        try:
            # Update caption to show listening status
            if self.eye_tracker:
                self.eye_tracker.set_caption("Listening...")
                
            self.speech_handler.start_listening()
            command = self.speech_handler.process_speech()
            
            if command:
                # Check for quick commands
                quick_cmd = self.speech_handler.check_quick_command(command)
                if quick_cmd:
                    self.handle_quick_command(quick_cmd)
                    return None
                
                # Update caption and process normal command
                if self.eye_tracker:
                    self.eye_tracker.set_caption(f"You: {command}")
                self.last_command_time = current_time
                return command
                
        except Exception as e:
            logging.error(f"Speech recognition error: {e}")
            if self.eye_tracker:
                self.eye_tracker.set_caption("Error understanding speech")
        finally:
            self.speech_handler.stop_listening()
            
        return None

    def handle_quick_command(self, cmd):
        """Handle quick command responses"""
        if cmd == "stop":
            self.safe_say("Stopping listening mode")
            self._update_status(BotStatus.IDLE)
        elif cmd == "pause":
            self.safe_say("Pausing voice recognition")
            self.speech_handler.stop_listening()
        elif cmd == "resume":
            self.safe_say("Resuming voice recognition")
            self.speech_handler.start_listening()
        elif cmd == "status":
            self.report_status()
        elif cmd == "clear_history":
            self.speech_handler.clear_command_history()
            self.safe_say("Command history cleared")

    def report_status(self):
        """Report current system status"""
        emotion = self.emotion_synth.get_current_emotion_str()
        history = len(self.speech_handler.get_command_history())
        self.safe_say(f"I am currently {emotion} and have processed {history} commands")

    def safe_say(self, text):
        """Enhanced speech output with better controls"""
        try:
            self.is_speaking = True
            self.can_listen = False
            
            if self.eye_tracker:
                self.eye_tracker.set_talking(True)
            
            with self.speech_lock:
                self.engine.say(text)
                self.engine.runAndWait()
                
            time.sleep(self.speak_cooldown)  # Add cooldown after speaking
                
        finally:
            if self.eye_tracker:
                self.eye_tracker.set_talking(False)
            self.is_speaking = False
            self.last_response_time = time.time()
            self.can_listen = True

    def adjust_voice_for_emotion(self, emotion):
        """Adjust voice properties based on emotion"""
        rate = self.base_voice_rate
        volume = 0.9
        
        if emotion == 'excited':
            rate *= 1.2  # Speed up
            volume = 1.0
        elif emotion == 'sad':
            rate *= 0.8  # Slow down
            volume = 0.7
            
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

    def greet_person(self):
        current_time = time.time()
        if current_time - self.last_greeting_time > self.greeting_cooldown:
            greeting = random.choice(self.person_greetings)
            self.safe_say(greeting)
            self.last_greeting_time = current_time
            
    def farewell_person(self):
        current_time = time.time()
        if current_time - self.last_greeting_time > self.greeting_cooldown:
            farewell = random.choice(self.person_goodbyes)
            self.safe_say(farewell)
            self.last_greeting_time = current_time

    def update_caption(self, text):
        """Update caption or timer display"""
        if self.eye_tracker:
            # Always show timer if it's forcing display, otherwise use normal logic
            if self.timer.force_display:
                display_text = self.timer.display_text
            else:
                display_text = self.timer.display_text if self.timer.running else text
                
            self.eye_tracker.set_caption(display_text)
            self.current_caption = display_text
            self.last_caption_update = time.time()

    def handle_speech(self, text):
        """Handle speech with improved emotion handling"""
        if self.is_speaking or not self.can_listen:
            return
            
        current_time = time.time()
        if current_time - self.last_response_time < self.speak_cooldown:
            return
            
        text = text.lower().strip()
        
        # Wake word detection
        wake_phrases = ["hey bot", "hey", "hello", "hi", "hey think", "okay bot"]
        
        if not self.is_active:
            if any(phrase in text for phrase in wake_phrases):
                print("Wake word detected:", text)
                self.is_active = True
                self._update_status(BotStatus.WAKE_DETECTED)
                
                # Visual feedback with new emotion system
                if self.eye_tracker:
                    self.eye_tracker.set_emotion('happy')
                
                return
                
        elif self.is_active:
            if "goodbye" in text or "bye" in text:
                self.is_active = False
                self._update_status(BotStatus.GOODBYE)
                if self.eye_tracker:
                    self.eye_tracker.set_emotion('neutral')
                self.safe_say("Goodbye!")
                return
            
            # Process command
            print("Processing command:", text)
            self._update_status(BotStatus.PROCESSING_COMMAND)
            
            try:
                if self.eye_tracker:
                    self.eye_tracker.set_emotion('focused')
                    
                response = self.get_chat_response(text)
                print("AI Response:", response)
                
                self._update_status(BotStatus.WAKE_DETECTED)
                if self.eye_tracker:
                    self.eye_tracker.set_emotion('happy')
                
                self.safe_say(response)
                
            except Exception as e:
                print("Error processing command:", e)
                if self.eye_tracker:
                    self.eye_tracker.set_emotion('error')
                self.safe_say("Sorry, I encountered an error.")

        # ...rest of existing code...

    def run(self):
        """Enhanced run loop with caption timeout"""
        self._update_status(BotStatus.IDLE)
        self.speech_handler.listen_in_background(self.handle_speech)
        
        while True:
            try:
                current_time = time.time()
                # Update caption more frequently when timer is running
                if self.timer.running:
                    self.update_caption("")  # Force refresh timer display
                # Only clear non-timer captions
                elif (self.current_caption and 
                      current_time - self.last_caption_update > self.caption_timeout):
                    self.update_caption("")
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.speech_handler.stop_listening()
                break

if __name__ == "__main__":
    api_key = "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"
    thinkbot = ThinkBot(api_key)
    while True:
        thinkbot.run()