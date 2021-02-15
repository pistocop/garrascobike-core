from typing import List

from loguru import logger
from elasticsearch import Elasticsearch


class ElasticManager:
    def __init__(self,
                 es_host: str,
                 es_port: str,
                 es_index: str,
                 es_search_size: int,
                 es_search_body: str,
                 es_source_list: List[str] = None,
                 es_scroll_time: str = "5m",
                 es_opaque_id: str = "matrix-builder@client",
                 ):
        """ TODO """
        self.es_host = es_host
        self.es_port = es_port
        self.es_index = es_index
        self.es_search_size = es_search_size
        self.es_search_body = es_search_body
        self.es_source_list = es_source_list
        self.es_scroll_time = es_scroll_time
        self.es_opaque_id = es_opaque_id
        self.es_connection = None
        self.scroll_id = None

    def _open_es_connection(self):
        logger.debug(f"Opening new es connection to `{self.es_host}:{self.es_port}`")
        self.es_connection = Elasticsearch(host=self.es_host,
                                           port=self.es_port,
                                           opaque_id=self.es_opaque_id)

    def search(self):
        if self.scroll_id:
            return self._scroll_other_data()
        else:
            return self._make_new_search()

    def _make_new_search(self):
        if not self.es_connection:
            self._open_es_connection()
        res = self.es_connection.search(index=self.es_index,
                                        body=self.es_search_body,
                                        _source=self.es_source_list,
                                        size=self.es_search_size,
                                        scroll=self.es_scroll_time)
        self._extract_scroll_id(res)
        return res

    def _scroll_other_data(self):
        res = self.es_connection.scroll(scroll_id=self.scroll_id,
                                        scroll=self.es_scroll_time)
        self._extract_scroll_id(res)
        return res

    def _extract_scroll_id(self, res: dict):
        if "_scroll_id" not in res:
            raise RuntimeError(f"Scroll id not found - result data: {type(res)} - `{res}`")
        self.scroll_id = res["_scroll_id"]
