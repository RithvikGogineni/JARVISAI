import os
import platform
import psutil
import pyautogui
import schedule
import time
from typing import Dict, Any, Optional, List
import subprocess
from datetime import datetime

# Platform-specific imports
system = platform.system().lower()
if system == 'windows':
    import keyboard
    import mouse
elif system == 'linux':
    import keyboard
    import mouse
    import Xlib
elif system == 'darwin':
    # macOS doesn't support mouse/keyboard packages
    pass

class SystemController:
    """
    System controller class that provides platform-agnostic system control functionality.
    Handles volume, brightness, power management, window management, and process control.
    """
    
    def __init__(self):
        """Initialize the system controller with platform-specific configurations."""
        self.system = system
        self._setup_platform_specific_imports()
        self._validate_platform_support()
    
    def _setup_platform_specific_imports(self):
        """Setup platform-specific imports and configurations."""
        self.platform_supported = True
        self.supported_features = {
            'volume': True,
            'brightness': True,
            'power': True,
            'window': True,
            'process': True
        }
        
        try:
            if self.system == 'windows':
                import win32api
                import win32con
                self.win32api = win32api
                self.win32con = win32con
            elif self.system == 'linux':
                import Xlib
                self.Xlib = Xlib
            elif self.system == 'darwin':
                # macOS specific setup
                pass
            else:
                self.platform_supported = False
                self.supported_features = {k: False for k in self.supported_features}
        except ImportError as e:
            print(f"Warning: Some platform-specific features may not be available: {str(e)}")
            self.platform_supported = False

    def _validate_platform_support(self):
        """Validate platform support for different features."""
        if not self.platform_supported:
            return

        # Check volume control support
        try:
            if self.system == 'darwin':
                subprocess.run(['osascript', '-e', 'get volume settings'], capture_output=True)
            elif self.system == 'linux':
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '0%'], capture_output=True)
        except Exception:
            self.supported_features['volume'] = False

        # Check brightness control support
        try:
            if self.system == 'darwin':
                subprocess.run(['osascript', '-e', 'tell application "System Events" to get brightness'], capture_output=True)
            elif self.system == 'linux':
                subprocess.run(['xrandr', '--output', '$(xrandr -q | grep " connected" | cut -d " " -f1)', '--brightness', '1'], capture_output=True)
        except Exception:
            self.supported_features['brightness'] = False

    def _execute_osascript(self, script: str) -> str:
        """
        Execute AppleScript command on macOS.
        
        Args:
            script (str): The AppleScript command to execute.
            
        Returns:
            str: Command output or error message.
        """
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                 capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error executing AppleScript: {str(e)}"

    def control_volume(self, action: str, value: Optional[int] = None) -> str:
        """
        Control system volume.
        
        Args:
            action (str): 'mute', 'unmute', 'up', 'down', 'set'
            value (Optional[int]): Volume level (0-100) for 'set' action
            
        Returns:
            str: Status message
        """
        if not self.supported_features['volume']:
            return "Volume control is not supported on this system"

        try:
            if self.system == 'windows':
                if action == 'mute':
                    keyboard.press_and_release('volume mute')
                elif action == 'up':
                    keyboard.press_and_release('volume up')
                elif action == 'down':
                    keyboard.press_and_release('volume down')
                elif action == 'set' and value is not None:
                    cmd = f'(New-Object -ComObject WScript.Shell).SendKeys([char]173); (New-Object -ComObject WScript.Shell).SendKeys([char]174); (New-Object -ComObject WScript.Shell).SendKeys([char]175);'
                    subprocess.run(['powershell', '-Command', cmd], capture_output=True)
            elif self.system == 'darwin':
                if action == 'mute':
                    self._execute_osascript('set volume output muted true')
                elif action == 'unmute':
                    self._execute_osascript('set volume output muted false')
                elif action == 'set' and value is not None:
                    self._execute_osascript(f'set volume output volume {value}')
            elif self.system == 'linux':
                if action == 'mute':
                    os.system('amixer -D pulse sset Master mute')
                elif action == 'unmute':
                    os.system('amixer -D pulse sset Master unmute')
                elif action == 'set' and value is not None:
                    os.system(f'amixer -D pulse sset Master {value}%')
            return f"Volume {action} successful"
        except Exception as e:
            return f"Error controlling volume: {str(e)}"

    def control_brightness(self, action: str, value: Optional[int] = None) -> str:
        """
        Control screen brightness.
        
        Args:
            action (str): 'up', 'down', 'set'
            value (Optional[int]): Brightness level (0-100) for 'set' action
            
        Returns:
            str: Status message
        """
        if not self.supported_features['brightness']:
            return "Brightness control is not supported on this system"

        try:
            if self.system == 'windows':
                if action == 'set' and value is not None:
                    cmd = f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{value})'
                    subprocess.run(['powershell', '-Command', cmd], capture_output=True)
            elif self.system == 'darwin':
                if action == 'set' and value is not None:
                    try:
                        os.system(f'brightness {value/100}')
                    except:
                        self._execute_osascript(f'tell application "System Events" to set brightness to {value/100}')
            elif self.system == 'linux':
                if action == 'set' and value is not None:
                    os.system(f'xrandr --output $(xrandr -q | grep " connected" | cut -d " " -f1) --brightness {value/100}')
            return f"Brightness {action} successful"
        except Exception as e:
            return f"Error controlling brightness: {str(e)}"

    def power_management(self, action: str) -> str:
        """
        Control system power state.
        
        Args:
            action (str): 'sleep', 'shutdown', 'restart', 'hibernate'
            
        Returns:
            str: Status message
        """
        if not self.supported_features['power']:
            return "Power management is not supported on this system"

        try:
            if self.system == 'windows':
                if action == 'sleep':
                    os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
                elif action == 'shutdown':
                    os.system('shutdown /s /t 0')
                elif action == 'restart':
                    os.system('shutdown /r /t 0')
                elif action == 'hibernate':
                    os.system('shutdown /h')
            elif self.system == 'darwin':
                if action == 'sleep':
                    self._execute_osascript('tell application "System Events" to sleep')
                elif action == 'shutdown':
                    self._execute_osascript('tell application "System Events" to shut down')
                elif action == 'restart':
                    self._execute_osascript('tell application "System Events" to restart')
            elif self.system == 'linux':
                if action == 'sleep':
                    os.system('systemctl suspend')
                elif action == 'shutdown':
                    os.system('shutdown -h now')
                elif action == 'restart':
                    os.system('shutdown -r now')
            return f"Power management action {action} initiated"
        except Exception as e:
            return f"Error in power management: {str(e)}"

    def window_management(self, action: str, window_name: Optional[str] = None) -> str:
        """
        Manage application windows.
        
        Args:
            action (str): 'minimize', 'maximize', 'close', 'focus'
            window_name (Optional[str]): Name of the window to manage
            
        Returns:
            str: Status message
        """
        if not self.supported_features['window']:
            return "Window management is not supported on this system"

        try:
            if window_name:
                if self.system == 'darwin':
                    if action == 'minimize':
                        self._execute_osascript(f'tell application "System Events" to set visible of process "{window_name}" to false')
                    elif action == 'maximize':
                        self._execute_osascript(f'tell application "System Events" to set visible of process "{window_name}" to true')
                    elif action == 'close':
                        self._execute_osascript(f'tell application "{window_name}" to quit')
                    elif action == 'focus':
                        self._execute_osascript(f'tell application "{window_name}" to activate')
                else:
                    windows = pyautogui.getWindowsWithTitle(window_name)
                    if not windows:
                        return f"Window '{window_name}' not found"
                    window = windows[0]
                    
                    if action == 'minimize':
                        window.minimize()
                    elif action == 'maximize':
                        window.maximize()
                    elif action == 'close':
                        window.close()
                    elif action == 'focus':
                        window.activate()
                return f"Window {action} successful"
            return "No window specified"
        except Exception as e:
            return f"Error in window management: {str(e)}"

    def process_control(self, action: str, process_name: str) -> str:
        """
        Control system processes.
        
        Args:
            action (str): 'start', 'stop', 'restart', 'status'
            process_name (str): Name of the process to control
            
        Returns:
            str: Status message
        """
        if not self.supported_features['process']:
            return "Process control is not supported on this system"

        try:
            if action == 'start':
                if self.system == 'windows':
                    os.system(f'start {process_name}')
                else:
                    os.system(f'{process_name} &')
            elif action == 'stop':
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        proc.terminate()
            elif action == 'restart':
                self.process_control('stop', process_name)
                time.sleep(1)
                self.process_control('start', process_name)
            elif action == 'status':
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        return f"Process {process_name} is running"
                return f"Process {process_name} is not running"
            return f"Process {action} successful"
        except Exception as e:
            return f"Error in process control: {str(e)}"

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dict[str, Any]: System information including platform, features, and status
        """
        return {
            'platform': self.system,
            'supported_features': self.supported_features,
            'platform_supported': self.platform_supported,
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

# Create a singleton instance
system_controller = SystemController() 