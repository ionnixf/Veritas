# Задача: запуск AuditLens AI через Docker

## Цель

Обернуть приложение в Docker так, чтобы оно запускалось **одной командой без
дополнительных флагов и переменных окружения**:

```bash
docker compose up
```

После запуска интерфейс и API должны быть доступны на
<http://127.0.0.1:8088> (проверка готовности: `/api/v1/health`).

Сейчас проект запускается только локально, через `./scripts/run_local.sh`,
и требует установленных на хосте `uv`, Python 3.12, Node.js 22.12+ и npm.

## Что уже есть в проекте

- **Бэкенд**: FastAPI + Uvicorn, один worker, CPU-only зависимости в
  `requirements.txt` (включая `xgboost-cpu`, `python-multipart`).
- **Фронтенд**: React + TypeScript + Vite в `frontend/`, собирается в
  `frontend/dist`. Бэкенд отдаёт этот каталог как статику с `/`
  (см. `src/auditlens/backend/app.py`), поэтому UI и API работают на одном
  origin и отдельный веб-сервер не нужен.
- **Модель**: замороженный XGBoost-пайплайн и метаданные в `models/`
  (нужны внутри образа, иначе приложение не поднимется).
- **Данные**: `data/` (датасеты Handbook) для запуска **не нужны**.
- **Демо-входы**: фикстуры лежат в `src/auditlens/backend/assets/`.

## Требования

1. `docker compose up` из корня проекта поднимает всё приложение. Отдельный
   `docker compose build` или `--build` не должен быть обязательным шагом.
2. Многоступенчатая сборка в одном `Dockerfile`:
   - стадия сборки фронтенда — Node 22 (`npm ci` + `npm run build -- --mode unified`);
   - рантайм — Python 3.12 (`pip install -r requirements.txt`).
3. В итоговый образ попадают только: `src/`, `models/`, собранный
   `frontend/dist/`, `pyproject.toml`, `requirements.txt`. Тесты, `data/`,
   `scripts/`, `frontend/node_modules` и кеши — не попадают.
4. Добавить `.dockerignore`, исключающий `.venv-app/`, `frontend/node_modules/`,
   `frontend/dist/`, `data/`, `tests/`, `__pycache__/`, `.pytest_cache/`,
   `.ruff_cache/`, `.git/`.
5. Порт `8088` публикуется на `127.0.0.1`. Переопределение через
   `AUDITLENS_PORT` допустимо, но не обязательно для базового запуска.
6. Запуск под непривилегированным пользователем; `uvicorn` — один worker,
   `POLARS_MAX_THREADS=2`, `OMP_NUM_THREADS=2`.
7. `HEALTHCHECK`, дергающий `/api/v1/health`.
8. Приложение не переписывать: Docker-обвязка не должна менять логику,
   контракты API и структуру каталогов, которые читает код.

## Критерии приёмки

- На чистой машине с Docker и Docker Compose `docker compose up` собирает и
  запускает приложение; повторный запуск не пересобирает образ без изменений.
- `curl http://127.0.0.1:8088/api/v1/health` возвращает `200`.
- «Run live demo» в UI отдаёт очередь из пяти транзакций (реальный инференс
  модели внутри контейнера).
- `docker compose down` останавливает и удаляет контейнер.
- `./scripts/run_local.sh` продолжает работать как раньше (локальный запуск
  без Docker не ломается).
