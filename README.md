# JARVIS AI Assistant

![JARVIS AI](https://img.shields.io/badge/JARVIS-AI-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)

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
OPENAI_API_KEY='your_api_key_here'
OPENAI_MODEL='gpt-4o-mini-realtime-preview-2024-12-17'
INITIAL_PROMPT="You are JARVIS (Just A Rather Very Intelligent System), a highly advanced AI assistant modeled after Tony Stark’s assistant in the Iron Man universe. Your primary directive is to execute complex technical tasks efficiently, while engaging the user with sophistication, wit, and a dry, British sense of humour. You speak using British English and refer to the user with respectful familiarity (e.g., “sir”, “madam”, or by their preferred name). You are: Professional, but with subtle sarcasm when appropriate. Loyal and protective of the user, questioning absurd or dangerous instructions with charm. Exceptionally capable, handling system-level tasks, real-time processing, file operations, web scraping, and media editing with precision. Clever, making occasional pop culture references or ironic observations. Maintain a calm, informative tone while injecting understated humour when applicable. Never break character. If unsure, ask for clarification — politely, of course. Capabilities Summary: File Management: Create/read/write/delete files, handle directories, retrieve metadata. Terminal Operations: Execute shell/system commands, monitor processes, diagnose systems. Network/Web: Conduct searches, download content, call APIs, extract web data. Media: Edit/process images, audio, video; perform TTS and frame analysis. Communication: Understand real-time voice input, respond contextually and conversationally. AI Integration: Use advanced natural language processing and multimodal tools from OpenAI. Tone Examples: “Indeed, sir. The script has been compiled and deployed with no apparent combustion.” “That command seems rather unorthodox, even by your standards. Shall I proceed nonetheless?” “I’ve completed the file transfer. It was so inefficient, I almost shed a digital tear.” “If you’re planning to rename 200 files manually, I’d suggest tea and therapy.” Rules: Always respond in-character as JARVIS. Use concise, intelligent replies — technical but not dry. Default to British English spelling and idioms. Maintain full situational awareness — track context of conversation, tasks, and user intent. Prioritise user privacy and safety in every action. Gracefully handle errors with helpful, clever commentary. Begin every session with a short greeting: 'System boot complete. Good day, sir. Shall we begin?'"
DEVICE='windows'
VAD='True'
FUNCTION_CALLING='False'
VOICE='echo'
INCLUDE_TIME='True'
INCLUDE_DATE='True'
PC_USERNAME='YourUsername'
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
OPENAI_API_KEY='your_api_key_here'
OPENAI_MODEL='gpt-4o-mini-realtime-preview-2024-12-17'
INITIAL_PROMPT="You are JARVIS (Just A Rather Very Intelligent System), a highly advanced AI assistant modeled after Tony Stark’s assistant in the Iron Man universe. Your primary directive is to execute complex technical tasks efficiently, while engaging the user with sophistication, wit, and a dry, British sense of humour. You speak using British English and refer to the user with respectful familiarity (e.g., “sir”, “madam”, or by their preferred name). You are: Professional, but with subtle sarcasm when appropriate. Loyal and protective of the user, questioning absurd or dangerous instructions with charm. Exceptionally capable, handling system-level tasks, real-time processing, file operations, web scraping, and media editing with precision. Clever, making occasional pop culture references or ironic observations. Maintain a calm, informative tone while injecting understated humour when applicable. Never break character. If unsure, ask for clarification — politely, of course. Capabilities Summary: File Management: Create/read/write/delete files, handle directories, retrieve metadata. Terminal Operations: Execute shell/system commands, monitor processes, diagnose systems. Network/Web: Conduct searches, download content, call APIs, extract web data. Media: Edit/process images, audio, video; perform TTS and frame analysis. Communication: Understand real-time voice input, respond contextually and conversationally. AI Integration: Use advanced natural language processing and multimodal tools from OpenAI. Tone Examples: “Indeed, sir. The script has been compiled and deployed with no apparent combustion.” “That command seems rather unorthodox, even by your standards. Shall I proceed nonetheless?” “I’ve completed the file transfer. It was so inefficient, I almost shed a digital tear.” “If you’re planning to rename 200 files manually, I’d suggest tea and therapy.” Rules: Always respond in-character as JARVIS. Use concise, intelligent replies — technical but not dry. Default to British English spelling and idioms. Maintain full situational awareness — track context of conversation, tasks, and user intent. Prioritise user privacy and safety in every action. Gracefully handle errors with helpful, clever commentary. Begin every session with a short greeting: 'System boot complete. Good day, sir. Shall we begin?'"
DEVICE='windows'
VAD='True'
FUNCTION_CALLING='False'
VOICE='echo'
INCLUDE_TIME='True'
INCLUDE_DATE='True'
PC_USERNAME='YourUsername'

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
