import sys
import typer
import spacy
import numpy as np
import pandas as pd
from tqdm import tqdm

from typer import Option
from typing import List, Optional
from loguru import logger


def init(es_endpoint: str, debug: bool):
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    if es_endpoint:
        logger.debug(f"Elasticsearch endpoint provided: `{es_endpoint}`, opening connection")
        logger.error("Currently, the es upload is not supported. Program will exit now.")
        exit(1)


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
            es_index: str = Option(""),
            es_endpoint: Optional[str] = Option(None, help="If provided, load the data on the elasticsearch endpoint"),
            debug: bool = Option(False, help="Show debug logs"),
            ):
    # Read the data
    init(es_endpoint, debug)
    df_raw = pd.read_csv(csv_path)

    # Parse the data
    df_raw_len = len(df_raw)
    df_raw["__text__"] = ""

    # join all columns text
    for column in text_columns:
        df_raw["__text__"] += df_raw[column].replace(np.nan, ' ') + " "

    # remove all `__text__` empty rows
    df = df_raw[df_raw["__text__"].str.strip().str.len() > 0]
    df_len = len(df)
    if df_len < df_raw_len:
        logger.debug(f"Dataframe reduced from {df_raw_len} to {df_len}")

    logger.debug("Start text parsing...")
    df["__text__"] = df["__text__"].apply(text_cleaning)
    logger.debug("Text parsing done!")

    # Start the extraction
    spacy.prefer_gpu()
    logger.info(f"Starting the extraction of {df_len} rows")
    df["entities"] = df["__text__"].progress_apply(entities_extractor)
    df = df.drop(columns=["tmp_text"])

    # Store the data


if __name__ == '__main__':
    typer.run(extract)
