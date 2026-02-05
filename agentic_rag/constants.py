
GEMINI_API_KEY = ""
GROQ_API_KEY=""
PATHWAY_LICENSE_KEY = ""
HOST = "0.0.0.0"
PORT = 8666
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
REQUEST_HEADERS = {
    'Content-Type': 'application/json',
}
DATA_FOLDER = "data"
CLEANED_DATA_FOLDER = "documentations"
DDGS_MAX_RESULTS_THRESHOLD = 5
THRESHOLD = 0.3
CONTEXT_KEY = "CONTEXT"
SYSTEM_INSTRUCTIONS_KEY = "SYSTEM_INSTRUCTIONS"
TOP_K = 5
CHUNK_SIZE = 512
CHUNK_OVERLAP = 20
UNSTRUCTURED_API_KEY = ''
UNSTRUCTURED_API_URL = 'https://api.unstructuredapp.io/general/v0/general'
CSV_FOLDER = "csv_files"
TABLE_KEY = "TABLE_FILE_NAME"
TABLE_SYNTAX = f"$[[table_{TABLE_KEY}]]"
OPENAI_API_KEY = ""
MAX_DECOMPOSITION_DEPTH = 4