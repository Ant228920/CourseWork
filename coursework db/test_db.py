from app.db import Database  # або просто from db import Database — залежно від твоєї структури

try:
    db = Database()
    conn = db.connect()
    print("✅ Підключення до бази даних успішне!")

    # Виконаємо простий запит, щоб упевнитися, що БД реально працює
    cols, rows = db.query_with_columns("SELECT version();")
    print("📦 Версія PostgreSQL:", rows[0][0])

except Exception as e:
    print("❌ Помилка підключення до БД:")
    print(e)
