from database.helpers.handle_exceptions_and_logging import handle_exceptions_and_logging
from database.models.models import ModelScore
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class ModelScoreRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return ModelScore

    @handle_exceptions_and_logging
    def score_insert(
        self,
        Value: float,
        Model_Id: int,
        Model_Score_Type_Id: int,
    ):
        new_model_score = ModelScore(
            Model_Id=Model_Id, Model_Score_Type_Id=Model_Score_Type_Id, Value=Value
        )
        self.session.add(new_model_score)
        self.session.commit()
