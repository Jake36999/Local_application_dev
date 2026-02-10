import argparse
import sys
import re
import logging
from pathlib import Path

# --- PATH CORRECTION ---
# Ensure project root is in sys.path so 'core' and 'utils' can be imported
# regardless of where the script is run from.
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from core.ingest_manager import IngestManager
from core.retrieval_controller import RetrievalController

# Configure logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def sanitize_input(text: str) -> str:
    """
    Removes potentially problematic characters from query strings.
    """
    if not text: return ""
    return re.sub(r'[^\w\s\.\-\?\!]', '', text).strip()

def main():
    parser = argparse.ArgumentParser(
        description="Aletheia RAG CLI - Technical Enhancements Build",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "mode", 
        choices=["ingest", "ask"], 
        help="System mode: 'ingest' to process documents, 'ask' to query the brain."
    )
    parser.add_argument(
        "--q", 
        help="The research question for Aletheia (required for 'ask' mode)"
    )
    args = parser.parse_args()

    if args.mode == "ingest":
        print("\n[INIT] Starting Aletheia Ingestion Engine...")
        print("[INFO] Scanning 'data/raw_landing' for new intelligence...")
        try:
            manager = IngestManager()
            manager.process_all()
            print("\n[SUCCESS] Ingestion cycle complete.\n")
        except Exception as e:
            # Catch fatal errors (config issues, missing folders)
            logging.error(f"Ingestion failed: {e}")
            print(f"\n[CRITICAL] System failure during ingestion: {e}")
            sys.exit(1)
    
    elif args.mode == "ask":
        if not args.q:
            print("\n[ERROR] 'ask' mode requires a query. Use: --q 'your question'")
            sys.exit(1)
            
        clean_q = sanitize_input(args.q)
        print(f"\n[QUERY] Researching: '{clean_q}'")
        print("[INFO] Accessing semantic memory and canonical truth...")
        
        try:
            controller = RetrievalController()
            answer = controller.query(clean_q)
            
            print("\n" + "="*60)
            print(" ALETHEIA EXPERT RESPONSE")
            print("="*60)
            print(answer)
            print("="*60 + "\n")
        except Exception as e:
            logging.error(f"Retrieval failed: {e}")
            print(f"\n[CRITICAL] Inference engine error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[HALT] Shutdown signal received. Exiting gracefully.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL] Unhandled error: {e}")
        sys.exit(1)