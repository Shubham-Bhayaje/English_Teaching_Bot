import flet as ft
import sys
import os
import json
import speech_recognition as sr
import pyttsx3
import threading
import queue
from openai import OpenAI
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("english_practice.log"), logging.StreamHandler()]
)
logger = logging.getLogger("english_practice_assistant")

# API Configuration - Set these variables directly in your code
OPENAI_BASE_URL = "https://models.inference.ai.azure.com"
OPENAI_API_KEY = ""  # You can set this variable when running the app

# Default configurations
CONFIG = {
    "voice": {
        "rate": 150,  # Slightly slower for better comprehension
        "voice_index": 0  # Index of the voice to use (0 is usually the default voice)
    },
    "ui": {
        "window_width": 400,
        "window_height": 600,
        "padding": 20
    },
    "practice": {
        "difficulty_level": "intermediate",  # beginner, intermediate, advanced
        "focus_areas": ["conversation", "grammar", "vocabulary"]
    }
}

# Function to load config from file if it exists
def load_config():
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                loaded_config = json.load(f)
                # Update CONFIG with loaded values
                for category in loaded_config:
                    if category in CONFIG:
                        CONFIG[category].update(loaded_config[category])
            logger.info("Config loaded from file")
    except Exception as e:
        logger.error(f"Error loading config: {e}")

# Load config at startup
load_config()

class EnglishPracticeAssistant:
    def __init__(self, api_key=None, base_url=None):
        # Use provided API credentials or fall back to defaults
        self.api_base_url = base_url or OPENAI_BASE_URL
        self.api_key = api_key or OPENAI_API_KEY
        
        if not self.api_key:
            logger.warning("No API key provided!")
        
        # Initialize OpenAI client
        self.client = OpenAI(
            base_url=self.api_base_url,
            api_key=self.api_key
        )
        
        # Initialize voice engine
        self.engine = None
        self.message_queue = queue.Queue()
        self.conversation_history = []
        
        # English practice specific attributes
        self.current_topic = None
        self.difficulty = CONFIG["practice"]["difficulty_level"]
        self.focus_areas = CONFIG["practice"]["focus_areas"]
        self.correction_mode = True  # Whether to correct user's English
        
        # Conversation topics for practice
        self.conversation_topics = [
            "Travel and vacation experiences",
            "Hobbies and interests",
            "Food and cooking",
            "Movies and entertainment",
            "Technology and gadgets",
            "Work and career goals",
            "Education and learning",
            "Family and relationships",
            "Cultural differences",
            "Current events",
            "Health and fitness",
            "Environmental issues"
        ]
        
    def initialize_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty("voices")
            # Get voice index from config, ensuring it's valid
            voice_index = min(CONFIG["voice"]["voice_index"], len(voices) - 1)
            self.engine.setProperty("voice", voices[voice_index].id)
            self.engine.setProperty("rate", CONFIG["voice"]["rate"])
            return True
        except Exception as e:
            logger.error(f"TTS initialization error: {e}")
            return False
    
    def speak(self, text):
        """Add text to speaking queue"""
        self.message_queue.put(text)
    
    def speaking_worker(self):
        """Worker thread to process speech queue"""
        while True:
            try:
                text = self.message_queue.get()
                if text == "QUIT":
                    break
                    
                if self.engine:
                    self.engine.say(text)
                    self.engine.runAndWait()
                self.message_queue.task_done()
            except Exception as e:
                logger.error(f"Speaking error: {e}")
    
    def suggest_topic(self):
        """Suggest a random conversation topic"""
        self.current_topic = random.choice(self.conversation_topics)
        return f"Let's talk about: {self.current_topic}"
    
    def generate_response(self, prompt):
        """Generate AI response using OpenAI API"""
        try:
            # Add the new message to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Prepare system message based on current settings
            system_prompt = f"""You are an English conversation practice assistant helping users improve their English skills.
            Current difficulty level: {self.difficulty}
            Focus areas: {', '.join(self.focus_areas)}
            
            Guidelines:
            - Keep responses natural, friendly and conversational
            - Use language appropriate for the {self.difficulty} level
            - Ask follow-up questions to encourage conversation
            - Provide gentle corrections for major mistakes without interrupting the flow
            - Occasionally introduce new vocabulary or expressions with brief explanations
            - Be encouraging and supportive
            
            If the user's message has English errors and correction mode is enabled, include a brief correction at the end of your response.
            
            Current topic: {self.current_topic or 'Open conversation'}
            """
            
            # Prepare messages including conversation history (with context limit)
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add last few conversation turns for context (limit to prevent token overflow)
            messages.extend(self.conversation_history[-5:])
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=200  # Allow slightly longer responses for language teaching
            )
            
            content = response.choices[0].message.content.strip()
            
            # Add assistant's response to conversation history
            self.conversation_history.append({"role": "assistant", "content": content})
            
            return content
        except Exception as e:
            logger.error(f"API error: {e}")
            return "Sorry, I encountered an error generating a response."
    
    def save_conversation(self):
        """Save conversation history to file"""
        try:
            with open("english_practice_history.json", "w") as f:
                json.dump(self.conversation_history, f)
            logger.info("Conversation saved successfully")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            
    def toggle_correction_mode(self):
        """Toggle whether to include corrections"""
        self.correction_mode = not self.correction_mode
        return f"Correction mode {'enabled' if self.correction_mode else 'disabled'}"
    
    def set_difficulty(self, level):
        """Set the difficulty level"""
        if level in ["beginner", "intermediate", "advanced"]:
            self.difficulty = level
            return f"Difficulty set to {level}"
        return "Invalid difficulty level. Choose beginner, intermediate, or advanced."


