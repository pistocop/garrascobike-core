import sys
import typer

from typing import List
from loguru import logger
from typer import Option

from matrix_builder import ElasticManager


def main(es_host: str = Option("localhost"),
         es_port: str = Option("9200"),
         es_sub_index: str = Option("reddit-submissions-trf"),
         es_com_index: str = Option("reddit-comments-trf"),
         es_search_size: int = Option(512),
         debug: bool = Option(False),
         ):
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    logger.debug(f"es_host: `{es_host}`")
    logger.debug(f"es_port: `{es_port}`")
    logger.debug(f"es_sub_index: `{es_sub_index}`")
    logger.debug(f"es_com_index: `{es_com_index}`")
    logger.debug(f"es_search_size: `{es_search_size}`")

    sub_body = """{
                  "query": {
                    "nested": {
                      "path": "entities",
                      "query": {
                        "match": {
                          "entities.label": "PRODUCT"
                        }
                      }
                    }
                  }
                }"""
    sub_source_list = []
    es = ElasticManager(es_host, es_port, es_sub_index, es_search_size, sub_body, sub_source_list)

    while True:
        res = es.search()
        n_res = len(res['hits']['hits'])
        logger.debug(f"Fetched `{n_res}` values")
        if not n_res > 0:
            break


if __name__ == '__main__':
    typer.run(main)
