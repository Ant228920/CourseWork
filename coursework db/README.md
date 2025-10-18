## Проєкт: Облік військових формувань та ресурсів (PostgreSQL + Tkinter)

- **СУБД**: PostgreSQL
- **Мова/GUI**: Python 3 + Tkinter, `tkcalendar`
- **Драйвер БД**: `psycopg2-binary`
- **Кодування**: UTF-8, всі назви колонок у БД — кирилицею (в лапках)

### Як запустити
1. Встановіть PostgreSQL та створіть БД (наприклад `militarydb`).
2. Встановіть залежності:
```bash
python -m venv .venv && .venv\\Scripts\\pip install -r requirements.txt
```
3. Налаштуйте доступ до БД у файлі `.env` (див. `.env.example`).
4. Імпортуйте схему та початкові дані:
```bash
psql -U <user> -d <db> -f sql/schema.sql
psql -U <user> -d <db> -f sql/seed.sql
```
5. Запустіть застосунок:
```bash
.venv\\Scripts\\python app\\app.py
```

### Структура репозиторію
- `sql/schema.sql` — створення таблиць, ключів, обмежень.
- `sql/seed.sql` — мінімальні довідники та користувач-адміністратор.
- `sql/queries.sql` — 10 прикладів запитів/агрегацій.
- `docs/ERD.md` — ER-діаграма (Mermaid) та опис сутностей.
- `app/` — вихідний код Tkinter застосунку.
- `requirements.txt` — залежності Python.
- `.env.example` — приклад налаштувань підключення до БД.
