-- =====================================================
-- DATABASE: MILITARY DISTRICT
-- =====================================================

-- Drop tables in reverse order (if exist)
DROP TABLE IF EXISTS access_requests CASCADE;
DROP TABLE IF EXISTS personnel_specialties CASCADE;
DROP TABLE IF EXISTS generals_info CASCADE;
DROP TABLE IF EXISTS facility_subunits CASCADE;
DROP TABLE IF EXISTS facilities CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
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
DROP TABLE IF EXISTS divisions CASCADE;
DROP TABLE IF EXISTS corps CASCADE;
DROP TABLE IF EXISTS armies CASCADE;
DROP TABLE IF EXISTS military_districts CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- =====================================================
-- 1. USER SYSTEM
-- =====================================================

-- User roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (name) VALUES
    ('Guest'),
    ('Administrator'),
    ('Operator'),
    ('Authorized');

-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email VARCHAR(255),
    role_id INT NOT NULL REFERENCES roles(id),
    confirmed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Access requests
CREATE TABLE access_requests (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    comment TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. MILITARY UNIT HIERARCHY
-- =====================================================

-- Military districts
CREATE TABLE military_districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE
);

-- Armies
CREATE TABLE armies (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    military_district_id INT NOT NULL REFERENCES military_districts(id) ON DELETE CASCADE
);

-- Corps
CREATE TABLE corps (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    army_id INT NOT NULL REFERENCES armies(id) ON DELETE CASCADE
);

-- Divisions
CREATE TABLE divisions (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    corps_id INT NOT NULL REFERENCES corps(id) ON DELETE CASCADE
);

-- Deployment locations
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    region VARCHAR(100),
    coordinates VARCHAR(100)
);

-- Military units
CREATE TABLE military_units (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    division_id INT NOT NULL REFERENCES divisions(id) ON DELETE CASCADE,
    location_id INT REFERENCES locations(id),
    commander_id INT -- will be filled after military_personnel creation
);

-- =====================================================
-- 3. INTERNAL UNIT STRUCTURE
-- =====================================================

-- Companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    commander_id INT
);

-- Platoons
CREATE TABLE platoons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    company_id INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    commander_id INT
);

-- Squads
CREATE TABLE squads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platoon_id INT NOT NULL REFERENCES platoons(id) ON DELETE CASCADE,
    commander_id INT
);

-- =====================================================
-- 4. MILITARY PERSONNEL
-- =====================================================

-- Personnel categories
CREATE TABLE personnel_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO personnel_categories (name) VALUES
    ('Officer Staff'),
    ('Sergeant Staff'),
    ('Private Staff');

-- Ranks
CREATE TABLE ranks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category_id INT NOT NULL REFERENCES personnel_categories(id)
);

INSERT INTO ranks (name, category_id) VALUES
    -- Officers
    ('General', 1),
    ('Colonel', 1),
    ('Lieutenant Colonel', 1),
    ('Major', 1),
    ('Captain', 1),
    ('Lieutenant', 1),
    -- Sergeants
    ('Master Sergeant', 2),
    ('Sergeant', 2),
    ('Warrant Officer', 2),
    -- Privates
    ('Corporal', 3),
    ('Private', 3);

-- Military specialties
CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE
);

-- Military personnel
CREATE TABLE military_personnel (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    rank_id INT NOT NULL REFERENCES ranks(id),
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    subunit_id INT, -- Subunit ID (company/platoon/squad)
    subunit_type VARCHAR(20), -- 'company', 'platoon', 'squad'
    enlistment_date DATE,
    birth_date DATE,
    CHECK (subunit_type IN ('company', 'platoon', 'squad', NULL))
);

-- Additional data for generals
CREATE TABLE generals_info (
    personnel_id INT PRIMARY KEY REFERENCES military_personnel(id) ON DELETE CASCADE,
    academy_graduation_date DATE,
    general_rank_date DATE,
    academy_name VARCHAR(255)
);

-- Personnel to specialties relationship (many-to-many)
CREATE TABLE personnel_specialties (
    personnel_id INT REFERENCES military_personnel(id) ON DELETE CASCADE,
    specialty_id INT REFERENCES specialties(id) ON DELETE CASCADE,
    PRIMARY KEY (personnel_id, specialty_id)
);

-- =====================================================
-- 5. EQUIPMENT AND WEAPONS
-- =====================================================

-- Equipment types
CREATE TABLE equipment_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100) -- "Combat Vehicle", "Transport Vehicle"
);

-- Equipment
CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    equipment_type_id INT NOT NULL REFERENCES equipment_types(id),
    model VARCHAR(255),
    serial_number VARCHAR(100),
    year_manufactured INT,
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    condition VARCHAR(50)
);

