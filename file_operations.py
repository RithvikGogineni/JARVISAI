import os
import shutil
from typing import Optional, List, Dict, Any
from datetime import datetime

class FileOperations:
    """
    A class to handle various file operations including creating, reading, writing,
    and managing files and directories.
    """
    
    def create_file(self, path: str, content: str = "") -> str:
        """
        Create a new file with optional content.
        
        Args:
            path (str): Path where the file should be created
            content (str, optional): Content to write to the file. Defaults to "".
            
        Returns:
            str: Success or error message
        """
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"File created successfully at {path}"
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def read_file(self, path: str) -> str:
        """
        Read content from a file.
        
        Args:
            path (str): Path of the file to read
            
        Returns:
            str: File content or error message
        """
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, path: str, content: str) -> str:
        """
        Write content to a file, overwriting existing content.
        
        Args:
            path (str): Path of the file to write to
            content (str): Content to write
            
        Returns:
            str: Success or error message
        """
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"File written successfully at {path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"

    def append_file(self, path: str, content: str) -> str:
        """
        Append content to an existing file.
        
        Args:
            path (str): Path of the file to append to
            content (str): Content to append
            
        Returns:
            str: Success or error message
        """
        try:
            with open(path, 'a') as f:
                f.write(content)
            return f"Content appended successfully to {path}"
        except Exception as e:
            return f"Error appending to file: {str(e)}"

    def delete_file(self, path: str) -> str:
        """
        Delete a file.
        
        Args:
            path (str): Path of the file to delete
            
        Returns:
            str: Success or error message
        """
        try:
            os.remove(path)
            return f"File deleted successfully: {path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    def create_directory(self, path: str) -> str:
        """
        Create a new directory.
        
        Args:
            path (str): Path where the directory should be created
            
        Returns:
            str: Success or error message
        """
        try:
            os.makedirs(path, exist_ok=True)
            return f"Directory created successfully at {path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"

    def list_directory(self, path: str) -> str:
        """
        List contents of a directory.
        
        Args:
            path (str): Path of the directory to list
            
        Returns:
            str: Directory contents or error message
        """
        try:
            items = os.listdir(path)
            result = []
            for item in items:
                full_path = os.path.join(path, item)
                is_dir = os.path.isdir(full_path)
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                result.append({
                    'name': item,
                    'type': 'directory' if is_dir else 'file',
                    'size': size,
                    'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
                })
            return str(result)
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    def delete_directory(self, path: str) -> str:
        """
        Delete a directory and its contents.
        
        Args:
            path (str): Path of the directory to delete
            
        Returns:
            str: Success or error message
        """
        try:
            shutil.rmtree(path)
            return f"Directory deleted successfully: {path}"
        except Exception as e:
            return f"Error deleting directory: {str(e)}"

    def get_file_info(self, path: str) -> str:
        """
        Get information about a file.
        
        Args:
            path (str): Path of the file to get info for
            
        Returns:
            str: File information or error message
        """
        try:
            stats = os.stat(path)
            info = {
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'accessed': datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'permissions': oct(stats.st_mode)[-3:]
            }
            return str(info)
        except Exception as e:
            return f"Error getting file info: {str(e)}"

    def get_directory_size(self, path: str) -> str:
        """
        Calculate the total size of a directory.
        
        Args:
            path (str): Path of the directory to calculate size for
            
        Returns:
            str: Directory size or error message
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return f"Directory size: {total_size} bytes"
        except Exception as e:
            return f"Error calculating directory size: {str(e)}" 