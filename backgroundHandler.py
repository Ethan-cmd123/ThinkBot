import subprocess
import sys
import time
import os
import threading
import queue
import logging
import logging.handlers
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import keyboard  

class ColorCodes:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class LogHandler:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.queue_handler = logging.handlers.QueueHandler(self.log_queue)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.queue_handler)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, display_callback):
        self.display_callback = display_callback

    def on_modified(self, event):
        if event.src_path.endswith('groqAi.py'):
            self.display_callback(f"{ColorCodes.WARNING}[FILE CHANGE] groqAi.py modified at {datetime.now()}{ColorCodes.RESET}")

class BackgroundManager:
    def __init__(self):
        self.log_handler = LogHandler()
        self.main_process = None
        self.observer = Observer()
        self.file_handler = FileChangeHandler(self.display_message)
        self.learning_status = None
        self.commands = {
            'help': self.show_help,
            'start': self.start_main,
            'learn': self.start_learning,
            'exit': self.cleanup,
            'clear': self.clear_screen
        }
        self.running = True
        self.current_process = None
        
    def start_file_monitoring(self):
        self.observer.schedule(self.file_handler, "c:\\Pookie.AI\\MainFrame", recursive=False)
        self.observer.start()

    def display_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        sys.stdout.flush()

    def monitor_output(self, pipe, prefix):
        for line in iter(pipe.readline, b''):
            decoded_line = line.decode('utf-8').strip()
            if "[LEARNING]" in decoded_line:
                self.display_message(f"{ColorCodes.GREEN}{decoded_line}{ColorCodes.RESET}")
            elif "error" in decoded_line.lower():
                self.display_message(f"{ColorCodes.ERROR}[{prefix}] {decoded_line}{ColorCodes.RESET}")
            elif "warning" in decoded_line.lower():
                self.display_message(f"{ColorCodes.WARNING}[{prefix}] {decoded_line}{ColorCodes.RESET}")
            else:
                self.display_message(f"{ColorCodes.BLUE}[{prefix}] {decoded_line}{ColorCodes.RESET}")

    def process_logs(self):
        while True:
            try:
                record = self.log_handler.log_queue.get(timeout=0.1)
                self.display_message(f"{ColorCodes.GREEN}[LOG] {record.getMessage()}{ColorCodes.RESET}")
            except queue.Empty:
                continue

    def show_help(self, *args):
        """Show available commands"""
        help_text = f"""
{ColorCodes.GREEN}Available Commands:{ColorCodes.RESET}
- help                  : Show this help message
- start                 : Start the AI interface
- learn "task"         : Enter learning mode with specific task
- clear                : Clear the screen
- exit                 : Exit the program
"""
        self.display_message(help_text)

    def clear_screen(self, *args):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def start_main(self, *args):
        """Start the main AI interface"""
        self.display_message(f"{ColorCodes.HEADER}Starting main.py...{ColorCodes.RESET}")
        
        self.current_process = subprocess.Popen(
            [sys.executable, "c:\\Pookie.AI\\MainFrame\\main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Monitor output in separate threads
        stdout_thread = threading.Thread(
            target=self.monitor_output,
            args=(self.current_process.stdout, "STDOUT"),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=self.monitor_output,
            args=(self.current_process.stderr, "STDERR"),
            daemon=True
        )

        stdout_thread.start()
        stderr_thread.start()

    def start_learning(self, *args):
        """Start learning mode with specific task"""
        if not args or not args[0]:
            self.display_message(f"{ColorCodes.ERROR}Please specify what to learn: learn \"task description\"{ColorCodes.RESET}")
            return
            
        task = args[0]
        self.display_message(f"{ColorCodes.GREEN}Starting learning mode for: {task}{ColorCodes.RESET}")
        # Implementation for direct learning mode
        # This could involve directly calling the AI teaching components
        try:
            from aiTeachingScript import AITeacher
            from aiLearningSupervisor import AILearningSupervior
            
            teacher = AITeacher("your_api_key")  # Replace with actual API key
            supervisor = AILearningSupervior()
            
            supervisor.backup_working_version()
            if teacher.teach(task):
                self.display_message(f"{ColorCodes.GREEN}Successfully learned: {task}{ColorCodes.RESET}")
            else:
                self.display_message(f"{ColorCodes.ERROR}Failed to learn: {task}{ColorCodes.RESET}")
        except Exception as e:
            self.display_message(f"{ColorCodes.ERROR}Learning error: {str(e)}{ColorCodes.RESET}")

    def handle_key_press(self):
        """Handle key press to return to launcher"""
        if self.current_process:
            self.display_message(f"{ColorCodes.WARNING}Key pressed. Returning to launcher...{ColorCodes.RESET}")
            self.current_process.terminate()
            self.current_process = None

    def process_command(self, cmd_line):
        """Process command line input"""
        if not cmd_line.strip():
            return

        # Split command and arguments, handling quoted strings
        parts = []
        current = []
        in_quotes = False
        
        for char in cmd_line.strip():
            if char == '"':
                in_quotes = not in_quotes
            elif char == ' ' and not in_quotes:
                if current:
                    parts.append(''.join(current))
                    current = []
            else:
                current.append(char)
        if current:
            parts.append(''.join(current))

        cmd = parts[0].lower()
        args = [arg.strip('"') for arg in parts[1:]]

        if cmd in self.commands:
            self.commands[cmd](*args)
        else:
            self.display_message(f"{ColorCodes.ERROR}Unknown command. Type 'help' for available commands.{ColorCodes.RESET}")

    def run(self):
        """Enhanced run loop with command processing"""
        try:
            self.display_message(f"{ColorCodes.HEADER}Background Handler Started. Type 'help' for commands.{ColorCodes.RESET}")
            self.start_file_monitoring()

            # Start log processing thread
            log_thread = threading.Thread(target=self.process_logs, daemon=True)
            log_thread.start()

            # Add keyboard listener
            keyboard.on_press(lambda _: self.handle_key_press())

            while self.running:
                try:
                    cmd = input(f"{ColorCodes.BLUE}> {ColorCodes.RESET}").strip()
                    self.process_command(cmd)
                except EOFError:
                    break

        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        """Clean shutdown of background handler"""
        self.display_message(f"{ColorCodes.WARNING}Shutting down...{ColorCodes.RESET}")
        if self.main_process:
            self.main_process.terminate()
        self.observer.stop()
        self.observer.join()
        keyboard.unhook_all()  # Remove keyboard hooks
        sys.exit(0)

if __name__ == "__main__":
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    manager = BackgroundManager()
    manager.run()
