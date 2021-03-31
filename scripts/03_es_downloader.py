import sys
import typer

from typing import TypedDict, List
from loguru import logger
from typer import Option
from es_manager import ElasticManager


def main(es_host: str = Option("localhost"),
         es_port: str = Option("9200"),
         es_index: str = Option("reddit-comments"),
         es_search_size: int = Option(512),
         debug: bool = Option(False),
         ):
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    # Some data are named differently based on the index type
    index_kind = "comments" if "comments" in es_index else "submissions"

    logger.debug(f"es_host: `{es_host=}`")
    logger.debug(f"es_port: `{es_port=}`")
    logger.debug(f"es_sub_index: `{es_index=}`")
    logger.debug(f"es_search_size: `{es_search_size=}`")
    logger.debug(f"index_kind: `{index_kind=}`")

    # TODO where put this query?
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

    products_list: List[ProductsInfo] = []

    es_mng = ElasticManager(es_host, es_port, "matrixBuilder@garrascobike")
    es_data = es_mng.new_search(es_index, sub_body, es_search_size)
    while es_data:
        res = es_mng.extract_search_data(es_data)
        products_list.extend(res)
        es_data = es_mng.scroll_search()
    logger.info(f"ES fetching completed, extracted {len(products_list)} infos")


class Entities(TypedDict):
    label: str
    text: str


class ProductsInfo(TypedDict):
    """
    Intersection of the info from es index "submissions" and "comments".

    [!] Note:
        "submission_id" is **not** present under submissions index.
         We use "index_kind" on the main code to manage this key correctly.
    """
    subreddit: str
    id: str
    created_utc: int
    entities: List[Entities]
    submission_id: str


if __name__ == '__main__':
    typer.run(main)
