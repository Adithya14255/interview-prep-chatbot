"""
Tech Interview Copilot - Streamlit Application
A sleek interview preparation tool using Gemini AI
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

# Configure page
st.set_page_config(
    page_title="Tech Interview Copilot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f1f1f;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
        color: #212529;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: #1a1a1a;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
        color: #1a1a1a;
    }
    .status-success {
        color: #2e7d32;
        font-weight: 600;
        background-color: #e8f5e8;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
    .status-error {
        color: #c62828;
        font-weight: 600;
        background-color: #ffebee;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }
    .section-divider {
        margin: 2rem 0;
        border-top: 1px solid #e0e0e0;
    }
    .interview-instructions {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #856404;
        font-weight: 500;
    }
    .progress-container {
        margin: 1rem 0;
    }
    .chat-message strong {
        color: #2c3e50;
        font-weight: 600;
    }
    .stTextArea textarea {
        color: #212529 !important;
        background-color: #ffffff !important;
    }
    .stTextInput input {
        color: #212529 !important;
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_gemini():
    """Initialize Gemini AI with API key"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        st.error("⚠️ Please set your Gemini API key in the .env file")
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
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix=f"_{file_name}") as tmp_file:
            if isinstance(file_content, str):
                tmp_file.write(file_content.encode('utf-8'))
            else:
                tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        # Upload to Gemini
        uploaded_file = genai.upload_file(
            path=tmp_file_path,
            display_name=file_name
        )
        
        # Clean up temporary file
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
    """Start an interactive interview simulation"""
    
    initial_prompt = f"""
    You are conducting a live technical interview simulation. I will provide you with a candidate's resume and a job description.

    Your role is to conduct a realistic interview by:
    1. First, briefly introduce yourself and the interview process (2-3 sentences)
    2. Then ask ONE question at a time - start with a warm-up question
    3. Wait for the candidate's response before moving to the next question
    4. Give brief feedback (1-2 sentences) on each answer before asking the next question
    5. Progress through different types of questions: technical basics → intermediate → advanced → behavioral → scenario-based
    6. After 8-10 questions, provide comprehensive feedback on their performance

    IMPORTANT RULES:
    - Ask only ONE question per response
    - Keep your feedback brief and encouraging
    - Adapt difficulty based on their answers
    - Remember their resume and this job description throughout
    - Don't list all questions at once - this is a live interview simulation

    **Job Description:**
    {job_description}

    **Resume:** (attached file)

    Start by introducing yourself and asking your first question.
    """
    
    try:
        response = model.generate_content([initial_prompt, resume_file])
        return response.text
    except Exception as e:
        st.error(f"Error starting interview: {str(e)}")
        return None

