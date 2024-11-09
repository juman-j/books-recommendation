import os
import pickle
import uuid

from loguru import logger


class ModelSaver:

    def __deserialize_model(self, byte_model: bytes):
        model = pickle.loads(byte_model)
        logger.debug("Model deserialization was successful.")

        return model

    def __serialize_model(self, model) -> bytes:
        bytes_model: bytes = pickle.dumps(model)
        logger.debug("Model serialization was successful.")

        return bytes_model

    def __get_local_model(self, model_uuid: uuid.UUID) -> bytes | None:
        path_0 = os.path.dirname(os.getcwd())
        path_1 = "saved_models"
        file_name = str(model_uuid) + ".pkl"
        filepath = os.path.join(path_0, path_1, file_name)

        if os.path.exists(filepath):
            with open(filepath, "rb") as file:
                byte_model = file.read()
            return byte_model
        return None

    def __save_locally_model(self, bytes_model: bytes, model_uuid: uuid.UUID) -> None:
        path_0 = os.path.dirname(os.getcwd())
        path_1 = "saved_models"
        file_name = str(model_uuid) + ".pkl"
        folder_path = os.path.join(path_0, path_1)
        filepath = os.path.join(path_0, path_1, file_name)

        # Check if the folder exists and create it if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Clear the contents of the folder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except FileNotFoundError as e:
                logger.debug(
                    f"FileServiceProvider __save_locally_model_cache(): "
                    f"Failed to delete the model {file_path}. Error: {e}"
                )
        with open(filepath, "wb") as file:
            file.write(bytes_model)

        logger.debug("The model was saved locally.")

    def save_model(self, model, model_uuid: uuid.UUID) -> None:
        bytes_model = self.__serialize_model(model)
        self.__save_locally_model(bytes_model, model_uuid)

    def get_model(self, model_uuid: uuid.UUID):
        byte_model = self.__get_local_model(model_uuid)

        if byte_model:
            model = self.__deserialize_model(byte_model)
        else:
            model = None

        return model
