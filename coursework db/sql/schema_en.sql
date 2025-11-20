-- Military District Management System Schema
-- Encoding: UTF-8
-- All table and column names in Ukrainian (in quotes)

-- User management
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

-- Military hierarchy
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

CREATE TABLE IF NOT EXISTS "бригада" (
    "id" BIGSERIAL PRIMARY KEY,
    "номер" INTEGER NOT NULL,
    "тип" TEXT NOT NULL,
    "армія_id" BIGINT NOT NULL REFERENCES "армія"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE ("армія_id", "номер")
);

CREATE TABLE IF NOT EXISTS "військова_частина" (
    "id" BIGSERIAL PRIMARY KEY,
    "номер" TEXT NOT NULL,
    "назва" TEXT,
    "дивізія_id" BIGINT REFERENCES "дивізія"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    "бригада_id" BIGINT REFERENCES "бригада"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    "місце_дислокації_id" BIGINT REFERENCES "місце_дислокації"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT check_unit_belongs CHECK (
        ("дивізія_id" IS NOT NULL AND "бригада_id" IS NULL) OR 
        ("дивізія_id" IS NULL AND "бригада_id" IS NOT NULL)
    )
);

-- Detailed subunit hierarchy
CREATE TABLE IF NOT EXISTS "рота" (
    "id" BIGSERIAL PRIMARY KEY,
    "номер" INTEGER NOT NULL,
    "назва" TEXT,
    "військова_частина_id" BIGINT NOT NULL REFERENCES "військова_частина"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    "командир_id" BIGINT REFERENCES "військовослужбовець"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE ("військова_частина_id", "номер")
);

CREATE TABLE IF NOT EXISTS "взвод" (
    "id" BIGSERIAL PRIMARY KEY,
    "номер" INTEGER NOT NULL,
    "назва" TEXT,
    "рота_id" BIGINT NOT NULL REFERENCES "рота"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    "командир_id" BIGINT REFERENCES "військовослужбовець"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE ("рота_id", "номер")
);

CREATE TABLE IF NOT EXISTS "відділення" (
    "id" BIGSERIAL PRIMARY KEY,
    "номер" INTEGER NOT NULL,
    "назва" TEXT,
    "взвод_id" BIGINT NOT NULL REFERENCES "взвод"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    "командир_id" BIGINT REFERENCES "військовослужбовець"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE ("взвод_id", "номер")
);

-- Locations
CREATE TABLE IF NOT EXISTS "місце_дислокації" (
    "id" BIGSERIAL PRIMARY KEY,
    "назва" TEXT NOT NULL,
    "адреса" TEXT,
    "координати" TEXT,
    "тип" TEXT NOT NULL DEFAULT 'база'
);

