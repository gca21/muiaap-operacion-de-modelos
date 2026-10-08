# Wine Quality

## Instalación

Desde la raíz del repositorio:

```bash
cd semana2/wine-quality-project
uv sync --locked
```


## Entrenamiento y evaluación

Desde `semana2/wine-quality-project`:

```bash
uv run --frozen python -m wine_quality.train
```

## Pruebas y estilo

Ejecutar la suite de pruebas:

```bash
uv run --frozen pytest
```

Comprobar el estilo con Ruff:

```bash
uv run --frozen ruff check .
```
