import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
import anthropic
from dotenv import load_dotenv
import os

# Available Claude models with descriptions
models = [
    "claude-3-5-haiku-20241022",   # Fastest, most compact
    "claude-3-5-sonnet-20241022",  # Balanced performance and capability
]

def claudeai_completion(prompt, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=st.session_state.selected_model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print(message.content[0].text, print(type(message.content[0].text)))
    return message.content[0].text

# Initialize session state for API key and model
if 'claude_api_key' not in st.session_state:
    # Try to load API key from .env file
    load_dotenv()
    env_api_key = os.getenv('CLAUDE_API_KEY')
    st.session_state.claude_api_key = env_api_key

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "claude-3-5-sonnet-20241022"  # default model

def check_api_key():
    """Check if Claude API key is available and prompt if needed"""
    if not st.session_state.claude_api_key:
        st.warning("No API key found in .env file. Please enter your Claude API key to continue")
        col1, col2 = st.columns([2, 1])
        with col1:
            api_key = st.text_input("Enter your Claude API key:", type="password")
        with col2:
            st.session_state.selected_model = st.selectbox(
                "Select Model:",
                models,
                index=models.index(st.session_state.selected_model)
            )
        if api_key:
            st.session_state.claude_api_key = api_key
            return True
        return False
    return True

def extract_video_id(youtube_url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'(?:youtube\.com\/embed\/)([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """Get transcript from YouTube video"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        return f"Error getting transcript: {str(e)}"

def get_claude_response(prompt, transcript_data):
    """Get response from Claude API with timestamp references"""
    try:
        # Create a formatted transcript with timestamps and make them clickable
        formatted_transcript = ""
        for entry in transcript_data:
            timestamp = format_timestamp(entry['start'])
            formatted_transcript += f"[{timestamp}] {entry['text']}\n"

        message = f"""Context: This is a transcript from a YouTube video.

Transcript:
{formatted_transcript}

User Question: {prompt}

Please provide a clear and concise answer based on the information from the transcript. When referencing specific content, include the timestamp in [MM:SS] format."""
        
        # Pass the API key to the claudeai_completion function
        api_key = st.session_state.claude_api_key
        return claudeai_completion(message, api_key)
    except Exception as e:
        return f"Error getting response: {str(e)}"

def get_initial_summary(transcript):
    """Get initial summary from Claude API"""
    try:
        message = f"""Context: This is a transcript from a YouTube video.

Transcript: {transcript}

Please provide a response in the following format:

## 📝 Main Topics
- [timestamp] Topic 1
- [timestamp] Topic 2
- [timestamp] Topic 3

## ❓ Suggested Questions
- [timestamp] Question 1
- [timestamp] Question 2
- [timestamp] Question 3

## 🔍 Interesting Details
- [timestamp] Detail 1
- [timestamp] Detail 2
- [timestamp] Detail 3

Note: Include relevant timestamps in [MM:SS] format for each point."""
    
        api_key = st.session_state.claude_api_key
        return claudeai_completion(message, api_key)
    except Exception as e:
        return f"Error getting summary: {str(e)}"

def format_timestamp(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_message_with_timestamps(message):
    """Convert timestamps in message to clickable buttons inline with the text"""
    timestamp_pattern = r'\[(\d{2}:\d{2})\]'
    
    # Split message into parts, preserving markdown formatting
    parts = []
    last_end = 0
    
    for match in re.finditer(timestamp_pattern, message):
        # Add text before timestamp
        parts.append(message[last_end:match.start()])
        
        # Add timestamp button placeholder
        timestamp = match.group(1)
        minutes, seconds = map(int, timestamp.split(':'))
        total_seconds = minutes * 60 + seconds
        # Use a unique placeholder that won't appear in normal text
        parts.append(f"{{timestamp_button_{total_seconds}}}")
        
        last_end = match.end()
    
    # Add remaining text
    parts.append(message[last_end:])
    
    return "".join(parts)

# Add this function definition before the main UI code
def create_timestamp_button(timestamp, total_seconds, key):
    """Create a button that seeks to specific timestamp in video and autoplays"""
    if st.button(f"▶️ {timestamp}", key=key):
        st.session_state.video_start_time = total_seconds
        st.session_state.autoplay = True  # Add autoplay flag
        st.rerun()

# Page config
st.set_page_config(page_title="YouTube Video Chat Assistant", layout="wide")

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'video_id' not in st.session_state:
    st.session_state.video_id = None

# Main UI
st.title("💬 YouTube Video Chat Assistant")

# Add API key check before proceeding
if not check_api_key():
    st.stop()

# Create two columns - one for video, one for chat
col1, col2 = st.columns([1, 1])

with col1:
    # Video player container with enhanced parameters
    if st.session_state.video_id:
        youtube_url = f"https://www.youtube.com/watch?v={st.session_state.video_id}"
        start_time = st.session_state.get('video_start_time', 0)
        autoplay = st.session_state.get('autoplay', False)
        st.video(youtube_url, start_time=start_time, autoplay=autoplay)

with col2:
    # Sidebar for video input
    st.header("Video Input")
    youtube_url = st.text_input("Enter YouTube Video URL:")
    
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id and video_id != st.session_state.video_id:
            st.session_state.video_id = video_id
            with st.spinner("Loading transcript..."):
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    # Store full transcript data including timestamps
                    st.session_state.transcript_data = transcript_list
                    # for debug purpose , display the transcript data
                    # st.write(transcript_list)
                    
                    
                    # Join text for Claude
                    st.session_state.transcript = ' '.join([item['text'] for item in transcript_list])
                    
                    if st.session_state.transcript:
                        st.success("✅ Transcript loaded successfully!")
                        with st.spinner("Analyzing content..."):
                            summary = get_initial_summary(st.session_state.transcript)
                            st.session_state.chat_history = [
                                ("assistant", "👋 Welcome! Here's an overview of the video content:\n\n" + summary)
                            ]
                            # Force refresh the page to load the video
                            st.rerun()
                    else:
                        st.error("Error loading transcript")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Main chat interface
if st.session_state.transcript and "Error" not in st.session_state.transcript:
    # Chat messages container
    chat_container = st.container()
    
    # Display chat history with clickable timestamps
    with chat_container:
        for role, message in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"### 🧑‍💻 You\n{message}")
            else:
                # Format message with timestamp placeholders
                formatted_message = format_message_with_timestamps(message)
                
                # Split message into lines to handle markdown properly
                lines = formatted_message.split('\n')
                
                # Process each line
                for line in lines:
                    # Check if line contains timestamp placeholder
                    if '{timestamp_button_' in line:
                        # Create columns for the line: text + button
                        timestamp_matches = re.finditer(r'\{timestamp_button_(\d+)\}', line)
                        
                        for match in timestamp_matches:
                            total_seconds = int(match.group(1))
                            minutes = total_seconds // 60
                            seconds = total_seconds % 60
                            timestamp = f"{minutes:02d}:{seconds:02d}"
                            
                            # Replace placeholder with actual button
                            button_col, text_col = st.columns([1, 15])
                            with button_col:
                                create_timestamp_button(timestamp, total_seconds, f"ts_{total_seconds}_{hash(line)}")
                            
                            with text_col:
                                # Display the text part of the line
                                text_part = line.replace(match.group(0), "").strip()
                                st.markdown(text_part)
                    else:
                        # Display regular lines normally
                        st.markdown(line)
    
    # User input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area("Your question:", key="user_question", height=100)
        cols = st.columns([1, 6, 1])
        with cols[1]:
            submit_button = st.form_submit_button("Send Message", use_container_width=True)
        
        if submit_button and user_input:
            # Get response
            with st.spinner("Thinking..."):
                response = get_claude_response(user_input, st.session_state.transcript_data)
            
            # Add to chat history
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("assistant", response))
            
            # Rerun to update chat
            st.rerun()
else:
    st.info("👈 Please enter a YouTube URL in the sidebar to start chatting!")
