from flask import Flask, render_template, request, jsonify
import os
import shutil
from loader import load_config
from rag_chain import create_or_update_rag_chain
from cache_manager import setup_cache, get_cached_response, add_to_cache
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory

app = Flask(__name__)
config = load_config()

# Ensure upload directory exists
os.makedirs(config["UPLOAD_DIR"], exist_ok=True)

# Global variables to track RAG chain, vector store, and memory
global_qa = None
global_db = None
global_memory = None
cache_db = None
is_first_upload = True  # Track if this is the first upload in the session

@app.route('/')
def index():
    """
    Render the main page with the PDF upload form and chat interface.
    """
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset():
    """
    Reset the vector store, memory, and cache to start fresh.
    """
    global global_qa, global_db, global_memory, cache_db, is_first_upload
    try:
        # Clear persistent vector store directory
        persist_dir = config.get("PERSIST_DIR", "db")
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print(f"Cleared vector store directory: {persist_dir}")
        os.makedirs(persist_dir, exist_ok=True)

        # Clear cache directory if it exists
        cache_dir = config.get("CACHE_DIR", "cache")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"Cleared cache directory: {cache_dir}")
        os.makedirs(cache_dir, exist_ok=True)

        global_qa = None
        global_db = None
        global_memory = None
        cache_db = None
        is_first_upload = True
        return jsonify({"message": "System reset successfully"}), 200
    except Exception as e:
        print(f"Error resetting system: {e}")
        return jsonify({"error": "Failed to reset system"}), 500

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """
    Handle PDF upload and initialize or update the RAG and CAG systems.
    """
    global global_qa, global_db, global_memory, cache_db, is_first_upload
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not any(file.filename.lower().endswith(ext) for ext in config["ALLOWED_EXT"]):
        return jsonify({"error": "Allowed file types are pdf"}), 400
    
    file_path = os.path.join(config["UPLOAD_DIR"], file.filename)
    file.save(file_path)
    
    # Reset vector store and cache on first upload to avoid unrelated data
    if is_first_upload:
        persist_dir = config.get("PERSIST_DIR", "db")
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print(f"Cleared vector store directory on first upload: {persist_dir}")
        os.makedirs(persist_dir, exist_ok=True)

        cache_dir = config.get("CACHE_DIR", "cache")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"Cleared cache directory on first upload: {cache_dir}")
        os.makedirs(cache_dir, exist_ok=True)

        global_db = None
        global_memory = None
        cache_db = None
        is_first_upload = False
    
    # Create or update RAG chain with the new PDF
    global_qa, global_db = create_or_update_rag_chain(file_path, config, existing_db=global_db)
    
    # Initialize cache if not already set
    if cache_db is None:
        cache_db = setup_cache()
    
    # Initialize memory if not already set
    if global_memory is None:
        message_history = ChatMessageHistory()
        global_memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=message_history,
            return_messages=True
        )
    
    # Assign memory to the RAG chain
    if global_qa:
        global_qa.memory = global_memory
    
    if global_qa is None or global_db is None:
        return jsonify({"error": "Failed to initialize chatbot"}), 500
    return jsonify({"message": f"PDF '{file.filename}' uploaded successfully and added to knowledge base"}), 200

@app.route('/get_response', methods=['POST'])
def get_response():
    """
    Handle user queries and return responses, using cache if available.
    """
    global global_qa, cache_db
    if global_qa is None:
        return jsonify({"error": "No PDF uploaded"}), 400
    
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    
    # Add context about the target PDF if specified
    target_pdf = data.get('target_pdf', '')
    if target_pdf:
        contextual_query = f"Based on the PDF '{target_pdf}', {query}"
    else:
        contextual_query = query
    
    # Generate new response
    try:
        result = global_qa({"question": contextual_query})
        answer = result['answer']
        
        # Cache the response (using original query to avoid caching with context)
        add_to_cache(query, answer, cache_db)
        return jsonify({"answer": answer}), 200
    except Exception as e:
        print(f"Error generating response: {e}")
        return jsonify({"error": "Failed to generate response"}), 500

@app.route('/debug_vector_store', methods=['GET'])
def debug_vector_store():
    """
    Debug endpoint to list all documents in the vector store.
    """
    if global_db is None:
        return jsonify({"error": "No vector store initialized"}), 400
    docs = global_db.get()
    return jsonify({
        "documents": docs['documents'],
        "metadatas": docs['metadatas']
    }), 200

if __name__ == '__main__':
    app.run(debug=True)