import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatbotWithMemory:
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            st.error("❌ GOOGLE_API_KEY not found in environment variables")
            st.stop()
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model - using correct model name
        self.model = genai.GenerativeModel('gemini-2.0-flash')  # or 'gemini-1.5-pro'
        
        # Initialize conversation history for memory
        self.conversation_history = []
        
        st.success("✅ Chatbot initialized successfully with Gemini!")
    
    def get_response(self, user_input):
        """Get AI response based on user input and memory"""
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "parts": [user_input]})
            
            # Start a new chat with history or continue existing
            if hasattr(self, 'chat') and self.chat:
                response = self.chat.send_message(user_input)
            else:
                # For the first message, include history as context
                history_context = self._format_conversation_history()
                prompt = f"{history_context}\n\nUser: {user_input}"
                response = self.model.generate_content(prompt)
                self.chat = self.model.start_chat(history=[])
            
            # Add AI response to history
            self.conversation_history.append({"role": "model", "parts": [response.text]})
            
            return response.text
            
        except Exception as e:
            return f"Error getting response: {str(e)}"
    
    def _format_conversation_history(self):
        """Format conversation history for context"""
        if not self.conversation_history:
            return "This is the start of the conversation."
        
        history_text = "Previous conversation:\n"
        for msg in self.conversation_history[-6:]:  # Last 6 messages for context
            role = "User" if msg["role"] == "user" else "AI"
            history_text += f"{role}: {msg['parts'][0]}\n"
        return history_text
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.conversation_history = []
        if hasattr(self, 'chat'):
            self.chat = None

def main():
    # Page configuration
    st.set_page_config(
        page_title="AI Chatbot with Memory",
        page_icon="🤖",
        layout="wide"
    )
    
    # Header
    st.title("🧠 AI Chatbot with Context Memory")
    st.markdown("This chatbot remembers our conversation during this session!")
    
    # Check for API key first
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("""
        🔑 **GOOGLE_API_KEY not found!**
        
        Please create a `.env` file in your project directory with:
        ```
        GOOGLE_API_KEY=your_actual_gemini_api_key_here
        ```
        
        Get your API key from: https://makersuite.google.com/app/apikey
        """)
        return
    
    # Initialize chatbot in session state
    if 'chatbot' not in st.session_state:
        with st.spinner("Initializing chatbot..."):
            st.session_state.chatbot = ChatbotWithMemory()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        
        # Display API key status (masked)
        if api_key:
            st.success(f"✅ API Key Loaded: {api_key[:10]}...{api_key[-4:]}")
        
        # Model info
        st.info("🤖 Model: gemini-2.5-flash")
        
        if st.button("🧹 Clear Conversation"):
            st.session_state.chatbot.clear_memory()
            st.session_state.messages = []
            st.rerun()
        
        # Memory info
        st.markdown("---")
        st.subheader("Memory Info")
        memory_length = len(st.session_state.chatbot.conversation_history)
        st.write(f"💬 Messages in memory: {memory_length}")
        
        # Display recent conversation
        if memory_length > 0:
            with st.expander("View Recent Conversation"):
                for i, msg in enumerate(st.session_state.chatbot.conversation_history[-3:]):
                    role = "👤 User" if msg["role"] == "user" else "🤖 AI"
                    st.text(f"{role}: {msg['parts'][0][:50]}...")
        
        st.markdown("---")
        st.subheader("How it works:")
        st.markdown("""
        - **Memory**: Remembers entire conversation
        - **Session-based**: Memory lasts until you close the tab
        - **Context-aware**: Understands references to previous messages
        - **Powered by**: Gemini 1.5 Flash
        """)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.get_response(prompt)
                st.markdown(response)
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()