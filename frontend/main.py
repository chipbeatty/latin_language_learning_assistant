import streamlit as st
from typing import Dict
import json
from collections import Counter
import re

from backend.get_transcript import YouTubeTranscriptDownloader
from backend.utils import validate_youtube_url

# Lazy load LangChain to avoid import errors when not needed
def get_latin_chain():
    from backend.langchain_setup import LatinLearningChain
    return LatinLearningChain()


# Page config
st.set_page_config(
    page_title="French Learning Assistant",
    page_icon="🏛️",
    layout="wide"
)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'latin_chain' not in st.session_state:
    st.session_state.latin_chain = None  # Will be initialized when needed

def render_header():
    """Render the header section"""
    st.title("🏛️ French Learning Assistant")
    st.markdown("""
    Transform YouTube transcripts into interactive French learning experiences.
    
    This tool demonstrates:
    - Base LLM Capabilities
    - RAG (Retrieval Augmented Generation)
    - Amazon Bedrock Integration
    - Agent-based Learning Systems
    """)

def render_sidebar():
    """Render the sidebar with component selection"""
    with st.sidebar:
        st.header("Development Stages")
        
        # Main component selection
        selected_stage = st.radio(
            "Select Stage:",
            [
                "1. Chat with Claude",
                "2. Raw Transcript",
                "3. Structured Data",
                "4. RAG Implementation",
                "5. Interactive Learning"
            ]
        )
        
        # Stage descriptions
        stage_info = {
            "1. Chat with Claude": """
            **Current Focus:**
            - Basic French learning
            - Understanding LLM capabilities
            - Identifying limitations
            """,
            
            "2. Raw Transcript": """
            **Current Focus:**
            - YouTube transcript download
            - Raw text visualization
            - Initial data examination
            """,
            
            "3. Structured Data": """
            **Current Focus:**
            - Text cleaning
            - Dialogue extraction
            - Data structuring
            """,
            
            "4. RAG Implementation": """
            **Current Focus:**
            - Bedrock embeddings
            - Vector storage
            - Context retrieval
            """,
            
            "5. Interactive Learning": """
            **Current Focus:**
            - Scenario generation
            - Audio synthesis
            - Interactive practice
            """
        }
        
        st.markdown("---")
        st.markdown(stage_info[selected_stage])
        
        return selected_stage

def render_chat_stage():
    """Render an improved chat interface"""
    st.header("Chat with Claude")

    # Initialize BedrockChat instance if not in session state
    if 'bedrock_chat' not in st.session_state:
        st.session_state.bedrock_chat = BedrockChat()

    # Introduction text
    st.markdown("""
    Start by exploring Claude's base French language capabilities. Try asking questions about French grammar, 
    vocabulary, or cultural aspects.
    """)

    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Chat input area
    if prompt := st.chat_input("Ask about French language..."):
        # Process the user input
        process_message(prompt)

    # Example questions in sidebar
    with st.sidebar:
        st.markdown("### Try These Examples")
        example_questions = [
            "How do I say 'Where is the train station?' in French?", 
            "What is the difference between the nominative and accusative cases in French?",  
            "How do you express politeness or formality in French?", 
            "How do I count objects in French?",  
            "What is the difference between 'salve' and 'ave' in French greetings?",
            "How do I ask for directions in French?"      
        ]
        
        for q in example_questions:
            if st.button(q, use_container_width=True, type="secondary"):
                # Process the example question
                process_message(q)
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat", type="primary"):
            st.session_state.messages = []
            st.rerun()

def process_message(message: str):
    """Process a message and generate a response"""
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(message)

    # Generate and display assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        response = st.session_state.bedrock_chat.generate_response(message)
        if response:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


def count_characters(text):
    """Count French letters and total characters in text"""
    if not text:
        return 0, 0

    def is_french(char):
        return 'A' <= char <= 'Z' or 'a' <= char <= 'z'

    french_chars = sum(1 for char in text if is_french(char))
    return french_chars, len(text)

