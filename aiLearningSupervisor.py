import ast
import importlib
import sys
from botBase import BotStatus

class AILearningSupervior:
    def __init__(self):
        self.last_working_version = None
        
    def validate_new_code(self):
        try:
            # Fix Windows path format
            with open("c:\\Pookie.AI\\MainFrame\\groqAi.py", "r") as file:
                content = file.read()
                
            # Parse and validate syntax
            ast.parse(content)
            
            # Try to reload the module
            if 'groqAi' in sys.modules:
                del sys.modules['groqAi']
            importlib.import_module('groqAi')
            
            return True
        except Exception as e:
            print(f"Validation error: {e}")
            if self.last_working_version:
                with open("c:\\Pookie.AI\\MainFrame\\groqAi.py", "w") as file:
                    file.write(self.last_working_version)
            return False
        
    def backup_working_version(self):
        # Fix Windows path format
        with open("c:\\Pookie.AI\\MainFrame\\groqAi.py", "r") as file:
            self.last_working_version = file.read()
