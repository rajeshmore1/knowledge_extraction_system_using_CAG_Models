from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import TokenTextSplitter

def load_and_split_pdf(pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 0) -> list:
    """
    Load a PDF and split it into chunks for processing.
    
    Args:
        pdf_path (str): Path to the PDF file
        chunk_size (int): Size of each chunk in characters
        chunk_overlap (int): Overlap between chunks in characters
    
    Returns:
        list: List of document chunks
    """
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter.split_documents(documents)
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return []