-- Weapon types
CREATE TABLE weapon_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100)
);

-- Weapons
CREATE TABLE weapons (
    id SERIAL PRIMARY KEY,
    weapon_type_id INT NOT NULL REFERENCES weapon_types(id),
    model VARCHAR(255),
    serial_number VARCHAR(100),
    caliber VARCHAR(50),
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    subunit_id INT, -- may belong to a subunit
    subunit_type VARCHAR(20),
    CHECK (subunit_type IN ('company', 'platoon', 'squad', NULL))
);

-- =====================================================
-- 6. INFRASTRUCTURE
-- =====================================================

-- Facilities
CREATE TABLE facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100), -- "Barracks", "Warehouse", "Headquarters", "Garage"
    address TEXT,
    military_unit_id INT NOT NULL REFERENCES military_units(id) ON DELETE CASCADE,
    location_id INT REFERENCES locations(id)
);

-- Facility to subunits relationship (where they are deployed)
CREATE TABLE facility_subunits (
    facility_id INT REFERENCES facilities(id) ON DELETE CASCADE,
    subunit_id INT NOT NULL,
    subunit_type VARCHAR(20) NOT NULL, -- 'company', 'platoon', 'squad'
    PRIMARY KEY (facility_id, subunit_id, subunit_type),
    CHECK (subunit_type IN ('company', 'platoon', 'squad'))
);

-- =====================================================
-- 7. ADDING FOREIGN KEYS FOR COMMANDERS
-- =====================================================

ALTER TABLE military_units
    ADD CONSTRAINT fk_military_units_commander
    FOREIGN KEY (commander_id) REFERENCES military_personnel(id);

ALTER TABLE companies
    ADD CONSTRAINT fk_companies_commander
    FOREIGN KEY (commander_id) REFERENCES military_personnel(id);

ALTER TABLE platoons
    ADD CONSTRAINT fk_platoons_commander
    FOREIGN KEY (commander_id) REFERENCES military_personnel(id);

ALTER TABLE squads
    ADD CONSTRAINT fk_squads_commander
    FOREIGN KEY (commander_id) REFERENCES military_personnel(id);

-- =====================================================
-- 8. INDEXES FOR QUERY OPTIMIZATION
-- =====================================================

CREATE INDEX idx_military_personnel_rank ON military_personnel(rank_id);
CREATE INDEX idx_military_personnel_unit ON military_personnel(military_unit_id);
CREATE INDEX idx_equipment_unit ON equipment(military_unit_id);
CREATE INDEX idx_weapons_unit ON weapons(military_unit_id);
CREATE INDEX idx_facilities_unit ON facilities(military_unit_id);
CREATE INDEX idx_armies_district ON armies(military_district_id);
CREATE INDEX idx_corps_army ON corps(army_id);
CREATE INDEX idx_divisions_corps ON divisions(corps_id);
CREATE INDEX idx_military_units_division ON military_units(division_id);

-- =====================================================
-- 9. SAMPLE DATA
-- =====================================================

-- Military district
INSERT INTO military_districts (name, code) VALUES
    ('Eastern Military District', 'EAST-01');

-- Army
INSERT INTO armies (number, name, military_district_id) VALUES
    ('5th', '5th Combined Arms Army', 1);

-- Corps
INSERT INTO corps (number, name, army_id) VALUES
    ('1st', '1st Army Corps', 1);

-- Division
INSERT INTO divisions (number, name, corps_id) VALUES
    ('10th', '10th Mechanized Division', 1);

-- Deployment location
INSERT INTO locations (name, address, region) VALUES
    ('Kyiv City', '1 Khreshchatyk Street', 'Kyiv Region');

-- Military unit
INSERT INTO military_units (number, name, division_id, location_id) VALUES
    ('A1234', '15th Separate Mechanized Brigade', 1, 1);

-- Specialties
INSERT INTO specialties (name, code) VALUES
    ('Tank Operator', 'TANK-01'),
    ('Sniper', 'SNIP-01'),
    ('Communications Specialist', 'COMM-01');

-- Equipment types
INSERT INTO equipment_types (name, category) VALUES
    ('BMP-2', 'Combat Vehicle'),
    ('T-64', 'Combat Vehicle'),
    ('KamAZ', 'Transport Vehicle');

-- Weapon types
INSERT INTO weapon_types (name, category) VALUES
    ('AK-74', 'Automatic Weapon'),
    ('SVD', 'Sniper Rifle'),
    ('RPG-7', 'Anti-Tank Weapon');

-- =====================================================
-- END OF SCRIPT
-- =====================================================

COMMENT ON DATABASE postgres IS 'Military District Database';