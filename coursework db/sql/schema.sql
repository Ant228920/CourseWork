-- Encoding: UTF-8
-- Примітка: всі назви таблиць і колонок у лапках з кирилицею

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

-- Споруди (склади, полігони, штаби)
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