def render_transcript_stage():
    """Render the raw transcript stage"""
    st.header("Raw Transcript Processing")
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="Enter a French lesson YouTube URL"
    )
    
    # Download button and processing
    if url:
        if st.button("Download Transcript"):
            try:
                downloader = YouTubeTranscriptDownloader()
                transcript = downloader.get_transcript(url)
                if transcript:
                    # Store the raw transcript text in session state
                    transcript_text = "\n".join([entry['text'] for entry in transcript])
                    st.session_state.transcript = transcript_text
                    
                    # Save transcript to file
                    video_id = downloader.extract_video_id(url)[0]
                    if video_id:
                        import os
                        transcript_dir = "backend/transcripts"
                        os.makedirs(transcript_dir, exist_ok=True)
                        transcript_path = os.path.join(transcript_dir, f"{video_id}.txt")
                        
                        with open(transcript_path, "w", encoding="utf-8") as f:
                            f.write(transcript_text)
                        
                        st.success(f"Transcript downloaded and saved to {transcript_path}!")
                    else:
                        st.error("Could not extract video ID from URL")
                else:
                    st.error("No transcript found for this video.")
            except Exception as e:
                st.error(f"Error downloading transcript: {str(e)}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Transcript")
        if st.session_state.transcript:
            st.text_area(
                label="Raw text",
                value=st.session_state.transcript,
                height=400,
                disabled=True
            )
    
        else:
            st.info("No transcript loaded yet")
    
    with col2:
        st.subheader("Transcript Stats")
        if st.session_state.transcript:
            # Calculate stats
            latin_chars, total_chars = count_characters(st.session_state.transcript)
            total_lines = len(st.session_state.transcript.split('\n'))
            
            # Display stats
            st.metric("Total Characters", total_chars)
            st.metric("Latin Characters", latin_chars)
            st.metric("Total Lines", total_lines)
        else:
            st.info("Load a transcript to see statistics")

def render_structured_stage():
    """Render the structured data stage"""
    st.header("Structured Data Processing")
    
    # List available transcripts
    import os
    transcript_dir = "backend/transcripts"
    if not os.path.exists(transcript_dir):
        st.error("No transcripts found. Please download some transcripts first.")
        return
        
    transcript_files = [f for f in os.listdir(transcript_dir) if f.endswith('.txt')]
    
    if not transcript_files:
        st.error("No transcripts found. Please download some transcripts first.")
        return
    
    # Select transcript to process
    selected_file = st.selectbox(
        "Select Transcript to Process",
        transcript_files,
        format_func=lambda x: f"Video ID: {x.replace('.txt', '')}"
    )
    
    if selected_file and st.button("Process Transcript"):
        with st.spinner("Processing transcript..."):
            # Read transcript
            transcript_path = os.path.join(transcript_dir, selected_file)
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
            
            # Structure the data
            from backend.structured_data import TranscriptStructurer
            structurer = TranscriptStructurer()
            structured_data = structurer.structure_transcript(transcript_text)
            
            if structured_data:
                # Save structured data
                structured_dir = "backend/structured"
                os.makedirs(structured_dir, exist_ok=True)
                output_path = os.path.join(structured_dir, selected_file)
                
                success = structurer.save_questions(structured_data, output_path)
                
                if success:
                    st.success(f"Successfully processed and saved to {output_path}")
                    
                    # Display preview
                    with st.expander("Preview Structured Data", expanded=True):
                        st.text(structured_data)
                else:
                    st.error("Failed to save structured data")
            else:
                st.error("Failed to structure the transcript")

def render_rag_stage():
    """Render the RAG implementation stage"""
    st.header("RAG System")
    
    # URL input for new transcripts
    url = st.text_input(
        "YouTube URL",
        placeholder="Enter a French lesson YouTube URL"
    )
    
    # Validate URL as user types
    if url:
        is_valid, message = validate_youtube_url(url)
        if not is_valid:
            st.warning(message)
    
    # Load transcript button
    if url and st.button("Load Transcript for RAG", disabled=not (url and validate_youtube_url(url)[0])):
        with st.spinner("Loading and processing transcript..."):
            if st.session_state.latin_chain is None:
                st.session_state.latin_chain = get_latin_chain()
            if st.session_state.latin_chain.load_transcript(url):
                st.success("Transcript loaded and processed successfully!")
            else:
                st.error("Failed to load transcript. Please check if captions are available.")
    
    # Query input
    query = st.text_input(
        "Ask a Question",
        placeholder="Ask anything about the French content..."
    )
    
    # Process query
    if query:
        with st.spinner("Processing your question..."):
            if st.session_state.latin_chain is None:
                st.session_state.latin_chain = get_latin_chain()
            response = st.session_state.latin_chain.process_question(query)
            if response:
                st.markdown("### Tutor's Response")
                st.write(response)

def reset_quiz_state():
    """Reset all quiz-related session state"""
    # Clear all session state except user preferences and quiz generator
    keys_to_keep = ['page', 'quiz_generator']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
            
    # Reinitialize quiz state
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.questions = []
    st.session_state.submitted = False
    st.session_state.quiz_started = False

