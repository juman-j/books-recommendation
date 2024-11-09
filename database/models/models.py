from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Model(Base):
    __tablename__ = "Model"

    Model_Id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    Model_GUID: Mapped[UUID]
    Last_Trained_Time: Mapped[datetime]
    State_Id: Mapped[int] = mapped_column(ForeignKey("Model_State.Model_State_Id"))
    Task_Type_Id: Mapped[int] = mapped_column(ForeignKey("Task_Type.Task_Type_Id"))
    Model_Type_Id: Mapped[int] = mapped_column(ForeignKey("Model_Type.Model_Type_Id"))
    Model_Configuration_Id: Mapped[int] = mapped_column(
        ForeignKey("Model_Configuration.Model_Configuration_Id")
    )

    Task_Type: Mapped["TaskType"] = relationship(back_populates="Models")
    Model_Type: Mapped["ModelType"] = relationship(back_populates="Models")
    Model_Configuration: Mapped["ModelConfiguration"] = relationship(
        back_populates="Models"
    )
    Scores: Mapped[list["ModelScore"]] = relationship(back_populates="Model")
    Hyperparameters: Mapped[list["ModelHyperparameter"]] = relationship(
        back_populates="Model"
    )


class TaskType(Base):
    __tablename__ = "Task_Type"

    Task_Type_Id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    Enum_Key: Mapped[str]

    Models: Mapped[list["Model"]] = relationship(back_populates="Task_Type")


class ModelState(Base):
    __tablename__ = "Model_State"

    Model_State_Id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    Enum_Key: Mapped[str]


class ModelScore(Base):
    __tablename__ = "Model_Score"

    Model_Score_Id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    Model_Id: Mapped[int] = mapped_column(ForeignKey("Model.Model_Id"))
    Model_Score_Type_Id: Mapped[int] = mapped_column(
        ForeignKey("Model_Score_Type.Model_Score_Type_Id")
    )
    Value: Mapped[float]

    Model: Mapped["Model"] = relationship(back_populates="Scores")
    Score_Type: Mapped["ModelScoreType"] = relationship(back_populates="Model_Scores")


class ModelScoreType(Base):
    __tablename__ = "Model_Score_Type"

    Model_Score_Type_Id: Mapped[int] = mapped_column(
        autoincrement=True, primary_key=True
    )
    Enum_Key: Mapped[str]

    Model_Scores: Mapped[list["ModelScore"]] = relationship(back_populates="Score_Type")


class ModelHyperparameter(Base):
    __tablename__ = "Model_Hyperparameter"

    Model_Hyperparameter_Id: Mapped[int] = mapped_column(
        autoincrement=True, primary_key=True
    )
    Value: Mapped[Optional[str]]
    Model_Id: Mapped[int] = mapped_column(ForeignKey("Model.Model_Id"))
    Model_Hyperparameter_Type_Id: Mapped[int] = mapped_column(
        ForeignKey("Model_Hyperparameter_Type.Model_Hyperparameter_Type_Id")
    )

    Hyperparameter_Types: Mapped[list["ModelHyperparameterType"]] = relationship(
        back_populates="Hyperparameters"
    )
    Model: Mapped["Model"] = relationship(back_populates="Hyperparameters")


class ModelHyperparameterType(Base):
    __tablename__ = "Model_Hyperparameter_Type"

    Model_Hyperparameter_Type_Id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    Enum_Key: Mapped[str]

    Hyperparameters: Mapped[list["ModelHyperparameter"]] = relationship(
        back_populates="Hyperparameter_Types"
    )


class ModelConfiguration(Base):
    __tablename__ = "Model_Configuration"

    Model_Configuration_Id: Mapped[int] = mapped_column(
        autoincrement=True, primary_key=True
    )
    Model_Type_Id: Mapped[int] = mapped_column(ForeignKey("Model_Type.Model_Type_Id"))
    Valid_From: Mapped[datetime]
    Valid_To: Mapped[datetime] = mapped_column(nullable=True)
    Json_Value: Mapped[str]

    Models: Mapped[list["Model"]] = relationship(back_populates="Model_Configuration")
    Model_Type: Mapped["ModelType"] = relationship(back_populates="Configuration")


class ModelType(Base):
    __tablename__ = "Model_Type"

    Model_Type_Id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    Enum_Key: Mapped[str]

    Models: Mapped[list["Model"]] = relationship(back_populates="Model_Type")
    Configuration: Mapped["ModelConfiguration"] = relationship(
        back_populates="Model_Type"
    )
