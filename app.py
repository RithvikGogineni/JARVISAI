import os
import streamlit as st
from dotenv import load_dotenv, set_key
import base64

# Try to import PIL, but don't fail if it's not available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from ai_control import AIController
from system_control import SystemController

# Load environment variables from .env
load_dotenv()

st.set_page_config(page_title="AI System Controller", layout="centered")

# Display the logo at the top of the app centered.
logo_path = "./assets/logo.png"
if os.path.exists(logo_path):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if PIL_AVAILABLE:
            st.image(logo_path)
        else:
            st.write("Logo display disabled - Pillow not available")

# Load avatar image for chat messages.
avatar_path = "./assets/full.png"
img = None
if PIL_AVAILABLE and os.path.exists(avatar_path):
    try:
        img = Image.open(avatar_path)
    except Exception as e:
        st.warning(f"Could not load avatar image: {str(e)}")

# Initialize chat history in session state.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize settings in session state.
if "settings" not in st.session_state:
    st.session_state.settings = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini-realtime-preview-2024-12-17"),
        "INITIAL_PROMPT": os.getenv("INITIAL_PROMPT", ""),
        "DEVICE": os.getenv("DEVICE", "unknown"),
        "FUNCTION_CALLING": os.getenv("FUNCTION_CALLING", "True").lower() in ("true", "1", "yes"),
        "VOICE": os.getenv("VOICE", "echo"),
        "INCLUDE_DATE": os.getenv("INCLUDE_DATE", "True").lower() in ("true", "1", "yes"),
        "INCLUDE_TIME": os.getenv("INCLUDE_TIME", "True").lower() in ("true", "1", "yes"),
        "PC_USERNAME": os.getenv("PC_USERNAME", "YourUsername")
    }

# Initialize the system controller
system_controller = SystemController()
system_info = system_controller.get_system_info()

# Initialize the AI controller if not already done.
if "ai_controller" not in st.session_state or st.session_state.ai_controller is None:
    st.session_state.ai_controller = AIController(
        api_key=st.session_state.settings["OPENAI_API_KEY"],
        model=st.session_state.settings["OPENAI_MODEL"],
        initial_prompt=st.session_state.settings["INITIAL_PROMPT"],
        include_date=st.session_state.settings["INCLUDE_DATE"],
        include_time=st.session_state.settings["INCLUDE_TIME"],
        mode="text",
        function_calling=st.session_state.settings["FUNCTION_CALLING"],
        voice=st.session_state.settings["VOICE"]
    )
    st.session_state.ai_controller.start_realtime()

# Create three tabs: Chat, Realtime Audio, and Settings.
tabs = st.tabs(["Chat", "Realtime", "Settings"])

