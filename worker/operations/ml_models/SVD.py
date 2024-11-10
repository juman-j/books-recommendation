from collections import defaultdict

from loguru import logger
from pandas import DataFrame as pd_DataFrame
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import GridSearchCV
from surprise.prediction_algorithms.algo_base import AlgoBase

from configurations.config import RATING_SCALE_MAX, RATING_SCALE_MIN
from worker.operations.ml_models.I_Model import I_Model


class SurpriseSVDModel(I_Model):
    algo = SVD

    def __init__(self) -> None:
        self.train_validate_data: Dataset = None
        self.full_data: Dataset = None
        self.train_data: Dataset = None
        self.validation_data: Dataset = None
        self.test_data: Dataset = None
        self.val_raw_ratings = None
        self.test_raw_ratings = None

    def data_preparation(self, dataframes: dict) -> None:
        reader = Reader(rating_scale=(RATING_SCALE_MIN, RATING_SCALE_MAX))

        train_data: pd_DataFrame = dataframes.get("train_data")
        validation_data: pd_DataFrame = dataframes.get("validation_data")
        test_data: pd_DataFrame = dataframes.get("test_data")
        train_validate_data: pd_DataFrame = dataframes.get("train_validate_data")
        full_data: pd_DataFrame = dataframes.get("full_data")

        self.train_data = Dataset.load_from_df(
            train_data[["user_id", "isbn", "rating"]], reader
        )
        self.validation_data = Dataset.load_from_df(
            validation_data[["user_id", "isbn", "rating"]], reader
        )
        self.test_data = Dataset.load_from_df(
            test_data[["user_id", "isbn", "rating"]], reader
        )
        self.train_validate_data = Dataset.load_from_df(
            train_validate_data[["user_id", "isbn", "rating"]], reader
        )
        self.full_data = Dataset.load_from_df(
            full_data[["user_id", "isbn", "rating"]], reader
        )

        self.val_raw_ratings = self.validation_data.raw_ratings
        self.test_raw_ratings = self.test_data.raw_ratings

        logger.debug("Done")

    def hyperparameter_selection(self, configuration_dict: dict) -> dict:
        lr_all = configuration_dict["Model_Hyperparameter_Config"]["Lr_All"]
        n_epochs = configuration_dict["Model_Hyperparameter_Config"]["N_epochs"]
        n_factors = configuration_dict["Model_Hyperparameter_Config"]["N_factors"]

        grid_search = GridSearchCV(
            algo_class=self.algo,
            param_grid={
                "n_epochs": n_epochs,
                "n_factors": n_factors,
                "lr_all": lr_all,
            },
            measures=["rmse"],
            cv=5,
        )

        grid_search.fit(data=self.train_data)
        params_dict: dict = grid_search.best_params["rmse"]

        logger.debug("Done")

        return params_dict

    # the code is taken from the surprise documentation
    @staticmethod
    def __precision_recall_at_k(
        predictions, k=10, threshold=0.7
    ) -> tuple[float, float]:
        user_est_true = defaultdict(list)
        for uid, _, true_r, est, _ in predictions:
            user_est_true[uid].append((est, true_r))

        precisions = dict()
        recalls = dict()
        for uid, user_ratings in user_est_true.items():

            # Sort user ratings by estimated value
            user_ratings.sort(key=lambda x: x[0], reverse=True)

            # Number of relevant items
            n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)

            # Number of recommended items in top k
            n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])

            # Number of relevant and recommended items in top k
            n_rel_and_rec_k = sum(
                ((true_r >= threshold) and (est >= threshold))
                for (est, true_r) in user_ratings[:k]
            )

            # Precision@K: Proportion of recommended items that are relevant
            # When n_rec_k is 0, Precision is undefined. We here set it to 0.

            precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0

            # Recall@K: Proportion of relevant items that are recommended
            # When n_rel is 0, Recall is undefined. We here set it to 0.

            recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

            mean_precision = sum(precisions.values()) / len(precisions)
            mean_recall = sum(recalls.values()) / len(recalls)

        return mean_precision, mean_recall

    def train_test_model(self, params: dict) -> dict:
        model: AlgoBase = self.algo(**params)
        model.fit(self.train_data.build_full_trainset())
        valset = self.validation_data.construct_testset(
            raw_testset=self.val_raw_ratings
        )
        predictions = model.test(valset)

        unbiased_rmse = accuracy.rmse(predictions=predictions, verbose=False)
        precisions, recalls = self.__precision_recall_at_k(predictions=predictions)

        metrics = {
            "Precision@k": precisions,
            "Recall@K": recalls,
            "RMSE": unbiased_rmse,
        }

        logger.debug("Done")

        return metrics

    def __get_final_metrics(self, params: dict) -> dict:

        model: AlgoBase = self.algo(**params)
        model.fit(self.train_validate_data.build_full_trainset())
        test_set = self.test_data.construct_testset(self.test_raw_ratings)
        predictions = model.test(test_set)

        unbiased_rmse = accuracy.rmse(predictions=predictions, verbose=False)
        precisions, recalls = self.__precision_recall_at_k(predictions=predictions)

        metrics = {
            "Precision@k": precisions,
            "Recall@K": recalls,
            "RMSE": unbiased_rmse,
        }

        logger.debug("Done")

        return metrics

    def fit_and_validate(self, dataframes: dict, configuration_dict: dict) -> dict:
        self.data_preparation(dataframes)
        params = self.hyperparameter_selection(configuration_dict)
        metrics = self.train_test_model(params)

        logger.debug("Done")

        return {"model_name": self, "params": params, "metrics": metrics}

    def fit_final_model(self, params: dict) -> dict:
        final_metrics = self.__get_final_metrics(params)
        model: AlgoBase = self.algo(**params)
        trained_model = model.fit(self.full_data.build_full_trainset())

        logger.debug("Done")
        logger.info(f"Final model has {round(final_metrics.get('RMSE'), 2)} RMSE")

        return {"model": trained_model, "metrics": final_metrics}
