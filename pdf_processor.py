# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import TokenTextSplitter

# def load_and_split_pdf(pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 0) -> list:
#     """
#     Load a PDF and split it into chunks for processing.
    
#     Args:
#         pdf_path (str): Path to the PDF file
#         chunk_size (int): Size of each chunk in characters
#         chunk_overlap (int): Overlap between chunks in characters
    
#     Returns:
#         list: List of document chunks
#     """
#     try:
#         loader = PyPDFLoader(pdf_path)
#         documents = loader.load()
#         text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
#         return text_splitter.split_documents(documents)
#     except Exception as e:
#         print(f"Error loading PDF: {e}")
#         return []


from langchain.docstore.document import Document
import pdfplumber

def load_and_split_pdf(pdf_path: str) -> list:
    """
    Load a PDF and split it into documents.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        list: List of Document objects.
    """
    try:
        documents = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract text
                text = page.extract_text()
                if not text:
                    continue
                
                # Extract tables (if any)
                tables = page.extract_tables()
                table_text = ""
                for table in tables:
                    for row in table:
                        table_text += " ".join([str(cell) for cell in row if cell]) + "\n"
                
                # Combine text and table content
                full_text = text + "\n" + table_text
                if full_text.strip():
                    doc = Document(
                        page_content=full_text,
                        metadata={"page": page_num + 1}
                    )
                    documents.append(doc)
        return documents
    except Exception as e:
        print(f"Error loading PDF {pdf_path}: {e}")
        return []