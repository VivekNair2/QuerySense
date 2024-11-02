import sqlite3
import bcrypt
import os
from dotenv import load_dotenv
import streamlit as st
from llama_index.core.agent import ReActAgent
from tools.realtime_search import realtime_search_tool
from tools.image_generation import generate_image_tool
from llama_index.llms.openai import OpenAI
from tools.vision import camera_query_tool
from tools.utube import search_video_tool, get_transcript_tool, get_video_captions_tool, get_video_url_tool
from tools.check_image import check_image
from tools.RAG import text_rag_tool
from youtube_transcript_api import YouTubeTranscriptApi

# Initialize environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Set up the system prompt
system_prompt = """
You are a helpful assistant who specializes in analyzing images and generating code for neural network architectures.
If the user provides an image, examine the image and generate the code accordingly.
If the user provides a text prompt, respond appropriately based on your role.
"""

# Initialize the language model with OpenAI
llm = OpenAI(model="gpt-4", system_prompt=system_prompt)

# Define tools available for the agent
tools = [
    check_image, generate_image_tool, camera_query_tool, realtime_search_tool,
    search_video_tool, get_video_url_tool, get_transcript_tool, get_video_captions_tool, text_rag_tool
]

# Initialize the ReActAgent with tools and language model
agent = ReActAgent.from_tools(
    tools=tools,
    llm=llm,
    verbose=True
)

# Set up SQLite database for storing user credentials
conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
conn.commit()

# Helper functions for authentication
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def signup_user(username, password):
    hashed_password = hash_password(password)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user:
        return check_password(password, user[0])
    return False

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.memory = []  # To store conversation history

# Signup UI
def show_signup():
    st.subheader("Create New Account")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Signup"):
        signup_user(username, password)
        st.success("Account created! Please log in.")
        # Rerun the app to go back to login
        st.experimental_rerun()

# Login UI
def show_login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            # Rerun the app to open the agent UI
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.memory = []  # Clear conversation history on logout
    st.success("Logged out successfully!")
    # Rerun the app to refresh to login screen
    st.experimental_rerun()

# Main app UI
def agent_ui():
    st.write(f"Welcome to the assistant, {st.session_state.username}!")
    prompt = st.text_input("Enter your query:")
    
    if st.button("Submit Query") and prompt:
        try:
            # Prepare the prompt with recent context
            context = "\n".join(st.session_state.memory[-10:])  # Last 10 interactions
            full_prompt = f"{context}\nUser: {prompt}"
            
            # Query the agent
            response = agent.query(full_prompt)
            
            # Store conversation in session memory
            st.session_state.memory.append(f"User: {prompt}")
            st.session_state.memory.append(f"Agent: {response}")
            
            st.write("Agent:", response)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Streamlit UI logic
st.title("AI Assistant with Login")
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        logout()
    agent_ui()
else:
    option = st.sidebar.selectbox("Choose Action", ["Login", "Signup"])
    if option == "Login":
        show_login()
    elif option == "Signup":
        show_signup()
