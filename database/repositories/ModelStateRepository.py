from database.models.models import ModelState
from database.repositories.PostgreBaseReposotory import PostgreBaseReposotory


class ModelStateRepository(PostgreBaseReposotory):

    @property
    def table(self):
        return ModelState
