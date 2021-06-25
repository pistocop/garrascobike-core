import pickle
from datetime import datetime
from os.path import join
from pathlib import Path
from typing import List
from typing import Tuple

import numpy as np
from bidict import bidict
from joblib import dump
from joblib import load
from loguru import logger
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from managers.data_manager import DataManager
from utils.class_interfaces import MLInterface


# noinspection DuplicatedCode
class KnnManager(MLInterface):
    max_product_words = 2

    def __init__(self):
        self.knn = None
        self.thread2int = None
        self.product2int = None
        self.train_matrix = None
        self.ml_params = {  # TODO load the parameters from config file
            "metric": 'minkowski',
            "p": 2,
            "algorithm": 'auto',
            "n_neighbors": 5,
            "n_jobs": -1,
        }

    def preprocess(self, dm: DataManager) -> DataManager:
        dm.text_normalization()
        dm.text_remove_if_all_numbers()
        dm.text_remove_if_n_words(n_words=KnnManager.max_product_words)
        return dm

    def train(self, dm: DataManager) -> None:
        df = dm.get_dataframe(delete_working_col=False)
        threads_unique = df['thread_id'].unique()
        products_unique = df['product_name'].unique()
        util_mtx_dimension = (len(threads_unique), len(products_unique))

        logger.info(f"Dataset len: {len(df)}, columns:{set(df.columns)}")
        logger.info(f"Unique threads:{len(threads_unique)}")
        logger.info(f"Unique products:{len(products_unique)}")
        logger.info(f"Utility matrix - shape predicted:{util_mtx_dimension}")

        # Build the indexer mapper
        self.thread2int = bidict({u: i for i, u in enumerate(df["thread_id"].unique())})
        self.product2int = bidict({m: i for i, m in enumerate(df["product_name"].unique())})

        # Map text to index
        threads_idx = [self.thread2int[u] for u in df["thread_id"]]
        products_idx = [self.product2int[m] for m in df["product_name"]]

        # Create matrix with 1 values [1,1,1,1,...[len(threads)]]
        data = np.ones(len(threads_idx), )

        # Create the utility matrix - sparse matrix [len(threads), len(products)]
        utility_matrix = csr_matrix((data, (threads_idx, products_idx)))
        assert utility_matrix.shape == util_mtx_dimension, f"A_sparse have a wrong dimension, expected:{util_mtx_dimension}"
        logger.info(f"Utility matrix shape:{utility_matrix.get_shape()}[threads, products]")

        # Train the model
        self.train_matrix = utility_matrix.transpose()  # shape required: (n_samples, n_features)
        self.knn = NearestNeighbors(metric=self.ml_params["metric"],
                                    p=self.ml_params["p"],
                                    algorithm=self.ml_params["algorithm"],
                                    n_neighbors=self.ml_params["n_neighbors"],
                                    n_jobs=self.ml_params["n_jobs"],
                                    )
        self.knn.fit(self.train_matrix)

    @staticmethod
    def path_builder(runtime_dir: str) -> dict:
        knn_path = join(runtime_dir, "knn.joblib")
        train_matrix_path = join(runtime_dir, "train_matrix.joblib")
        thread2int_path = join(runtime_dir, "thread2int.pkl")
        product2int_path = join(runtime_dir, "product2int.pkl")
        paths_collection = {
            "knn_path": knn_path,
            "train_matrix_path": train_matrix_path,
            "thread2int_path": thread2int_path,
            "product2int_path": product2int_path,
        }
        return paths_collection

    def store_model(self, path: str) -> str:
        # Path init
        run_id = datetime.today().strftime('%Y%m%d%H%M%S')
        runtime_dir = join(path, run_id)
        Path(runtime_dir).mkdir(parents=True, exist_ok=True)

        # Path builders
        paths_collection = KnnManager.path_builder(runtime_dir)

        # Store the data
        dump(self.knn, paths_collection['knn_path'])
        dump(self.train_matrix, paths_collection['train_matrix_path'])
        open(paths_collection['thread2int_path'], 'wb').write(pickle.dumps(self.thread2int))
        open(paths_collection['product2int_path'], 'wb').write(pickle.dumps(self.product2int))
        return runtime_dir

    def load_model(self, path: str) -> None:
        # Path builder
        paths_collection = KnnManager.path_builder(path)

        # Load the data
        self.knn = load(paths_collection['knn_path'])
        self.train_matrix = load(paths_collection['train_matrix_path'])
        self.thread2int = pickle.loads(open(paths_collection['thread2int_path'], 'rb').read())
        self.product2int = pickle.loads(open(paths_collection['product2int_path'], 'rb').read())

    def get_prediction(self,
                       product_name: str,
                       neighbors: int = 10
                       ) -> List[Tuple[int, str]]:
        product_id = self.product2int.get(product_name, None)

        if not product_id:
            msg = f"Product {product_name} not found."
            logger.warning(msg)
            raise ValueError(msg)
        logger.debug(f"Searching '{product_name}' - id:{product_id}")

        distances, indices = self.knn.kneighbors(self.train_matrix[product_id], n_neighbors=neighbors + 1)
        distances, indices = distances.tolist().pop(), indices.tolist().pop()
        results = [(dis, self.product2int.inverse[idx]) for dis, idx in zip(distances, indices)]
        return results
