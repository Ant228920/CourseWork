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
-- 2. USER & SECURITY SYSTEM
-- =====================================================

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (name) VALUES ('Guest'), ('Administrator'), ('Operator'), ('Authorized');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    confirmed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE keys (
    id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role_id INT NOT NULL REFERENCES roles(id) ON UPDATE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id)
);

CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    login VARCHAR(100) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
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
    commander_id INT,
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
    ('General', 1, 4), ('Colonel', 1, 4), ('Lieutenant Colonel', 1, 3), ('Major', 1, 3),
    ('Captain', 1, 2), ('Lieutenant', 1, 2),
    ('Master Sergeant', 2, 1), ('Sergeant', 2, 1), ('Warrant Officer', 2, 1),
    ('Corporal', 3, 1), ('Private', 3, 0);

CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE
);

INSERT INTO specialties (name, code) VALUES
('Tank Operator', 'T-01'), ('Sniper', 'S-01'), ('Medic', 'M-01'), ('Engineer', 'E-01');

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

CREATE TABLE personnel_specialties (
    personnel_id INT REFERENCES military_personnel(id) ON DELETE CASCADE,
    specialty_id INT REFERENCES specialties(id) ON DELETE CASCADE,
    PRIMARY KEY (personnel_id, specialty_id)
);

-- =====================================================
-- 6. EQUIPMENT & WEAPONS
-- =====================================================

CREATE TABLE equipment_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100)
);

INSERT INTO equipment_types (name, category) VALUES
('T-64', 'Combat Vehicle'), ('KamAZ', 'Transport Vehicle'), ('BMP-2', 'Combat Vehicle');

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
('AK-74', 'Small Arms'), ('D-30', 'Artillery'), ('RPG-7', 'Anti-Tank');

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

-- Trigger for commander rank validation
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
-- 9. SEED DATA (Test Data)
-- =====================================================

-- 9.1 Users
WITH new_admin AS (
    INSERT INTO users (email, confirmed) VALUES ('admin@mil.gov', TRUE) RETURNING id
), new_oper AS (
    INSERT INTO users (email, confirmed) VALUES ('oper@mil.gov', TRUE) RETURNING id
), new_auth AS (
    INSERT INTO users (email, confirmed) VALUES ('auth@mil.gov', TRUE) RETURNING id
)
INSERT INTO keys (login, password, role_id, user_id)
SELECT 'admin', '$pbkdf2-sha256$29000$ay0l5FxLCWGslRICYOw9Zw$6.2rvfsMII8pxzBc7YobXKcpcdn/7r42ql10Txyj/zo', (SELECT id FROM roles WHERE name='Administrator'), id FROM new_admin
UNION ALL
SELECT 'operator', '$pbkdf2-sha256$29000$ay0l5FxLCWGslRICYOw9Zw$6.2rvfsMII8pxzBc7YobXKcpcdn/7r42ql10Txyj/zo', (SELECT id FROM roles WHERE name='Operator'), id FROM new_oper
UNION ALL
SELECT 'user', '$pbkdf2-sha256$29000$ay0l5FxLCWGslRICYOw9Zw$6.2rvfsMII8pxzBc7YobXKcpcdn/7r42ql10Txyj/zo', (SELECT id FROM roles WHERE name='Authorized'), id FROM new_auth;

-- 9.2 Locations
INSERT INTO locations (name, address, region, coordinates) VALUES
('Штаб Округу', 'м. Київ, вул. Повітрофлотська, 1', 'Київська обл.', '50.45, 30.52'),
('Полігон "Десна"', 'смт. Десна', 'Чернігівська обл.', '50.92, 30.75'),
('Військове містечко Яворів', 'м. Яворів', 'Львівська обл.', '49.94, 23.38');

-- 9.3 Hierarchy
INSERT INTO military_districts (name, code) VALUES ('Північний ОК', 'N-01');

INSERT INTO armies (number, name, military_district_id) VALUES ('1', '1-ша Танкова Армія', 1);
INSERT INTO corps (number, name, army_id) VALUES ('8', '8-й Армійський Корпус', 1);

INSERT INTO divisions (number, name, corps_id) VALUES ('72', '72-га Механізована Дивізія', 1);
INSERT INTO brigades (number, name, corps_id) VALUES ('93', '93-тя ОМБр', 1);

-- 9.4 Units (Without commanders initially)
INSERT INTO military_units (number, name, division_id, location_id) VALUES
('A2167', '1-й Механізований Батальйон', 1, 2); -- In Division 72

INSERT INTO military_units (number, name, brigade_id, location_id) VALUES
('A1302', 'Танковий Батальйон', 1, 3); -- In Brigade 93

-- 9.5 Personnel
INSERT INTO military_personnel (last_name, first_name, rank_id, military_unit_id, enlistment_date, birth_date) VALUES
('Коваленко', 'Іван', (SELECT id FROM ranks WHERE name='Colonel'), 1, '2010-05-20', '1980-01-15'), -- Cmdr Unit 1
('Петренко', 'Петро', (SELECT id FROM ranks WHERE name='Lieutenant Colonel'), 2, '2012-08-10', '1985-03-20'), -- Cmdr Unit 2
('Сидоренко', 'Олег', (SELECT id FROM ranks WHERE name='Captain'), 1, '2015-01-15', '1990-07-12'), -- Cmdr Company
('Бойко', 'Андрій', (SELECT id FROM ranks WHERE name='Lieutenant'), 1, '2018-03-01', '1995-11-30'), -- Cmdr Platoon
('Гончар', 'Микола', (SELECT id FROM ranks WHERE name='Sergeant'), 1, '2019-05-05', '1998-02-14'); -- Cmdr Squad

-- 9.6 Assign Unit Commanders
UPDATE military_units SET commander_id = 1 WHERE id = 1;
UPDATE military_units SET commander_id = 2 WHERE id = 2;

-- 9.7 Subunits
INSERT INTO companies (name, military_unit_id, commander_id) VALUES ('1-ша Рота', 1, 3);
INSERT INTO platoons (name, company_id, commander_id) VALUES ('1-й Взвод', 1, 4);
INSERT INTO squads (name, platoon_id, commander_id) VALUES ('1-ше Відділення', 1, 5);

-- 9.8 Equipment & Weapons
INSERT INTO equipment (equipment_type_id, model, serial_number, year_manufactured, military_unit_id, condition) VALUES
((SELECT id FROM equipment_types WHERE name='T-64'), 'Т-64БВ', 'TNK001', 1985, 2, 'справна'),
((SELECT id FROM equipment_types WHERE name='KamAZ'), 'КамАЗ-4310', 'TRK111', 2005, 1, 'справна');

INSERT INTO weapons (weapon_type_id, model, serial_number, caliber, military_unit_id) VALUES
((SELECT id FROM weapon_types WHERE name='AK-74'), 'АК-74М', 'AK12345', '5.45', 1),
((SELECT id FROM weapon_types WHERE name='D-30'), 'Д-30', 'ART555', '122mm', 1);

-- 9.9 Infrastructure
INSERT INTO facilities (name, type, address, military_unit_id, location_id) VALUES
('Казарма №1', 'Barracks', 'вул. Полкова, 5', 1, 2);

INSERT INTO facility_subunits (facility_id, subunit_id, subunit_type) VALUES (1, 1, 'platoon'); -- 1st platoon in Barracks 1