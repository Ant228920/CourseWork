-- Повний SQL-скрипт для створення БД та всіх таблиць
-- Database: military

-- DROP DATABASE IF EXISTS military;

CREATE DATABASE military
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Ukrainian_Ukraine.1251'
    LC_CTYPE = 'Ukrainian_Ukraine.1251'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Підключитися до БД military перед виконанням наступних команд
\c military;

-- Створення всіх таблиць
CREATE TABLE IF NOT EXISTS "роль" (
	"id" BIGSERIAL PRIMARY KEY,
	"назва" TEXT NOT NULL UNIQUE,
	"опис" TEXT
);

CREATE TABLE IF NOT EXISTS "користувач" (
	"id" BIGSERIAL PRIMARY KEY,
	"логін" TEXT NOT NULL UNIQUE,
	"пароль" TEXT NOT NULL,
	"роль_id" BIGINT NOT NULL REFERENCES "роль"("id") ON UPDATE CASCADE,
	"email" TEXT,
	"телефон" TEXT,
	"підтверджено" BOOLEAN NOT NULL DEFAULT FALSE,
	"дата_створення" TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Ієрархія формувань
CREATE TABLE IF NOT EXISTS "військовий_округ" (
	"id" BIGSERIAL PRIMARY KEY,
	"назва" TEXT NOT NULL UNIQUE,
	"штаб" TEXT,
	"командувач" TEXT
);

CREATE TABLE IF NOT EXISTS "армія" (
	"id" BIGSERIAL PRIMARY KEY,
	"номер" INTEGER NOT NULL,
	"назва" TEXT,
	"військовий_округ_id" BIGINT NOT NULL REFERENCES "військовий_округ"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	UNIQUE ("військовий_округ_id", "номер")
);

CREATE TABLE IF NOT EXISTS "корпус" (
	"id" BIGSERIAL PRIMARY KEY,
	"номер" INTEGER NOT NULL,
	"армія_id" BIGINT NOT NULL REFERENCES "армія"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	UNIQUE ("армія_id", "номер")
);

CREATE TABLE IF NOT EXISTS "дивізія" (
	"id" BIGSERIAL PRIMARY KEY,
	"номер" INTEGER NOT NULL,
	"тип" TEXT NOT NULL,
	"корпус_id" BIGINT NOT NULL REFERENCES "корпус"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	UNIQUE ("корпус_id", "номер")
);

CREATE TABLE IF NOT EXISTS "військова_частина" (
	"id" BIGSERIAL PRIMARY KEY,
	"номер" TEXT NOT NULL,
	"назва" TEXT,
	"дивізія_id" BIGINT NOT NULL REFERENCES "дивізія"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	UNIQUE ("дивізія_id", "номер")
);

CREATE TABLE IF NOT EXISTS "підрозділ" (
	"id" BIGSERIAL PRIMARY KEY,
	"тип" TEXT NOT NULL,
	"назва" TEXT,
	"військова_частина_id" BIGINT NOT NULL REFERENCES "військова_частина"("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Персонал
CREATE TABLE IF NOT EXISTS "військовослужбовець" (
	"id" BIGSERIAL PRIMARY KEY,
	"прізвище" TEXT NOT NULL,
	"ім'я" TEXT NOT NULL,
	"по_батькові" TEXT,
	"звання" TEXT NOT NULL,
	"посада" TEXT,
	"дата_народження" DATE,
	"дата_прийняття" DATE,
	"підрозділ_id" BIGINT NOT NULL REFERENCES "підрозділ"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
	"військова_частина_id" BIGINT NOT NULL REFERENCES "військова_частина"("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Техніка
CREATE TABLE IF NOT EXISTS "тип_техніки" (
	"id" BIGSERIAL PRIMARY KEY,
	"назва" TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "техніка" (
	"id" BIGSERIAL PRIMARY KEY,
	"інвентарний_номер" TEXT NOT NULL UNIQUE,
	"модель" TEXT NOT NULL,
	"тип_техніки_id" BIGINT NOT NULL REFERENCES "тип_техніки"("id") ON UPDATE CASCADE,
	"рік_випуску" INTEGER CHECK ("рік_випуску" BETWEEN 1940 AND EXTRACT(YEAR FROM NOW())::INT),
	"стан" TEXT NOT NULL DEFAULT 'справна',
	"військова_частина_id" BIGINT REFERENCES "військова_частина"("id") ON DELETE SET NULL ON UPDATE CASCADE,
	"підрозділ_id" BIGINT REFERENCES "підрозділ"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- Озброєння
CREATE TABLE IF NOT EXISTS "тип_озброєння" (
	"id" BIGSERIAL PRIMARY KEY,
	"назва" TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "озброєння" (
	"id" BIGSERIAL PRIMARY KEY,
	"серійний_номер" TEXT NOT NULL UNIQUE,
	"модель" TEXT NOT NULL,
	"тип_озброєння_id" BIGINT NOT NULL REFERENCES "тип_озброєння"("id") ON UPDATE CASCADE,
	"стан" TEXT NOT NULL DEFAULT 'справне',
	"військова_частина_id" BIGINT REFERENCES "військова_частина"("id") ON DELETE SET NULL ON UPDATE CASCADE,
	"підрозділ_id" BIGINT REFERENCES "підрозділ"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- Споруди
CREATE TABLE IF NOT EXISTS "споруда" (
	"id" BIGSERIAL PRIMARY KEY,
	"назва" TEXT NOT NULL,
	"тип" TEXT NOT NULL,
	"адреса" TEXT,
	"військова_частина_id" BIGINT REFERENCES "військова_частина"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- Заявки гостей на доступ
CREATE TABLE IF NOT EXISTS "заявка_доступу" (
	"id" BIGSERIAL PRIMARY KEY,
	"користувач_id" BIGINT NOT NULL REFERENCES "користувач"("id") ON DELETE CASCADE ON UPDATE CASCADE,
	"статус" TEXT NOT NULL DEFAULT 'новий',
	"дата_створення" TIMESTAMP NOT NULL DEFAULT NOW(),
	"коментар" TEXT
);

-- Індекси
CREATE INDEX IF NOT EXISTS idx_армія_округ ON "армія" ("військовий_округ_id");
CREATE INDEX IF NOT EXISTS idx_корпус_армія ON "корпус" ("армія_id");
CREATE INDEX IF NOT EXISTS idx_дивізія_корпус ON "дивізія" ("корпус_id");
CREATE INDEX IF NOT EXISTS idx_частина_дивізія ON "військова_частина" ("дивізія_id");
CREATE INDEX IF NOT EXISTS idx_підрозділ_частина ON "підрозділ" ("військова_частина_id");
CREATE INDEX IF NOT EXISTS idx_військовослужбовець_підрозділ ON "військовослужбовець" ("підрозділ_id");
CREATE INDEX IF NOT EXISTS idx_техніка_частина ON "техніка" ("військова_частина_id");
CREATE INDEX IF NOT EXISTS idx_озброєння_частина ON "озброєння" ("військова_частина_id");

-- ========== ПОЧАТКОВІ ДАНІ ==========

-- Ролі користувачів
INSERT INTO "роль" ("назва", "опис") VALUES
	('Адміністратор', 'Повний доступ до системи'),
	('Оператор', 'CRUD операції, пошук, виконання запитів'),
	('Авторизований', 'Перегляд даних, пошук, вбудовані запити'),
	('Гість', 'Перегляд даних, подача заявок на доступ')
ON CONFLICT ("назва") DO NOTHING;

-- Адміністратор (пароль: admin123)
INSERT INTO "користувач" ("логін", "пароль", "роль_id", "email", "підтверджено")
SELECT 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeaLgBN4tk3Dk9c9K', r."id", 'admin@military.gov.ua', TRUE
FROM "роль" r WHERE r."назва"='Адміністратор'
ON CONFLICT ("логін") DO NOTHING;

-- Тестовий оператор (пароль: operator123)
INSERT INTO "користувач" ("логін", "пароль", "роль_id", "email", "підтверджено")
SELECT 'operator', '$2b$12$8Ec0oJXXhYAOGx5PnqFOWuEP7yB.bPdY6i3F0nGjRgC3LMNgKJh7K', r."id", 'operator@military.gov.ua', TRUE
FROM "роль" r WHERE r."назва"='Оператор'
ON CONFLICT ("логін") DO NOTHING;

-- Військові округи
INSERT INTO "військовий_округ" ("назва", "штаб", "командувач") VALUES
	('Східний військовий округ', 'м. Дніпро', 'генерал-лейтенант Іваненко І.І.'),
	('Західний військовий округ', 'м. Львів', 'генерал-лейтенант Петренко П.П.'),
	('Південний військовий округ', 'м. Одеса', 'генерал-лейтенант Сидоренко С.С.'),
	('Північний військовий округ', 'м. Чернігів', 'генерал-лейтенант Коваленко К.К.')
ON CONFLICT ("назва") DO NOTHING;

-- Армії
INSERT INTO "армія" ("номер", "назва", "військовий_округ_id")
SELECT 1, '1-ша танкова армія', в."id" FROM "військовий_округ" в WHERE в."назва"='Східний військовий округ'
UNION ALL
SELECT 2, '2-га механізована армія', в."id" FROM "військовий_округ" в WHERE в."назва"='Східний військовий округ'
UNION ALL
SELECT 3, '3-тя повітряно-десантна армія', в."id" FROM "військовий_округ" в WHERE в."назва"='Західний військовий округ'
UNION ALL
SELECT 4, '4-та артилерійська армія', в."id" FROM "військовий_округ" в WHERE в."назва"='Південний військовий округ'
ON CONFLICT ("військовий_округ_id", "номер") DO NOTHING;

-- Корпуси
INSERT INTO "корпус" ("номер", "армія_id")
SELECT 1, а."id" FROM "армія" а WHERE а."номер"=1
UNION ALL
SELECT 2, а."id" FROM "армія" а WHERE а."номер"=1
UNION ALL
SELECT 1, а."id" FROM "армія" а WHERE а."номер"=2
UNION ALL
SELECT 1, а."id" FROM "армія" а WHERE а."номер"=3
ON CONFLICT ("армія_id", "номер") DO NOTHING;

-- Дивізії
INSERT INTO "дивізія" ("номер", "тип", "корпус_id")
SELECT 1, 'танкова', к."id" FROM "корпус" к JOIN "армія" а ON а."id"=к."армія_id" WHERE а."номер"=1 AND к."номер"=1
UNION ALL
SELECT 2, 'механізована', к."id" FROM "корпус" к JOIN "армія" а ON а."id"=к."армія_id" WHERE а."номер"=1 AND к."номер"=1
UNION ALL
SELECT 1, 'артилерійська', к."id" FROM "корпус" к JOIN "армія" а ON а."id"=к."армія_id" WHERE а."номер"=1 AND к."номер"=2
UNION ALL
SELECT 1, 'повітряно-десантна', к."id" FROM "корпус" к JOIN "армія" а ON а."id"=к."армія_id" WHERE а."номер"=3 AND к."номер"=1
ON CONFLICT ("корпус_id", "номер") DO NOTHING;

-- Військові частини
INSERT INTO "військова_частина" ("номер", "назва", "дивізія_id")
SELECT 'А1234', '15-та танкова бригада', д."id" 
FROM "дивізія" д JOIN "корпус" к ON к."id"=д."корпус_id" JOIN "армія" а ON а."id"=к."армія_id" 
WHERE а."номер"=1 AND к."номер"=1 AND д."номер"=1
UNION ALL
SELECT 'А5678', '23-тя механізована бригада', д."id"
FROM "дивізія" д JOIN "корпус" к ON к."id"=д."корпус_id" JOIN "армія" а ON а."id"=к."армія_id"
WHERE а."номер"=1 AND к."номер"=1 AND д."номер"=2
UNION ALL
SELECT 'А9999', '7-ма артилерійська бригада', д."id"
FROM "дивізія" д JOIN "корпус" к ON к."id"=д."корпус_id" JOIN "армія" а ON а."id"=к."армія_id"
WHERE а."номер"=1 AND к."номер"=2 AND д."номер"=1
ON CONFLICT ("дивізія_id", "номер") DO NOTHING;

-- Підрозділи
INSERT INTO "підрозділ" ("тип", "назва", "військова_частина_id")
SELECT 'батальйон', '1-й танковий батальйон', ч."id" FROM "військова_частина" ч WHERE ч."номер"='А1234'
UNION ALL
SELECT 'батальйон', '2-й танковий батальйон', ч."id" FROM "військова_частина" ч WHERE ч."номер"='А1234'
UNION ALL
SELECT 'рота', '1-ша розвідувальна рота', ч."id" FROM "військова_частина" ч WHERE ч."номер"='А1234'
UNION ALL
SELECT 'батальйон', '1-й механізований батальйон', ч."id" FROM "військова_частина" ч WHERE ч."номер"='А5678'
UNION ALL
SELECT 'дивізіон', '1-й артилерійський дивізіон', ч."id" FROM "військова_частина" ч WHERE ч."номер"='А9999';

-- Типи техніки
INSERT INTO "тип_техніки" ("назва") VALUES
	('Танки'),
	('БТР'),
	('БМП'),
	('Артилерія'),
	('Автомобілі'),
	('Інженерна техніка')
ON CONFLICT ("назва") DO NOTHING;

-- Типи озброєння
INSERT INTO "тип_озброєння" ("назва") VALUES
	('Стрілецька зброя'),
	('Гранатомети'),
	('ПЗРК'),
	('Міномети'),
	('Кулемети'),
	('Снайперські гвинтівки')
ON CONFLICT ("назва") DO NOTHING;

-- Приклади техніки
INSERT INTO "техніка" ("інвентарний_номер", "модель", "тип_техніки_id", "рік_випуску", "стан", "військова_частина_id")
SELECT 'Т001', 'Т-64БВ', тт."id", 2018, 'справна', ч."id"
FROM "тип_техніки" тт, "військова_частина" ч 
WHERE тт."назва"='Танки' AND ч."номер"='А1234'
UNION ALL
SELECT 'Т002', 'Т-72АМТ', тт."id", 2020, 'справна', ч."id"
FROM "тип_техніки" тт, "військова_частина" ч
WHERE тт."назва"='Танки' AND ч."номер"='А1234'
UNION ALL
SELECT 'Б001', 'БТР-4Е', тт."id", 2019, 'справна', ч."id"
FROM "тип_техніки" тт, "військова_частина" ч
WHERE тт."назва"='БТР' AND ч."номер"='А5678'
ON CONFLICT ("інвентарний_номер") DO NOTHING;

-- Приклади озброєння
INSERT INTO "озброєння" ("серійний_номер", "модель", "тип_озброєння_id", "стан", "військова_частина_id")
SELECT 'АК001', 'АК-74М', то."id", 'справне', ч."id"
FROM "тип_озброєння" то, "військова_частина" ч
WHERE то."назва"='Стрілецька зброя' AND ч."номер"='А1234'
UNION ALL
SELECT 'РПГ001', 'РПГ-7В', то."id", 'справне', ч."id"
FROM "тип_озброєння" то, "військова_частина" ч
WHERE то."назва"='Гранатомети' AND ч."номер"='А1234'
ON CONFLICT ("серійний_номер") DO NOTHING;

-- Приклади військовослужбовців
INSERT INTO "військовослужбовець" ("прізвище", "ім'я", "по_батькові", "звання", "посада", "дата_народження", "дата_прийняття", "підрозділ_id", "військова_частина_id")
SELECT 'Шевченко', 'Тарас', 'Григорович', 'майор', 'командир батальйону', '1985-03-09', '2020-01-15', п."id", ч."id"
FROM "підрозділ" п, "військова_частина" ч
WHERE п."назва"='1-й танковий батальйон' AND ч."номер"='А1234'
UNION ALL
SELECT 'Франко', 'Іван', 'Якович', 'капітан', 'заступник командира', '1990-07-22', '2021-06-10', п."id", ч."id"
FROM "підрозділ" п, "військова_частина" ч
WHERE п."назва"='1-й танковий батальйон' AND ч."номер"='А1234'
UNION ALL
SELECT 'Лесь', 'Українка', 'Петрівна', 'лейтенант', 'командир взводу', '1995-02-25', '2022-03-01', п."id", ч."id"
FROM "підрозділ" п, "військова_частина" ч
WHERE п."назва"='1-ша розвідувальна рота' AND ч."номер"='А1234';

-- Приклади споруд
INSERT INTO "споруда" ("назва", "тип", "адреса", "військова_частина_id")
SELECT 'Склад №1', 'склад', 'вул. Військова, 15', ч."id"
FROM "військова_частина" ч WHERE ч."номер"='А1234'
UNION ALL
SELECT 'Штаб бригади', 'штаб', 'вул. Центральна, 1', ч."id"
FROM "військова_частина" ч WHERE ч."номер"='А1234'
UNION ALL
SELECT 'Полігон для стрільб', 'полігон', 'Навчальний полігон №3', ч."id"
FROM "військова_частина" ч WHERE ч."номер"='А1234';

-- Завершено створення БД та наповнення початковими даними
