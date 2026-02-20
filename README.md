# Сервис управления арендой общежитий (места в комнатах)

Стек: Python + Flask + SQLite + Bootstrap (CDN).

## Быстрый старт

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask --app run.py init-db
flask --app run.py run
```

Откройте:
- Клиент: http://127.0.0.1:5000/
- Админка: http://127.0.0.1:5000/admin

## Что есть

Клиент:
- Подача заявки на заселение/переселение
- Просмотр статуса по коду заявки

Сервер (админка):
- Комнаты и места (койко-места)
- Студенты и текущие заселения
- Очередь заявок, подтверждение/отклонение
- Переселение между местами
