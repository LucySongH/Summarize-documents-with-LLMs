import PyPDF2
import docx
import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
import time

def initialize_model():
    """Initialize the LLaMA model via Ollama"""
    try:
        # Try llama2 first (more commonly available)
        model_id = "llama2"
        model = Ollama(model=model_id)
        print(f"Successfully initialized model: {model_id}")
        return model
    except Exception as e:
        print(f"Error initializing llama2: {e}")
        try:
            # Fallback to llama2:7b if available
            model_id = "llama2:7b"
            model = Ollama(model=model_id)
            print(f"Successfully initialized model: {model_id}")
            return model
        except Exception as e2:
            print(f"Error initializing llama2:7b: {e2}")
            print("Please make sure Ollama is installed and running with a compatible model")
            return None

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None

def extract_text_from_txt(file_path):
    """Extract text from a TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return None

def extract_text_from_document(file_path):
    """Extract text from various document formats."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return None
    
    file_extension = file_path.suffix.lower()
    
    print(f"Processing file: {file_path.name} ({file_extension})")
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        print(f"Unsupported file format: {file_extension}")
        print("Supported formats: .pdf, .docx, .txt")
        return None

def create_summary_prompt(text, min_words=300, max_words=500):
    """Create a prompt for document summarization with specified length."""
    prompt_template = ChatPromptTemplate.from_template(
        """Please provide a detailed summary of the following document, 
        capturing the main ideas, key arguments, and significant details. 
        The summary should be comprehensive, covering all major sections or themes, 
        and should be between {min_words} and {max_words} words in length. 
        Ensure the summary is clear, concise, and well-structured, 
        avoiding excessive repetition or minor details:

        {text}

        Summary:"""
    )
    return prompt_template.format(text=text, min_words=min_words, max_words=max_words)

def get_user_file_path():
    """Get file path from user input with validation."""
    print("\n" + "="*60)
    print("DOCUMENT SUMMARIZATION TOOL")
    print("="*60)
    print("Supported formats: PDF (.pdf), Word (.docx), Text (.txt)")
    print("="*60)
    
    while True:
        file_path = input("\nEnter the path to your document: ").strip()
        
        if not file_path:
            print("Please enter a valid file path.")
            continue
        
        # Remove quotes if user added them
        file_path = file_path.strip('"\'')
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            print("Please check the path and try again.")
            continue
        
        file_extension = Path(file_path).suffix.lower()
        supported_formats = ['.pdf', '.docx', '.txt']
        
        if file_extension not in supported_formats:
            print(f"Unsupported file format: {file_extension}")
            print(f"Supported formats: {', '.join(supported_formats)}")
            continue
        
        return file_path

def save_summary_to_file(summary, original_file_path):
    """Save the summary to a text file."""
    try:
        original_name = Path(original_file_path).stem
        summary_file = f"{original_name}_summary.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("DOCUMENT SUMMARY\n")
            f.write("="*50 + "\n\n")
            f.write(summary)
        
        print(f"\nSummary saved to: {summary_file}")
        return summary_file
    except Exception as e:
        print(f"Error saving summary: {e}")
        return None

def summarize_document(file_path):
    """Main function to summarize a document."""
    print(f"\nProcessing: {Path(file_path).name}")
    
    # Initialize model
    print("Initializing AI model...")
    model = initialize_model()
    if model is None:
        return
    
    # Extract text from document
    print("Extracting text from document...")
    text = extract_text_from_document(file_path)
    if text is None:
        return
    
    if not text.strip():
        print("No text content found in the document.")
        return
    
    print(f"Extracted {len(text)} characters of text")
    
    # Create summary prompt
    prompt = create_summary_prompt(text)
    
    # Generate summary
    try:
        print("Generating summary...")
        summary = model.invoke(prompt)
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(summary)
        print("="*60)
        
        # Ask if user wants to save the summary
        save_choice = input("\nWould you like to save this summary to a file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            save_summary_to_file(summary, file_path)
        
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")

def main():
    """Main function with user interaction."""
    try:
        while True:
            file_path = get_user_file_path()
            summarize_document(file_path)
            
            # Ask if user wants to process another document
            another = input("\nWould you like to summarize another document? (y/n): ").strip().lower()
            if another not in ['y', 'yes']:
                break
        
        print("\nThank you for using the Document Summarization Tool!")
        
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
