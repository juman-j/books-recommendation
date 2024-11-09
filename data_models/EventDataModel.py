from pydantic import BaseModel, Field, model_validator

from database.repositories.TaskTypeRepository import TaskTypeRepository


class EventDataModel(BaseModel):
    task_type_id: int
    task_type: str = Field(init=False)

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: dict):
        task_types_dict = TaskTypeRepository().get_task_types()
        values["task_type"] = task_types_dict.get(values.get("task_type_id"))

        assert (
            values["task_type"] is not None
        ), "This task type is not supported by this application."

        return values
