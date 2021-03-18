from typing import List

import pandas as pd


def create_es_actions(df: pd.DataFrame, es_index: str = "my-index") -> List[dict]:
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
