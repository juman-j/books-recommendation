from database.models.models import ModelType
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class ModelTypeRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return ModelType
