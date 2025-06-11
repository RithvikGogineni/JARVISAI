import os
from typing import Dict, Any, Optional, List, Tuple
import requests
import json
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips
import soundfile as sf
import librosa
import torch
import openai
from dotenv import load_dotenv
import sounddevice as sd
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

class MediaOperations:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Initialize models for image generation
        self.image_models = {
            'dalle': 'dall-e-3',
            'stable_diffusion': 'stabilityai/stable-diffusion-2-1'
        }
        
        # Initialize audio models
        self.audio_models = {
            'whisper': 'openai/whisper-large-v3',
            'tts': 'microsoft/speecht5_tts'
        }

        self.audio_settings = {
            'sample_rate': 44100,
            'channels': 2,
            'dtype': np.float32
        }

    def generate_image(self, prompt: str, model: str = 'dalle', size: str = '1024x1024', 
                      style: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate images using various AI models.
        Args:
            prompt: Description of the image to generate
            model: Model to use ('dalle', 'stable_diffusion')
            size: Image size (e.g., '1024x1024')
            style: Optional style to apply
        """
        try:
            if model == 'dalle':
                response = openai.Image.create(
                    prompt=prompt,
                    n=1,
                    size=size,
                    style=style
                )
                return {
                    "success": True,
                    "url": response['data'][0]['url']
                }
            elif model == 'stable_diffusion':
                # Implementation for Stable Diffusion
                pass
            else:
                return {"error": f"Unsupported model: {model}"}
        except Exception as e:
            return {"error": str(e)}

    def generate_audio(self, text: str, voice: str = 'alloy', model: str = 'tts') -> Dict[str, Any]:
        """
        Generate audio from text using various TTS models.
        Args:
            text: Text to convert to speech
            voice: Voice to use
            model: Model to use ('tts', 'whisper')
        """
        try:
            if model == 'tts':
                response = openai.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text
                )
                output_path = f"generated_audio_{voice}.mp3"
                response.stream_to_file(output_path)
                return {
                    "success": True,
                    "path": output_path
                }
            else:
                return {"error": f"Unsupported model: {model}"}
        except Exception as e:
            return {"error": str(e)}

    def process_image(self, image_path: str, operations: List[str]) -> str:
        """
        Process an image with various operations.
        
        Args:
            image_path (str): Path to the input image
            operations (List[str]): List of operations to perform
            
        Returns:
            str: Path to the processed image or error message
        """
        try:
            # Read the image
            img = cv2.imread(image_path)
            if img is None:
                return f"Error: Could not read image from {image_path}"
            
            # Apply operations
            for operation in operations:
                if operation == 'grayscale':
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                elif operation == 'blur':
                    img = cv2.GaussianBlur(img, (5, 5), 0)
                elif operation == 'sharpen':
                    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                    img = cv2.filter2D(img, -1, kernel)
                elif operation == 'edge':
                    img = cv2.Canny(img, 100, 200)
            
            # Save the processed image
            output_path = os.path.splitext(image_path)[0] + '_processed' + os.path.splitext(image_path)[1]
            cv2.imwrite(output_path, img)
            return f"Image processed successfully. Saved to {output_path}"
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def process_video(self, video_path: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process videos with various operations.
        Args:
            video_path: Path to the video
            operations: List of operations to apply
        """
        try:
            video = VideoFileClip(video_path)
            
            for op in operations:
                if op['type'] == 'trim':
                    video = video.subclip(op['start'], op['end'])
                elif op['type'] == 'resize':
                    video = video.resize(width=op['width'], height=op['height'])
                elif op['type'] == 'speed':
                    video = video.speedx(op['factor'])
                elif op['type'] == 'add_audio':
                    audio = AudioFileClip(op['audio_path'])
                    video = video.set_audio(audio)
            
            output_path = f"processed_{os.path.basename(video_path)}"
            video.write_videofile(output_path)
            return {
                "success": True,
                "path": output_path
            }
        except Exception as e:
            return {"error": str(e)}

    def process_audio(self, audio_path: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process audio files with various operations.
        Args:
            audio_path: Path to the audio file
            operations: List of operations to apply
        """
        try:
            y, sr = librosa.load(audio_path)
            
            for op in operations:
                if op['type'] == 'trim':
                    y = y[int(op['start'] * sr):int(op['end'] * sr)]
                elif op['type'] == 'speed':
                    y = librosa.effects.time_stretch(y, rate=op['factor'])
                elif op['type'] == 'pitch':
                    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=op['steps'])
                elif op['type'] == 'volume':
                    y = y * op['factor']
            
            output_path = f"processed_{os.path.basename(audio_path)}"
            sf.write(output_path, y, sr)
            return {
                "success": True,
                "path": output_path
            }
        except Exception as e:
            return {"error": str(e)}

    def create_video(self, image_paths: List[str], output_path: str, fps: int = 30) -> str:
        """
        Create a video from a sequence of images.
        
        Args:
            image_paths (List[str]): List of paths to input images
            output_path (str): Path to save the output video
            fps (int): Frames per second
            
        Returns:
            str: Success or error message
        """
        try:
            # Read the first image to get dimensions
            first_image = cv2.imread(image_paths[0])
            if first_image is None:
                return f"Error: Could not read first image from {image_paths[0]}"
            
            height, width, layers = first_image.shape
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Add each image to the video
            for image_path in image_paths:
                img = cv2.imread(image_path)
                if img is not None:
                    video.write(img)
            
            # Release the video writer
            video.release()
            return f"Video created successfully. Saved to {output_path}"
        except Exception as e:
            return f"Error creating video: {str(e)}"

    def generate_3d_model(self, prompt: str, output_format: str = 'obj') -> Dict[str, Any]:
        """
        Generate 3D models using AI.
        Args:
            prompt: Description of the 3D model
            output_format: Output format ('obj', 'stl', 'glb')
        """
        try:
            # Implementation for 3D model generation
            # This would typically involve calling a 3D model generation API
            pass
        except Exception as e:
            return {"error": str(e)}

    def record_audio(self, duration: float, output_path: str) -> str:
        """
        Record audio for a specified duration.
        
        Args:
            duration (float): Duration of recording in seconds
            output_path (str): Path to save the recorded audio
            
        Returns:
            str: Success or error message
        """
        try:
            # Record audio
            recording = sd.rec(
                int(duration * self.audio_settings['sample_rate']),
                samplerate=self.audio_settings['sample_rate'],
                channels=self.audio_settings['channels'],
                dtype=self.audio_settings['dtype']
            )
            sd.wait()
            
            # Save the recording
            sf.write(output_path, recording, self.audio_settings['sample_rate'])
            return f"Audio recorded successfully. Saved to {output_path}"
        except Exception as e:
            return f"Error recording audio: {str(e)}"
    
    def play_audio(self, audio_path: str) -> str:
        """
        Play an audio file.
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            str: Success or error message
        """
        try:
            # Read the audio file
            data, samplerate = sf.read(audio_path)
            
            # Play the audio
            sd.play(data, samplerate)
            sd.wait()
            return "Audio played successfully"
        except Exception as e:
            return f"Error playing audio: {str(e)}"

    def extract_frames(self, video_path: str, output_dir: str, fps: int = 1) -> str:
        """
        Extract frames from a video.
        
        Args:
            video_path (str): Path to the input video
            output_dir (str): Directory to save the extracted frames
            fps (int): Frames per second to extract
            
        Returns:
            str: Success or error message
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Open the video
            video = cv2.VideoCapture(video_path)
            if not video.isOpened():
                return f"Error: Could not open video {video_path}"
            
            # Get video properties
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            video_fps = video.get(cv2.CAP_PROP_FPS)
            frame_interval = int(video_fps / fps)
            
            # Extract frames
            frame_number = 0
            while True:
                success, frame = video.read()
                if not success:
                    break
                
                if frame_number % frame_interval == 0:
                    output_path = os.path.join(output_dir, f"frame_{frame_number:04d}.jpg")
                    cv2.imwrite(output_path, frame)
                
                frame_number += 1
            
            # Release the video
            video.release()
            return f"Frames extracted successfully to {output_dir}"
        except Exception as e:
            return f"Error extracting frames: {str(e)}"

# Create a singleton instance
media_operations = MediaOperations() 