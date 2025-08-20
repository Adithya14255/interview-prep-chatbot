"""
AI Interview Assistant - Modern Voice-Enabled Interview Preparation
A sophisticated interview preparation platform with advanced AI capabilities
"""

import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx
import io
import os
from dotenv import load_dotenv
import time
import tempfile

# Load environment variables
load_dotenv()

# Modern page configuration
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "AI Interview Assistant - Your personal interview preparation companion"
    }
)

# Modern theme configuration using native Streamlit theming
def configure_theme():
    """Configure modern dark theme with Streamlit native theming"""
    # Create config directory if it doesn't exist
    config_dir = ".streamlit"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # Create config.toml with modern theme
    config_content = '''
[theme]
base = "dark"
primaryColor = "#60A5FA"
backgroundColor = "#0F172A"
secondaryBackgroundColor = "#1E293B"
textColor = "#F1F5F9"
font = "sans serif"
'''
    
    config_path = os.path.join(config_dir, "config.toml")
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(config_content)

# Apply theme configuration
configure_theme()

def initialize_gemini():
    """Initialize Gemini AI with API key validation"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        st.error("Gemini API Key Required")
        st.info("Please configure your Gemini API key in the `.env` file")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

def extract_text_from_file(uploaded_file):
    """Extract text content from uploaded file"""
    try:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        
        elif uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        
        else:
            st.error("Unsupported file format")
            return None
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def upload_file_to_gemini(file_content, file_name, mime_type):
    """Upload file to Gemini Files API"""
    try:
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix=f"_{file_name}") as tmp_file:
            if isinstance(file_content, str):
                tmp_file.write(file_content.encode('utf-8'))
            else:
                tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        uploaded_file = genai.upload_file(
            path=tmp_file_path,
            display_name=file_name
        )
        
        os.unlink(tmp_file_path)
        
        # Wait for file processing
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_file = genai.get_file(uploaded_file.name)
        
        if uploaded_file.state.name == "FAILED":
            raise Exception("File processing failed")
            
        return uploaded_file
        
    except Exception as e:
        st.error(f"Error uploading file to Gemini: {str(e)}")
        return None

def start_interactive_interview(model, resume_file, job_description):
    """Initialize interactive interview session"""
    initial_prompt = f"""
    You are a professional AI interview assistant conducting a technical interview simulation. 
    I will provide you with a candidate's resume and a job description.

    Your role is to conduct a realistic interview by:
    1. First, briefly introduce yourself as an AI interview assistant and explain the process (2-3 sentences)
    2. Ask ONE question at a time - start with a warm-up question
    3. Wait for the candidate's response before moving to the next question
    4. Provide brief, constructive feedback (1-2 sentences) on each answer before asking the next question
    5. Progress through different types of questions: technical basics → intermediate → advanced → behavioral → scenario-based
    6. After 8-10 questions, provide comprehensive performance feedback

    IMPORTANT GUIDELINES:
    - Ask only ONE question per response
    - Keep feedback brief and professional
    - Adapt difficulty based on their answers
    - Remember their resume and job requirements throughout
    - This is a live interview simulation - don't list all questions at once
    - Maintain a professional, supportive tone throughout

    **Job Description:**
    {job_description}

    **Resume:** (attached file)

    Begin by introducing yourself and asking your first question.
    """
    
    try:
        response = model.generate_content([initial_prompt, resume_file])
        return response.text
    except Exception as e:
        st.error(f"Error starting interview: {str(e)}")
        return None

def generate_interview_feedback(chat_session):
    """Generate comprehensive feedback after interview completion"""
    feedback_prompt = """
    The interview simulation is now complete. Please provide comprehensive performance feedback in a professional format.

    Structure your feedback as follows:

    ## Interview Performance Analysis

    ### Strengths Demonstrated:
    - List 3-4 key strengths shown during the interview

    ### Areas for Development:
    - List 2-3 specific areas that need improvement

    ### Technical Assessment:
    - Rate technical knowledge (1-10 scale)
    - Evaluate problem-solving approach
    - Note any skill gaps relative to role requirements

    ### Communication Evaluation:
    - Assess clarity and articulation
    - Evaluate confidence and presence
    - Review behavioral response quality

    ### Recommendations:
    - Provide specific study suggestions
    - Identify key practice areas
    - Share interview improvement strategies

    ### Overall Readiness:
    - Current readiness assessment for this role
    - Recommended preparation timeline
    - Confidence level for similar interviews

    Provide honest, constructive feedback with actionable improvement suggestions.
    """
    
    try:
        response = chat_session.send_message(feedback_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating feedback: {str(e)}")
        return None

def main():
    """Main application with modern Streamlit UI"""
    
    # Initialize session state
    initialize_session_state()
    
    # Modern header with logo and title
    render_header()
    
    # Main content area
    if not st.session_state.session_started:
        render_setup_screen()
    else:
        render_interview_screen()

def initialize_session_state():
    """Initialize all session state variables"""
    default_states = {
        'model': None,
        'chat_history': [],
        'resume_uploaded': False,
        'resume_file': None,
        'job_description': "",
        'session_started': False,
        'chat_session': None,
        'question_count': 0,
        'interview_complete': False
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize AI model
    if st.session_state.model is None:
        st.session_state.model = initialize_gemini()

def render_header():
    """Render modern application header"""
    st.markdown("# AI Interview Assistant")
    st.markdown("*Professional interview preparation with advanced AI*")
    st.divider()

def render_setup_screen():
    """Render the initial setup screen"""
    # Setup tabs
    tab1, tab2 = st.tabs(["Resume Upload", "Job Details"])
    
    with tab1:
        render_resume_upload()
    
    with tab2:
        render_job_description()
    
    # Start button
    st.markdown("### Ready to Begin?")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("Start Interview Session", type="primary", use_container_width=True):
            if validate_setup():
                with st.spinner("Starting interview session..."):
                    start_interview_session()

def render_resume_upload():
    """Render resume upload section"""
    if not st.session_state.resume_uploaded:
        st.markdown("#### Upload Your Resume")
        st.info("Upload your resume to personalize the interview experience")
        
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_file is not None:
            with st.spinner("Processing your resume..."):
                file_content = uploaded_file.getvalue()
                gemini_file = upload_file_to_gemini(
                    file_content, 
                    uploaded_file.name, 
                    uploaded_file.type
                )
                
                if gemini_file:
                    st.session_state.resume_file = gemini_file
                    st.session_state.resume_uploaded = True
                    st.success("Resume processed successfully!")
                    
                    time.sleep(0.5)
                    st.rerun()
    else:
        st.success("Resume ready for analysis")
        if st.button("Upload Different Resume", type="secondary"):
            st.session_state.resume_uploaded = False
            st.session_state.resume_file = None
            st.info("Please upload a new resume file")
            time.sleep(0.5)
            st.rerun()

def render_job_description():
    """Render job description input section"""
    st.markdown("#### Job Description")
    st.info("Paste the job description to tailor interview questions")
    
    job_desc = st.text_area(
        "Job Description",
        height=300,
        placeholder="Paste the complete job description here...\n\nThe AI will analyze requirements and tailor questions accordingly.",
        value=st.session_state.job_description,
        label_visibility="collapsed"
    )
    
    if job_desc != st.session_state.job_description:
        st.session_state.job_description = job_desc
        
    # Job description analysis
    if st.session_state.job_description.strip():
        word_count = len(st.session_state.job_description.split())
        st.caption(f"Analysis ready • {word_count} words")

def validate_setup():
    """Validate setup before starting interview"""
    if not st.session_state.resume_uploaded:
        st.error("Please upload your resume first")
        return False
    
    if not st.session_state.job_description.strip():
        st.error("Please provide the job description")
        return False
    
    return True

def start_interview_session():
    """Initialize and start the interview session"""
    with st.spinner("AI is preparing your personalized interview..."):
        initial_response = start_interactive_interview(
            st.session_state.model,
            st.session_state.resume_file,
            st.session_state.job_description
        )
        
        if initial_response:
            st.session_state.chat_session = st.session_state.model.start_chat(history=[])
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": initial_response
            })
            st.session_state.session_started = True
            st.session_state.question_count = 1
            
            st.success("Interview session initialized!")
            
            time.sleep(0.5)
            st.rerun()

def render_interview_screen():
    """Render the active interview interface"""
    if not st.session_state.interview_complete:
        render_active_interview()
    else:
        render_interview_complete()

def render_active_interview():
    """Render active interview interface"""
    # Interview header
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.metric("Question", f"{st.session_state.question_count}/10")
    
    with col2:
        progress = min(st.session_state.question_count / 10, 1.0)
        st.progress(progress, text="Interview Progress")
    
    with col3:
        st.info("Chat Mode")
    
    st.divider()
    
    # Control panel
    render_text_controls()
    
    st.divider()
    
    # Chat history
    render_chat_history()

def render_text_controls():
    """Render text input interface"""
    user_input = st.text_area(
        "Your Response",
        placeholder="Type your answer here...",
        height=120,
        key="text_response"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Submit Answer", type="primary", use_container_width=True) and user_input.strip():
            with st.spinner("Processing your response..."):
                process_user_response(user_input, is_voice=False)
                st.success("Response submitted successfully!")
                time.sleep(0.5)
                st.rerun()
    
    with col2:
        if st.button("Skip Question", use_container_width=True):
            with st.spinner("Moving to next question..."):
                handle_skip_question()
                time.sleep(0.5)
                st.rerun()
    
    with col3:
        if st.button("End Interview", use_container_width=True, type="secondary"):
            with st.spinner("Ending interview..."):
                handle_end_interview()
                time.sleep(0.5)
                st.rerun()

def render_chat_history():
    """Render chat history with modern styling"""
    st.markdown("### Interview Conversation")
    
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

def render_interview_complete():
    """Render interview completion screen"""
    st.markdown("## Interview Complete!")
    st.success("Congratulations! You've completed your interview session.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("Start New Interview", type="primary", use_container_width=True):
            with st.spinner("Preparing new interview..."):
                reset_session()
                time.sleep(0.5)
                st.rerun()
    
    st.divider()
    
    # Show final conversation
    render_chat_history()

def process_user_response(user_response: str, is_voice: bool = False):
    """Process user response and generate next question"""
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_response
    })
    
    with st.spinner("AI is analyzing your response..."):
        try:
            st.session_state.question_count += 1
            
            # Check if interview should end
            if st.session_state.question_count >= 10:
                # Generate final feedback
                feedback = generate_interview_feedback(st.session_state.chat_session)
                if feedback:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": feedback
                    })
                    st.session_state.interview_complete = True
            else:
                # Continue with next question
                prompt = f"""The candidate answered: '{user_response}'

