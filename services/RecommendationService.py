import uuid
from datetime import datetime, timezone

from loguru import logger

from data_models.EventDataModel import EventDataModel
from database.repositories.ModelConfigurationRepository import (
    ModelConfigurationRepository,
)
from database.repositories.ModelHyperparameterRepository import (
    ModelHyperparameterRepository,
)
from database.repositories.ModelHyperparameterTypeRepository import (
    ModelHyperparameterTypeRepository,
)
from database.repositories.ModelRepository import ModelRepository
from database.repositories.ModelScoreRepository import ModelScoreRepository
from database.repositories.ModelScoreTypeRepository import ModelScoreTypeRepository
from worker.operations.ModelTrainer import ModelTrainer
from worker.operations.Preprocesor import Preprocesor


class RecommendationService:

    def __init__(self, event_data: EventDataModel) -> None:
        self.task_type = event_data.task_type
        self._preprocesor = Preprocesor(event_data.task_type)
        self._model_trainer = ModelTrainer(event_data.task_type_id)
        self._model_configuration_repo = ModelConfigurationRepository()
        self._model_score_type_repo = ModelScoreTypeRepository()
        self._moel_hyperparam_type_repo = ModelHyperparameterTypeRepository()
        self._model_repo = ModelRepository()
        self._model_hyperparam_repo = ModelHyperparameterRepository()
        self._model_score_repo = ModelScoreRepository()

    def __get_config_val(self) -> dict:
        configuration_dict = self._model_configuration_repo.get_model_config_dict(
            self.task_type
        )
        logger.debug("Done")

        return configuration_dict

    def __get_metadata_types(self) -> tuple[dict, dict]:
        score_type_dict = self._model_score_type_repo.get_score_type()
        hyperparameter_type_dict = (
            self._moel_hyperparam_type_repo.get_hyperparameter_type()
        )
        logger.debug("Done")

        return score_type_dict, hyperparameter_type_dict

    def __insert_metadata(
        self,
        model_uuid: uuid.UUID,
        params: dict,
        metrics: dict,
        model_type_id: int,
        score_type_dict: dict,
        hyperparameter_type_dict: dict,
        model_config_id=1,
        state_id=1,
        task_type_id=1,
    ) -> None:
        now = datetime.now(timezone.utc)
        model_id = self._model_repo.model_insert(
            Model_GUID=model_uuid,
            Last_Trained_Time=now,
            State_Id=state_id,
            Task_Type_Id=task_type_id,
            Model_Type_Id=model_type_id,
            Model_Configuration_Id=model_config_id,
        )

        for metric in metrics.keys():
            if metric in score_type_dict.keys():
                self._model_score_repo.score_insert(
                    Model_Id=model_id,
                    Value=metrics.get(metric),
                    Model_Score_Type_Id=score_type_dict.get(metric),
                )

        for param in params.keys():
            if param in hyperparameter_type_dict.keys():
                self._model_hyperparam_repo.hyperparameter_insert(
                    Model_Id=model_id,
                    Value=str(params.get(param)),
                    Model_Hyperparameter_Type_Id=hyperparameter_type_dict.get(param),
                )

        logger.debug("Done")

    def run(self) -> None:
        configuration_dict: dict = self.__get_config_val()
        dataframes: dict = self._preprocesor.run(configuration_dict)
        train_result: dict = self._model_trainer.run(dataframes, configuration_dict)

        model_uuid = train_result["model_uuid"]
        params = train_result["params"]
        metrics = train_result["metrics"]
        model_type_id = train_result["model_type_id"]

        score_type_dict, hyperparameter_type_dict = self.__get_metadata_types()

        self.__insert_metadata(
            model_uuid,
            params,
            metrics,
            model_type_id,
            score_type_dict,
            hyperparameter_type_dict,
        )

        logger.success("The task has been successfully completed.")
