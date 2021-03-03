import numpy as np
import pandas as pd
from typing import List, Callable
from loguru import logger
from tqdm import tqdm


class DataManager:

    def __init__(self,
                 csv_path: str,
                 working_col="__text__"):
        """
        Used to load, aggregate and parse the data.
        Two usages:
            - pass `working_col` name of your text column to analyze
            - don't pass `working_col` but instead call `join_columns` to create
            one column with the join of text from other columns.
            In this way we analyze one text and optimize the entities' extraction process.
            [!] Note: if you need to analyze multiple text columns separately, create
            multiple DataManager: this class is not created for this use case
        Args:
            csv_path:
            working_col:
        """
        tqdm.pandas()
        self.__text__ = working_col
        self.csv_path = csv_path
        self.df = self._load_csv(csv_path)
        self.df[self.__text__] = ""
        self.df_len = len(self.df)
        self.columns_joined_flag = False

    @staticmethod
    def _load_csv(csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        return df

    def join_columns(self, columns_to_join: List[str]):
        """
        Used to join columns under one column named `working_col`.
        This permit to us to call the extraction process only 1 time per row.
        Args:
            columns_to_join: List of columns name that will be joined under `working_col` column

        Returns: None, change the internal dataframe instance
        """
        for column_name in columns_to_join:
            self.df[self.__text__] += self.df[column_name].replace(np.nan, ' ') + " "
        self.columns_joined_flag = True

    def remove_empty_rows(self):
        df = self.df
        __text__ = self.__text__

        self.df = df[df[__text__].str.strip().str.len() > 0]
        df_len = len(df)
        if df_len < self.df_len:
            logger.debug(f"Dataframe reduced from {self.df_len} to {df_len}")
            self.df_len = df_len

    def text_parsing(self, fn_cleaning: Callable[[str], str]):
        self.df[self.__text__] = self.df[self.__text__].apply(fn_cleaning)

    def entities_extraction(self, extraction_fn: Callable[[str], List[dict]]):
        self.df["entities"] = self.df[self.__text__].progress_apply(extraction_fn)

    def get_dataframe(self, delete_working_col: True):
        if delete_working_col:
            return self.df.drop(columns=[self.__text__])
        return self.df


def basic_text_cleaning(text: str) -> str:
    text = text.replace("\\n", "")
    return text
