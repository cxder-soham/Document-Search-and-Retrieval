from elasticsearch import Elasticsearch

class SearchEngine:
    def __init__(self, es_host):
        self.es = Elasticsearch([es_host])
        self.index_name = "documents"
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name)

    def index_document(self, doc_id, content):
        self.es.index(index=self.index_name, id=doc_id, body={"content": content})

    def search(self, query):
        response = self.es.search(
            index=self.index_name,
            body={"query": {"match": {"content": query}}}
        )
        return [
            {"doc_id": hit["_id"], "content": hit["_source"]["content"]}
            for hit in response["hits"]["hits"]
        ]