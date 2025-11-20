-- Military District Management System - Validation and Constraints
-- Additional constraints and validation rules

-- Add check constraints for data validation

-- Validate military ranks order
ALTER TABLE "звання" ADD CONSTRAINT check_rank_order CHECK ("порядок" > 0);

-- Validate birth date for military personnel
ALTER TABLE "військовослужбовець" ADD CONSTRAINT check_birth_date CHECK (
    "дата_народження" IS NULL OR "дата_народження" <= CURRENT_DATE
);

-- Validate enlistment date for military personnel
ALTER TABLE "військовослужбовець" ADD CONSTRAINT check_enlistment_date CHECK (
    "дата_прийняття" IS NULL OR "дата_прийняття" <= CURRENT_DATE
);

-- Validate birth date vs enlistment date
ALTER TABLE "військовослужбовець" ADD CONSTRAINT check_birth_vs_enlistment CHECK (
    "дата_народження" IS NULL OR "дата_прийняття" IS NULL OR 
    "дата_прийняття" >= "дата_народження" + INTERVAL '16 years'
);

-- Validate equipment year of manufacture
ALTER TABLE "техніка" ADD CONSTRAINT check_equipment_year CHECK (
    "рік_випуску" IS NULL OR "рік_випуску" BETWEEN 1940 AND EXTRACT(YEAR FROM NOW())::INT
);

-- Validate inventory numbers format
ALTER TABLE "техніка" ADD CONSTRAINT check_inventory_number_format CHECK (
    "інвентарний_номер" ~ '^[A-Z0-9]+$'
);

-- Validate serial numbers format
ALTER TABLE "озброєння" ADD CONSTRAINT check_serial_number_format CHECK (
    "серійний_номер" ~ '^[A-Z0-9]+$'
);

-- Validate military unit numbers format
ALTER TABLE "військова_частина" ADD CONSTRAINT check_unit_number_format CHECK (
    "номер" ~ '^[A-Z0-9]+$'
);

