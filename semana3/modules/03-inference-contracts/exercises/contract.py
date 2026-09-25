from pydantic import BaseModel, Field

class WineInputSchema(BaseModel):
    sample_id: int = Field(..., description="Unique identifier for the wine sample"),
    fixed_acidity: float = Field(...),
    volatile_acidity: float = Field(...),
    citric_acid: float = Field(...),
    residual_sugar: float = Field(...),
    chlorides: float = Field(...),
    free_sulfur_dioxide: float = Field(...),
    total_sulfur_dioxide: float = Field(...),
    density: float = Field(...),
    ph: float = Field(...),
    sulphates: float = Field(...),
    alcohol: float = Field(...)

if __name__ == "__main__":
    mi_contrato = WineInputSchema(
        sample_id=1,
        fixed_acidity=7.4,
        volatile_acidity=0.7,
        citric_acid=0.0,
        residual_sugar=1.9,
        chlorides=0.076,
        free_sulfur_dioxide=11.0,
        total_sulfur_dioxide=34.0,
        density=0.9978,
        ph=3.51,
        sulphates=0.56,
        alcohol=9.4
    )