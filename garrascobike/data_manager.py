import numpy as np
import pandas as pd
from typing import List, Callable
from loguru import logger


class DataManager:
    """
    Used to load, aggregate and parse the data
    """

    def __init__(self, csv_path: str, working_col="__text__"):
        self.__text__ = working_col
        self.csv_path = csv_path
        self.df = self._load_csv(csv_path)
        self.df_len = len(self.df)
        logger.debug(f"Loaded {self.df_len} rows from `{self.csv_path}`")

    @staticmethod
    def _load_csv(csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        return df

    def join_columns(self, columns_to_join: List[str]):
        """
        Used to join columns under one column named `working_col`.
        This permit to us to call the extraction process only 1 time per row.
        """
        self.df[self.__text__] = ""
        for column_name in columns_to_join:
            self.df[self.__text__] += self.df[column_name].replace(np.nan, ' ') + " "

    def remove_empty_rows(self):
        df = self.df
        __text__ = self.__text__
        self.df = df[df[__text__].str.strip().str.len() > 0]
        df_len = len(df)
        if df_len < self.df_len:
            logger.debug(f"Dataframe reduced from {self.df_len} to {df_len}")
            self.df_len = df_len

    def text_parsing(self):
        self.df[self.__text__] = self.df[self.__text__].apply(basic_text_cleaning)

    def entities_extraction(self, extraction_fn: Callable):
        self.df["entities"] = self.df[self.__text__].progress_apply(extraction_fn)


def basic_text_cleaning(text: str) -> str:
    text = text.replace("\\n", "")
    return text
