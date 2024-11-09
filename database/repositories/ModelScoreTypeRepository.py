from database.helpers.handle_exceptions_and_logging import handle_exceptions_and_logging
from database.models.models import ModelScoreType
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class ModelScoreTypeRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return ModelScoreType

    @handle_exceptions_and_logging
    def get_score_type(self) -> dict:
        result = self.session.query(
            self.table.Model_Score_Type_Id, self.table.Enum_Key
        ).all()

        score_type_dict = {row[1]: row[0] for row in result}

        return score_type_dict
