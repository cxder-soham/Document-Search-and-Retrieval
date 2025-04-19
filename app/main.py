from flask import Flask, request, jsonify
from flask_cors import CORS
from .search import SearchEngine
from .storage import Storage
from dotenv import load_dotenv
import os
import io
from PyPDF2 import PdfReader
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes
storage = Storage(os.getenv("AWS_S3_BUCKET"))
search_engine = SearchEngine(os.getenv("ELASTICSEARCH_HOST"))

@app.route("/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    try:
        # Determine file type
        filename = file.filename.lower()
        if filename.endswith('.txt'):
            content = file.read().decode("utf-8")
            logger.debug(f"Text file content: {content[:100]}...")
        elif filename.endswith('.pdf'):
            pdf = PdfReader(file)
            content = ""
            for page in pdf.pages:
                content += page.extract_text() or ""
            logger.debug(f"PDF extracted content: {content[:100]}...")
            if not content.strip():
                return jsonify({"error": "No text extracted from PDF"}), 400
        else:
            return jsonify({"error": "Unsupported file type. Use .txt or .pdf"}), 400

        # Extract title (first meaningful line or cleaned filename)
        title = os.path.splitext(file.filename)[0].replace("_", " ").title()
        if content.strip():
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) < 100 and not line.startswith(('#', '-', '*')):
                    title = line
                    break

        # Reset file stream for S3 upload
        file.seek(0)
        # Upload to S3
        doc_id = storage.upload_file(file)
        logger.debug(f"Uploaded to S3 with doc_id: {doc_id}")
        # Index content in Elasticsearch
        search_engine.index_document(doc_id, content, title)
        logger.debug(f"Indexed document with doc_id: {doc_id}")
        return jsonify({"message": "Document uploaded", "doc_id": doc_id}), 201
    except Exception as e:
        logger.error(f"Error in upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["GET", "POST"])
def search_documents():
    if request.method == "POST":
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "JSON body with 'query' field required"}), 400
        query = data["query"]
    else:  # GET
        query = request.args.get("q")
        if not query:
            return jsonify({"error": "Query parameter 'q' required"}), 400

    try:
        logger.debug(f"Searching for query: {query}")
        results = search_engine.search(query)
        return jsonify({
            "query": query,
            "total_results": len(results),
            "results": results
        }), 200
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)