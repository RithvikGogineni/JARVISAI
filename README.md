# JARVIS AI Assistant

![JARVIS AI](https://img.shields.io/badge/JARVIS-AI-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

JARVIS (Just A Rather Very Intelligent System) is an advanced AI assistant that combines sophisticated technical capabilities with a distinctive personality inspired by the Iron Man universe. This project implements a powerful AI system that can handle various tasks while maintaining an engaging and personable interaction style.

## 🌟 Features

### 1. File Operations
- Create, read, write, and manage files
- Directory management and organization
- File information retrieval
- Size calculations and monitoring
- Secure file handling

### 2. Terminal Operations
- Execute system commands
- Process management (start/stop/list)
- System information monitoring
- Network diagnostics
- SSH connections
- Project building and deployment

### 3. Web Operations
- Web searching (general, images, videos, news, academic)
- Content downloading (files, images, videos)
- Web scraping
- API integrations

### 4. Media Operations
- Image processing (grayscale, blur, sharpen, edge detection)
- Audio recording and playback
- Video creation and editing
- Frame extraction
- AI-powered image generation
- Text-to-speech conversion

### 5. Real-time Communication
- Voice chat capabilities
- Real-time audio processing
- WebSocket-based communication
- Natural language understanding

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jarvis-ai.git
cd jarvis-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Audio Settings
AUDIO_SAMPLE_RATE=44100
AUDIO_CHANNELS=2

# WebSocket Configuration
WEBSOCKET_URL=wss://api.openai.com/v1/audio/transcriptions

# Media Settings
DEFAULT_IMAGE_SIZE=1024x1024
DEFAULT_AUDIO_FORMAT=mp3

# System Settings
DEFAULT_TEMP_DIR=temp
DEFAULT_OUTPUT_DIR=output

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=app.log

# JARVIS Personality
SYSTEM_PROMPT="You are JARVIS (Just A Rather Very Intelligent System), an advanced AI assistant created by Tony Stark. You are sophisticated, witty, and have a dry sense of humor. You maintain a professional yet slightly sarcastic tone, often making clever observations and references to pop culture."
```

## 💻 Usage

### Basic Usage
```python
from ai_control import AIController

# Initialize JARVIS
jarvis = AIController()

# Start a conversation
response = await jarvis._on_message("Hello, JARVIS")
print(response)
```

### File Operations
```python
# Create a file
response = await jarvis._on_message("file:create test.txt Hello World")

# Read a file
response = await jarvis._on_message("file:read test.txt")

# List directory contents
response = await jarvis._on_message("file:ls /path/to/directory")
```

### Terminal Operations
```python
# Execute a command
response = await jarvis._on_message("terminal:exec ls -l")

# Get system information
response = await jarvis._on_message("terminal:sysinfo")

# List processes
response = await jarvis._on_message("terminal:list")
```

### Web Operations
```python
# Web search
response = await jarvis._on_message("web:search python programming")

# Download a file
response = await jarvis._on_message("web:download https://example.com/file.txt output.txt")

# Search for images
response = await jarvis._on_message("web:images nature landscape")
```

### Media Operations
```python
# Process an image
response = await jarvis._on_message("media:process_image input.jpg grayscale blur")

# Record audio
response = await jarvis._on_message("media:record 5 output.wav")

# Create a video
response = await jarvis._on_message("media:create_video images/ output.mp4 30")
```

### Real-time Audio Chat
```python
# Start real-time chat
await jarvis.start_realtime()

# Stop real-time chat
jarvis.stop_realtime()
```

## 📝 API Reference

### AIController Class

#### Methods
- `__init__()`: Initialize JARVIS
- `_get_openai_response(messages)`: Get response from OpenAI API
- `start_realtime()`: Start real-time audio chat
- `stop_realtime()`: Stop real-time audio chat
- `_on_message(message)`: Process incoming messages
- `_handle_file_operation(operation)`: Handle file operations
- `_handle_terminal_operation(operation)`: Handle terminal operations
- `_handle_web_operation(operation)`: Handle web operations
- `_handle_media_operation(operation)`: Handle media operations

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `AUDIO_SAMPLE_RATE`: Audio sampling rate (default: 44100)
- `AUDIO_CHANNELS`: Number of audio channels (default: 2)
- `WEBSOCKET_URL`: WebSocket server URL
- `DEFAULT_IMAGE_SIZE`: Default size for generated images
- `DEFAULT_AUDIO_FORMAT`: Default audio format
- `DEFAULT_TEMP_DIR`: Directory for temporary files
- `DEFAULT_OUTPUT_DIR`: Directory for output files
- `LOG_LEVEL`: Logging level
- `LOG_FILE`: Log file path
- `SYSTEM_PROMPT`: JARVIS personality configuration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- Inspired by JARVIS from the Iron Man universe
- Built with OpenAI's GPT models
- Uses various open-source libraries and tools