Provide brief feedback (1-2 sentences) on their answer, then ask your next interview question. 
This is question #{st.session_state.question_count} of approximately 8-10 total questions. 
Keep your response concise and professional."""
                
                response = st.session_state.chat_session.send_message(prompt)
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response.text
                })
        
        except Exception as e:
            st.error(f"Error processing response: {str(e)}")

def handle_skip_question():
    """Handle skipping current question"""
    st.session_state.chat_history.append({
        "role": "user",
        "content": "[Question skipped]"
    })
    
    with st.spinner("Moving to next question..."):
        try:
            st.session_state.question_count += 1
            
            if st.session_state.question_count >= 10:
                feedback = generate_interview_feedback(st.session_state.chat_session)
                if feedback:
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": feedback
                    })
                    st.session_state.interview_complete = True
            else:
                prompt = f"The candidate skipped the previous question. Please ask your next interview question. This is question #{st.session_state.question_count} of approximately 8-10 total questions."
                response = st.session_state.chat_session.send_message(prompt)
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response.text
                })
                    
        except Exception as e:
            st.error(f"Error skipping question: {str(e)}")

def handle_end_interview():
    """Handle ending interview early"""
    with st.spinner("Generating final analysis..."):
        try:
            feedback = generate_interview_feedback(st.session_state.chat_session)
            if feedback:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": feedback
                })
                st.session_state.interview_complete = True
                    
        except Exception as e:
            st.error(f"Error ending interview: {str(e)}")

def reset_session():
    """Reset all session state for new interview"""
    keys_to_reset = [
        'chat_history', 'resume_uploaded', 'resume_file', 'job_description', 
        'session_started', 'chat_session', 'question_count', 'interview_complete'
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            if key in ['chat_history']:
                st.session_state[key] = []
            elif key in ['resume_uploaded', 'session_started', 'interview_complete']:
                st.session_state[key] = False
            elif key in ['question_count']:
                st.session_state[key] = 0
            else:
                st.session_state[key] = None

if __name__ == "__main__":
    main()
