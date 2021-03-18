import spacy

from enum import Enum
from typing import List
from spacy import Language


class SupportedLanguages(Enum):
    en = "en"
    it = "it"

    def __str__(self):
        return str(self.value)


class SpacyManager:
    # TODO how manage the models and the requirements.txt?
    #  Problem: we need to install / download the model before can import, the challenge
    #  is to download only the model used. But if placed in requirements.txt we need to download everything,
    #  instead if we use the spacy download feature we download the model each time (showed no persistence).
    _spacy_models = {
        "transformers": {
            SupportedLanguages.en: "en_core_web_trf",
            SupportedLanguages.it: "it_core_news_lg"
        },
        "standard": {
            SupportedLanguages.en: "en_core_web_sm",
            SupportedLanguages.it: "it_core_news_sm"
        }
    }

    def __init__(self,
                 language: SupportedLanguages = SupportedLanguages.en,
                 use_transformers: bool = False,
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
        model = spacy.load(self.model_name)
        return model

    def extract_entities(self, text: str) -> List[dict]:
        text_data = self.model(text)
        entities = self._extraction_parser(text_data)
        return entities

    @staticmethod
    def _extraction_parser(text_parsed) -> List[dict]:
        entities = [{"text": entity.text, "label": entity.label_}
                    for entity in text_parsed.ents]
        return entities

    @staticmethod
    def _check_gpu(use_gpu: bool):
        if use_gpu:
            gpu_loaded = spacy.prefer_gpu()
            if not gpu_loaded:
                raise RuntimeError("GPU required but not found")
