from worker.operations.ml_models.I_Model import I_Model


class NeuralNet(I_Model):

    def data_preparation(self, dataframes: dict) -> dict:
        return {
            "train_data": None,
            "validation_data": None,
            "train_validate_data": None,
            "test_data": None,
            "full_data": None,
        }

    def hyperparameter_selection(self) -> dict:
        pass

    def train_test_model(self, params: dict) -> dict:
        pass

    def fit_and_validate(self, dataframes: dict) -> dict:
        params = {}
        metrics = {
            "Precision@k": None,
            "Recall@K": None,
            "RMSE": 100,
        }

        return {"model_name": self, "params": params, "metrics": metrics}

    def fit_final_model(self, params: dict) -> dict:
        pass