# --------------------- Chat Tab (tab[0]) ---------------------
with tabs[0]:
    st.title("💬 Chat with AI System Controller")
    
    # Display system status
    st.subheader("System Status")
    status_col1, status_col2, status_col3 = st.columns(3)
    with status_col1:
        st.metric("CPU Usage", f"{system_info['cpu_usage']}%")
    with status_col2:
        st.metric("Memory Usage", f"{system_info['memory_usage']}%")
    with status_col3:
        st.metric("Disk Usage", f"{system_info['disk_usage']}%")
    
    # Add system control buttons
    st.subheader("Quick System Controls")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if system_info['supported_features']['volume']:
            if st.button("🔊 Volume Up"):
                result = st.session_state.ai_controller.handle_system_control("volume", {"action": "up"})
                st.toast(result)
            if st.button("🔈 Volume Down"):
                result = st.session_state.ai_controller.handle_system_control("volume", {"action": "down"})
                st.toast(result)
        else:
            st.warning("Volume control not supported on this system")
    
    with col2:
        if system_info['supported_features']['window']:
            if st.button("💻 Minimize All"):
                result = st.session_state.ai_controller.handle_system_control("window", {"action": "minimize", "window_name": "all"})
                st.toast(result)
            if st.button("🖥️ Maximize All"):
                result = st.session_state.ai_controller.handle_system_control("window", {"action": "maximize", "window_name": "all"})
                st.toast(result)
        else:
            st.warning("Window management not supported on this system")
    
    with col3:
        if system_info['supported_features']['power']:
            if st.button("🌙 Sleep"):
                result = st.session_state.ai_controller.handle_system_control("power", {"action": "sleep"})
                st.toast(result)
            if st.button("🔄 Restart"):
                result = st.session_state.ai_controller.handle_system_control("power", {"action": "restart"})
                st.toast(result)
        else:
            st.warning("Power management not supported on this system")
    
    st.divider()
    
    # Add example commands
    st.subheader("Example Commands")
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        st.markdown("""
        **System Control:**
        - "Set volume to 50%"
        - "Minimize Chrome window"
        - "Put system to sleep"
        
        **File Operations:**
        - "Create a file named test.txt"
        - "List files in downloads folder"
        - "Delete the file example.txt"
        """)
    
    with example_col2:
        st.markdown("""
        **Web Operations:**
        - "Search for Python tutorials"
        - "Download the first image of cats"
        - "Find recent news about AI"
        
        **Media Operations:**
        - "Generate an image of a sunset"
        - "Transcribe the audio file speech.mp3"
        - "Edit this image to make it brighter"
        """)
    
    st.divider()
    
    # Chat interface
    prompt = st.chat_input("Ask the AI to control your system...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = st.session_state.ai_controller.ask_sync(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar=img):
                st.markdown(message["content"])
        else:
            with st.chat_message("user"):
                st.markdown(message["content"])

# --------------------- Realtime Audio Tab (tab[1]) ---------------------
with tabs[1]:
    st.header("🎙️ Realtime Audio Chat")
    if "realtime_controller" not in st.session_state or st.session_state.realtime_controller is None:
        if st.button("Start Realtime Audio Chat"):
            st.session_state.realtime_controller = AIController(
                api_key=st.session_state.settings["OPENAI_API_KEY"],
                model=st.session_state.settings["OPENAI_MODEL"],
                initial_prompt=st.session_state.settings["INITIAL_PROMPT"],
                include_date=st.session_state.settings["INCLUDE_DATE"],
                include_time=st.session_state.settings["INCLUDE_TIME"],
                mode="realtime",
                function_calling=st.session_state.settings["FUNCTION_CALLING"],
                voice=st.session_state.settings["VOICE"]
            )
            st.session_state.realtime_controller.start_realtime()
            st.success("Realtime audio chat started.")
            st.rerun()
    else:
        if st.button("Stop Realtime Audio Chat"):
            st.session_state.realtime_controller.stop_realtime()
            st.session_state.realtime_controller = None
            st.success("Realtime audio chat stopped.")
            st.rerun()

# --------------------- Settings Tab (tab[2]) ---------------------
with tabs[2]:
    st.header("Settings")
    
    # Display platform information
    st.subheader("Platform Information")
    st.info(f"Current Platform: {system_info['platform']}")
    st.json(system_info['supported_features'])
    
    with st.form("settings_form"):
        api_key = st.text_input("OpenAI API Key", value=st.session_state.settings["OPENAI_API_KEY"], type="password")
        model = st.selectbox(
            "OpenAI Model", 
            options=["gpt-4o-mini-realtime-preview-2024-12-17", "gpt-4o-realtime-preview-2024-12-17"],
            index=0 if st.session_state.settings["OPENAI_MODEL"] == "gpt-4o-mini-realtime-preview-2024-12-17" else 1
        )
        initial_prompt = st.text_area("Initial Prompt", value=st.session_state.settings["INITIAL_PROMPT"])
        device = st.text_input("Device", value=st.session_state.settings["DEVICE"])
        function_calling = st.checkbox("Function Calling", value=st.session_state.settings["FUNCTION_CALLING"])
        voice_options = ["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse"]
        voice = st.selectbox(
            "Voice", 
            options=voice_options, 
            index=voice_options.index(st.session_state.settings["VOICE"]) if st.session_state.settings["VOICE"] in voice_options else 0
        )
        include_date = st.checkbox("Include Date", value=st.session_state.settings["INCLUDE_DATE"])
        include_time = st.checkbox("Include Time", value=st.session_state.settings["INCLUDE_TIME"])
        pc_username = st.text_input("PC Username", value=st.session_state.settings["PC_USERNAME"])
        
        submitted = st.form_submit_button("Save Settings")
        if submitted:
            st.session_state.settings["OPENAI_API_KEY"] = api_key
            st.session_state.settings["OPENAI_MODEL"] = model
            st.session_state.settings["INITIAL_PROMPT"] = initial_prompt
            st.session_state.settings["DEVICE"] = device
            st.session_state.settings["FUNCTION_CALLING"] = function_calling
            st.session_state.settings["VOICE"] = voice
            st.session_state.settings["INCLUDE_DATE"] = include_date
            st.session_state.settings["INCLUDE_TIME"] = include_time
            st.session_state.settings["PC_USERNAME"] = pc_username

            env_path = ".env"
            set_key(env_path, "OPENAI_API_KEY", api_key)
            set_key(env_path, "OPENAI_MODEL", model)
            set_key(env_path, "INITIAL_PROMPT", initial_prompt)
            set_key(env_path, "DEVICE", device)
            set_key(env_path, "FUNCTION_CALLING", str(function_calling))
            set_key(env_path, "VOICE", voice)
            set_key(env_path, "INCLUDE_DATE", str(include_date))
            set_key(env_path, "INCLUDE_TIME", str(include_time))
            set_key(env_path, "PC_USERNAME", pc_username)
            st.success("Settings saved to .env file. Restart or restart realtime chat to apply changes.")
