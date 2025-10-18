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

\c military;

-- Access tables
CREATE TABLE IF NOT EXISTS roles (
	id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL UNIQUE,
	description TEXT
);

CREATE TABLE IF NOT EXISTS users (
	id BIGSERIAL PRIMARY KEY,
	login TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL,
	role_id BIGINT NOT NULL REFERENCES roles(id) ON UPDATE CASCADE,
	email TEXT,
	phone TEXT,
	confirmed BOOLEAN NOT NULL DEFAULT FALSE,
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Military hierarchy
CREATE TABLE IF NOT EXISTS military_districts (
	id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL UNIQUE,
	headquarters TEXT,
	commander TEXT
);

CREATE TABLE IF NOT EXISTS armies (
	id BIGSERIAL PRIMARY KEY,
	number INTEGER NOT NULL,
	name TEXT,
	military_district_id BIGINT NOT NULL REFERENCES military_districts(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	UNIQUE (military_district_id, number)
);

CREATE TABLE IF NOT EXISTS corps (
	id BIGSERIAL PRIMARY KEY,
	number INTEGER NOT NULL,
	army_id BIGINT NOT NULL REFERENCES armies(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	UNIQUE (army_id, number)
);

CREATE TABLE IF NOT EXISTS divisions (
	id BIGSERIAL PRIMARY KEY,
	number INTEGER NOT NULL,
	type TEXT NOT NULL,
	corps_id BIGINT NOT NULL REFERENCES corps(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	UNIQUE (corps_id, number)
);

CREATE TABLE IF NOT EXISTS military_units (
	id BIGSERIAL PRIMARY KEY,
	number TEXT NOT NULL,
	name TEXT,
	division_id BIGINT NOT NULL REFERENCES divisions(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	UNIQUE (division_id, number)
);

CREATE TABLE IF NOT EXISTS subunits (
	id BIGSERIAL PRIMARY KEY,
	type TEXT NOT NULL,
	name TEXT,
	military_unit_id BIGINT NOT NULL REFERENCES military_units(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Personnel
CREATE TABLE IF NOT EXISTS military_personnel (
	id BIGSERIAL PRIMARY KEY,
	last_name TEXT NOT NULL,
	first_name TEXT NOT NULL,
	middle_name TEXT,
	rank TEXT NOT NULL,
	position TEXT,
	birth_date DATE,
	enlistment_date DATE,
	subunit_id BIGINT NOT NULL REFERENCES subunits(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	military_unit_id BIGINT NOT NULL REFERENCES military_units(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Equipment
CREATE TABLE IF NOT EXISTS equipment_types (
	id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS equipment (
	id BIGSERIAL PRIMARY KEY,
	inventory_number TEXT NOT NULL UNIQUE,
	model TEXT NOT NULL,
	equipment_type_id BIGINT NOT NULL REFERENCES equipment_types(id) ON UPDATE CASCADE,
	year_manufactured INTEGER CHECK (year_manufactured BETWEEN 1940 AND EXTRACT(YEAR FROM NOW())::INT),
	condition TEXT NOT NULL DEFAULT 'operational',
	military_unit_id BIGINT REFERENCES military_units(id) ON DELETE SET NULL ON UPDATE CASCADE,
	subunit_id BIGINT REFERENCES subunits(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Weapons
CREATE TABLE IF NOT EXISTS weapon_types (
	id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS weapons (
	id BIGSERIAL PRIMARY KEY,
	serial_number TEXT NOT NULL UNIQUE,
	model TEXT NOT NULL,
	weapon_type_id BIGINT NOT NULL REFERENCES weapon_types(id) ON UPDATE CASCADE,
	condition TEXT NOT NULL DEFAULT 'operational',
	military_unit_id BIGINT REFERENCES military_units(id) ON DELETE SET NULL ON UPDATE CASCADE,
	subunit_id BIGINT REFERENCES subunits(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Facilities
CREATE TABLE IF NOT EXISTS facilities (
	id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	type TEXT NOT NULL,
	address TEXT,
	military_unit_id BIGINT REFERENCES military_units(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Access requests
CREATE TABLE IF NOT EXISTS access_requests (
	id BIGSERIAL PRIMARY KEY,
	user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
	status TEXT NOT NULL DEFAULT 'new',
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	comment TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_armies_district ON armies (military_district_id);
CREATE INDEX IF NOT EXISTS idx_corps_army ON corps (army_id);
CREATE INDEX IF NOT EXISTS idx_divisions_corps ON divisions (corps_id);
CREATE INDEX IF NOT EXISTS idx_units_division ON military_units (division_id);
CREATE INDEX IF NOT EXISTS idx_subunits_unit ON subunits (military_unit_id);
CREATE INDEX IF NOT EXISTS idx_personnel_subunit ON military_personnel (subunit_id);
CREATE INDEX IF NOT EXISTS idx_equipment_unit ON equipment (military_unit_id);
CREATE INDEX IF NOT EXISTS idx_weapons_unit ON weapons (military_unit_id);
