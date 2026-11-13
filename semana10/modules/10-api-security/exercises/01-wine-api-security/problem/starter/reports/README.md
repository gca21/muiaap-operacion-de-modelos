# S10.7 — Informe de carga

Informe de la prueba de carga de S10.7, completado a partir de los CSV versionados.

## Cómo se ha medido

| Dato | Valor |
| --- | --- |
| Comando de la API | `uv run fastapi dev` (1 proceso) |
| Comando de Locust | `uv run --group load locust -f locustfile.py --headless -u 20 -r 5 -t 1m --host http://127.0.0.1:8000 --csv reports/s10` |
| Cliente usado | `front`, autenticación correcta |
| `rate_limit_per_minute` del cliente | 60 |

Archivos generados por Locust y versionados junto a este informe:
`s10_stats.csv`, `s10_failures.csv` y `s10_stats_history.csv`.

## Resultados

Copia los valores de la fila `POST /v1/predictions` y de `Aggregated` de
`s10_stats.csv`.

| Endpoint | Peticiones | RPS | p50 (ms) | p95 (ms) | Fallos | % 429 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `POST /v1/predictions` | 759 | 12.849 | 5 | 6 | 707 | 93.1 % |
| `POST /v1/predictions [422]` | 77 | 1.304 | 5 | 6 | 69 | 89.6 % |
| `GET /health` | 85 | 1.439 | 4 | 5 | 0 | — |
| Aggregated | 921 | 15.592 | 5 | 6 | 776 | 84.3 % |

Según `s10_failures.csv`, hubo 707 respuestas 429 en predicciones normales y
69 en solicitudes con datos inválidos. Las 8 solicitudes inválidas restantes
recibieron el 422 esperado. En total hubo 776 respuestas 429.

## Análisis

- Locust envió 836 peticiones de predicción en total. 60 pasaron y 776 recibieron 429, consistente con el límite de 60 por minuto.
- El 93.1 % de las predicciones normales y el 89.6 % de las solicitudes inválidas recibieron 429. Las restantes inválidas obtuvieron el 422 esperado.
- `/health` tuvo latencia p50 de 4 ms y p95 de 5 ms. Las predicciones tuvieron p50 de 5 ms y p95 de 6 ms.
- Con dos workers y contadores en memoria, cada proceso mantendría su propio contador. La cuota podría aplicarse de forma desigual y superar el límite global.
- Para medir capacidad, usaría un cliente válido con scope `predict` y una cuota suficientemente alta para que el rate limit no interfiera.
