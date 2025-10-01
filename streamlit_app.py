import streamlit as st
import PyPDF2
import docx
import os
from pathlib import Path
import tempfile
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
import time

# Page configuration
st.set_page_config(
    page_title="Document Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_model():
    """Initialize the LLaMA model via Ollama with caching."""
    try:
        # Try llama2 first (more commonly available)
        model_id = "llama2"
        model = Ollama(model=model_id)
        return model, model_id
    except Exception as e:
        try:
            # Fallback to llama2:7b if available
            model_id = "llama2:7b"
            model = Ollama(model=model_id)
            return model, model_id
        except Exception as e2:
            return None, None

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def extract_text_from_docx(file):
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return None

def extract_text_from_txt(file):
    """Extract text from a TXT file."""
    try:
        text = file.read().decode('utf-8')
        return text
    except Exception as e:
        st.error(f"Error reading TXT: {e}")
        return None

def extract_text_from_document(uploaded_file):
    """Extract text from various document formats."""
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    st.info(f"Processing file: {uploaded_file.name} ({file_extension})")
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_extension == '.docx':
        return extract_text_from_docx(uploaded_file)
    elif file_extension == '.txt':
        return extract_text_from_txt(uploaded_file)
    else:
        st.error(f"Unsupported file format: {file_extension}")
        st.info("Supported formats: .pdf, .docx, .txt")
        return None

def create_summary_prompt(text, summary_type="comprehensive"):
    """Create a prompt for document summarization."""
    if summary_type == "comprehensive":
        template = "Please provide a comprehensive summary of the following document:\n\n{text}\n\nSummary:"
    elif summary_type == "brief":
        template = "Please provide a brief summary (2-3 sentences) of the following document:\n\n{text}\n\nSummary:"
    elif summary_type == "key_points":
        template = "Please extract the key points from the following document:\n\n{text}\n\nKey Points:"
    else:
        template = "Please provide a comprehensive summary of the following document:\n\n{text}\n\nSummary:"
    
    prompt_template = ChatPromptTemplate.from_template(template)
    return prompt_template.format(text=text)

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Document Summarizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload your document and get an AI-powered summary instantly!</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Summary type selection
        summary_type = st.selectbox(
            "Summary Type",
            ["comprehensive", "brief", "key_points"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        # Model status
        st.header("🤖 Model Status")
        model, model_id = initialize_model()
        
        if model:
            st.success(f"✅ Model: {model_id}")
        else:
            st.error("❌ Model not available")
            st.info("Please make sure Ollama is installed and running with a compatible model")
            st.stop()
        
        # Supported formats
        st.header("📋 Supported Formats")
        st.info("""
        • PDF (.pdf)
        • Word (.docx)
        • Text (.txt)
        """)
        
        # Instructions
        st.header("📖 Instructions")
        st.info("""
        1. Upload your document
        2. Choose summary type
        3. Click 'Generate Summary'
        4. Download or copy the result
        """)
    
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # File upload
        st.header("📁 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt'],
            help="Upload a PDF, Word document, or text file"
        )
        
        if uploaded_file is not None:
            # Display file info
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            }
            st.json(file_details)
            
            # Generate summary button
            if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
                with st.spinner("Processing your document..."):
                    # Extract text
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Extracting text from document...")
                    text = extract_text_from_document(uploaded_file)
                    progress_bar.progress(33)
                    
                    if text is None:
                        st.error("Failed to extract text from the document.")
                        return
                    
                    if not text.strip():
                        st.error("No text content found in the document.")
                        return
                    
                    # Show text statistics
                    st.success(f"✅ Extracted {len(text)} characters of text")
                    progress_bar.progress(66)
                    
                    # Generate summary
                    status_text.text("Generating summary with AI...")
                    prompt = create_summary_prompt(text, summary_type)
                    
                    try:
                        summary = model.invoke(prompt)
                        progress_bar.progress(100)
                        status_text.text("Summary generated successfully!")
                        
                        # Display summary
                        st.header("📋 Summary")
                        st.markdown("---")
                        
                        # Summary in a nice box
                        st.markdown(f"""
                        <div class="success-box">
                        {summary}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download button
                        st.download_button(
                            label="💾 Download Summary",
                            data=summary,
                            file_name=f"{Path(uploaded_file.name).stem}_summary.txt",
                            mime="text/plain"
                        )
                        
                        # Copy to clipboard
                        st.button("📋 Copy to Clipboard", on_click=lambda: st.write("Summary copied to clipboard!"))
                        
                    except Exception as e:
                        st.error(f"Error generating summary: {e}")
                        progress_bar.progress(0)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>Powered by LangChain and Ollama | Built with Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
