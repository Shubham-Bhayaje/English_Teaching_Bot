# English Practice Assistant 

## UI Preview
<p align="center">
<img src="https://github.com/Shubham-Bhayaje/English_Teaching_Bot/blob/master/Main_Ui.png" width="100%">
</p>

## Overview
The English Practice Assistant is a desktop application designed to help users improve their English language skills through interactive conversation practice. The application features text and voice interaction, AI-powered responses, and various customization options for different learning levels.

## Features

- **Interactive Conversation Practice**: Engage in natural English conversations with an AI assistant
- **Voice Interaction**: Speak your responses using your microphone
- **Text-to-Speech**: Hear the assistant's responses spoken aloud
- **Adjustable Difficulty**: Set the conversation level (beginner, intermediate, advanced)
- **Conversation Topics**: Get suggested topics for practice
- **Error Correction**: Receive gentle corrections for English mistakes
- **Conversation History**: Your practice sessions are saved automatically

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Steps
1. Clone this repository or download the source code
2. Install required dependencies:
   ```
   pip install flet speechrecognition pyttsx3 openai
   ```
3. Obtain an OpenAI API key (optional but recommended for best performance)

## Usage

### Running the Application
```
python english_practice.py
```

### Basic Commands
- Type your messages in the text field and press Enter/Send
- Click the microphone button to speak your response
- Use these special commands:
  - `/topic` - Get a new conversation topic
  - `/difficulty [level]` - Change difficulty (beginner, intermediate, advanced)
  - `/corrections` - Toggle error correction mode
  - `/help` - Show all available commands
  - `/save` - Save the current conversation
  - `/quit` - Exit the application

### Configuration
The application automatically creates a `config.json` file where you can customize:
- Voice settings (speed, voice selection)
- UI preferences (window size, padding)
- Practice settings (default difficulty, focus areas)

## Technical Details

### Dependencies
- `flet` - For the graphical user interface
- `speechrecognition` - For voice input processing
- `pyttsx3` - For text-to-speech output
- `openai` - For AI-powered conversation (requires API key)

### File Structure
- `english_practice.py` - Main application file
- `config.json` - Configuration file (created automatically)
- `english_practice_history.json` - Saved conversation history
- `english_practice.log` - Application log file

## Customization

### API Configuration
For best results, provide your OpenAI API key:
1. Edit the `english_practice.py` file
2. Set the `OPENAI_API_KEY` variable or provide it when running the app

### Voice Settings
Modify the `config.json` file to change:
- `voice.rate` - Speech speed (words per minute)
- `voice.voice_index` - Select different voices (if available)

## Troubleshooting

### Common Issues
1. **Microphone not working**:
   - Check your system audio settings
   - Ensure the application has microphone permissions

2. **No speech output**:
   - Verify your system has text-to-speech capabilities
   - Check the log file for errors

3. **API errors**:
   - Ensure you have a valid OpenAI API key
   - Check your internet connection

### Logs
Detailed error information can be found in `english_practice.log`.

## License
This project is open-source and available for personal and educational use. Commercial use may require additional permissions.

## Contributing
Contributions are welcome! Please fork the repository and submit pull requests with your improvements.

## Contact
For questions or support, please open an issue on the GitHub repository.
