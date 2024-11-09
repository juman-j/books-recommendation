from abc import ABC, abstractmethod


class I_Model(ABC):

    @abstractmethod
    def data_preparation(self, dataframes: dict):
        pass

    @abstractmethod
    def hyperparameter_selection(self, configuration_dict: dict) -> dict:
        return dict

    @abstractmethod
    def train_test_model(self, params: dict) -> dict:
        # do training and test on validation sample
        pass

    @abstractmethod
    def fit_and_validate(self, dataframes: dict, configuration_dict: dict) -> dict:
        pass

    @abstractmethod
    def fit_final_model(self, params: dict) -> dict:
        pass
