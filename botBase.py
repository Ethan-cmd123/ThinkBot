from enum import Enum

class BotStatus(Enum):
    IDLE = "Idle"
    LISTENING_WAKE = "Listening for wake word"
    WAKE_DETECTED = "Wake word detected"
    LISTENING_COMMAND = "Listening for command"
    PROCESSING_COMMAND = "Processing command"
    FINISHED_SAYING_RESPONSE = "Finished saying response"
    ERROR = "Error occurred"
    GOODBYE = "Goodbye"
    LEARNING_MODE = "Learning Mode"
    LEARNING_INPUT = "Learning Input"
