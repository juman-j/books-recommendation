from database.helpers.handle_exceptions_and_logging import handle_exceptions_and_logging
from database.models.models import TaskType
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class TaskTypeRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return TaskType

    @handle_exceptions_and_logging
    def get_task_types(self) -> dict:
        result = self.session.query(TaskType).all()
        task_types_dict = {row.Task_Type_Id: row.Enum_Key for row in result}

        return task_types_dict

    @handle_exceptions_and_logging
    def insert_data(self, Enum_Key: str):
        self.session.add(self.table(Enum_Key=Enum_Key))
        self.session.commit()
