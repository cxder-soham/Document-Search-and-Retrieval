from flask import Flask, request, jsonify
from .search import SearchEngine
from .storage import Storage
from dotenv import load_dotenv
import os
import io

load_dotenv()

app = Flask(__name__)
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
        # Read file content into memory
        content = file.read().decode("utf-8")
        # Reset file stream to start for S3 upload
        file.seek(0)
        # Upload to S3
        doc_id = storage.upload_file(file)
        # Index content in Elasticsearch
        search_engine.index_document(doc_id, content)
        return jsonify({"message": "Document uploaded", "doc_id": doc_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["GET"])
def search_documents():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400
    try:
        results = search_engine.search(query)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)