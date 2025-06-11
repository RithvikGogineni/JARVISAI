import os
import subprocess
import paramiko
import asyncio
import json
from typing import Dict, Any, List, Optional, Union
import shlex
from pathlib import Path
import docker
import git
import yaml
import requests
from datetime import datetime
import logging
import platform
import psutil

class TerminalOperations:
    def __init__(self):
        self.ssh_clients = {}
        self.docker_client = docker.from_env() if self._check_docker() else None
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('TerminalOperations')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('terminal_operations.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _check_docker(self) -> bool:
        """Check if Docker is installed and running."""
        try:
            subprocess.run(['docker', 'info'], capture_output=True, check=True)
            return True
        except:
            return False

    def execute_command(self, command: str) -> str:
        """
        Execute a terminal command.
        
        Args:
            command (str): Command to execute
            
        Returns:
            str: Command output or error message
        """
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def execute_command_with_output(self, command: str) -> str:
        """
        Execute a terminal command and return both stdout and stderr.
        
        Args:
            command (str): Command to execute
            
        Returns:
            str: Command output including both stdout and stderr
        """
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = f"Return code: {result.returncode}\n"
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}"
            return output
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def start_process(self, process_name: str) -> str:
        """
        Start a new process.
        
        Args:
            process_name (str): Name of the process to start
            
        Returns:
            str: Success or error message
        """
        try:
            subprocess.Popen(process_name, shell=True)
            return f"Process started: {process_name}"
        except Exception as e:
            return f"Error starting process: {str(e)}"

    def stop_process(self, process_name: str) -> str:
        """
        Stop a running process.
        
        Args:
            process_name (str): Name of the process to stop
            
        Returns:
            str: Success or error message
        """
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == process_name:
                    proc.terminate()
                    return f"Process stopped: {process_name}"
            return f"Process not found: {process_name}"
        except Exception as e:
            return f"Error stopping process: {str(e)}"

    def list_processes(self) -> str:
        """
        List all running processes.
        
        Returns:
            str: List of processes or error message
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            return str(processes)
        except Exception as e:
            return f"Error listing processes: {str(e)}"

    def get_system_info(self) -> str:
        """
        Get system information.
        
        Returns:
            str: System information or error message
        """
        try:
            info = {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
            return str(info)
        except Exception as e:
            return f"Error getting system info: {str(e)}"

    def get_network_info(self) -> str:
        """
        Get network information.
        
        Returns:
            str: Network information or error message
        """
        try:
            info = {
                'interfaces': psutil.net_if_addrs(),
                'connections': psutil.net_connections(),
                'io_counters': psutil.net_io_counters()
            }
            return str(info)
        except Exception as e:
            return f"Error getting network info: {str(e)}"

    def ssh_connect(self, host: str, username: str, password: Optional[str] = None,
                   key_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to a remote host via SSH.
        Args:
            host: Host address
            username: Username for authentication
            password: Password for authentication
            key_filename: Path to SSH key file
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_filename:
                client.connect(host, username=username, key_filename=key_filename)
            else:
                client.connect(host, username=username, password=password)
            
            self.ssh_clients[host] = client
            return {"success": True, "message": f"Connected to {host}"}
        except Exception as e:
            self.logger.error(f"Error connecting to {host}: {str(e)}")
            return {"error": str(e)}

    def ssh_execute(self, host: str, command: str) -> Dict[str, Any]:
        """
        Execute a command on a remote host.
        Args:
            host: Host to execute command on
            command: Command to execute
        """
        try:
            if host not in self.ssh_clients:
                return {"error": f"No connection to {host}"}

            stdin, stdout, stderr = self.ssh_clients[host].exec_command(command)
            return {
                "success": True,
                "stdout": stdout.read().decode(),
                "stderr": stderr.read().decode(),
                "return_code": stdout.channel.recv_exit_status()
            }
        except Exception as e:
            self.logger.error(f"Error executing command on {host}: {str(e)}")
            return {"error": str(e)}

    def build_project(self, project_path: str, build_type: str = 'auto') -> Dict[str, Any]:
        """
        Build a project based on its type.
        Args:
            project_path: Path to the project
            build_type: Type of build ('auto', 'python', 'node', 'java', 'docker')
        """
        try:
            if build_type == 'auto':
                build_type = self._detect_project_type(project_path)

            if build_type == 'python':
                return self._build_python_project(project_path)
            elif build_type == 'node':
                return self._build_node_project(project_path)
            elif build_type == 'java':
                return self._build_java_project(project_path)
            elif build_type == 'docker':
                return self._build_docker_project(project_path)
            else:
                return {"error": f"Unsupported build type: {build_type}"}
        except Exception as e:
            self.logger.error(f"Error building project: {str(e)}")
            return {"error": str(e)}

    def _detect_project_type(self, project_path: str) -> str:
        """Detect the type of project based on its files."""
        if os.path.exists(os.path.join(project_path, 'requirements.txt')):
            return 'python'
        elif os.path.exists(os.path.join(project_path, 'package.json')):
            return 'node'
        elif os.path.exists(os.path.join(project_path, 'pom.xml')):
            return 'java'
        elif os.path.exists(os.path.join(project_path, 'Dockerfile')):
            return 'docker'
        return 'unknown'

    def _build_python_project(self, project_path: str) -> Dict[str, Any]:
        """Build a Python project."""
        try:
            # Create virtual environment
            venv_path = os.path.join(project_path, 'venv')
            subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
            
            # Install dependencies
            pip_path = os.path.join(venv_path, 'bin', 'pip') if os.name != 'nt' else os.path.join(venv_path, 'Scripts', 'pip')
            subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], cwd=project_path, check=True)
            
            return {"success": True, "message": "Python project built successfully"}
        except Exception as e:
            return {"error": str(e)}

    def _build_node_project(self, project_path: str) -> Dict[str, Any]:
        """Build a Node.js project."""
        try:
            # Install dependencies
            subprocess.run(['npm', 'install'], cwd=project_path, check=True)
            
            # Run build script if it exists
            if 'build' in json.load(open(os.path.join(project_path, 'package.json')))['scripts']:
                subprocess.run(['npm', 'run', 'build'], cwd=project_path, check=True)
            
            return {"success": True, "message": "Node.js project built successfully"}
        except Exception as e:
            return {"error": str(e)}

    def _build_java_project(self, project_path: str) -> Dict[str, Any]:
        """Build a Java project."""
        try:
            # Build using Maven
            subprocess.run(['mvn', 'clean', 'install'], cwd=project_path, check=True)
            return {"success": True, "message": "Java project built successfully"}
        except Exception as e:
            return {"error": str(e)}

    def _build_docker_project(self, project_path: str) -> Dict[str, Any]:
        """Build a Docker project."""
        try:
            if not self.docker_client:
                return {"error": "Docker is not available"}

            # Build Docker image
            image, logs = self.docker_client.images.build(
                path=project_path,
                tag=f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            return {
                "success": True,
                "message": "Docker project built successfully",
                "image_id": image.id
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_3d_model(self, prompt: str, output_format: str = 'obj',
                         style: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a 3D model using AI.
        Args:
            prompt: Description of the 3D model
            output_format: Output format ('obj', 'stl', 'glb')
            style: Optional style to apply
        """
        try:
            # This is a placeholder for 3D model generation
            # You would typically integrate with a 3D model generation API here
            # For example, using OpenAI's API or a specialized 3D model generation service
            
            # Example implementation using a hypothetical API:
            # response = requests.post(
            #     'https://api.3dmodelgenerator.com/generate',
            #     json={
            #         'prompt': prompt,
            #         'format': output_format,
            #         'style': style
            #     }
            # )
            # return response.json()
            
            return {
                "success": True,
                "message": "3D model generation is not implemented yet",
                "note": "This requires integration with a 3D model generation API"
            }
        except Exception as e:
            self.logger.error(f"Error generating 3D model: {str(e)}")
            return {"error": str(e)}

    def vibe_code(self, prompt: str, language: str = 'python',
                 style: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate code with a specific vibe or style.
        Args:
            prompt: Description of the code to generate
            language: Programming language
            style: Optional coding style
        """
        try:
            # This is a placeholder for vibe coding
            # You would typically integrate with an AI code generation API here
            # For example, using OpenAI's Codex or similar service
            
            # Example implementation using a hypothetical API:
            # response = requests.post(
            #     'https://api.codegenerator.com/generate',
            #     json={
            #         'prompt': prompt,
            #         'language': language,
            #         'style': style
            #     }
            # )
            # return response.json()
            
            return {
                "success": True,
                "message": "Vibe coding is not implemented yet",
                "note": "This requires integration with a code generation API"
            }
        except Exception as e:
            self.logger.error(f"Error in vibe coding: {str(e)}")
            return {"error": str(e)}

# Create a singleton instance
terminal_operations = TerminalOperations() 