import os
from datetime import datetime
from os.path import join
from pathlib import Path
from typing import Callable
from typing import List

import numpy as np
import pandas as pd
from loguru import logger
from tqdm import tqdm


class DataManager:

    def __init__(self,
                 file_path: str,
                 working_col="__text__",
                 working_col_init=True):
        """
        Used to load, aggregate and parse the data.

        **Note**: if you need to analyze multiple text columns separately, create
        multiple DataManager: this class is not created for this use case

        Two main usages:
            - pass `working_col` name of your text column to analyze
            - don't pass `working_col` but instead call `join_columns` to create
            one column with the join of text from other columns.
            In this way we analyze one text and optimize the entities' extraction process.

        Args:
            file_path:
            working_col:
        """
        tqdm.pandas()
        self.data_loaders: dict[str, Callable] = {"csv": self._load_csv,
                                                  "parquet": self._load_parquet}

        self.__text__ = working_col
        self.file_path = file_path
        self.df = self._load_dataframe(file_path)
        if working_col_init:
            self.df[self.__text__] = ""
        self.df_len = len(self.df)
        self.columns_joined_flag = False

    @staticmethod
    def _load_csv(file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        return df

    @staticmethod
    def _load_parquet(file_path: str) -> pd.DataFrame:
        df = pd.read_parquet(file_path)
        return df

    def _check_extension(self, extension: str):
        supported_extensions = self.data_loaders.keys()
        if extension not in supported_extensions:
            # Use visitors pattern if more than parquet format will be required
            raise NotImplementedError(f"Format `{extension}` not supported. "
                                      f"Supported formats: [`{supported_extensions}`]")

    # Dataset methods
    def get_dataframe(self, delete_working_col: bool = True):
        if delete_working_col:
            return self.df.drop(columns=[self.__text__])
        return self.df

    def store_dataframe(self, path: str, out_extension: str = "parquet") -> str:
        run_id = datetime.today().strftime('%Y%m%d%H%M%S')
        runtime_dir = join(path, run_id)
        Path(runtime_dir).mkdir(parents=True, exist_ok=True)

        self._check_extension(out_extension)

        # Currently only parquet is supported
        file_path = join(runtime_dir, "extraction.parquet")
        self.df.to_parquet(file_path)
        return file_path

    def _load_dataframe(self, file_path: str) -> pd.DataFrame:
        """
        Load data from different sources extensions.

        Private method because user should use `get_dataframe` if want the df, that
        method remove __text__ working column.

        Args:
            file_path: path to the file with the data

        Returns:
            Pandas dataframe with the data loaded
        """
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension[1:]  # remove starting `.`
        self._check_extension(file_extension)
        data_loader = self.data_loaders[file_extension]
        df = data_loader(file_path)
        return df

    # Entities extraction methods
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
        """
        Remove empty rows of the __text__ column (the only important for this class)
        Returns:
            self.df reduced
        """
        df = self.df
        __text__ = self.__text__

        self.df = df[df[__text__].str.strip().str.len() > 0]
        df_len = len(df)
        if df_len < self.df_len:
            logger.debug(f"Dataframe reduced from {self.df_len} to {df_len}")
            self.df_len = df_len

    def text_parsing(self, fn_cleaning: Callable[[str], str]):
        self.df[self.__text__] = self.df[self.__text__].apply(fn_cleaning)

    def text_normalization(self):
        self.df[self.__text__] = self.df[self.__text__].str.casefold()
        self.df[self.__text__] = self.df[self.__text__].str.strip()

    def text_remove_if_all_numbers(self):
        def has_numbers(input_string: str):
            return all(char.isdigit() for char in input_string)

        self.df['text_all_digits'] = self.df[self.__text__].apply(has_numbers)
        self.df = self.df[self.df["text_all_digits"] == False]
        self.df = self.df.drop("text_all_digits", 1)

    def text_remove_if_n_words(self, n_words: 2):
        """
        Remove rows if the text is composed by more than `n_words` words
        """
        self.df = self.df[self.df[self.__text__].str.split().str.len().lt(n_words)]

    def entities_extraction(self, extraction_fn: Callable[[str], List[dict]]):
        self.df["entities"] = self.df[self.__text__].progress_apply(extraction_fn)
