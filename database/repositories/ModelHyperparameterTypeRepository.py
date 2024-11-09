from database.helpers.handle_exceptions_and_logging import handle_exceptions_and_logging
from database.models.models import ModelHyperparameterType
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class ModelHyperparameterTypeRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return ModelHyperparameterType

    @handle_exceptions_and_logging
    def get_hyperparameter_type(self) -> dict:
        result = self.session.query(
            self.table.Model_Hyperparameter_Type_Id,
            self.table.Enum_Key,
        ).all()

        hyperparameter_type_dict = {row[1]: row[0] for row in result}

        return hyperparameter_type_dict
