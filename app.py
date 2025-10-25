import streamlit as st
import requests
import os
import tempfile
from pathlib import Path
import time

# ========== CONFIGURATION ==========
BOT_TOKEN = "8451092816:AAHGVdql3RN3pGphlH_8FTggRQw1zl6P5Cg"
DEFAULT_CHAT_ID = "1599595167"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB Telegram limit

# Create temporary directory for uploads
UPLOAD_DIR = Path(tempfile.gettempdir()) / "telegram_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
# ===================================

# Page configuration
st.set_page_config(
    page_title="Telegram File Uploader",
    page_icon="📤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }
    .status-success {
        color: #10b981;
        font-weight: 600;
    }
    .status-error {
        color: #ef4444;
        font-weight: 600;
    }
    .upload-section {
        border: 2px dashed #d1d5db;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.3s ease;
    }
    .upload-section:hover {
        border-color: #6366f1;
        background: #f0f4ff;
    }
    .config-badge {
        background: #f0f4ff;
        color: #6366f1;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-family: monospace;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .progress-bar {
        background: linear-gradient(90deg, #6366f1, #10b981);
        border-radius: 10px;
        height: 10px;
    }
</style>
""", unsafe_allow_html=True)

def test_bot_connection():
    """Test if bot token is valid and bot is accessible"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                return True, f"✅ Bot is connected: @{data['result']['username']}"
        return False, "❌ Bot token is invalid"
    except Exception as e:
        return False, f"❌ Connection failed: {str(e)}"

def send_to_telegram(file_path, chat_id, file_name):
    """Send file to Telegram using the bot"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        
        # Prepare caption
        caption = f"""📦 File uploaded via Telegram Uploader
📄 File: {file_name}
🕒 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
🌐 Source: Streamlit Web App"""
        
        # Prepare the file and data
        with open(file_path, 'rb') as file:
            files = {'document': (file_name, file)}
            data = {
                'chat_id': chat_id,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            
            # Send the request
            response = requests.post(url, data=data, files=files, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return True, "File sent successfully to Telegram!"
                else:
                    return False, f"Telegram API error: {result.get('description', 'Unknown error')}"
            else:
                return False, f"HTTP Error {response.status_code}: {response.text}"
                
    except requests.exceptions.Timeout:
        return False, "Request timeout: File might be too large or network issue"
    except Exception as e:
        return False, f"Error sending file: {str(e)}"

def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 Bytes"
    size_names = ["Bytes", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"

def cleanup_temp_files():
    """Clean up temporary files in upload directory"""
    try:
        for file_path in UPLOAD_DIR.glob("*"):
            try:
                file_path.unlink()
            except:
                pass
    except:
        pass

def main():
    # Header Section
    st.markdown('<div class="main-header">📤 Telegram File Uploader</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Send files directly to Telegram - Fast, Secure & Free!</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'custom_chat_id' not in st.session_state:
        st.session_state.custom_chat_id = ""
    if 'upload_mode' not in st.session_state:
        st.session_state.upload_mode = "quick"
    
    # Sidebar for configuration and info
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Bot Status
        st.subheader("Bot Status")
        if st.button("Test Bot Connection"):
            with st.spinner("Testing connection..."):
                success, message = test_bot_connection()
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Mode Selection
        st.subheader("Upload Mode")
        upload_mode = st.radio(
            "Choose upload mode:",
            ["Quick Upload", "Custom Chat"],
            index=0 if st.session_state.upload_mode == "quick" else 1,
            key="mode_selector"
        )
        st.session_state.upload_mode = "quick" if upload_mode == "Quick Upload" else "custom"
        
        # Custom Chat ID Input
        if st.session_state.upload_mode == "custom":
            st.subheader("Custom Chat Settings")
            custom_chat_id = st.text_input(
                "Your Chat ID:",
                value=st.session_state.custom_chat_id,
                placeholder="Enter your numeric Chat ID (e.g., 1599595167)",
                key="chat_id_input"
            )
            if custom_chat_id:
                st.session_state.custom_chat_id = custom_chat_id
                if custom_chat_id.isdigit():
                    st.success("✅ Chat ID saved!")
                else:
                    st.error("❌ Please enter a valid numeric Chat ID")
        
        # Configuration Info
        st.subheader("Current Configuration")
        st.markdown(f'<div class="config-badge">Bot: Ready</div>', unsafe_allow_html=True)
        
        if st.session_state.upload_mode == "quick":
            st.markdown(f'<div class="config-badge">Chat ID: {DEFAULT_CHAT_ID}</div>', unsafe_allow_html=True)
            st.info("📝 Using default chat ID")
        else:
            if st.session_state.custom_chat_id:
                st.markdown(f'<div class="config-badge">Chat ID: {st.session_state.custom_chat_id}</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please enter your Chat ID")
        
        # Instructions
        st.header("📖 Instructions")
        with st.expander("How to get your Chat ID"):
            st.markdown("""
            1. **Start Chat with Bot**: Message [@GlobalFileUploaderBot](https://t.me/GlobalFileUploaderBot)
            2. **Send Any Message**: The bot will automatically detect your Chat ID
            3. **Copy Your Chat ID**: Use it in "Custom Chat" mode
            """)
        
        with st.expander("File Requirements"):
            st.markdown("""
            - **Max File Size**: 50MB (Telegram limit)
            - **Supported Types**: All file types
            - **Security**: Files are sent directly to Telegram, no storage
            """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 File Upload")
        
        # Upload section
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose a file to upload",
            type=None,
            key="file_uploader",
            help="Select any file up to 50MB in size"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            
            # File information
            st.subheader("📄 File Information")
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.metric("File Name", uploaded_file.name)
            with col_info2:
                st.metric("File Size", format_file_size(uploaded_file.size))
            with col_info3:
                file_type = uploaded_file.type if uploaded_file.type else "Unknown"
                st.metric("File Type", file_type)
            
            # File preview for images
            if uploaded_file.type and uploaded_file.type.startswith('image/'):
                st.subheader("🖼️ Preview")
                st.image(uploaded_file, use_column_width=True)
            
            # Upload button
            st.subheader("🚀 Send to Telegram")
            
            # Get appropriate chat ID
            if st.session_state.upload_mode == "quick":
                chat_id = DEFAULT_CHAT_ID
                mode_info = "Quick Upload Mode"
            else:
                if not st.session_state.custom_chat_id or not st.session_state.custom_chat_id.isdigit():
                    st.error("❌ Please enter a valid Chat ID in the sidebar")
                    return
                chat_id = st.session_state.custom_chat_id
                mode_info = "Custom Chat Mode"
            
            st.info(f"**Mode**: {mode_info} | **Chat ID**: {chat_id}")
            
            if st.button("📨 Send File to Telegram", type="primary", use_container_width=True):
                # Validate file size
                if uploaded_file.size > MAX_FILE_SIZE:
                    st.error(f"❌ File size exceeds Telegram limit of 50MB. Your file: {format_file_size(uploaded_file.size)}")
                    return
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Save file temporarily
                    temp_file_path = UPLOAD_DIR / uploaded_file.name
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Simulate progress
                    for percent in range(0, 101, 10):
                        progress_bar.progress(percent)
                        status_text.text(f"Uploading... {percent}%")
                        time.sleep(0.1)
                    
                    # Send to Telegram
                    status_text.text("Sending to Telegram...")
                    success, message = send_to_telegram(temp_file_path, chat_id, uploaded_file.name)
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                    
                    # Show result
                    progress_bar.progress(100)
                    time.sleep(0.5)
                    
                    if success:
                        st.balloons()
                        st.success(f"✅ {message}")
                        
                        # Show success details
                        col_s1, col_s2 = st.columns(2)
                        with col_s1:
                            st.metric("Status", "Success")
                        with col_s2:
                            st.metric("File Sent", uploaded_file.name)
                    else:
                        st.error(f"❌ {message}")
                        
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
                    # Clean up on error
                    try:
                        if 'temp_file_path' in locals():
                            os.unlink(temp_file_path)
                    except:
                        pass
                
                finally:
                    # Clear progress
                    time.sleep(2)
                    progress_bar.empty()
                    status_text.empty()
        
        else:
            # Show upload instructions when no file is selected
            st.info("💡 **Upload Instructions:**")
            st.markdown("""
            - Click **"Browse files"** or drag and drop a file
            - Select any file type (videos, images, documents, etc.)
            - Maximum file size: **50MB**
            - Files are sent directly to Telegram via bot
            """)
    
    with col2:
        st.header("✨ Features")
        
        # Feature cards
        features = [
            {
                "icon": "⚡",
                "title": "Instant Delivery",
                "description": "Files sent directly to Telegram in seconds"
            },
            {
                "icon": "🔒",
                "title": "Secure & Private",
                "description": "No file storage, direct Telegram transfer"
            },
            {
                "icon": "🌐",
                "title": "Global Access",
                "description": "Available worldwide for all users"
            },
            {
                "icon": "📱",
                "title": "All File Types",
                "description": "Support for videos, images, documents, audio"
            },
            {
                "icon": "🚀",
                "title": "Fast & Reliable",
                "description": "Built on Telegram's robust API"
            },
            {
                "icon": "🎯",
                "title": "Easy to Use",
                "description": "Simple interface, no registration required"
            }
        ]
        
        for feature in features:
            with st.container():
                st.markdown(f"""
                <div class="feature-card">
                    <h3>{feature['icon']} {feature['title']}</h3>
                    <p>{feature['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
        
        # Quick stats
        st.header("📊 Quick Info")
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Max File Size", "50 MB")
        with col_stat2:
            st.metric("Supported Types", "All")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Made with ❤️ using Streamlit | "
        "<a href='https://t.me/GlobalFileUploaderBot' target='_blank'>Get Chat ID</a>"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # Clean up temp files on startup
    cleanup_temp_files()
    main()
