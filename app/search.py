from elasticsearch import Elasticsearch
import logging
import html

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, es_host):
        self.es = Elasticsearch([es_host])
        self.index_name = "documents"
        if not self.es.indices.exists(index=self.index_name):
            logger.debug(f"Creating Elasticsearch index: {self.index_name}")
            self.es.indices.create(index=self.index_name)
        else:
            logger.debug(f"Index {self.index_name} already exists")

    def index_document(self, doc_id, content, title=None):
        logger.debug(f"Indexing document {doc_id} with content: {content[:100]}...")
        body = {"content": content}
        if title:
            body["title"] = title
        self.es.index(index=self.index_name, id=doc_id, body=body)
        logger.debug(f"Successfully indexed document {doc_id}")

    def search(self, query):
        logger.debug(f"Executing search query: {query}")
        response = self.es.search(
            index=self.index_name,
            body={
                "query": {
                    "query_string": {
                        "query": query,
                        "default_field": "content"
                    }
                },
                "highlight": {
                    "fields": {
                        "content": {
                            "fragment_size": 200,
                            "number_of_fragments": 3
                        }
                    },
                    "pre_tags": ["<b>"],
                    "post_tags": ["</b>"]
                },
                "size": 5
            }
        )
        results = [
            {
                "doc_id": hit["_id"],
                "title": hit["_source"].get("title", "Untitled"),
                "content_preview": (
                    self._clean_highlight(hit["highlight"]["content"])
                    if "highlight" in hit and hit["highlight"].get("content")
                    else self._truncate_content(hit["_source"]["content"])
                ),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]
        logger.debug(f"Search returned {len(results)} results")
        return results

    def _clean_highlight(self, fragments):
        """Combine and clean highlighted fragments."""
        cleaned = " ".join(html.unescape(fragment) for fragment in fragments)
        cleaned = " ".join(cleaned.split())
        return cleaned

    def _truncate_content(self, content, max_length=200):
        """Truncate content to max_length and clean special characters."""
        content = content.replace("\r\n", " ").replace("\n", " ").replace("\u2022", "-")
        content = " ".join(content.split())
        return content[:max_length] + "..." if len(content) > max_length else content