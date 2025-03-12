import speech_recognition as sr
import threading
import queue
import time

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Optimize speech detection parameters
        self.recognizer.pause_threshold = 1.0        # Wait 1 second of silence to mark end of phrase
        self.recognizer.non_speaking_duration = 0.5  # Time of silence needed to mark end
        self.recognizer.phrase_threshold = 0.3       # Minimum length of speaking to be considered a phrase
        self.recognizer.energy_threshold = 1000      # Keep existing energy threshold
        self.recognizer.dynamic_energy_adjustment_ratio = 1.5  # More sensitive to volume changes
        self.recognizer.dynamic_energy_adjustment_damping = 0.15  # Smoother volume adaptation
        
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.command_history = []
        self.max_history = 10
        self.result_callback = None
        
        # Add speech validation parameters
        self.min_audio_length = 0.3  # Minimum length of audio to process (seconds)
        self.min_text_length = 2     # Minimum length of recognized text
        self.noise_words = {'', ' ', 'um', 'uh', 'ah', 'eh'}  # Words to ignore

        self.last_processed_text = None  # Add this to prevent self-hearing
        self.last_process_time = time.time()
        self.min_time_between_commands = 1.0  # Minimum seconds between commands

    def listen_in_background(self, callback):
        """Start continuous background listening"""
        self.result_callback = callback
        self.is_listening = True
        
        def listen_loop():
            with sr.Microphone() as source:
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                while self.is_listening:
                    try:
                        # Add energy threshold to filter out silence
                        if self.recognizer.energy_threshold < 1000:
                            self.recognizer.energy_threshold = 1000
                            
                        audio = self.recognizer.listen(
                            source,
                            timeout=None,
                            phrase_time_limit=None
                        )
                        
                        # Process in separate thread if audio has content
                        if audio and len(audio.frame_data) > 0:
                            threading.Thread(
                                target=self._process_audio,
                                args=(audio,),
                                daemon=True
                            ).start()
                            
                    except sr.WaitTimeoutError:
                        continue
                        
        self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listen_thread.start()

    def _process_audio(self, audio):
        """Process audio with better validation"""
        try:
            current_time = time.time()
            if current_time - self.last_process_time < self.min_time_between_commands:
                return None

            # Check audio length
            if len(audio.frame_data) / 32000 < self.min_audio_length:  # 16000 Hz * 2 bytes per sample
                return None

            text = self.recognizer.recognize_google(audio).lower().strip()
            
            # Prevent processing duplicate/self-heard commands
            if (text and 
                text != self.last_processed_text and 
                len(text) >= self.min_text_length and 
                text not in self.noise_words and 
                not text.isspace()):
                
                self.last_processed_text = text
                self.last_process_time = current_time
                self.command_history.append(text)
                
                if len(self.command_history) > self.max_history:
                    self.command_history.pop(0)
                if self.result_callback:
                    self.result_callback(text)
                    
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"Recognition error: {e}")

    def stop_listening(self):
        """Stop background listening"""
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=1)
