from __future__ import annotations

from pydantic import BaseModel, Field

# Matriz anidada: {clave -> {sub-clave -> bool}}.
Matrix = dict[str, dict[str, bool]]


class RolesOut(BaseModel):
    matrix: Matrix = Field(default_factory=dict)  # rol -> capacidad -> bool


class RolesIn(BaseModel):
    matrix: Matrix


class ClinicFeaturesOut(BaseModel):
    matrix: Matrix = Field(default_factory=dict)  # clinic_id -> feature -> bool


class ClinicFeaturesIn(BaseModel):
    matrix: Matrix


class MyFeaturesOut(BaseModel):
    features: dict[str, bool] = Field(default_factory=dict)
