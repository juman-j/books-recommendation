from database.helpers.handle_exceptions_and_logging import handle_exceptions_and_logging
from database.models.models import ModelHyperparameter
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class ModelHyperparameterRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return ModelHyperparameter

    @handle_exceptions_and_logging
    def hyperparameter_insert(
        self,
        Value: str,
        Model_Id: int,
        Model_Hyperparameter_Type_Id: int,
    ):
        self.session.add(
            self.table(
                Model_Id=Model_Id,
                Model_Hyperparameter_Type_Id=Model_Hyperparameter_Type_Id,
                Value=Value,
            )
        )
        self.session.commit()
