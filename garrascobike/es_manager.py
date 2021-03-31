import json
import pandas as pd

from typing import List, Optional
from typing import TypedDict
from loguru import logger
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class EsResults(TypedDict):
    _scroll_id: str
    took: int
    timed_out: bool
    _shards: dict
    hits: dict


class ElasticManager:
    def __init__(self,
                 es_host: str,
                 es_port: str,
                 es_opaque_id: str = "ElastiManager@client"
                 ):
        self.es_host = es_host
        self.es_port = es_port
        self.es_opaque_id = es_opaque_id
        self.scroll_id = None
        self.es_connection = self._new_es_connection()

    @staticmethod
    def _extract_scroll_id(res: dict) -> str:
        scroll_id = res.get("_scroll_id")
        if not scroll_id:
            raise RuntimeError(f"Scroll id not found - result data: {type(res)} - `{res}`")
        return scroll_id

    @staticmethod
    def create_es_actions_from_dataframe(df: pd.DataFrame, es_index: str = "my-index") -> List[dict]:
        """
        Create a list of "actions" that could be used to feed the elasticsearch bulk operator.
        The actions contains the instructions to store all the dataa inside `df` into the `es_index` index.
        Args:
            df: pandas dataframe with the data to upload on es
            es_index: the name of the es index where store the data

        Returns:
            list of dictionaries, each one with instruction to store one row of the dataset
        """
        es_actions = []  # Use closure to store data

        def register_action(*args):
            values = {}
            for key, val in args[0].iteritems():
                values[key] = val

            entry = {
                "_index": es_index,
                "_id": values["id"],
                "_source": values
            }
            es_actions.append(entry)

        # noinspection PyTypeChecker
        df.apply(register_action, axis=1, raw=False)
        assert len(es_actions) == len(df), f"Registration mismatch: `{len(es_actions)=}` != `{len(df)=}`"

        return es_actions

    @staticmethod
    def store_es_actions(output_file_path: str, actions: List[dict]) -> None:
        """
        Store actions locally in a es-bulk ready format.
        Use to store data on a file for later upload using the official ES bulk API.

        Example:
        Assuming file stored is `bulk_upload.njson` the endpoint is:
        `curl -s -H "Content-Type: application/x-ndjson" -XPOST localhost:9200/_bulk --data-binary "@bulk_upload.njson"`

        Args:
            output_file_path: file path and name, suggested `.njson` as file extension name
            actions: list of dictionaries with the data to store

        """
        with open(output_file_path, "w") as f:
            for entry in actions:
                if not entry:
                    print(f"Entry `{entry}` is empty")
                    continue
                action_line = {"index": {"_index": entry.pop("_index"),
                                         "_id": entry.pop("_id")
                                         }
                               }
                data_line = entry.pop("_source")
                f.write(json.dumps(action_line))
                f.write("\n")
                f.write(json.dumps(data_line))
                f.write("\n")

    @staticmethod
    def extract_search_data(es_results: EsResults) -> List[dict]:
        search_data: List[dict] = []
        for res in es_results["hits"]["hits"]:
            search_data.append(res["_source"])
        return search_data

    def _new_es_connection(self):
        logger.debug(f"Opening new es connection to `{self.es_host}:{self.es_port}`")
        es_connection = Elasticsearch(host=self.es_host,
                                      port=self.es_port,
                                      opaque_id=self.es_opaque_id)
        return es_connection

    def _scroll_other_data(self,
                           es_scroll_time: str = "5m"
                           ) -> EsResults:
        res = self.es_connection.scroll(scroll_id=self.scroll_id,
                                        scroll=es_scroll_time)
        self._extract_scroll_id(res)
        return res

    def new_search(self,
                   es_index: str,
                   es_search_body: str,
                   es_search_size: int,
                   es_source_list: List[str] = None,
                   es_scroll_time: str = "5m"
                   ) -> Optional[EsResults]:
        # TODO documentation
        if self.scroll_id:
            logger.debug(f"Overwriting last search, removing ex scroll_id:`{self.scroll_id}`")
            self.scroll_id = None

        data: EsResults = self.es_connection.search(index=es_index,
                                                    body=es_search_body,
                                                    _source=es_source_list,
                                                    size=es_search_size,
                                                    scroll=es_scroll_time)

        self.scroll_id = self._extract_scroll_id(data)
        n_res = len(data['hits']['hits'])
        if n_res == 0:
            return None

        return data

    def scroll_search(self,
                      es_scroll_time: str = "5m"
                      ) -> Optional[EsResults]:
        """
        Call this function **after** `new_search` function.

        Return further X data from the search query, or None if no new data are retrieved.
        Where X is the `es_search_size` value passed at the `new_search` function.
        Args:
            es_scroll_time: timing for the scroll_id expiration.
            After this time you cannot scroll new results.

        Returns:
            None if no new data are found, or a dictionary with `EsResults` format
        """
        if not self.scroll_id:
            raise RuntimeError("Cannot scroll new data, `scroll_id` not set.")

        data = self._scroll_other_data(es_scroll_time)
        n_res = len(data['hits']['hits'])

        if n_res == 0:
            return None
        return data

    def bulk_upload(self, actions: List[dict], **args):
        """
        Upload the actions to elasticsearch.

        Note: a better approach could be used, without create and store in memory
        all the `actions`, because `helpers.bulk` take an iterator.
        However this kind of approach led the class to expose a less reusable methods.

        Args:
            actions: list of dictionaries with the actions to upload data on es
            *args: arguments to enrich the `helpers.bulk` behaviour, see it for reference
        """
        n_success, errors = helpers.bulk(self.es_connection, actions, **args)
        if n_success < len(errors):
            logger.error(f"Not all the data was uploaded: {n_success=} > {len(errors)=}")
            for idx, e in enumerate(errors):
                logger.error(f"Error n^{idx}: `{e}`")
