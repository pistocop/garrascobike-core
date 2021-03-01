from enum import Enum

import spacy
from codetiming import Timer
from loguru import logger
from spacy import Language


class Lang(Enum):
    en = "en"


class SpacyManager:
    """
    Class to manage the spacy models,
    expose simple API focused only on text extraction
    """
    # TODO how manage the models and the requirements.txt?
    _spacy_models = {
        "transformers": {
            Lang.en: "en_core_web_trf"
        },
        "standard": {
            Lang.en: "en_core_web_sm"
        }
    }

    def __init__(self,
                 language: Lang,
                 use_transformers: False,
                 use_gpu: bool = False):
        if use_gpu:
            gpu_loaded = spacy.prefer_gpu()
            if not gpu_loaded:
                raise RuntimeError("GPU required but not found")

        model_family = "transformers" if use_transformers else "standard"
        self.language = language
        self.model_name = self._spacy_models[model_family][language]
        self.model = self._model_load()

    @Timer(name="Model loader",
           text="Model loaded in {minutes:.1f} minutes",
           logger=logger.debug)
    def _model_load(self) -> Language:
        logger.debug(f"Loading spacy model: `{self.model_name}`...")
        model = spacy.load(self.model_name)
        logger.debug(f"Spacy model: `{self.model_name}` loaded!")
        return model

    @staticmethod
    def _extraction_parser(text_parsed):
        entities = [{"text": text_parsed.text,
                     "label": text_parsed.label_} for x in text_parsed.ents]
        return entities

    def extract_entities(self, text: str):
        text_data = self.model(text)
        entities = self._extraction_parser(text_data)  # TODO check the warning
