from datetime import datetime
from uuid import UUID

from sqlalchemy import desc

from database.helpers.handle_exceptions_and_logging import handle_exceptions_and_logging
from database.models.models import Model
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class ModelRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return Model

    @handle_exceptions_and_logging
    def model_insert(
        self,
        Model_GUID: str,
        Last_Trained_Time: datetime,
        State_Id: int,
        Task_Type_Id: int,
        Model_Type_Id: int,
        Model_Configuration_Id: int,
    ) -> int:
        new_model = self.table(
            Model_GUID=Model_GUID,
            Last_Trained_Time=Last_Trained_Time,
            State_Id=State_Id,
            Task_Type_Id=Task_Type_Id,
            Model_Type_Id=Model_Type_Id,
            Model_Configuration_Id=Model_Configuration_Id,
        )

        self.session.add(new_model)
        self.session.flush()
        model_id = new_model.Model_Id
        self.session.commit()

        return model_id

    @handle_exceptions_and_logging
    def get_model_uuid(self, task_type_id: int) -> UUID:
        model_uuid = (
            self.session.query(self.table.Model_GUID)
            .filter(self.table.Task_Type_Id == task_type_id)
            .order_by(desc(self.table.Model_Id))
            .limit(1)
            .scalar()
        )

        return model_uuid
