from elasticsearch import Elasticsearch
from constant.config import ES_URL, ES_INDEX_JOB_SEARCH, ES_INDEX_RESUME_SEARCH

class ElasticSearchDB:
    ES_URL = ES_URL
    ES_INDEX_JOB_SEARCH = ES_INDEX_JOB_SEARCH
    ES_INDEX_RESUME_SEARCH = ES_INDEX_RESUME_SEARCH

    @staticmethod
    def setup_elasticsearch_connection() -> Elasticsearch:
        return Elasticsearch([ElasticSearchDB.ES_URL])
