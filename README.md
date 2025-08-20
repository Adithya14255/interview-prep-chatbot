# Interview Prep Chatbot

A modern, sleek Streamlit-based interview preparation chatbot with clean chat interface.

## Features

- **Smart Resume Analysis**: Upload your resume (PDF, DOCX, TXT) once per session
- **Job Description Matching**: Paste any job description for tailored questions
- **Interactive Interview Simulation**: Real-time Q&A with an AI interviewer
- **Progressive Questioning**: Questions adapt based on your answers and increase in difficulty
- **Instant Feedback**: Get brief feedback after each answer before moving to the next question
- **Comprehensive Evaluation**: Detailed performance analysis at the end
- **Professional UI**: Clean, centered layout with progress tracking

## How It Works

### 🎯 Interactive Interview Flow
1. **Upload Resume & Job Description**: One-time setup per session
2. **Start Interview Simulation**: AI interviewer introduces the process
3. **Answer Questions One by One**: 
   - Respond to each question individually
   - Get immediate feedback on your answer
   - Progress through 8-10 questions of increasing difficulty
4. **Receive Final Feedback**: Comprehensive performance evaluation with actionable insights

### 🎙️ Interview Experience
- **Warm-up Questions**: Start with easier questions to build confidence
- **Technical Assessment**: Progress through beginner → intermediate → advanced topics
- **Behavioral Questions**: Situational and soft skills evaluation
- **Real-time Adaptation**: Questions adapt based on your performance
- **Skip Options**: Can skip difficult questions if needed
- **Progress Tracking**: Visual progress bar shows interview completion

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an account or sign in
3. Generate an API key
4. Copy the API key

### 3. Configure Environment

1. Open the `.env` file
2. Replace `your_gemini_api_key_here` with your actual Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage Guide

### Step 1: Upload Resume
- Click "Choose your resume file"
- Select a PDF, DOCX, or TXT file (max 2GB)
- Wait for the upload confirmation

### Step 2: Enter Job Description
- Paste the complete job description in the text area
- Include requirements, responsibilities, and qualifications

### Step 3: Start Interview Simulation
- Click "Start Interview Simulation"
- AI interviewer will introduce themselves and the process
- Begin answering questions one by one

### Step 4: Interactive Interview
- **Answer Each Question**: Type your response in the text area
- **Get Feedback**: Receive brief feedback before the next question
- **Track Progress**: Monitor your progress through the interview
- **Options Available**:
  - Submit Answer: Provide your response and get feedback
  - Skip Question: Move to next question if stuck
  - End Interview: Complete early and get feedback

### Step 5: Performance Evaluation
- Receive comprehensive feedback covering:
  - Strengths demonstrated
  - Areas for improvement
  - Technical assessment
  - Communication skills
  - Specific recommendations
  - Overall readiness rating

### Step 6: New Interview
- Click "Start New Interview" to practice with different job/resume

## Application Structure

```
chatbot/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (API key)
└── README.md          # This file
```

## Key Features Explained

### Resume Processing
- Supports multiple file formats (PDF, DOCX, TXT)
- Uploads to Gemini Files API for efficient processing
- Stores file reference in session state (no re-upload needed)

### AI Analysis
- Uses Gemini 1.5 Pro for comprehensive analysis
- Compares resume content against job requirements
- Identifies strengths, gaps, and preparation areas

### Interview Questions
- **Technical Questions**: Based on job requirements and resume skills
- **Behavioral Questions**: Tailored to role and company culture
- **Scenario-Based Questions**: Real-world problems for the position
- **Difficulty Levels**: Beginner, Intermediate, Expert categorization

### Chat Functionality
- Persistent context throughout the session
- No need to re-upload resume or re-enter job description
- Intelligent follow-up responses
- Maintains conversation history

## Technical Specifications

### Dependencies
- **Streamlit**: Web application framework
- **google-generativeai**: Gemini AI integration
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX document processing
- **python-dotenv**: Environment variable management

### API Constraints
- Max file size: 2GB
- File retention: 48 hours
- Total storage: 20GB per project
- Uses free tier resources

### Security Notes
- API key stored in environment variables
- Temporary files cleaned up after upload
- No permanent storage of user data

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your Gemini API key is correctly set in `.env`
   - Verify the key is valid and has proper permissions

2. **File Upload Issues**
   - Check file format (PDF, DOCX, TXT only)
   - Ensure file size is under 2GB
   - Try refreshing the page if upload fails

3. **Chat Not Working**
   - Make sure you've uploaded a resume and entered a job description
   - Check your internet connection
   - Restart the application if needed

### Error Messages

- `⚠️ Please set your Gemini API key in the .env file`: Configure your API key
- `⚠️ Please upload your resume first`: Complete the resume upload step
- `⚠️ Please enter the job description`: Fill in the job description text area

## Best Practices

### For Best Results
1. **Complete Resume**: Ensure your resume includes all relevant skills and experience
2. **Full Job Description**: Include the complete job posting with requirements
3. **Specific Questions**: Ask detailed follow-up questions for better responses
4. **Context Awareness**: The AI remembers your resume and JD throughout the session

### Performance Tips
1. **File Size**: Smaller files upload faster (though 2GB max is supported)
2. **Clear Text**: Ensure resume text is clear and well-formatted
3. **Detailed JD**: More detailed job descriptions yield better analysis

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure your Gemini API key is valid and properly configured
4. Check the Streamlit console for detailed error messages

## License

This project is open source and available for personal and educational use.
