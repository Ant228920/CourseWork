-- =====================================================
-- DATABASE: MILITARY DISTRICT (Final Architecture)
-- =====================================================

-- 1. CLEANUP
DROP TABLE IF EXISTS artillery_attributes CASCADE;
DROP TABLE IF EXISTS vehicle_attributes CASCADE;
DROP TABLE IF EXISTS facility_subunits CASCADE;
DROP TABLE IF EXISTS facilities CASCADE;
DROP TABLE IF EXISTS requests CASCADE;
DROP TABLE IF EXISTS keys CASCADE;
DROP TABLE IF EXISTS personnel_specialties CASCADE;
DROP TABLE IF EXISTS generals_info CASCADE;
DROP TABLE IF EXISTS weapons CASCADE;
DROP TABLE IF EXISTS weapon_types CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS equipment_types CASCADE;
DROP TABLE IF EXISTS military_personnel CASCADE;
DROP TABLE IF EXISTS specialties CASCADE;
DROP TABLE IF EXISTS ranks CASCADE;
DROP TABLE IF EXISTS personnel_categories CASCADE;
DROP TABLE IF EXISTS squads CASCADE;
DROP TABLE IF EXISTS platoons CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS military_units CASCADE;
DROP TABLE IF EXISTS brigades CASCADE;
DROP TABLE IF EXISTS divisions CASCADE;
DROP TABLE IF EXISTS corps CASCADE;
DROP TABLE IF EXISTS armies CASCADE;
DROP TABLE IF EXISTS military_districts CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- =====================================================
-- 2. USER & SECURITY SYSTEM (Correct Architecture)
-- =====================================================

-- Roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (name) VALUES ('Guest'), ('Administrator'), ('Operator'), ('Authorized');

-- Users (Profile Info Only - NO PASSWORDS HERE)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    confirmed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Keys (Authentication Info)
CREATE TABLE keys (
    id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role_id INT NOT NULL REFERENCES roles(id) ON UPDATE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id)
);

-- Requests (Unified Registry)
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    login VARCHAR(100) NOT NULL,
    request_type VARCHAR(50) NOT NULL, -- 'password_reset', 'role_operator'
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- =====================================================
-- 3. MILITARY HIERARCHY
-- =====================================================

CREATE TABLE military_districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE
);

CREATE TABLE armies (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    military_district_id INT NOT NULL REFERENCES military_districts(id) ON DELETE CASCADE
);

CREATE TABLE corps (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    army_id INT NOT NULL REFERENCES armies(id) ON DELETE CASCADE
);

CREATE TABLE divisions (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    corps_id INT NOT NULL REFERENCES corps(id) ON DELETE CASCADE
);

CREATE TABLE brigades (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    corps_id INT NOT NULL REFERENCES corps(id) ON DELETE CASCADE
);

CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    region VARCHAR(100),
    coordinates VARCHAR(100)
);

CREATE TABLE military_units (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    division_id INT REFERENCES divisions(id) ON DELETE CASCADE,
    brigade_id INT REFERENCES brigades(id) ON DELETE CASCADE,
    location_id INT REFERENCES locations(id),
    commander_id INT, -- FK added later
    CONSTRAINT check_division_or_brigade CHECK (
        (division_id IS NOT NULL AND brigade_id IS NULL) OR
        (division_id IS NULL AND brigade_id IS NOT NULL)
    )
);

-- =====================================================
-- 4. SUBUNITS
-- =====================================================

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    commander_id INT
);

CREATE TABLE platoons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    company_id INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    commander_id INT
);

CREATE TABLE squads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platoon_id INT NOT NULL REFERENCES platoons(id) ON DELETE CASCADE,
    commander_id INT
);

-- =====================================================
-- 5. PERSONNEL
-- =====================================================

CREATE TABLE personnel_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO personnel_categories (name) VALUES ('Officer Staff'), ('Sergeant Staff'), ('Private Staff');

CREATE TABLE ranks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category_id INT NOT NULL REFERENCES personnel_categories(id),
    command_level INT DEFAULT 0
);

INSERT INTO ranks (name, category_id, command_level) VALUES
    ('General', 1, 4), ('Colonel', 1, 4), ('Lieutenant Colonel', 1, 3), ('Major', 1, 3), ('Captain', 1, 2), ('Lieutenant', 1, 2),
    ('Master Sergeant', 2, 1), ('Sergeant', 2, 1), ('Warrant Officer', 2, 1),
    ('Corporal', 3, 1), ('Private', 3, 0);

CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE
);

INSERT INTO specialties (name, code) VALUES
('Tank Operator', 'T-01'), ('Sniper', 'S-01'), ('Medic', 'M-01');

CREATE TABLE military_personnel (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    rank_id INT NOT NULL REFERENCES ranks(id),
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    enlistment_date DATE,
    birth_date DATE
);

