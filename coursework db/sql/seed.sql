-- Мінімальне наповнення даних
INSERT INTO "роль" ("назва", "опис") VALUES
	('Адміністратор', 'Повний доступ'),
	('Оператор', 'CRUD, пошук, запити'),
	('Авторизований', 'Перегляд, пошук, вбудовані запити'),
	('Гість', 'Перегляд, може надіслати заявку')
ON CONFLICT ("назва") DO NOTHING;

-- Пароль необхідно замінити на реальний хеш (bcrypt)
INSERT INTO "користувач" ("логін", "пароль", "роль_id", "email", "підтверджено")
SELECT 'admin', '$2b$12$placeholderhashplaceholderhashplacehol', r.id, 'admin@example.com', TRUE
FROM "роль" r WHERE r."назва"='Адміністратор'
ON CONFLICT ("логін") DO NOTHING;
