
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from pdf_processor import load_and_split_pdf
import os

def create_or_update_rag_chain(pdf_path: str, config: dict, persist_dir: str = "db", existing_db: Chroma = None) -> ConversationalRetrievalChain:

    try:
        print(f"Processing PDF: {pdf_path}")
        documents = load_and_split_pdf(pdf_path)
        if not documents:
            raise ValueError(f"No documents loaded from PDF: {pdf_path}")

        # Add metadata to documents to track their source PDF
        pdf_filename = os.path.basename(pdf_path)
        for doc in documents:
            doc.metadata["source_pdf"] = pdf_filename

        # Log extracted documents for debugging
        print(f"Extracted {len(documents)} documents from {pdf_path}:")
        for i, doc in enumerate(documents):
            print(f"Document {i+1}: {doc.page_content[:200]}...")

        # Initialize embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=config["GOOGLE_API_KEY"]
        )

        # If an existing vector store is provided, append new documents; otherwise, create a new one
        if existing_db:
            print(f"Appending documents to existing vector store from {pdf_path}")
            existing_db.add_documents(documents)
            db = existing_db
        else:
            print(f"Creating new Chroma vector store for {pdf_path}")
            db = Chroma.from_documents(documents, embeddings, persist_directory=persist_dir)

        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=config["GOOGLE_API_KEY"],
            temperature=0.3
        )

        # Set up memory
        message_history = ChatMessageHistory()
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=message_history,
            return_messages=True
        )

        # Create or update RAG chain without strict source filtering
        print("Creating/Updating RAG chain")
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=db.as_retriever(search_type="mmr", search_kwargs={"k": 5}),
            memory=memory
        )
        return qa_chain, db
    except Exception as e:
        print(f"Error creating/updating RAG chain: {e}")
        return None, None