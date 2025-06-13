from langchain.embeddings import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

def create_rag_chain(pdf_path: str, config: dict, persist_dir: str = "db") -> ConversationalRetrievalChain:
    """
    Create a RAG chain using Gemini API for embeddings and generation.
    
    Args:
        pdf_path (str): Path to the PDF file
        config (dict): Configuration dictionary with API key
        persist_dir (str): Directory to persist vector store
    
    Returns:
        ConversationalRetrievalChain: Configured RAG chain
    """
    try:
        # Load and split PDF
        documents = load_and_split_pdf(pdf_path)
        if not documents:
            raise ValueError("No documents loaded from PDF")

        # Set up embeddings and vector store
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=config["GOOGLE_API_KEY"])
        db = Chroma.from_documents(documents, embeddings, persist_directory=persist_dir)
        db.persist()

        # Set up LLM and memory
        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=config["GOOGLE_API_KEY"], temperature=0.3)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Create RAG chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=db.as_retriever(search_kwargs={"k": 3}),
            memory=memory
        )
        return qa_chain
    except Exception as e:
        print(f"Error creating RAG chain: {e}")
        return None