from enum import Enum
from typing import List

import spacy
from loguru import logger
from spacy import Language


class SupportedLanguages(Enum):
    en = "en"


class SpacyManager:
    # TODO how manage the models and the requirements.txt?
    _spacy_models = {
        "transformers": {
            SupportedLanguages.en: "en_core_web_trf"
        },
        "standard": {
            SupportedLanguages.en: "en_core_web_sm"
        }
    }

    def __init__(self,
                 language: SupportedLanguages,
                 use_transformers: False,
                 use_gpu: bool = False):
        """
            Class to manage the spacy models,
            expose simple API focused only on text extraction

        Args:
            language: the language of the text will be analyzed
            use_transformers: load heavy - but with the best accuracy - ML models
            use_gpu: use the GPU or raise an error
        """
        self._check_gpu(use_gpu)

        model_family = "transformers" if use_transformers else "standard"
        self.language = language
        self.model_name = self._spacy_models[model_family][language]
        self.model = self._model_load()

    def _model_load(self) -> Language:
        logger.debug(f"Loading spacy model: `{self.model_name}`...")
        model = spacy.load(self.model_name)
        logger.debug(f"Spacy model: `{self.model_name}` loaded!")
        return model

    def extract_entities(self, text: str) -> List[dict]:
        text_data = self.model(text)
        entities = self._extraction_parser(text_data)  # TODO check the warning
        return entities

    @staticmethod
    def _extraction_parser(text_parsed) -> List[dict]:
        entities = [{"text": text_parsed.text,
                     "label": text_parsed.label_} for x in text_parsed.ents]
        return entities

    @staticmethod
    def _check_gpu(use_gpu: bool):
        if use_gpu:
            gpu_loaded = spacy.prefer_gpu()
            if not gpu_loaded:
                raise RuntimeError("GPU required but not found")
