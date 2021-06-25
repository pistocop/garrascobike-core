import sys
from enum import Enum

import typer
from loguru import logger
from typer import Option

from managers.data_manager import DataManager
from managers.knn_manager import KnnManager


class MLModels(str, Enum):
    knn = 'knn'


# noinspection DuplicatedCode
def main(presence_data_path: str = Option("./data/03_correlation_data/presence_dataset/20210331124802/presences.csv"),
         ml_model: MLModels = Option(MLModels.knn),
         output_path: str = Option("./data/04_recommendation_models/knn/"),
         debug: bool = Option(False),
         ):
    # Init
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    logger.debug(f"presence_data_path: `{presence_data_path=}`")
    logger.debug(f"ml_model: `{ml_model=}`")
    logger.debug(f"output_path: `{output_path=}`")
    logger.debug(f"debug: `{debug=}`")

    # Data Loading
    logger.info("Data loading...")
    dm = DataManager(presence_data_path, working_col="product_name", working_col_init=False)
    ml_manager = KnnManager()  # Only 1 model available currently

    # Data preprocessing
    logger.info("Data preprocessing...")
    dm = ml_manager.preprocess(dm)

    # Model training
    logger.info("Model training...")
    ml_manager.train(dm)

    # Model storing
    logger.info(f"Model storing at {output_path}...")
    ml_manager.store_model(output_path)

    logger.info("Recommendation trainer completed!")


if __name__ == '__main__':
    typer.run(main)
