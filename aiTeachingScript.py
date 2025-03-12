import os
import shutil
from datetime import datetime
from groq import Groq
import ast

class AITeacher:
    def __init__(self, api_key):
        self.client = Groq(api_key="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")
        # Fix Windows path format
        self.iterations_folder = "c:\\Pookie.AI\\MainFrame\\mainframeIterations"
        os.makedirs(self.iterations_folder, exist_ok=True)
        
    def backup_current_ai(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source = "c:\\Pookie.AI\\MainFrame\\groqAi.py"
        backup_path = f"{self.iterations_folder}\\groqAi_{timestamp}.py"
        shutil.copy2(source, backup_path)
        return backup_path
        
    def generate_function_code(self, task_description):
        prompt = f"""
        Create a Python function implementation for the following task: {task_description}
        Requirements:
        - Return ONLY the raw Python function code
        - No XML tags or special formatting
        - Must include docstring
        - Must include error handling
        - Function should be well-documented
        
        Example format:
        def function_name(params):
            '''docstring'''
            try:
                # implementation
            except Exception as e:
                print(f"Error:" + e)
                return None
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="deepseek-r1-distill-llama-70b"
        )
        
        # Clean up response to remove any XML tags or special formatting
        code = response.choices[0].message.content.strip()
        code = code.replace('<think>', '')
        code = code.replace('</think>', '')
        code = code.replace('```python', '')
        code = code.replace('```', '')
        
        # Verify it looks like valid Python code
        if not code.startswith('def '):
            print("Invalid code generated, missing function definition")
            return None
            
        print("\nGenerated code:")
        print("==============")
        print(code)
        print("==============\n")
        
        return code

    def integrate_new_function(self, function_code):
        if not function_code:
            return False
            
        try:
            with open("c:\\Pookie.AI\\MainFrame\\groqAi.py", "r") as file:
                content = file.read()
                
            # Insert new function before main
            insert_point = content.find("if __name__ == \"__main__\":")
            if insert_point == -1:
                print("Could not find insertion point")
                return False
                
            new_content = (
                content[:insert_point] + 
                "\n\n" + function_code + "\n\n" +
                content[insert_point:]
            )
            
            with open("c:\\Pookie.AI\\MainFrame\\groqAi.py", "w") as file:
                file.write(new_content)
                
            return True
            
        except Exception as e:
            print(f"Error integrating code: {e}")
            return False

    def teach(self, task):
        print(f"\nTeaching new task: {task}")
        backup_path = self.backup_current_ai()
        
        try:
            function_code = self.generate_function_code(task)
            if function_code and self.integrate_new_function(function_code):
                print("Successfully integrated new function")
                return True
            else:
                print("Failed to generate or integrate valid code")
                shutil.copy2(backup_path, "c:\\Pookie.AI\\MainFrame\\groqAi.py")
                return False
        except Exception as e:
            print(f"Error during teaching: {e}")
            shutil.copy2(backup_path, "c:\\Pookie.AI\\MainFrame\\groqAi.py")
            return False
