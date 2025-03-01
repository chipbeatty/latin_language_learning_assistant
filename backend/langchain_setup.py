from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_aws import ChatBedrock
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Import our existing transcript downloader
from .get_transcript import YouTubeTranscriptDownloader

# Load environment variables
load_dotenv()

class LatinTranscriptLoader:
    """Custom document loader for YouTube Latin lessons"""
    
    def __init__(self):
        self.downloader = YouTubeTranscriptDownloader()
    
    def load_from_url(self, url: str) -> List[Document]:
        """Load transcript from YouTube URL and convert to LangChain Documents"""
        # Get transcript using our existing downloader
        transcript = self.downloader.get_transcript(url)
        if not transcript:
            return []
        
        # Convert transcript to text
        text = "\n".join([entry['text'] for entry in transcript])
        
        # Create LangChain Document
        metadata = {"source": url}
        return [Document(page_content=text, metadata=metadata)]

class LatinLearningChain:
    """Main class for Latin learning RAG implementation"""
    
    def __init__(self):
        # Initialize Bedrock client with Claude v2
        self.llm = ChatBedrock(
            model_id="anthropic.claude-v2",
            region_name="us-east-1",
            model_kwargs={
                "temperature": 0.5,
                "max_tokens": 500,
                "messages": []
            }
        )
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        
        # Create text splitter optimized for Latin text
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "]
        )
        
        # Initialize document loader
        self.loader = LatinTranscriptLoader()
        
        # Initialize ChromaDB
        self.db_dir = "chroma_db"
        os.makedirs(self.db_dir, exist_ok=True)
        self.vectorstore = None
        
        # Create conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create custom prompt template
        self.qa_template = """You are a helpful French language tutor. Use the following context to answer the student's question.
        If you don't know the answer, just say you don't know. Don't try to make up an answer.

        Context: {context}

        Chat History: {chat_history}
        
        Student's Question: {question}

        Tutor's Response:"""
        
        self.qa_prompt = PromptTemplate(
            template=self.qa_template,
            input_variables=["context", "chat_history", "question"]
        )

    def load_transcript(self, url: str) -> bool:
        """Load and process a new transcript"""
        # Load documents
        documents = self.loader.load_from_url(url)
        if not documents:
            return False
            
        # Split documents
        splits = self.text_splitter.split_documents(documents)
        
        # Create or update vector store
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            collection_name="french_transcripts",
            persist_directory=self.db_dir
        )
        
        return True

    def create_chain(self) -> Optional[ConversationalRetrievalChain]:
        """Create the RAG chain for question answering"""
        if not self.vectorstore:
            return None
            
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": self.qa_prompt}
        )

    def process_question(self, question: str) -> Optional[str]:
        """Process a student's question and return the tutor's response"""
        chain = self.create_chain()
        if not chain:
            return "Please load a transcript first."
            
        try:
            response = chain.invoke({"question": question})
            return response['answer']
        except Exception as e:
            return f"Error processing question: {str(e)}"
