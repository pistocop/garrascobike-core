# noinspection PyUnresolvedReferences
import __init__  # used to import from `garrascobike`
import sys
import typer
import pandas as pd

from typer import Option
from loguru import logger
from typing import List, Optional
from codetiming import Timer

from data_manager import DataManager, basic_text_cleaning
from spacy_manager import SupportedLanguages, SpacyManager


def create_es_actions(df: pd.DataFrame,
                      es_index: str
                      ) -> List[dict]:
    es_data = []

    def register_action(*args):
        values = {}
        for key, val in args[0].iteritems():
            values[key] = val

        entry = {
            "_index": es_index,
            "_id": values["id"],
            "_source": values
        }
        es_data.append(entry)

    # noinspection PyTypeChecker
    df.apply(register_action, axis=1, raw=False)
    assert len(es_data) == len(df), f"Registration mismatch"

    return es_data


def extract(csv_path: str = Option("./data/submissions.csv", help="Path to the csv"),
            text_columns: List[str] = Option(["title", "selftext"], help="Columns name with text to analyze"),
            use_transformers: bool = Option(False, help="Use heavy but good ML models"),
            use_gpu: bool = Option(False, help="Enable if a GPU is available"),
            language: SupportedLanguages = Option(SupportedLanguages.en, help="Language of the text to analyze"),
            es_index: str = Option(""),
            es_endpoint: Optional[str] = Option(None, help="If provided, load the data on the elasticsearch endpoint"),
            debug: bool = Option(False, help="Show debug logs"),
            ):
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    logger.info("Data management starting...")

    dm = DataManager(csv_path)
    logger.debug(f"Loaded {dm.df_len} rows from dataset at `{csv_path}`!")

    dm.join_columns(text_columns)
    logger.debug(f"Columns `{text_columns}` joined under `{dm.__text__}` column")

    dm.text_parsing(basic_text_cleaning)
    logger.debug(f"Text cleaned using `{basic_text_cleaning}`")

    dm.remove_empty_rows()
    logger.debug(f"Rows cleaned, new size: {dm.df_len}")

    mlm = SpacyManager(language, use_transformers, use_gpu)
    logger.debug(f"Loaded model `{mlm.model_name}`, run on GPU:{use_gpu}")

    dm.entities_extraction(mlm.extract_entities)
    logger.debug(f"Rows cleaned, new size: {dm.df_len}")

    logger.info("Data management completed!")


if __name__ == '__main__':
    typer.run(extract)