-- Military ranks and specialties
CREATE TABLE IF NOT EXISTS "звання" (
    "id" BIGSERIAL PRIMARY KEY,
    "назва" TEXT NOT NULL UNIQUE,
    "категорія" TEXT NOT NULL CHECK ("категорія" IN ('офіцерський', 'сержантський', 'рядовий')),
    "порядок" INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "військова_спеціальність" (
    "id" BIGSERIAL PRIMARY KEY,
    "назва" TEXT NOT NULL UNIQUE,
    "код" TEXT NOT NULL UNIQUE,
    "опис" TEXT
);

-- Personnel
CREATE TABLE IF NOT EXISTS "військовослужбовець" (
    "id" BIGSERIAL PRIMARY KEY,
    "прізвище" TEXT NOT NULL,
    "ім'я" TEXT NOT NULL,
    "по_батькові" TEXT,
    "звання_id" BIGINT NOT NULL REFERENCES "звання"("id") ON UPDATE CASCADE,
    "посада" TEXT,
    "дата_народження" DATE,
    "дата_прийняття" DATE,
    "військова_спеціальність_id" BIGINT REFERENCES "військова_спеціальність"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    "відділення_id" BIGINT REFERENCES "відділення"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    "військова_частина_id" BIGINT NOT NULL REFERENCES "військова_частина"("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Specific attributes for different rank categories
CREATE TABLE IF NOT EXISTS "атрибути_офіцера" (
    "id" BIGSERIAL PRIMARY KEY,
    "військовослужбовець_id" BIGINT NOT NULL REFERENCES "військовослужбовець"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "дата_закінчення_академії" DATE,
    "дата_присвоєння_звання" DATE,
    "нагороди" TEXT,
    "стаж_служби" INTEGER,
    UNIQUE ("військовослужбовець_id")
);

CREATE TABLE IF NOT EXISTS "атрибути_сержанта" (
    "id" BIGSERIAL PRIMARY KEY,
    "військовослужбовець_id" BIGINT NOT NULL REFERENCES "військовослужбовець"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "дата_присвоєння_звання" DATE,
    "курси_підвищення_кваліфікації" TEXT,
    "стаж_у_званні" INTEGER,
    UNIQUE ("військовослужбовець_id")
);

CREATE TABLE IF NOT EXISTS "атрибути_рядового" (
    "id" BIGSERIAL PRIMARY KEY,
    "військовослужбовець_id" BIGINT NOT NULL REFERENCES "військовослужбовець"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "дата_призову" DATE,
    "термін_служби" INTEGER,
    "призовне_відділення" TEXT,
    UNIQUE ("військовослужбовець_id")
);

-- Equipment and weapons
CREATE TABLE IF NOT EXISTS "тип_техніки" (
    "id" BIGSERIAL PRIMARY KEY,
    "назва" TEXT NOT NULL UNIQUE,
    "категорія" TEXT NOT NULL CHECK ("категорія" IN ('бойова', 'транспортна', 'спеціальна'))
);

CREATE TABLE IF NOT EXISTS "техніка" (
    "id" BIGSERIAL PRIMARY KEY,
    "інвентарний_номер" TEXT NOT NULL UNIQUE,
    "модель" TEXT NOT NULL,
    "тип_техніки_id" BIGINT NOT NULL REFERENCES "тип_техніки"("id") ON UPDATE CASCADE,
    "рік_випуску" INTEGER CHECK ("рік_випуску" BETWEEN 1940 AND EXTRACT(YEAR FROM NOW())::INT),
    "стан" TEXT NOT NULL DEFAULT 'справна',
    "військова_частина_id" BIGINT REFERENCES "військова_частина"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    "відділення_id" BIGINT REFERENCES "відділення"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- Specific attributes for different equipment types
CREATE TABLE IF NOT EXISTS "атрибути_БМП" (
    "id" BIGSERIAL PRIMARY KEY,
    "техніка_id" BIGINT NOT NULL REFERENCES "техніка"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "броня" TEXT,
    "озброєння" TEXT,
    "екіпаж" INTEGER,
    "десант" INTEGER,
    UNIQUE ("техніка_id")
);

CREATE TABLE IF NOT EXISTS "атрибути_тягача" (
    "id" BIGSERIAL PRIMARY KEY,
    "техніка_id" BIGINT NOT NULL REFERENCES "техніка"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "вантажопідйомність" INTEGER,
    "тип_двигуна" TEXT,
    "пальне" TEXT,
    UNIQUE ("техніка_id")
);

CREATE TABLE IF NOT EXISTS "атрибути_автотранспорту" (
    "id" BIGSERIAL PRIMARY KEY,
    "техніка_id" BIGINT NOT NULL REFERENCES "техніка"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "вантажопідйомність" INTEGER,
    "тип_кузова" TEXT,
    "пальне" TEXT,
    UNIQUE ("техніка_id")
);

-- Weapons
CREATE TABLE IF NOT EXISTS "тип_озброєння" (
    "id" BIGSERIAL PRIMARY KEY,
    "назва" TEXT NOT NULL UNIQUE,
    "категорія" TEXT NOT NULL CHECK ("категорія" IN ('стрілецька', 'артилерійська', 'ракетна', 'спеціальна'))
);

CREATE TABLE IF NOT EXISTS "озброєння" (
    "id" BIGSERIAL PRIMARY KEY,
    "серійний_номер" TEXT NOT NULL UNIQUE,
    "модель" TEXT NOT NULL,
    "тип_озброєння_id" BIGINT NOT NULL REFERENCES "тип_озброєння"("id") ON UPDATE CASCADE,
    "стан" TEXT NOT NULL DEFAULT 'справне',
    "військова_частина_id" BIGINT REFERENCES "військова_частина"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    "відділення_id" BIGINT REFERENCES "відділення"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- Specific attributes for different weapon types
CREATE TABLE IF NOT EXISTS "атрибути_карабіна" (
    "id" BIGSERIAL PRIMARY KEY,
    "озброєння_id" BIGINT NOT NULL REFERENCES "озброєння"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "калібр" TEXT,
    "дальність_стрільби" INTEGER,
    "швидкострільність" INTEGER,
    UNIQUE ("озброєння_id")
);

CREATE TABLE IF NOT EXISTS "атрибути_автомата" (
    "id" BIGSERIAL PRIMARY KEY,
    "озброєння_id" BIGINT NOT NULL REFERENCES "озброєння"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "калібр" TEXT,
    "дальність_стрільби" INTEGER,
    "швидкострільність" INTEGER,
    "режими_стрільби" TEXT,
    UNIQUE ("озброєння_id")
);

CREATE TABLE IF NOT EXISTS "атрибути_артилерії" (
    "id" BIGSERIAL PRIMARY KEY,
    "озброєння_id" BIGINT NOT NULL REFERENCES "озброєння"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "калібр" TEXT,
    "дальність_стрільби" INTEGER,
    "тип_снаряду" TEXT,
    "екіпаж" INTEGER,
    UNIQUE ("озброєння_id")
);

CREATE TABLE IF NOT EXISTS "атрибути_ракетного_озброєння" (
    "id" BIGSERIAL PRIMARY KEY,
    "озброєння_id" BIGINT NOT NULL REFERENCES "озброєння"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "тип_ракети" TEXT,
    "дальність_ураження" INTEGER,
    "тип_цілі" TEXT,
    "екіпаж" INTEGER,
    UNIQUE ("озброєння_id")
);

-- Infrastructure
CREATE TABLE IF NOT EXISTS "споруда" (
    "id" BIGSERIAL PRIMARY KEY,
    "назва" TEXT NOT NULL,
    "тип" TEXT NOT NULL,
    "адреса" TEXT,
    "військова_частина_id" BIGINT REFERENCES "військова_частина"("id") ON DELETE SET NULL ON UPDATE CASCADE,
    "місце_дислокації_id" BIGINT REFERENCES "місце_дислокації"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- Access requests
CREATE TABLE IF NOT EXISTS "заявка_доступу" (
    "id" BIGSERIAL PRIMARY KEY,
    "користувач_id" BIGINT NOT NULL REFERENCES "користувач"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    "статус" TEXT NOT NULL DEFAULT 'новий',
    "дата_створення" TIMESTAMP NOT NULL DEFAULT NOW(),
    "коментар" TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_армія_округ ON "армія" ("військовий_округ_id");
CREATE INDEX IF NOT EXISTS idx_корпус_армія ON "корпус" ("армія_id");
CREATE INDEX IF NOT EXISTS idx_дивізія_корпус ON "дивізія" ("корпус_id");
CREATE INDEX IF NOT EXISTS idx_бригада_армія ON "бригада" ("армія_id");
CREATE INDEX IF NOT EXISTS idx_частина_дивізія ON "військова_частина" ("дивізія_id");
CREATE INDEX IF NOT EXISTS idx_частина_бригада ON "військова_частина" ("бригада_id");
CREATE INDEX IF NOT EXISTS idx_рота_частина ON "рота" ("військова_частина_id");
CREATE INDEX IF NOT EXISTS idx_взвод_рота ON "взвод" ("рота_id");
CREATE INDEX IF NOT EXISTS idx_відділення_взвод ON "відділення" ("взвод_id");
CREATE INDEX IF NOT EXISTS idx_військовослужбовець_відділення ON "військовослужбовець" ("відділення_id");
CREATE INDEX IF NOT EXISTS idx_військовослужбовець_частина ON "військовослужбовець" ("військова_частина_id");
CREATE INDEX IF NOT EXISTS idx_військовослужбовець_звання ON "військовослужбовець" ("звання_id");
CREATE INDEX IF NOT EXISTS idx_техніка_частина ON "техніка" ("військова_частина_id");
CREATE INDEX IF NOT EXISTS idx_озброєння_частина ON "озброєння" ("військова_частина_id");
CREATE INDEX IF NOT EXISTS idx_споруда_частина ON "споруда" ("військова_частина_id");
CREATE INDEX IF NOT EXISTS idx_місце_дислокації ON "місце_дислокації" ("назва");