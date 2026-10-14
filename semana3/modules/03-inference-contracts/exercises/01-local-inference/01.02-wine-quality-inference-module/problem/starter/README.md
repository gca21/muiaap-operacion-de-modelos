# Starter — Módulo local de inferencia de vino

Este es el único proyecto de código que recibe el alumnado. Implementad los
`TODO` siguiendo el orden del `../readme.md` y haced pasar las pruebas sin mirar
la solución del profesorado.

El profesor colocará `wine_quality_classifier.joblib` dentro de `models/` antes
del taller. El modelo ya está entrenado: no hay que modificarlo ni reentrenarlo.


## Decisiones de diseño:

* El preprocesado recae sobre la clase WineFeatures, facilitando la transformación de un modelo de pydantic a un array con las features necesarias.

* El fichero inference es el encargado de encapsular e implementar las funcionalidades relacionadas con el modelo y sus predicciones, lo que simplifica la carga y manejo de un modelo desde un archivo .joblib