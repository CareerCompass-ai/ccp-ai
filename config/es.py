from elasticsearch import Elasticsearch
import constant.config as constant

class ElasticSearchDB:
    ES_URL = constant.ES_URL
    ES_INDEX_JOB_SEARCH = constant.ES_INDEX_JOB_SEARCH
    ES_INDEX_RESUME_SEARCH = constant.ES_INDEX_RESUME_SEARCH

    @staticmethod
    def setup_elasticsearch_connection() -> Elasticsearch:
        return Elasticsearch(
            constant.ES_URL, 
            basic_auth=[constant.ES_USERNAME, constant.ES_PASSWORD], 
            timeout=30
        )
