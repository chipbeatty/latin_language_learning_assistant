# Latin Learning Assistant

An interactive tool that helps users learn Latin through YouTube video transcripts, powered by Amazon Bedrock and Claude v2.

**Difficulty:** Level 200 *(Due to RAG implementation and multiple AWS services integration)*

**Business Goal:**
A progressive learning tool that demonstrates how RAG and agents can enhance language learning by grounding responses in real Latin lesson content. The system shows the evolution from basic LLM responses to a fully contextual learning assistant, helping students understand both the technical implementation and practical benefits of RAG.

**Technical Features:**
1. Process and structure Latin/English content for RAG
2. Optimal chunking and embedding of Latin language content
3. Progressive demonstration from base LLM to RAG
4. Context-aware retrieval of Latin language examples
5. Balance between direct answers and learning guidance
6. Generation of multiple-choice questions from retrieved content

**Technical Stack:**
* Amazon Bedrock
   * Claude v2 for text generation
   * Titan for embeddings (planned)
* Streamlit for web interface
* ChromaDB for vector storage
* YouTube Transcript API for content sourcing
* Python with pandas for data visualization

**Project Structure:**
* `frontend/`: Streamlit web interface
* `backend/`: Core functionality
  * `chat.py`: Amazon Bedrock integration
  * `get_transcript.py`: YouTube transcript processing
  * `rag.py`: RAG implementation
  * `structured_data.py`: Text analysis tools

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your AWS credentials in a `.env` file:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```
4. Run the Streamlit app:
   ```bash
   PYTHONPATH=/path/to/project streamlit run frontend/main.py
   ```

## Development Stages

1. **Base LLM**: Direct interaction with Claude v2
2. **Raw Transcript**: YouTube transcript processing
3. **Structured Data**: Latin text analysis
4. **RAG Implementation**: Context-aware responses
5. **Interactive Features**: Enhanced learning tools

## Security Note

Never commit the `.env` file containing your AWS credentials. It is included in `.gitignore` by default.
