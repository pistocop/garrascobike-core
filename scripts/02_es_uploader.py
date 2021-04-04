import sys

import typer
from loguru import logger
from typer import Option

# noinspection PyUnresolvedReferences
import __init__  # used to import from `garrascobike`
from data_manager import DataManager
from es_manager import ElasticManager


class HelpMsg:
    es_index = "Name of the ES index where load the data"
    es_host = "ES endpoint"
    es_port = "ES endpoint port"
    input_file = "Path to the file (csv, parquet) with data to load into ES"
    debug = "Show debug logs"


def extract(es_index: str = Option(..., help=HelpMsg.es_index),
            es_host: str = Option("localhost", help=HelpMsg.es_host),
            es_port: str = Option("9200", help=HelpMsg.es_port),
            input_file: str = Option("./data/entities_extractions/extraction.parquet", help=HelpMsg.input_file),
            debug: bool = Option(False, help=HelpMsg.debug),
            ):
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    logger.debug(f"Input data: "
                 f"{es_index =} | "
                 f"{es_host =} | "
                 f"{es_port =} | "
                 f"{input_file =} | "
                 f"{debug =}"
                 )
    data_mng = DataManager(input_file)
    df = data_mng.get_dataframe()
    logger.info(f"Loaded {len(df)} rows from `{input_file}`")

    es_mng = ElasticManager(es_host, es_port)
    es_actions = es_mng.create_es_actions_from_dataframe(df, es_index)
    logger.info(f"Es actions created: {len(es_actions)=}")

    logger.info(f"Uploading `{len(es_actions)}` data on elasticsearch...")
    es_mng.bulk_upload(es_actions)
    logger.info(f"Upload completed!")


if __name__ == '__main__':
    typer.run(extract)
