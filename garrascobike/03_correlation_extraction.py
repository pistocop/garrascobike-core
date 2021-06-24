import csv
import sys
from datetime import datetime
from os.path import join
from pathlib import Path
from typing import List
from typing import Optional
from typing import TypedDict

import typer
from loguru import logger
from typer import Option

from managers.es_manager import ElasticManager


class Entities(TypedDict):
    label: str
    text: str


class ProductsInfo(TypedDict):
    """
        Intersection of the info from es index "submissions" and "comments".

        [!] Note: "submission_id" is **not** present under submissions index.
    """
    id: str
    submission_id: Optional[str]
    entities: List[Entities]


def main(es_host: str = Option("localhost"),
         es_port: str = Option("9200"),
         es_index_list: List[str] = Option(["reddit-comments", "reddit-submissions"]),
         es_search_size: int = Option(512),
         output_path: str = Option("./data/03_correlation_data/presence_dataset/"),
         debug: bool = Option(False),
         ):
    # Init
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    logger.debug(f"es_host: `{es_host=}`")
    logger.debug(f"es_port: `{es_port=}`")
    logger.debug(f"es_sub_index: `{es_index_list=}`")
    logger.debug(f"es_search_size: `{es_search_size=}`")

    es_source_list = ["id", "submission_id", "entities.label", "entities.text"]
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

    # Search the products
    es_mng = ElasticManager(es_host, es_port, "matrixBuilder@garrascobike")
    es_data = es_mng.new_search(es_index_list=es_index_list,
                                es_search_body=sub_body,
                                es_search_size=es_search_size,
                                es_source_list=es_source_list
                                )

    res_list: List[ProductsInfo] = []
    while es_data:
        res = es_mng.extract_search_data(es_data)
        res_list.extend(res)
        es_data = es_mng.scroll_search()
    logger.info(f"ES fetching completed, extracted {len(res_list)} entries")

    # Aggregate results
    brands = set()
    products_tracker: List[List[str]] = []

    for entry in res_list:
        thread_id = entry.get("submission_id", entry["id"])
        entities_list = entry["entities"]

        for entity in entities_list:
            label, text = entity["label"], entity["text"]
            if label == "PRODUCT":
                brands.add(text)
                products_tracker.append([thread_id, text])

    assert len(products_tracker) >= len(res_list), f"Error: {len(products_tracker)} >= {len(res_list)}"

    # Store results
    run_id = datetime.today().strftime('%Y%m%d%H%M%S')
    runtime_dir = join(output_path, run_id)
    Path(runtime_dir).mkdir(parents=True, exist_ok=True)
    file_path = join(runtime_dir, "presences.csv")

    logger.info(f"Writing {file_path} file")
    with open(file_path, 'w', newline='') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(['thread_id', 'product_name'])
        wr.writerows(products_tracker)

    logger.info("Extraction completed!")


if __name__ == '__main__':
    typer.run(main)