def generate_interview_feedback(chat_session):
    """Generate comprehensive feedback after the interview"""
    
    feedback_prompt = """
    The interview simulation is now complete. Please provide comprehensive feedback on the candidate's performance.

    Structure your feedback as follows:

    ## 📊 INTERVIEW PERFORMANCE SUMMARY

    ### ✅ **Strengths Demonstrated:**
    - List 3-4 key strengths shown during the interview

    ### 🎯 **Areas for Improvement:**
    - List 2-3 specific areas to work on

    ### 📈 **Technical Assessment:**
    - Rate technical knowledge (1-10)
    - Comment on problem-solving approach
    - Note any gaps in required skills

    ### 🗣️ **Communication & Soft Skills:**
    - Clarity of explanations
    - Confidence level
    - Behavioral responses quality

    ### 💡 **Recommendations:**
    - Specific study suggestions
    - Practice areas to focus on
    - Interview tips for improvement

    ### 🎯 **Overall Readiness:**
    - Current readiness level for this role
    - Timeline suggestion for improvement
    - Confidence rating for similar interviews

    Make it encouraging but honest, with actionable advice.
    """
    
    try:
        response = chat_session.send_message(feedback_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating feedback: {str(e)}")
        return None

def main():
    # Initialize session state
    if 'model' not in st.session_state:
        st.session_state.model = initialize_gemini()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'resume_uploaded' not in st.session_state:
        st.session_state.resume_uploaded = False
    
    if 'resume_file' not in st.session_state:
        st.session_state.resume_file = None
    
    if 'job_description' not in st.session_state:
        st.session_state.job_description = ""
    
    if 'session_started' not in st.session_state:
        st.session_state.session_started = False
    
    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = None
    
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    
    if 'interview_complete' not in st.session_state:
        st.session_state.interview_complete = False

    # Header
    st.markdown('<h1 class="main-header">🤖 Tech Interview Copilot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive AI interview simulation - Practice with a virtual interviewer</p>', unsafe_allow_html=True)

    # Setup Section
    if not st.session_state.session_started:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
        # Resume Upload
        st.subheader("📄 Upload Your Resume")
        
        if not st.session_state.resume_uploaded:
            uploaded_file = st.file_uploader(
                "Choose your resume file",
                type=['pdf', 'docx', 'txt'],
                help="Supported formats: PDF, DOCX, TXT (Max 2GB)"
            )
            
            if uploaded_file is not None:
                with st.spinner("Processing resume..."):
                    # Extract text content
                    file_content = uploaded_file.getvalue()
                    
                    # Upload to Gemini
                    gemini_file = upload_file_to_gemini(
                        file_content, 
                        uploaded_file.name, 
                        uploaded_file.type
                    )
                    
                    if gemini_file:
                        st.session_state.resume_file = gemini_file
                        st.session_state.resume_uploaded = True
                        st.success(f"✅ Resume uploaded successfully: {uploaded_file.name}")
                        st.rerun()
        else:
            st.markdown('<p class="status-success">✅ Resume uploaded and ready</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Job Description Input
        st.subheader("💼 Job Description")
        job_desc = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Copy and paste the full job description, including requirements, responsibilities, and qualifications...",
            value=st.session_state.job_description
        )
        
        if job_desc != st.session_state.job_description:
            st.session_state.job_description = job_desc
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Start Session Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Interview Simulation", type="primary", use_container_width=True):
                if not st.session_state.resume_uploaded:
                    st.error("⚠️ Please upload your resume first")
                elif not st.session_state.job_description.strip():
                    st.error("⚠️ Please enter the job description")
                else:
                    with st.spinner("Starting your interactive interview simulation..."):
                        # Start interactive interview
                        initial_response = start_interactive_interview(
                            st.session_state.model,
                            st.session_state.resume_file,
                            st.session_state.job_description
                        )
                        
                        if initial_response:
                            # Create chat session
                            st.session_state.chat_session = st.session_state.model.start_chat(history=[])
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": initial_response
                            })
                            
                            st.session_state.session_started = True
                            st.session_state.question_count = 1
                            st.success("🎉 Interview simulation started! The interviewer is ready to begin.")
                            st.rerun()

    # Chat Interface
    if st.session_state.session_started:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        if not st.session_state.interview_complete:
            st.subheader("🎙️ Live Interview Simulation")
            st.markdown("**Instructions:** Answer each question as you would in a real interview. The interviewer will provide brief feedback and ask the next question.")
        else:
            st.subheader("📋 Interview Complete - Final Feedback")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong style="color: #1976d2;">You:</strong><br><span style="color: #1a1a1a;">{message["content"]}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message"><strong style="color: #388e3c;">Interviewer:</strong><br><span style="color: #1a1a1a;">{message["content"]}</span></div>', unsafe_allow_html=True)
        
        # Chat input (only show if interview not complete)
        if not st.session_state.interview_complete:
            user_input = st.text_area(
                "Your answer:",
                placeholder="Type your answer here... Be specific and provide examples when possible.",
                key="chat_input",
                height=100
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("📤 Submit Answer", type="primary", use_container_width=True) and user_input.strip():
                    # Add user message to history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    with st.spinner("Interviewer is reviewing your answer..."):
                        try:
                            # Increment question count
                            st.session_state.question_count += 1
                            
                            # Check if we should end the interview
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
                                prompt = f"The candidate answered: '{user_input}'\n\nProvide brief feedback (1-2 sentences) on their answer, then ask your next interview question. This is question #{st.session_state.question_count} of approximately 8-10 total questions."
                                response = st.session_state.chat_session.send_message(prompt)
                                
                                # Add AI response to history
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": response.text
                                })
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error during interview: {str(e)}")
            
            with col2:
                if st.button("🔄 Skip Question", type="secondary", use_container_width=True):
                    # Add skip message
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": "[Skipped this question]"
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
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error skipping question: {str(e)}")
            
            with col3:
                if st.button("⏹️ End Interview", type="secondary", use_container_width=True):
                    with st.spinner("Generating final feedback..."):
                        try:
                            feedback = generate_interview_feedback(st.session_state.chat_session)
                            if feedback:
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": feedback
                                })
                                st.session_state.interview_complete = True
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error ending interview: {str(e)}")
            
            # Progress indicator
            progress = min(st.session_state.question_count / 10, 1.0)
            st.progress(progress, text=f"Interview Progress: Question {st.session_state.question_count}/~10")
        
        else:
            # Interview complete - show restart option
            st.success("🎉 Interview simulation complete! Review your feedback above.")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Start New Interview", type="primary", use_container_width=True):
                    # Clear session state
                    for key in ['chat_history', 'resume_uploaded', 'resume_file', 'job_description', 'session_started', 'chat_session', 'question_count', 'interview_complete']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

    # Footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.9rem;">Built with ❤️ using Streamlit and Gemini AI</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
