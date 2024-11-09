import json
from datetime import datetime, timezone
from uuid import UUID

from loguru import logger
from sqlalchemy import join, or_
from sqlalchemy.engine.row import Row

from database.helpers.handle_exceptions_and_logging import handle_exceptions_and_logging
from database.models.models import Model, ModelConfiguration, ModelType
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class ModelConfigurationRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return ModelConfiguration

    @handle_exceptions_and_logging
    def __get_raw_config(self) -> list[Row]:
        model_type_config_join = join(
            ModelType,
            ModelConfiguration,
            ModelType.Model_Type_Id == ModelConfiguration.Model_Type_Id,
        )

        result = (
            self.session.query(
                ModelType.Enum_Key,
                ModelType.Model_Type_Id,
                ModelConfiguration.Json_Value,
                ModelConfiguration.Model_Configuration_Id,
            )
            .select_from(model_type_config_join)
            .filter(ModelConfiguration.Valid_From <= datetime.now(timezone.utc))
            .filter(
                or_(
                    ModelConfiguration.Valid_To > datetime.now(timezone.utc),
                    ModelConfiguration.Valid_To == None,
                )
            )
            .order_by(ModelConfiguration.Model_Type_Id)
            .all()
        )

        return result

    def __parse_into_dict(self, raw_db_answer: list[Row]) -> dict:
        configuration_dict = {}

        for row in raw_db_answer:
            model_config = json.loads(row[2])
            model_config["Enum_Key"] = row[0]
            model_config["Model_Type_Id"] = row[1]
            model_config["Model_Configuration_Id"] = row[3]
            configuration_dict[row[0]] = model_config

        logger.debug("ModelConfigurationRepository __parse_into_dict(): OK.")
        return configuration_dict

    def get_model_config_dict(self, task_type: str) -> dict:
        raw_config = self.__get_raw_config()
        configuration_dict = self.__parse_into_dict(raw_config)

        configuration_dict_for_task = configuration_dict.get(task_type)
        assert isinstance(configuration_dict_for_task, dict)

        logger.debug("ModelConfigurationRepository get_model_config_dict(): OK.")

        return configuration_dict_for_task

    @handle_exceptions_and_logging
    def __get_json_value(self, model_uuid: UUID) -> str:
        model_configuration_id = (
            self.session.query(Model.Model_Configuration_Id)
            .filter(Model.Model_GUID == model_uuid)
            .scalar()
        )
        raw_json_value = (
            self.session.query(self.table.Json_Value)
            .filter(self.table.Model_Configuration_Id == model_configuration_id)
            .scalar()
        )

        return raw_json_value

    def get_threshold(self, model_uuid: UUID) -> int:
        raw_json_value = self.__get_json_value(model_uuid)
        json_value: dict = json.loads(raw_json_value)
        threshold = json_value.get("Threshold")

        assert threshold is not None

        logger.debug("ModelConfigurationRepository get_threshold(): OK.")

        return threshold
