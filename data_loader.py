# data_loader.py
import os
import sys
import pandas as pd

def load_csv_dataset(file_path: str) -> pd.DataFrame:
    """Safely extracts tabular data matrices from local storage components."""
    print(f"📂 [Data Loader] Opening source data asset: {file_path}")
    if not os.path.exists(file_path):
        print(f"❌ Error: Required data file target '{file_path}' does not exist.")
        sys.exit(1)
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"❌ Error: Malformed dataset schema parsing crash: {str(e)}")
        sys.exit(1)

def extract_text_from_binary_stream(file_bytes: bytes, filename: str) -> str:
    """
    Decodes incoming raw request binary streams into regular python strings.
    Iterates through internal structures dynamically if a PDF document is supplied.
    """
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            return extracted_text
        except ImportError:
            # Fallback system if environment is missing pypdf dependencies
            return file_bytes.decode('utf-8', errors='ignore')
    else:
        return file_bytes.decode('utf-8', errors='ignore')