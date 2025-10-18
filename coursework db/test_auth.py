from app.db import Database
from app.auth import AuthService

try:
    db = Database()
    auth = AuthService(db)
    
    print("✅ Підключення до бази даних успішне!")
    
    # Перевіримо структуру таблиць
    print("\n📋 Структура таблиці 'користувач':")
    cols, rows = db.query_with_columns("SELECT * FROM \"users\" LIMIT 1;")
    print("Колонки:", cols)
    
    print("\n📋 Структура таблиці 'роль':")
    cols, rows = db.query_with_columns("SELECT * FROM \"roles\" LIMIT 1;")
    print("Колонки:", cols)
    
    # Перевіримо всіх користувачів
    print("\n👥 Всі користувачі:")
    cols, rows = db.query_with_columns("SELECT * FROM \"users\";")
    print("Колонки:", cols)
    for row in rows:
        print("Рядок:", dict(row))
    
    # Перевіримо ролі
    print("\n🎭 Всі ролі:")
    cols, rows = db.query_with_columns("SELECT * FROM \"roles\";")
    print("Колонки:", cols)
    for row in rows:
        print("Рядок:", dict(row))
    
    # Тестуємо запит авторизації
    print("\n🔍 Тестуємо запит авторизації:")
    user = auth.get_user_by_login("admin")
    if user:
        print("✅ Користувач знайдений:", user)
    else:
        print("❌ Користувач не знайдений")
        
except Exception as e:
    print("❌ Помилка:")
    print(e)
    import traceback
    traceback.print_exc()