-- Validate email format for users
ALTER TABLE "користувач" ADD CONSTRAINT check_email_format CHECK (
    "email" IS NULL OR "email" ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

-- Validate phone format for users
ALTER TABLE "користувач" ADD CONSTRAINT check_phone_format CHECK (
    "телефон" IS NULL OR "телефон" ~ '^\+?[0-9\s\-\(\)]+$'
);

-- Validate coordinates format
ALTER TABLE "місце_дислокації" ADD CONSTRAINT check_coordinates_format CHECK (
    "координати" IS NULL OR "координати" ~ '^[0-9]+\.[0-9]+,\s*[0-9]+\.[0-9]+$'
);

-- Validate military specialty codes
ALTER TABLE "військова_спеціальність" ADD CONSTRAINT check_specialty_code CHECK (
    "код" ~ '^[0-9]{3}$'
);

-- Add triggers for automatic validation

-- Function to validate commander hierarchy
CREATE OR REPLACE FUNCTION validate_commander_hierarchy()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the person is assigned as commander
    IF NEW."посада" LIKE '%командир%' THEN
        -- Get the person's rank
        DECLARE
            person_rank_category TEXT;
            subunit_type TEXT;
        BEGIN
            SELECT з."категорія" INTO person_rank_category
            FROM "звання" з
            WHERE з."id" = NEW."звання_id";
            
            -- Check if officer can command this subunit
            IF person_rank_category = 'офіцерський' THEN
                -- Officers can command any subunit
                RETURN NEW;
            ELSIF person_rank_category IN ('сержантський', 'рядовий') THEN
                -- Sergeants and privates can only command platoons and squads
                IF NEW."відділення_id" IS NOT NULL THEN
                    -- Check if this is a squad commander
                    RETURN NEW;
                ELSIF NEW."посада" LIKE '%взвод%' THEN
                    -- Check if this is a platoon commander
                    RETURN NEW;
                ELSE
                    RAISE EXCEPTION 'Сержанти та рядові можуть командувати тільки взводами та відділеннями';
                END IF;
            END IF;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for commander hierarchy validation
CREATE TRIGGER trigger_validate_commander_hierarchy
    BEFORE INSERT OR UPDATE ON "військовослужбовець"
    FOR EACH ROW
    EXECUTE FUNCTION validate_commander_hierarchy();

-- Function to validate military unit assignment
CREATE OR REPLACE FUNCTION validate_unit_assignment()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if unit belongs to either division or brigade, but not both
    IF NEW."дивізія_id" IS NOT NULL AND NEW."бригада_id" IS NOT NULL THEN
        RAISE EXCEPTION 'Військова частина не може належати одночасно дивізії та бригаді';
    END IF;
    
    IF NEW."дивізія_id" IS NULL AND NEW."бригада_id" IS NULL THEN
        RAISE EXCEPTION 'Військова частина повинна належати або дивізії, або бригаді';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for unit assignment validation
CREATE TRIGGER trigger_validate_unit_assignment
    BEFORE INSERT OR UPDATE ON "військова_частина"
    FOR EACH ROW
    EXECUTE FUNCTION validate_unit_assignment();

-- Function to validate equipment assignment
CREATE OR REPLACE FUNCTION validate_equipment_assignment()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if equipment is assigned to both unit and subunit
    IF NEW."військова_частина_id" IS NOT NULL AND NEW."відділення_id" IS NOT NULL THEN
        -- Verify that the subunit belongs to the unit
        DECLARE
            subunit_unit_id BIGINT;
        BEGIN
            SELECT в."військова_частина_id" INTO subunit_unit_id
            FROM "відділення" від
            JOIN "взвод" в ON в."id" = від."взвод_id"
            JOIN "рота" р ON р."id" = в."рота_id"
            WHERE від."id" = NEW."відділення_id";
            
            IF subunit_unit_id != NEW."військова_частина_id" THEN
                RAISE EXCEPTION 'Відділення не належить до вказаної військової частини';
            END IF;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for equipment assignment validation
CREATE TRIGGER trigger_validate_equipment_assignment
    BEFORE INSERT OR UPDATE ON "техніка"
    FOR EACH ROW
    EXECUTE FUNCTION validate_equipment_assignment();

-- Create trigger for weapon assignment validation
CREATE TRIGGER trigger_validate_weapon_assignment
    BEFORE INSERT OR UPDATE ON "озброєння"
    FOR EACH ROW
    EXECUTE FUNCTION validate_equipment_assignment();

-- Function to validate personnel assignment
CREATE OR REPLACE FUNCTION validate_personnel_assignment()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if personnel is assigned to both unit and subunit
    IF NEW."військова_частина_id" IS NOT NULL AND NEW."відділення_id" IS NOT NULL THEN
        -- Verify that the subunit belongs to the unit
        DECLARE
            subunit_unit_id BIGINT;
        BEGIN
            SELECT в."військова_частина_id" INTO subunit_unit_id
            FROM "відділення" від
            JOIN "взвод" в ON в."id" = від."взвод_id"
            JOIN "рота" р ON р."id" = в."рота_id"
            WHERE від."id" = NEW."відділення_id";
            
            IF subunit_unit_id != NEW."військова_частина_id" THEN
                RAISE EXCEPTION 'Відділення не належить до вказаної військової частини';
            END IF;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for personnel assignment validation
CREATE TRIGGER trigger_validate_personnel_assignment
    BEFORE INSERT OR UPDATE ON "військовослужбовець"
    FOR EACH ROW
    EXECUTE FUNCTION validate_personnel_assignment();

-- Function to automatically update commander assignments
CREATE OR REPLACE FUNCTION update_commander_assignment()
RETURNS TRIGGER AS $$
BEGIN
    -- If this person is assigned as a commander, update the corresponding subunit
    IF NEW."посада" LIKE '%командир%' THEN
        IF NEW."посада" LIKE '%рота%' THEN
            -- Update company commander
            UPDATE "рота" SET "командир_id" = NEW."id" 
            WHERE "військова_частина_id" = NEW."військова_частина_id" 
            AND "номер" = 1; -- Assuming first company
        ELSIF NEW."посада" LIKE '%взвод%' THEN
            -- Update platoon commander
            UPDATE "взвод" SET "командир_id" = NEW."id" 
            WHERE "рота_id" IN (
                SELECT "id" FROM "рота" WHERE "військова_частина_id" = NEW."військова_частина_id"
            ) AND "номер" = 1; -- Assuming first platoon
        ELSIF NEW."посада" LIKE '%відділення%' THEN
            -- Update squad commander
            UPDATE "відділення" SET "командир_id" = NEW."id" 
            WHERE "взвод_id" IN (
                SELECT "id" FROM "взвод" 
                JOIN "рота" ON "рота"."id" = "взвод"."рота_id"
                WHERE "рота"."військова_частина_id" = NEW."військова_частина_id"
            ) AND "номер" = 1; -- Assuming first squad
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic commander assignment
CREATE TRIGGER trigger_update_commander_assignment
    AFTER INSERT OR UPDATE ON "військовослужбовець"
    FOR EACH ROW
    EXECUTE FUNCTION update_commander_assignment();

-- Function to validate rank progression
CREATE OR REPLACE FUNCTION validate_rank_progression()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the new rank is higher than the previous one
    IF OLD."звання_id" IS NOT NULL AND NEW."звання_id" != OLD."звання_id" THEN
        DECLARE
            old_rank_order INTEGER;
            new_rank_order INTEGER;
        BEGIN
            SELECT "порядок" INTO old_rank_order FROM "звання" WHERE "id" = OLD."звання_id";
            SELECT "порядок" INTO new_rank_order FROM "звання" WHERE "id" = NEW."звання_id";
            
            -- Lower number means higher rank
            IF new_rank_order > old_rank_order THEN
                RAISE EXCEPTION 'Не можна понизити звання без спеціального дозволу';
            END IF;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for rank progression validation
CREATE TRIGGER trigger_validate_rank_progression
    BEFORE UPDATE ON "військовослужбовець"
    FOR EACH ROW
    EXECUTE FUNCTION validate_rank_progression();

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_військовослужбовець_звання_категорія ON "військовослужбовець" ("звання_id");
CREATE INDEX IF NOT EXISTS idx_військовослужбовець_спеціальність ON "військовослужбовець" ("військова_спеціальність_id");
CREATE INDEX IF NOT EXISTS idx_техніка_тип_категорія ON "техніка" ("тип_техніки_id");
CREATE INDEX IF NOT EXISTS idx_озброєння_тип_категорія ON "озброєння" ("тип_озброєння_id");
CREATE INDEX IF NOT EXISTS idx_звання_категорія ON "звання" ("категорія");
CREATE INDEX IF NOT EXISTS idx_звання_порядок ON "звання" ("порядок");

-- Add full-text search indexes
CREATE INDEX IF NOT EXISTS idx_військовослужбовець_пошук ON "військовослужбовець" 
USING gin(to_tsvector('ukrainian', "прізвище" || ' ' || "ім'я" || ' ' || COALESCE("по_батькові", '')));

CREATE INDEX IF NOT EXISTS idx_військова_частина_пошук ON "військова_частина" 
USING gin(to_tsvector('ukrainian', "номер" || ' ' || COALESCE("назва", '')));

-- Add comments for documentation
COMMENT ON TABLE "військовий_округ" IS 'Військові округи - найвищий рівень військової організації';
COMMENT ON TABLE "армія" IS 'Армії - об''єднання корпусів та бригад';
COMMENT ON TABLE "корпус" IS 'Корпуси - об''єднання дивізій';
COMMENT ON TABLE "дивізія" IS 'Дивізії - основні тактичні з''єднання';
COMMENT ON TABLE "бригада" IS 'Бригади - окремі військові з''єднання';
COMMENT ON TABLE "військова_частина" IS 'Військові частини - основні адміністративні одиниці';
COMMENT ON TABLE "рота" IS 'Роти - підрозділи військових частин';
COMMENT ON TABLE "взвод" IS 'Взводи - підрозділи рот';
COMMENT ON TABLE "відділення" IS 'Відділення - найменші підрозділи';
COMMENT ON TABLE "військовослужбовець" IS 'Особовий склад військових частин';
COMMENT ON TABLE "звання" IS 'Військові звання з категоріями та порядком';
COMMENT ON TABLE "військова_спеціальність" IS 'Військові спеціальності з кодами';
COMMENT ON TABLE "місце_дислокації" IS 'Місця дислокації військових частин';
COMMENT ON TABLE "техніка" IS 'Військова техніка з інвентарними номерами';
COMMENT ON TABLE "озброєння" IS 'Військове озброєння з серійними номерами';
COMMENT ON TABLE "споруда" IS 'Споруди військових частин';
