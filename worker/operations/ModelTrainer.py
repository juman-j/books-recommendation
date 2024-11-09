import uuid

from loguru import logger

from worker.operations.ml_models.NeuralNet import NeuralNet
from worker.operations.ml_models.SVD import SurpriseSVDModel
from worker.operations.ModelSaver import ModelSaver


class ModelTrainer:

    def __init__(self, task_type_id: int) -> None:
        # There may be logic here for implementations of
        # different preprocesing pipelines depending on the type of task.
        self.task_type_id = task_type_id
        self.__svd = SurpriseSVDModel()
        self.__neural_net = NeuralNet()
        self.__model_saver = ModelSaver()

    def __model_selection(self, dataframes: dict, configuration_dict: dict) -> dict:
        svd_result = self.__svd.fit_and_validate(dataframes, configuration_dict)
        net_result = self.__neural_net.fit_and_validate(dataframes)
        results = [net_result, svd_result]
        selected_model = min(results, key=lambda x: x["metrics"]["RMSE"])

        logger.debug("Done")

        return selected_model

    def __save_best_model(self, model: NeuralNet | SurpriseSVDModel) -> uuid.UUID:
        model_uuid = uuid.uuid4()
        self.__model_saver.save_model(model, model_uuid)

        logger.debug("Done")

        return model_uuid

    def run(self, dataframes: dict, configuration_dict: dict) -> dict:
        selected_model = self.__model_selection(dataframes, configuration_dict)
        model: NeuralNet | SurpriseSVDModel = selected_model["model_name"]
        params: dict = selected_model["params"]
        metrics: dict = selected_model["metrics"]

        result = model.fit_final_model(params)
        model: NeuralNet | SurpriseSVDModel = result["model"]
        metrics: dict = result["metrics"]

        model_uuid = self.__save_best_model(model)

        logger.debug("Done")

        return {
            "model_uuid": model_uuid,
            "params": params,
            "metrics": metrics,
            "model_type_id": self.task_type_id,
        }
