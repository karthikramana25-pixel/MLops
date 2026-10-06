"""Request and response schemas for the inference API."""

from pydantic import BaseModel, ConfigDict, Field


class IrisFeatures(BaseModel):
    """Four measurements used to classify an Iris flower (centimetres)."""

    model_config = ConfigDict(extra="forbid")

    sepal_length: float = Field(gt=0, le=10)
    sepal_width: float = Field(gt=0, le=10)
    petal_length: float = Field(gt=0, le=10)
    petal_width: float = Field(gt=0, le=10)


class Prediction(BaseModel):
    class_id: int = Field(ge=0, le=2)
    class_name: str
    probabilities: dict[str, float]
