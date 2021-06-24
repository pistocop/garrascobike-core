import sys
from typing import List

import typer
from loguru import logger
from typer import Option

# noinspection PyUnresolvedReferences
import __init__  # used to import from `garrascobike`
from managers.data_manager import DataManager
from utils.text_parsers import basic_text_cleaning
from managers.spacy_manager import SpacyManager
from managers.spacy_manager import SupportedLanguages


class HelpMsg:
    csv_path = "Path to the csv"
    text_columns = "Columns name with text to analyze"
    use_transformers = "Use heavy but good ML models"
    output_directory = "Path where store the `extraction.parquet` file"
    use_gpu = "Enable if a GPU is available"
    language = "Language of the text to analyze"
    debug = "Show debug logs"


def extract(csv_path: str = Option("./data/01_subreddit_extractions/data.csv", help=HelpMsg.csv_path),
            text_columns: List[str] = Option(["title", "selftext"], help=HelpMsg.text_columns),
            use_transformers: bool = Option(False, help=HelpMsg.use_transformers),
            output_directory: str = Option("./data/02_entities_extractions/", help=HelpMsg.output_directory),
            use_gpu: bool = Option(False, help=HelpMsg.use_gpu),
            language: SupportedLanguages = Option("en", help=HelpMsg.language),
            debug: bool = Option(False, help=HelpMsg.debug),
            ):
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    logger.debug(f"Input data: "
                 f"csv_path: `{csv_path}` - "
                 f"text_columns: `{text_columns}` - "
                 f"use_transformers: `{use_transformers}` - "
                 f"output_directory: `{output_directory}` - "
                 f"use_gpu: `{use_gpu}` - "
                 f"language: `{language}` - ")

    logger.info("Data extraction starting...")
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
    logger.debug(f"Entities extracted")

    output_file = dm.store_dataframe(output_directory)
    logger.debug(f"Entities stored at `{output_file}`")

    logger.info("Data extraction completed!")


if __name__ == '__main__':
    typer.run(extract)
