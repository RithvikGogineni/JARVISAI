import os
from dotenv import load_dotenv
import json
import base64
import threading
import websocket
import sounddevice as sd
import numpy as np
import datetime
import subprocess
import time
from queue import Queue
from typing import Dict, Any, Optional, Callable
import openai
from system_control import SystemController
from file_operations import FileOperations
from terminal_operations import TerminalOperations
from web_operations import WebOperations
from media_operations import MediaOperations
import soundfile as sf
import websockets
import asyncio

load_dotenv()

class AIController:
    """
    AIController class that integrates AI capabilities with system control functionality.
    This class provides both text and audio-based interaction with system control features.
    """
    
    def __init__(self, api_key: str, device: str = "unknown", model: str = "gpt-4o-mini-realtime-preview-2024-12-17",
                 initial_prompt: str = "", include_date: bool = True, include_time: bool = True,
                 mode: str = "text", function_calling: bool = True, voice: str = "echo"):
        """
        Initialize the AI Controller with system control capabilities.
        
        Args:
            api_key (str): OpenAI API key.
            device (str, optional): Device identifier. Defaults to "unknown".
            model (str, optional): OpenAI model to use. Defaults to "gpt-4o-mini-realtime-preview-2024-12-17".
            initial_prompt (str, optional): Initial system prompt. Defaults to "".
            include_date (bool, optional): Whether to include date in messages. Defaults to True.
            include_time (bool, optional): Whether to include time in messages. Defaults to True.
            mode (str, optional): "realtime" for audio chat or "text" for text-only chat. Defaults to "text".
            function_calling (bool, optional): Enable or disable function calling. Defaults to True.
            voice (str, optional): Voice to use for audio responses. Defaults to "echo".
        """
        self.api_key = api_key
        self.device = device
        self.model = model
        self.initial_prompt = initial_prompt
        self.include_date = include_date
        self.include_time = include_time
        self.mode = mode
        self.function_calling = function_calling
        self.voice = voice
        self.pc_username = os.getenv("PC_USERNAME", "YourUsername")

        # Initialize system controller
        self.system_controller = SystemController()
        self.file_operations = FileOperations()
        self.terminal_operations = TerminalOperations()
        self.web_operations = WebOperations()
        self.media_operations = MediaOperations()

        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.dtype = np.int16
        self.audio_queue = Queue()
        self.is_recording = False
        
        # Initialize WebSocket
        self.ws = None
        self.ws_thread = None

        # Initialize messages with system information
        self.messages = self._initialize_messages()
        
        # Define available functions
        self.available_functions = {
            # System Control Functions
            "control_volume": self.handle_system_control,
            "control_brightness": self.handle_system_control,
            "power_management": self.handle_system_control,
            "window_management": self.handle_system_control,
            "process_control": self.handle_system_control,
            
            # File Operations
            "create_file": self.handle_file_operation,
            "read_file": self.handle_file_operation,
            "write_file": self.handle_file_operation,
            "append_file": self.handle_file_operation,
            "delete_file": self.handle_file_operation,
            "create_directory": self.handle_file_operation,
            "list_directory": self.handle_file_operation,
            "delete_directory": self.handle_file_operation,
            "get_file_info": self.handle_file_operation,
            "get_directory_size": self.handle_file_operation,
            
            # Terminal Operations
            "execute_command": self.handle_terminal_operation,
            "execute_command_with_output": self.handle_terminal_operation,
            "start_process": self.handle_terminal_operation,
            "stop_process": self.handle_terminal_operation,
            "list_processes": self.handle_terminal_operation,
            "get_system_info": self.handle_terminal_operation,
            "get_network_info": self.handle_terminal_operation,
            
            # Web Operations
            "search_web": self.handle_web_operation,
            "search_images": self.handle_web_operation,
            "search_videos": self.handle_web_operation,
            "search_news": self.handle_web_operation,
            "search_academic": self.handle_web_operation,
            "download_file": self.handle_web_operation,
            "download_image": self.handle_web_operation,
            "download_video": self.handle_web_operation,
            
            # Media Operations
            "generate_image": self.handle_media_operation,
            "edit_image": self.handle_media_operation,
            "analyze_image": self.handle_media_operation,
            "generate_audio": self.handle_media_operation,
            "transcribe_audio": self.handle_media_operation,
            "edit_audio": self.handle_media_operation
        }

    def _initialize_messages(self) -> list:
        """Initialize messages with system information and available functions."""
        messages = [
            {
                "role": "system",
                "content": f"""You are an AI assistant with control over the user's system. 
                You can perform various operations including file management, terminal commands, 
                web operations, media handling, and system control.
                
                Current system: {self.device}
                Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                You have access to the following operations:
                1. System Control: volume, brightness, power, window, and process management
                2. File Operations: create, read, write, append, delete files and directories
                3. Terminal Operations: execute commands, manage processes, get system info
                4. Web Operations: search, download content
                5. Media Operations: generate, edit, analyze images and audio
                
                Always confirm the operation before executing it and provide feedback after completion."""
            }
        ]
        
        if self.initial_prompt:
            messages.append({"role": "user", "content": self.initial_prompt})
            messages.append({"role": "assistant", "content": "I understand. How can I help you?"})
        
        return messages

    def append_tools_to_message(self, message: str) -> str:
        """
        Append date and time to messages if enabled.
        
        Args:
            message (str): The original message.
            
        Returns:
            str: Message with date and time appended if enabled.
        """
        now = datetime.datetime.now()
        additions = []
        if self.include_date:
            additions.append(f"Date: {now.strftime('%Y-%m-%d')}")
        if self.include_time:
            additions.append(f"Time: {now.strftime('%H:%M:%S')}")
        if additions:
            return f"{message} ({' | '.join(additions)})"
        return message

    def send_text_message(self, message: str, role: str = "user"):
        """
        Send a text message through the WebSocket connection.
        
        Args:
            message (str): The message to send.
            role (str, optional): The role of the message sender. Defaults to "user".
        """
        full_text = self.append_tools_to_message(message)
        conversation_event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": role,
                "content": [
                    {"type": "input_text", "text": full_text}
                ]
            }
        }
        self.ws.send(json.dumps(conversation_event))
        response_create_event = {
            "type": "response.create",
            "response": {
                "modalities": ["text"]
            }
        }
        self.ws.send(json.dumps(response_create_event))

    def ask_sync(self, prompt: str) -> str:
        """Send a text message and get a synchronous response"""
        try:
            # Add system control functions to the message
            message = self._append_tools_to_message(prompt)
            
            # Send message and get response
            response = self._get_openai_response(message)
            
            # Handle any system control actions in the response
            if self.function_calling:
                self._handle_system_control(response)
            
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def _append_tools_to_message(self, prompt: str) -> str:
        """Append available system control functions to the message"""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "control_volume",
                    "description": "Control system volume",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["mute", "unmute", "up", "down", "set"],
                                "description": "Volume control action"
                            },
                            "value": {
                                "type": "integer",
                                "description": "Volume value (0-100) for 'set' action"
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            # Add other system control functions here
        ]
        
        return f"{prompt}\n\nAvailable functions: {json.dumps(tools)}"

    def _get_openai_response(self, message: str) -> str:
        """Get response from OpenAI API"""
        # Implementation depends on your OpenAI API version
        # This is a placeholder
        return "Response from OpenAI"

    def _handle_system_control(self, response: str):
        """Handle system control actions in the response"""
        try:
            # Parse response for function calls
            # Implementation depends on your OpenAI API version
            pass
        except Exception as e:
            print(f"Error handling system control: {e}")

    def handle_system_control(self, action: str, params: Dict[str, Any]) -> str:
        """Handle system control actions"""
        try:
            if action == "volume":
                return self.system_controller.control_volume(**params)
            elif action == "brightness":
                return self.system_controller.control_brightness(**params)
            elif action == "power":
                return self.system_controller.power_management(**params)
            elif action == "window":
                return self.system_controller.window_management(**params)
            elif action == "process":
                return self.system_controller.process_control(**params)
            else:
                return f"Unknown action: {action}"
        except Exception as e:
            return f"Error executing {action}: {str(e)}"

    def handle_file_operation(self, operation: str, params: Dict[str, Any]) -> str:
        """Handle file operations."""
        try:
            if operation == "create_file":
                return self.file_operations.create_file(params.get("path"), params.get("content"))
            elif operation == "read_file":
                return self.file_operations.read_file(params.get("path"))
            elif operation == "write_file":
                return self.file_operations.write_file(params.get("path"), params.get("content"))
            elif operation == "append_file":
                return self.file_operations.append_file(params.get("path"), params.get("content"))
            elif operation == "delete_file":
                return self.file_operations.delete_file(params.get("path"))
            elif operation == "create_directory":
                return self.file_operations.create_directory(params.get("path"))
            elif operation == "list_directory":
                return self.file_operations.list_directory(params.get("path"))
            elif operation == "delete_directory":
                return self.file_operations.delete_directory(params.get("path"))
            elif operation == "get_file_info":
                return self.file_operations.get_file_info(params.get("path"))
            elif operation == "get_directory_size":
                return self.file_operations.get_directory_size(params.get("path"))
            return "Invalid file operation"
        except Exception as e:
            return f"Error in file operation: {str(e)}"

    def handle_terminal_operation(self, operation: str, params: Dict[str, Any]) -> str:
        """Handle terminal operations."""
        try:
            if operation == "execute_command":
                return self.terminal_operations.execute_command(params.get("command"))
            elif operation == "execute_command_with_output":
                return self.terminal_operations.execute_command_with_output(params.get("command"))
            elif operation == "start_process":
                return self.terminal_operations.start_process(params.get("process_name"))
            elif operation == "stop_process":
                return self.terminal_operations.stop_process(params.get("process_name"))
            elif operation == "list_processes":
                return self.terminal_operations.list_processes()
            elif operation == "get_system_info":
                return self.terminal_operations.get_system_info()
            elif operation == "get_network_info":
                return self.terminal_operations.get_network_info()
            return "Invalid terminal operation"
        except Exception as e:
            return f"Error in terminal operation: {str(e)}"

    def handle_web_operation(self, operation: str, params: Dict[str, Any]) -> str:
        """Handle web operations."""
        try:
            if operation == "search_web":
                return self.web_operations.search_web(params.get("query"))
            elif operation == "search_images":
                return self.web_operations.search_images(params.get("query"))
            elif operation == "search_videos":
                return self.web_operations.search_videos(params.get("query"))
            elif operation == "search_news":
                return self.web_operations.search_news(params.get("query"))
            elif operation == "search_academic":
                return self.web_operations.search_academic(params.get("query"))
            elif operation == "download_file":
                return self.web_operations.download_file(params.get("url"), params.get("path"))
            elif operation == "download_image":
                return self.web_operations.download_image(params.get("url"), params.get("path"))
            elif operation == "download_video":
                return self.web_operations.download_video(params.get("url"), params.get("path"))
            return "Invalid web operation"
        except Exception as e:
            return f"Error in web operation: {str(e)}"

    def handle_media_operation(self, operation: str, params: Dict[str, Any]) -> str:
        """Handle media operations."""
        try:
            if operation == "generate_image":
                return self.media_operations.generate_image(params.get("prompt"))
            elif operation == "edit_image":
                return self.media_operations.edit_image(params.get("path"), params.get("instruction"))
            elif operation == "analyze_image":
                return self.media_operations.analyze_image(params.get("path"))
            elif operation == "generate_audio":
                return self.media_operations.generate_audio(params.get("text"))
            elif operation == "transcribe_audio":
                return self.media_operations.transcribe_audio(params.get("path"))
            elif operation == "edit_audio":
                return self.media_operations.edit_audio(params.get("path"), params.get("instruction"))
            return "Invalid media operation"
        except Exception as e:
            return f"Error in media operation: {str(e)}"

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio recording"""
        if status:
            print(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())

    def start_realtime(self):
        """Start realtime audio processing"""
        if self.mode != "realtime":
            return
        
        # Initialize audio stream
        self.audio_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._audio_callback
        )
        
        # Start WebSocket connection
        self.ws = websocket.WebSocketApp(
            f"wss://api.openai.com/v1/audio/speech",
            header={"Authorization": f"Bearer {self.api_key}"},
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        # Start audio recording
        self.is_recording = True
        self.audio_stream.start()

    def stop_realtime(self):
        """Stop realtime audio processing"""
        self.is_recording = False
        if hasattr(self, 'audio_stream'):
            self.audio_stream.stop()
            self.audio_stream.close()
        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join()

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            if "text" in data:
                print(f"AI: {data['text']}")
            elif "audio" in data:
                audio_data = base64.b64decode(data["audio"])
                # Play audio using sounddevice
                sd.play(np.frombuffer(audio_data, dtype=np.int16), self.sample_rate)
                sd.wait()
        except Exception as e:
            print(f"Error processing message: {e}")

    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        print("WebSocket connection closed")

# Create a singleton instance
ai_controller = AIController(api_key=os.getenv("OPENAI_API_KEY")) 