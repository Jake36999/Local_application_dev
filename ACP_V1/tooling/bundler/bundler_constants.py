"""
Configuration constants for Directory Bundler.
Centralized location for all magic numbers and configuration values.
"""

# ==========================================
# FILE PROCESSING CONSTANTS
# ==========================================

# Maximum file size in megabytes
DEFAULT_MAX_FILE_SIZE_MB = 50.0
ABSOLUTE_MAX_FILE_SIZE_MB = 500.0

# Chunk size for processing
DEFAULT_CHUNK_SIZE_MB = 2.0
MAX_CHUNK_SIZE_MB = 10.0

# Content preview length
CONTENT_PREVIEW_LENGTH = 2000

# Scan depth limit
DEFAULT_SCAN_DEPTH = 10
MAX_SCAN_DEPTH = 50

# ==========================================
# IGNORE PATTERNS
# ==========================================

DEFAULT_IGNORE_DIRS = [
    # Python/Virtualenv
    ".venv", "venv", "env", "virtualenv", ".virtualenv", ".envs",
    "__pycache__", ".pytest_cache", ".mypy_cache", "site-packages", "dist-packages",
    # Node.js
    "node_modules", ".npm",
    # Version Control & Git internals (huge!)
    ".git", ".hg", ".svn", ".bzr", "bundler_scans",
    # Build/Dist
    "dist", "build", "target", "vendor", "wheelhouse", ".eggs",
    # IDE
    ".idea", ".vscode", ".DS_Store", "__MACOSX",
    # Configuration
    ".env",
    # Heavy library dirs (site-packages, conda env libs)
    "lib", "lib64", "bin", "share", ".local", "conda", "opt"
]

IGNORE_FILE_NAMES = [
    ".env", ".env.local", ".env.development", ".env.production",
    ".env.test", ".env.staging", ".python-version"
]

BINARY_EXTENSIONS = [
    ".exe", ".dll", ".so", ".dylib", ".bin", 
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".pyc", ".pyo", ".pyd"
]

VISION_EXTENSIONS = [
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"
]

# ==========================================
# FILE TYPE CLASSIFICATIONS
# ==========================================

CODE_EXTENSIONS = [
    '.py', '.js', '.ts', '.tsx', '.jsx', '.java', 
    '.cpp', '.c', '.cs', '.rb', '.go', '.rs', 
    '.php', '.swift', '.kt', '.scala', '.clj'
]

CONFIG_EXTENSIONS = [
    '.json', '.yaml', '.yml', '.toml', '.ini', 
    '.conf', '.cfg', '.config', '.env'
]

DOCUMENTATION_EXTENSIONS = [
    '.md', '.rst', '.txt', '.adoc', '.textile'
]

MARKUP_EXTENSIONS = [
    '.html', '.xml', '.svg', '.xhtml'
]

STYLESHEET_EXTENSIONS = [
    '.css', '.scss', '.sass', '.less', '.styl'
]

DATA_EXTENSIONS = [
    '.csv', '.sql', '.db', '.sqlite'
]

# ==========================================
# RAG / EMBEDDINGS
# ==========================================

EMBEDDING_MODEL_NAME = "text-embedding-nomic-embed-text-v1.5"
SIMILARITY_THRESHOLD = 0.75

# ==========================================
# SECURITY CONSTANTS
# ==========================================

# Dangerous function names for Python analysis
DANGEROUS_FUNCTIONS = [
    "eval", "exec", "compile", "__import__",
    "subprocess", "system", "popen",
    "pickle", "marshal", "shelve",
    "import_module", "load_module",
    "os.system"
]

# I/O operation function names
IO_FUNCTIONS = [
    "open", "read", "write", "print", "input",
    "socket", "send", "recv", "request",
    "urllib", "http", "requests"
]

# Secret pattern names for detection
SECRET_PATTERNS = [
    (r'API_KEY\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded API key'),
    (r'SECRET\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded secret'),
    (r'PASSWORD\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded password'),
    (r'TOKEN\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded token'),
    (r'PRIVATE_KEY\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded private key'),
    (r'AWS_ACCESS_KEY\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded AWS access key'),
    (r'AWS_SECRET_KEY\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded AWS secret key'),
]

# Dangerous code patterns
DANGEROUS_PATTERNS = [
    (r'eval\s*\(', 'Use of eval() function'),
    (r'exec\s*\(', 'Use of exec() function'),
    (r'compile\s*\(', 'Use of compile() function'),
    (r'subprocess\.', 'Use of subprocess module'),
    (r'os\.system\s*\(', 'Use of os.system()'),
    (r'pickle\.', 'Use of pickle module (code execution risk)'),
    (r'marshal\.', 'Use of marshal module'),
]

# ==========================================
# LM STUDIO CONFIGURATION
# ==========================================

DEFAULT_LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
DEFAULT_LM_STUDIO_TEMPERATURE = 0.3
DEFAULT_LM_STUDIO_MAX_TOKENS = 200
LM_STUDIO_REQUEST_TIMEOUT = 30

# AI Persona system prompts
AI_PERSONAS = {
    'security_auditor': """You are a security expert analyzing code for vulnerabilities.
Focus on: OWASP Top 10, injection attacks, authentication flaws, sensitive data exposure.""",
    
    'code_tutor': """You are an experienced programming instructor.
Focus on: best practices, code quality, readability, maintainability, refactoring suggestions.""",
    
    'documentation_expert': """You are a technical documentation specialist.
Focus on: docstring quality, README completeness, API documentation, code comments.""",
    
    'performance_analyst': """You are a performance optimization expert.
Focus on: bottlenecks, algorithmic complexity, memory usage, caching opportunities.""",
    
    'default': """You are a code analysis assistant.
Provide balanced insights on security, quality, and maintainability."""
}

# ==========================================
# API CONFIGURATION
# ==========================================

DEFAULT_API_PORT = 8000
MAX_API_WORKERS = 4
API_RATE_LIMIT_REQUESTS = 100
API_RATE_LIMIT_WINDOW_SECONDS = 60

# ==========================================
# CACHING CONFIGURATION
# ==========================================

DEFAULT_CACHE_DIR = ".bundler_cache"
CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_MAX_SIZE_MB = 100

# ==========================================
# PROGRESS BAR CONFIGURATION
# ==========================================

PROGRESS_BAR_LENGTH = 50
PROGRESS_UPDATE_INTERVAL = 0.1  # seconds

# ==========================================
# OUTPUT CONFIGURATION
# ==========================================

SCAN_STORAGE_ROOT = "bundler_scans"
OUTPUT_FORMAT_VERSION = "1.0.0"
BUNDLER_VERSION = "v4.5.0-enhanced"

# ==========================================
# VALIDATION LIMITS
# ==========================================

MAX_INPUT_LENGTH = 1000
MAX_UID_LENGTH = 32
MIN_UID_LENGTH = 8
MAX_PATH_LENGTH = 500

# Numeric input ranges
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 1.0
MAX_TOKENS_MIN = 1
MAX_TOKENS_MAX = 4096
FILE_SIZE_MIN_MB = 0.1