def render_interactive_stage():
    """Render the interactive learning stage"""
    st.header("Interactive Learning")
    
    # Initialize session state for quiz
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    
    # Practice type selection
    practice_type = st.selectbox(
        "Select Practice Type",
        ["-- Select practice type --", "Vocabulary Quiz", "Dialogue Practice", "Listening Exercise"],
        index=0
    )
    
    # Validate practice type selection
    if practice_type == "-- Select practice type --":
        st.info("Please select a practice type to begin.")
        return
    
    if practice_type == "Vocabulary Quiz":
        # Initialize quiz generator if not in session state
        if 'quiz_generator' not in st.session_state:
            from backend.interactive import QuizGenerator
            st.session_state.quiz_generator = QuizGenerator()
            
        # Get available files
        structured_files = st.session_state.quiz_generator.get_available_files()
        
        if not structured_files:
            st.error("No structured data found. Please process some transcripts first.")
            return
        
        # Select file to use
        selected_file = st.selectbox(
            "Select Video Questions",
            ["-- Select a video --"] + structured_files,
            format_func=lambda x: x if x == "-- Select a video --" else f"Video ID: {x.replace('.txt', '')}"
        )
        
        # Validate selection
        if selected_file == "-- Select a video --":
            st.info("Please select a video to load questions from.")
            return
        
        # Only show Start Quiz button if quiz hasn't started
        if not st.session_state.quiz_started:
            if selected_file and st.button("Start Quiz"):
                try:
                    questions = st.session_state.quiz_generator.load_questions(selected_file)
                    if questions:
                        reset_quiz_state()
                        st.session_state.questions = questions
                        st.session_state.quiz_started = True
                        st.success("Quiz started! Good luck!")
                        st.rerun()
                    else:
                        st.error("No questions found in the selected video.")
                except Exception as e:
                    st.error(f"Error loading questions: {str(e)}")
        
        # Display current question if available
        if st.session_state.questions and len(st.session_state.questions) > st.session_state.current_question:
            current_q = st.session_state.questions[st.session_state.current_question]
            
            # Display question
            st.markdown(f"### Question {st.session_state.current_question + 1}")
            st.markdown(current_q['question'])
            
            # Display choices
            choice = st.radio(
                "Choose your answer:",
                current_q['choices'],
                key=f"q_{st.session_state.current_question}"
            )
            
            # Initialize session state for current question
            if 'submitted' not in st.session_state:
                st.session_state.submitted = False

            # Question interface
            cols = st.columns([3, 1])
            with cols[0]:
                # Initialize feedback state if not exists
                if 'feedback' not in st.session_state:
                    st.session_state.feedback = None
                    
                # Show feedback from previous submission
                if st.session_state.feedback:
                    if st.session_state.feedback['correct']:
                        st.success('✅ Correct! Great job!')
                    else:
                        st.error('❌ Incorrect.')
                        st.info(f'The correct answer was: {st.session_state.feedback["correct_answer"]}')
                
                # Show appropriate button based on state
                if not st.session_state.submitted:
                    submit = st.button('Submit Answer')
                    if submit:
                        is_correct = st.session_state.quiz_generator.validate_answer(current_q, choice)
                        if is_correct:
                            st.session_state.score += 1
                        st.session_state.feedback = {
                            'correct': is_correct,
                            'correct_answer': current_q['correct_answer']
                        }
                        st.session_state.submitted = True
                        st.rerun()
                else:
                    next_q = st.button('Next Question')
                    if next_q:
                        if st.session_state.current_question < len(st.session_state.questions) - 1:
                            st.session_state.current_question += 1
                            st.session_state.submitted = False
                            st.session_state.feedback = None
                            st.rerun()
                        else:
                            st.success("🎉 You've completed all questions!")

            # Show score and progress
            with cols[1]:
                total_questions = len(st.session_state.questions)
                current_q_num = st.session_state.current_question + 1
                
                if current_q_num == total_questions and st.session_state.submitted:
                    st.success(f'Quiz completed!\nFinal score: {st.session_state.score}/{total_questions}')
                    if st.button('Start Over'):
                        reset_quiz_state()
                        st.session_state.quiz_started = False
                        st.rerun()
                else:
                    st.info(f'Question {current_q_num} of {total_questions}')
                    st.markdown(f"Score: {st.session_state.score}/{current_q_num if st.session_state.submitted else current_q_num - 1}")
            
            # Display progress
            progress = current_q_num / total_questions
            st.progress(progress)
    
    # Future sections for additional features can be added here
    pass

def main():
    render_header()
    selected_stage = render_sidebar()
    
    # Render appropriate stage
    if selected_stage == "1. Chat with Nova":
        render_chat_stage()
    elif selected_stage == "2. Raw Transcript":
        render_transcript_stage()
    elif selected_stage == "3. Structured Data":
        render_structured_stage()
    elif selected_stage == "4. RAG Implementation":
        render_rag_stage()
    elif selected_stage == "5. Interactive Learning":
        render_interactive_stage()
    
    # Debug section at the bottom
    with st.expander("Debug Information"):
        st.json({
            "selected_stage": selected_stage,
            "transcript_loaded": st.session_state.transcript is not None,
            "chat_messages": len(st.session_state.messages)
        })

if __name__ == "__main__":
    main()