CREATE TABLE generals_info (
    personnel_id INT PRIMARY KEY REFERENCES military_personnel(id) ON DELETE CASCADE,
    academy_graduation_date DATE,
    academy_name VARCHAR(255)
);

-- =====================================================
-- 6. EQUIPMENT & WEAPONS (With Attributes)
-- =====================================================

CREATE TABLE equipment_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100)
);

INSERT INTO equipment_types (name, category) VALUES
('T-64', 'Combat Vehicle'), ('KamAZ', 'Transport Vehicle');

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    equipment_type_id INT NOT NULL REFERENCES equipment_types(id),
    model VARCHAR(255),
    serial_number VARCHAR(100),
    year_manufactured INT,
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    condition VARCHAR(50)
);

CREATE TABLE vehicle_attributes (
    equipment_id INT PRIMARY KEY REFERENCES equipment(id) ON DELETE CASCADE,
    max_speed_kmh INT,
    armor_thickness_mm INT
);

CREATE TABLE weapon_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100)
);

INSERT INTO weapon_types (name, category) VALUES
('AK-74', 'Small Arms'), ('D-30', 'Artillery');

CREATE TABLE weapons (
    id SERIAL PRIMARY KEY,
    weapon_type_id INT NOT NULL REFERENCES weapon_types(id),
    model VARCHAR(255),
    serial_number VARCHAR(100),
    caliber VARCHAR(50),
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE
);

CREATE TABLE artillery_attributes (
    weapon_id INT PRIMARY KEY REFERENCES weapons(id) ON DELETE CASCADE,
    max_range_km DECIMAL(10,2)
);

-- =====================================================
-- 7. INFRASTRUCTURE
-- =====================================================

CREATE TABLE facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    address TEXT,
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    location_id INT REFERENCES locations(id)
);

CREATE TABLE facility_subunits (
    facility_id INT REFERENCES facilities(id) ON DELETE CASCADE,
    subunit_id INT NOT NULL,
    subunit_type VARCHAR(20) NOT NULL,
    PRIMARY KEY (facility_id, subunit_id, subunit_type)
);

-- =====================================================
-- 8. CONSTRAINTS & TRIGGERS
-- =====================================================

ALTER TABLE military_units ADD CONSTRAINT fk_unit_commander FOREIGN KEY (commander_id) REFERENCES military_personnel(id);
ALTER TABLE companies ADD CONSTRAINT fk_company_commander FOREIGN KEY (commander_id) REFERENCES military_personnel(id);
ALTER TABLE platoons ADD CONSTRAINT fk_platoon_commander FOREIGN KEY (commander_id) REFERENCES military_personnel(id);
ALTER TABLE squads ADD CONSTRAINT fk_squad_commander FOREIGN KEY (commander_id) REFERENCES military_personnel(id);

-- Trigger for commander rank
CREATE OR REPLACE FUNCTION check_commander_rank() RETURNS TRIGGER AS $$
DECLARE
    lvl INT;
    req INT;
BEGIN
    IF NEW.commander_id IS NULL THEN RETURN NEW; END IF;
    SELECT r.command_level INTO lvl FROM military_personnel p JOIN ranks r ON p.rank_id = r.id WHERE p.id = NEW.commander_id;

    IF TG_TABLE_NAME = 'squads' THEN req := 1;
    ELSIF TG_TABLE_NAME = 'platoons' THEN req := 1;
    ELSIF TG_TABLE_NAME = 'companies' THEN req := 2;
    ELSIF TG_TABLE_NAME = 'military_units' THEN req := 3;
    ELSE req := 0; END IF;

    IF lvl < req THEN RAISE EXCEPTION 'Insufficient rank for command'; END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER chk_squad_cmd BEFORE INSERT OR UPDATE ON squads FOR EACH ROW EXECUTE FUNCTION check_commander_rank();
CREATE TRIGGER chk_platoon_cmd BEFORE INSERT OR UPDATE ON platoons FOR EACH ROW EXECUTE FUNCTION check_commander_rank();
CREATE TRIGGER chk_company_cmd BEFORE INSERT OR UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION check_commander_rank();
CREATE TRIGGER chk_unit_cmd BEFORE INSERT OR UPDATE ON military_units FOR EACH ROW EXECUTE FUNCTION check_commander_rank();

-- =====================================================
-- 9. SEED ADMIN USER (Correct Way)
-- =====================================================

-- 1. Create profile in users (no password here!)
WITH new_admin AS (
    INSERT INTO users (email, confirmed)
    VALUES ('admin@military.gov.ua', TRUE)
    RETURNING id
)
-- 2. Create login info in keys
INSERT INTO keys (login, password, role_id, user_id)
SELECT
    'admin',
    '$pbkdf2-sha256$29000$ay0l5FxLCWGslRICYOw9Zw$6.2rvfsMII8pxzBc7YobXKcpcdn/7r42ql10Txyj/zo', -- Замініть на реальний хеш, якщо треба
    (SELECT id FROM roles WHERE name='Administrator'),
    id
FROM new_admin;