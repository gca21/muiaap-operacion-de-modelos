"""TODO: transformación de una muestra validada en el vector del modelo."""

# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
FEATURE_NAMES = (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
)

# Implementa WineFeatures y preprocess_wine_request(). El orden anterior debe
# coincidir con el artefacto, no con un orden arbitrario del CSV.

from .contracts import WineQualityRequest

PREPROCESSING_VERSION = "wine-red-features-v1"

class WineFeatures():
    def __init__(self, request: WineQualityRequest):
        self.fixed_acidity = request.fixed_acidity
        self.volatile_acidity = request.volatile_acidity
        self.citric_acid = request.citric_acid
        self.residual_sugar = request.residual_sugar
        self.chlorides = request.chlorides
        self.free_sulfur_dioxide = request.free_sulfur_dioxide
        self.total_sulfur_dioxide = request.total_sulfur_dioxide
        self.density = request.density
        self.ph = request.ph
        self.sulphates = request.sulphates
        self.alcohol = request.alcohol

    def as_vector(self) -> list:
        return [
            self.fixed_acidity,
            self.volatile_acidity,
            self.citric_acid,
            self.residual_sugar,
            self.chlorides,
            self.free_sulfur_dioxide,
            self.total_sulfur_dioxide,
            self.density,
            self.ph,
            self.sulphates,
            self.alcohol
        ]

def preprocess_wine_request(request: WineQualityRequest) -> WineFeatures:
    return WineFeatures(request)