def main(page: ft.Page, api_key=None):
    # Create assistant instance with provided API key
    assistant = EnglishPracticeAssistant(api_key=api_key)
    
    # Initialize speech engine
    tts_initialized = assistant.initialize_tts()
    
    # Window setup
    page.window_width = CONFIG["ui"]["window_width"]
    page.window_height = CONFIG["ui"]["window_height"]
    page.title = "English Practice Assistant"
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.LIGHT  # Use light mode for better text visibility
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = CONFIG["ui"]["padding"]
    
    # Start speaking worker thread
    speaking_thread = threading.Thread(target=assistant.speaking_worker, daemon=True)
    speaking_thread.start()
    
    # UI Components
    header = ft.Container(
        content=ft.Text("English Practice Assistant", size=24, weight=ft.FontWeight.BOLD),
        margin=ft.margin.only(bottom=20)
    )
    
    # Conversation area with chat-like UI
    conversation = ft.ListView(
        expand=True, 
        spacing=10, 
        padding=10,
        auto_scroll=True
    )
    
    conversation_container = ft.Container(
        content=conversation,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=10,
        padding=10,
        expand=True
    )
    
    # Status indicator
    status = ft.Text("Ready", color="green")
    
    # Text input for manual commands
    text_input = ft.TextField(
        hint_text="Type in English...",
        border_radius=30,
        expand=True
    )
    
    def add_message(text, is_user=True):
        conversation.controls.append(
            ft.Container(
                content=ft.Text(text, color="black"),  # Set text color to black
                bgcolor=ft.colors.BLUE_50 if is_user else ft.colors.GREEN_50,  # Lighter backgrounds for better black text visibility
                padding=10,
                border_radius=10,
                width=page.window_width * 0.7,
                alignment=ft.alignment.center_right if is_user else ft.alignment.center_left
            )
        )
        page.update()
    
    def process_input(input_text):
        if not input_text.strip():
            return
            
        # Check for special commands
        if input_text.startswith("/"):
            command = input_text.lower().split()
            if command[0] == "/topic":
                topic_suggestion = assistant.suggest_topic()
                add_message(f"System: {topic_suggestion}", is_user=False)
                assistant.speak(topic_suggestion)
                return
            elif command[0] == "/difficulty":
                if len(command) > 1:
                    result = assistant.set_difficulty(command[1])
                    add_message(f"System: {result}", is_user=False)
                    assistant.speak(result)
                    return
            elif command[0] == "/corrections":
                result = assistant.toggle_correction_mode()
                add_message(f"System: {result}", is_user=False)
                assistant.speak(result)
                return
            elif command[0] in ["/help", "/commands"]:
                help_text = """Available commands:
/topic - Suggest a new conversation topic
/difficulty [beginner|intermediate|advanced] - Set difficulty level
/corrections - Toggle correction mode
/help - Show this help message
/save - Save conversation
/quit - Exit application"""
                add_message(f"System: {help_text}", is_user=False)
                return
            elif command[0] == "/save":
                assistant.save_conversation()
                add_message("System: Conversation saved successfully", is_user=False)
                return
            elif command[0] == "/quit":
                assistant.speak("Goodbye! Thanks for practicing your English.")
                # Allow time for goodbye message
                save_and_quit_timer = threading.Timer(2.0, lambda: (assistant.save_conversation(), sys.exit()))
                save_and_quit_timer.start()
                return
        
        # Add user message to UI
        add_message(f"You: {input_text}", is_user=True)
        
        # Process with AI
        status.value = "Processing..."
        page.update()
        
        response = assistant.generate_response(input_text)
        add_message(f"Assistant: {response}", is_user=False)
        
        # Speak response
        assistant.speak(response)
        
        # Reset status
        status.value = "Ready"
        page.update()
    
    def send_button_click(e):
        input_text = text_input.value
        text_input.value = ""
        page.update()
        process_input(input_text)
    
    def text_input_on_submit(e):
        send_button_click(e)
    
    text_input.on_submit = text_input_on_submit
    
    send_button = ft.IconButton(
        icon=ft.icons.SEND,
        on_click=send_button_click
    )
    
    input_row = ft.Row(
        [text_input, send_button],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    
    def voice_button_click(e):
        btn = e.control
        btn.disabled = True
        status.value = "Listening..."
        page.update()
        
        def recognition_thread():
            try:
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    status.value = "Speak now..."
                    page.update()
                    
                    try:
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    except sr.WaitTimeoutError:
                        status.value = "No speech detected"
                        page.update()
                        assistant.speak("I didn't hear anything. Please try again.")
                        return
                
                # Recognition
                status.value = "Recognizing..."
                page.update()
                
                try:
                    user_input = recognizer.recognize_google(audio, language="en-US")
                    process_input(user_input)
                    
                except sr.UnknownValueError:
                    status.value = "Couldn't understand audio"
                    page.update()
                    assistant.speak("Sorry, I didn't catch that. Could you repeat?")
                except sr.RequestError:
                    status.value = "Speech service error"
                    page.update()
                    assistant.speak("Speech recognition service unavailable")
            except Exception as e:
                logger.error(f"Recognition error: {e}")
                status.value = f"Error: {str(e)}"
                page.update()
            finally:
                btn.disabled = False
                page.update()
        
        # Run recognition in separate thread
        threading.Thread(target=recognition_thread, daemon=True).start()
    
    # Voice button with microphone icon
    voice_button = ft.FloatingActionButton(
        icon=ft.icons.MIC,
        on_click=voice_button_click,
        bgcolor=ft.colors.BLUE,
    )
    
    # Bottom toolbar with practice options
    def difficulty_change(e):
        difficulty = e.control.value
        result = assistant.set_difficulty(difficulty)
        add_message(f"System: {result}", is_user=False)
    
    difficulty_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("beginner", "Beginner"),
            ft.dropdown.Option("intermediate", "Intermediate"),
            ft.dropdown.Option("advanced", "Advanced"),
        ],
        value=assistant.difficulty,
        on_change=difficulty_change,
        width=150
    )
    
    def new_topic_click(e):
        topic_suggestion = assistant.suggest_topic()
        add_message(f"System: {topic_suggestion}", is_user=False)
        assistant.speak(topic_suggestion)
    
    new_topic_button = ft.ElevatedButton(
        "New Topic",
        on_click=new_topic_click,
        icon=ft.icons.TOPIC
    )
    
    practice_toolbar = ft.Row(
        [
            ft.Text("Level:"),
            difficulty_dropdown,
            new_topic_button
        ],
        alignment=ft.MainAxisAlignment.SPACE_AROUND
    )
    
    # Error message if TTS not initialized
    if not tts_initialized:
        def dismiss_banner(e):
            banner = e.control.parent
            banner.open = False
            page.update()
            
        page.add(
            ft.Banner(
                bgcolor=ft.colors.RED_100,
                leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.RED, size=40),
                content=ft.Text("Text-to-speech engine failed to initialize. Voice output disabled."),
                actions=[
                    ft.TextButton("Dismiss", on_click=dismiss_banner),
                ],
                open=True
            )
        )
    
    # Add everything to the page
    page.add(
        header,
        conversation_container,
        ft.Container(
            content=status,
            margin=ft.margin.symmetric(vertical=10)
        ),
        input_row,
        ft.Container(
            content=practice_toolbar,
            margin=ft.margin.only(top=10, bottom=10)
        ),
        voice_button
    )
    
    # Welcome message
    welcome_message = """Hello! I'm your English practice assistant. I'm here to help you improve your English conversation skills.

Type messages in English and I'll respond naturally. I can also give you gentle corrections to help you learn.

Try these commands:
/topic - Get a new conversation topic
/difficulty [level] - Change difficulty (beginner, intermediate, advanced)
/help - See all commands

Let's start practicing! How are you feeling today?"""

    assistant.speak("Hello! I'm your English practice assistant. How are you feeling today?")
    add_message(f"Assistant: {welcome_message}", is_user=False)

# Example of how to run the app with an API key
if __name__ == "__main__":
    # You can set the API key here
    my_api_key = ""  # Replace with your actual API key
    
    # Define a function that will be called by ft.app
    def start_app(page):
        main(page, api_key=my_api_key)
    
    ft.app(target=start_app)