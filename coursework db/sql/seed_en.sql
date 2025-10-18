-- Seed data for English schema
INSERT INTO roles (name, description) VALUES
	('Адміністратор', 'Повний доступ до системи'),
	('Оператор', 'CRUD операції, пошук, виконання запитів'),
	('Авторизований', 'Перегляд даних, пошук, вбудовані запити'),
	('Гість', 'Перегляд даних, подача заявок на доступ')
ON CONFLICT (name) DO NOTHING;

-- Admin user (password: admin123)
INSERT INTO users (login, password, role_id, email, confirmed)
SELECT 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeaLgBN4tk3Dk9c9K', r.id, 'admin@military.gov.ua', TRUE
FROM roles r WHERE r.name='Адміністратор'
ON CONFLICT (login) DO NOTHING;

-- Test operator (password: operator123)
INSERT INTO users (login, password, role_id, email, confirmed)
SELECT 'operator', '$2b$12$8Ec0oJXXhYAOGx5PnqFOWuEP7yB.bPdY6i3F0nGjRgC3LMNgKJh7K', r.id, 'operator@military.gov.ua', TRUE
FROM roles r WHERE r.name='Оператор'
ON CONFLICT (login) DO NOTHING;
