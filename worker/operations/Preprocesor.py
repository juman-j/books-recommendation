import numpy as np
from loguru import logger
from pandas import DataFrame, concat, read_csv, to_numeric

from configurations.config import (
    BOOKS_DF,
    RATINGS_DF,
    TEST_SIZE,
    USERS_DF,
    VALIDATION_SIZE,
)


class Preprocesor:
    def __init__(self, task_type: str) -> None:
        # There may be logic here for implementations of
        # different preprocesing pipelines depending on the type of task.
        self.task_type = task_type

    @staticmethod
    def __read_data() -> tuple[DataFrame, DataFrame, DataFrame]:
        books_df = read_csv(BOOKS_DF, dtype={3: "str"})
        ratings_df = read_csv(RATINGS_DF)
        users_df = read_csv(USERS_DF)

        return books_df, ratings_df, users_df

    @staticmethod
    def __rename_columns(
        books_df: DataFrame, ratings_df: DataFrame, users_df: DataFrame
    ) -> tuple[DataFrame, DataFrame, DataFrame]:

        books_df.rename(
            columns={
                "ISBN": "isbn",
                "Book-Title": "book_title",
                "Book-Author": "book_author",
                "Year-Of-Publication": "year",
                "Publisher": "publisher",
            },
            inplace=True,
        )
        ratings_df.rename(
            columns={
                "ISBN": "isbn",
                "User-ID": "user_id",
                "Book-Rating": "rating",
            },
            inplace=True,
        )
        users_df.rename(
            columns={"User-ID": "user_id"},
            inplace=True,
        )

        return books_df, ratings_df, users_df

    @staticmethod
    def __year_to_num(books_df: DataFrame) -> DataFrame:
        books_df[books_df.columns[3]] = to_numeric(
            books_df[books_df.columns[3]], errors="coerce"
        )  # If ‘coerce’, then invalid parsing will be set as NaN.
        books_df.dropna(subset=["year"], axis=0, inplace=True)
        books_df["year"] = books_df["year"].astype(int)

        return books_df

    @staticmethod
    def __drop_columns(
        books_df: DataFrame, users_df: DataFrame
    ) -> tuple[DataFrame, DataFrame]:

        users_df.drop(["Location", "Age"], axis=1, inplace=True)
        books_df.drop(
            ["Image-URL-S", "Image-URL-M", "Image-URL-L"], axis=1, inplace=True
        )
        filtered_df = books_df[(books_df["year"] == 0) | (books_df["year"] > 2004)]
        filtered_df = filtered_df.astype({"year": float})
        filtered_df.loc[:, "year"] = np.nan
        books_df.drop(index=filtered_df.index, inplace=True)  # drop this

        return books_df, users_df

    @staticmethod
    def __merge_df(
        books_df: DataFrame, ratings_df: DataFrame, users_df: DataFrame
    ) -> DataFrame:
        ratings_users = users_df.merge(right=ratings_df, how="inner", on="user_id")
        ratings_users = ratings_users.merge(right=books_df, how="inner", on="isbn")
        ratings_users.drop(
            ["book_title", "book_author", "year", "publisher"], axis=1, inplace=True
        )

        return ratings_df

    @staticmethod
    def __drop_zero_rating(data: DataFrame, groupby_column: str) -> DataFrame:
        grouped_sum_ratings = data.groupby([groupby_column]).sum()["rating"]
        zero_ratings = grouped_sum_ratings[grouped_sum_ratings == 0]
        data = data[~data[groupby_column].isin(zero_ratings.index)]

        return data

    @staticmethod
    def __more_than_ratings(
        data: DataFrame, groupby_column: str, min_ratings: int
    ) -> DataFrame:
        grouped_count_ratings = data.groupby([groupby_column]).count()["rating"]
        more_than = grouped_count_ratings[grouped_count_ratings >= min_ratings]
        data = data[data[groupby_column].isin(more_than.index)]

        return data

    def __clean_up_data(
        self, data: DataFrame, groupby_column: str, min_ratings: int
    ) -> DataFrame:
        data = self.__drop_zero_rating(data, groupby_column)
        data = self.__more_than_ratings(data, groupby_column, min_ratings)

        return data

    @staticmethod
    def __train_test(
        data: DataFrame,
    ) -> tuple[DataFrame, DataFrame]:
        train_data = DataFrame(columns=data.columns)
        test_data = DataFrame(columns=data.columns)

        for _, user_data in data.groupby("user_id"):
            rated_data = user_data[user_data["rating"] > 0]
            test_count = int(len(rated_data) * TEST_SIZE)

            test_indices = np.random.choice(
                rated_data.index, size=test_count, replace=False
            )
            user_test_data = user_data.loc[test_indices]
            user_train_data = user_data.drop(test_indices)

            test_data = concat([test_data, user_test_data])
            train_data = concat([train_data, user_train_data])

        train_data = train_data.reset_index(drop=True)
        test_data = test_data.reset_index(drop=True)

        return train_data, test_data

    @staticmethod
    def __validation_data(test_data: DataFrame) -> tuple[DataFrame, DataFrame]:
        data_shuffled = test_data.sample(frac=1, random_state=42).reset_index(drop=True)
        val_set_size = int(len(test_data) * VALIDATION_SIZE)

        validation_data = data_shuffled[:val_set_size]
        test_data = data_shuffled[val_set_size:]

        return validation_data, test_data

    @staticmethod
    def __normalization(
        train_data: DataFrame,
        test_data: DataFrame,
        validation_data: DataFrame,
    ) -> tuple[DataFrame, DataFrame, DataFrame]:
        train_data["rating"] = (train_data["rating"] - np.min(train_data["rating"])) / (
            np.max(train_data["rating"]) - np.min(train_data["rating"])
        )
        test_data["rating"] = (test_data["rating"] - np.min(train_data["rating"])) / (
            np.max(train_data["rating"]) - np.min(train_data["rating"])
        )
        validation_data["rating"] = (
            validation_data["rating"] - np.min(train_data["rating"])
        ) / (np.max(train_data["rating"]) - np.min(train_data["rating"]))

        return train_data, test_data, validation_data

    @staticmethod
    def __concatenate(train_data: DataFrame, validation_data: DataFrame) -> DataFrame:
        result_df = concat([train_data, validation_data], ignore_index=True)
        return result_df

    def run(self, configuration_dict: dict) -> dict:
        books_df, ratings_df, users_df = self.__read_data()
        books_df, ratings_df, users_df = self.__rename_columns(
            books_df, ratings_df, users_df
        )
        books_df = self.__year_to_num(books_df)
        books_df, users_df = self.__drop_columns(books_df, users_df)
        full_data = self.__merge_df(books_df, ratings_df, users_df)
        full_data = self.__clean_up_data(
            data=full_data,
            groupby_column="user_id",
            min_ratings=int(
                configuration_dict["Model_runtime_parameters"]["Min_User_Rating"]
            ),
        )
        full_data = self.__clean_up_data(
            data=full_data,
            groupby_column="isbn",
            min_ratings=int(
                configuration_dict["Model_runtime_parameters"]["Min_Book_Rating"]
            ),
        )

        train_data, test_data = self.__train_test(full_data)
        validation_data, test_data = self.__validation_data(test_data)
        train_data, test_data, validation_data = self.__normalization(
            train_data, test_data, validation_data
        )
        train_validate_data = self.__concatenate(train_data, validation_data)

        train_data.drop(train_data.columns[0], axis=1, inplace=True)
        validation_data.drop(validation_data.columns[0], axis=1, inplace=True)
        train_validate_data.drop(train_validate_data.columns[0], axis=1, inplace=True)
        test_data.drop(test_data.columns[0], axis=1, inplace=True)
        full_data.drop(full_data.columns[0], axis=1, inplace=True)

        train_data.rename(columns={"user_id": "user", "isbn": "item"}, inplace=True)
        validation_data.rename(
            columns={"user_id": "user", "isbn": "item"}, inplace=True
        )
        train_validate_data.rename(
            columns={"user_id": "user", "isbn": "item"}, inplace=True
        )
        test_data.rename(columns={"user_id": "user", "isbn": "item"}, inplace=True)
        full_data.rename(columns={"user_id": "user", "isbn": "item"}, inplace=True)

        logger.info("Preprocesing is done.")

        return {
            "train_data": train_data,
            "validation_data": validation_data,
            "train_validate_data": train_validate_data,
            "test_data": test_data,
            "full_data": full_data,
        }
