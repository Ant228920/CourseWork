from app.db import Database
from app.auth import AuthService

try:
    db = Database()
    auth = AuthService(db)
    
    print("✅ Підключення до бази даних успішне!")
    
    # Тестуємо з реальними даними з БД
    print("\n🔍 Тестуємо авторизацію з 'user1':")
    user = auth.get_user_by_login("user1")
    if user:
        print("✅ Користувач знайдений:", user)
        print("Пароль в БД:", user['password'])
        
        # Тестуємо верифікацію пароля
        print("\n🔐 Тестуємо верифікацію пароля:")
        is_valid = auth.verify("user1", user['password'])
        print(f"Пароль 'user1' валідний: {is_valid}")
        
        # Тестуємо повний логін
        print("\n🚪 Тестуємо повний логін:")
        login_result = auth.login("user1", "user1")
        if login_result:
            print("✅ Логін успішний:", login_result)
        else:
            print("❌ Логін не вдався")
    else:
        print("❌ Користувач не знайдений")
        
except Exception as e:
    print("❌ Помилка:")
    print(e)
    import traceback
    traceback.print_exc()
