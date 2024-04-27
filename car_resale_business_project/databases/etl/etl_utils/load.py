import time
import psycopg2 as pg2

def insert_data(conn, query, data, table_name):
    if len(data) == 0:
        print(f"No data to insert into table {table_name}!")
        return
    try:
        with conn.cursor() as cur:
            if isinstance(data, list):
                cur.executemany(query, data)
            else:
                cur.execute(query, data)
                
            conn.commit()
            # print(f"Data successfully inserted into table '{table_name}'!")
            
    except (Exception, pg2.DatabaseError) as error:
        print(f"Error inserting data into table '{table_name}':", error)
        conn.rollback()


def load_seller_dim(conn, seller_dims, initial_data_loading):
    if initial_data_loading:
        # SQL query
        query = """
            INSERT INTO dim_seller(name, type, seller_oltp_id)
            VALUES (%s, %s, %s);
        """
        data = [
            (
                seller_dim.name,
                seller_dim.type,
                seller_dim.oltp_id
            )
            for seller_dim in seller_dims
        ]
    else:
        query = """
            DO
            $$
            DECLARE
                oltp_id_exists BOOLEAN;
            BEGIN
                -- Check if the record with the specified oltp_id exists
                SELECT TRUE INTO oltp_id_exists FROM dim_seller WHERE seller_oltp_id = %s;
                
                -- If the record exists, perform the update operation
                IF oltp_id_exists THEN
                    UPDATE dim_seller
                    SET name = %s,
                        type = %s
                    WHERE seller_oltp_id = %s;
                ELSE
                    -- Otherwise, perform the insert operation
                    INSERT INTO dim_seller (name, type, seller_oltp_id)
                    VALUES (%s, %s, %s);	
                END IF;
            END
            $$;
        """
        data = [
            (
                seller_dim.oltp_id,

                seller_dim.name,
                seller_dim.type,
                seller_dim.oltp_id,

                seller_dim.name,
                seller_dim.type,
                seller_dim.oltp_id,
            )
            for seller_dim in seller_dims
        ]
        
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'dim_seller')


def load_buyer_dim(conn, buyer_dims, initial_data_loading):
    if initial_data_loading == False:
        query = """
            DO
            $$
            DECLARE
                oltp_id_exists BOOLEAN;
            BEGIN
                -- Check if the record with the specified oltp_id exists
                SELECT TRUE INTO oltp_id_exists FROM dim_buyer WHERE buyer_oltp_id = %s;
                
                -- If the record exists, perform the update operation
                IF oltp_id_exists THEN
                    UPDATE dim_buyer
                    SET 
                        first_name = %s, 
                        age = %s, 
                        age_group = %s, 
                        sex = %s
                    WHERE buyer_oltp_id = %s;
                END IF;
            END
            $$;
        """
        data = [
            (
                buyer_dim.oltp_id,

                buyer_dim.first_name,
                buyer_dim.age,
                buyer_dim.age_group,
                buyer_dim.sex,
                buyer_dim.oltp_id
            )
            for buyer_dim in buyer_dims
        ]
        
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'dim_buyer')


def load_car_dim(conn, car_dims, initial_data_loading):
    if initial_data_loading == False:
        query = """
            DO
            $$
            DECLARE
                oltp_id_exists BOOLEAN;
            BEGIN
                -- Check if the record with the specified oltp_id exists
                SELECT TRUE INTO oltp_id_exists FROM dim_car WHERE vin = %s;
                
                -- If the record exists, perform the update operation
                IF oltp_id_exists THEN
                    UPDATE dim_car
                    SET 
                        manufacture_year = %s,
                        make = %s,
                        model = %s,
                        trim = %s,
                        body = %s,
                        transmission = %s,
                        color = %s
                    WHERE vin = %s;
                ELSE
                    -- Otherwise, perform the insert operation
                    INSERT INTO dim_car(vin, manufacture_year, make, model, trim, body, transmission, color)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s);
                END IF;
            END
            $$;
        """
        data = [
            (
                car_dim.vin,

                car_dim.manufacture_year,
                car_dim.make,
                car_dim.model,
                car_dim.trim,
                car_dim.body_type,
                car_dim.transmission,
                car_dim.color,
                car_dim.vin,

                car_dim.vin,
                car_dim.manufacture_year,
                car_dim.make,
                car_dim.model,
                car_dim.trim,
                car_dim.body_type,
                car_dim.transmission,
                car_dim.color
            )
            for car_dim in car_dims
        ]
        
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'dim_car')


def load_location_dim(conn, location_dims):
    # Since dim_location is a slowly changing dimension, its update will be identical to a regular insert (updating the is_valid field will execute a trigger in the OLAP database)
    # SQL query
    query = """
        INSERT INTO dim_location(country, city, address_oltp_id)
        VALUES (%s, %s, %s);
    """
    data = [
        (
            location_dim.country,
            location_dim.city,
            location_dim.oltp_id
        )
        for location_dim in location_dims
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'dim_location')


def load_car_repair_type_dim(conn, repair_types, initial_data_loading):
    query = """
        INSERT INTO dim_car_repair_type(repair_type)
        VALUES (%s);
    """
    data = [
        (
            repair_type_dim.repair_type,
        )
        for repair_type_dim in repair_types
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'dim_car_repair_type')


def load_fact_car_purchase(conn, car_purchases, insert_new_employee, initial_data_loading):
    if initial_data_loading:
        if insert_new_employee:
            query = """
                WITH insert_dim_car AS (
                    INSERT INTO dim_car(vin, manufacture_year, make, model, trim, body, transmission, color)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING vin
                ), insert_dim_employee AS (
                    INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING employee_id
                ), insert_dim_date AS (
                    INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING date_id
                )

                INSERT INTO fact_car_purchase(
                    car_vin, seller_id, employee_id, location_id, date_id,
                    price, car_years, odometer, condition, employee_experience
                )
                VALUES
                    (
                        (SELECT vin FROM insert_dim_car),
                        (SELECT seller_id FROM dim_seller WHERE seller_oltp_id=%s),
                        (SELECT employee_id FROM insert_dim_employee),
                        (SELECT location_id FROM dim_location WHERE address_oltp_id=%s AND is_valid = 1),
                        (SELECT date_id FROM insert_dim_date),
                        %s, %s, %s, %s, %s
                    );
            """
            data = [
                (
                    car_purchase.car_dim.vin,
                    car_purchase.car_dim.manufacture_year,
                    car_purchase.car_dim.make,
                    car_purchase.car_dim.model,
                    car_purchase.car_dim.trim,
                    car_purchase.car_dim.body_type,
                    car_purchase.car_dim.transmission,
                    car_purchase.car_dim.color,
                    car_purchase.employee_dim.first_name,
                    car_purchase.employee_dim.age,
                    car_purchase.employee_dim.age_group,
                    car_purchase.employee_dim.sex,
                    car_purchase.employee_dim.salary,
                    car_purchase.employee_dim.work_experience,
                    car_purchase.employee_dim.oltp_id,
                    car_purchase.date_dim.date,
                    car_purchase.date_dim.year,
                    car_purchase.date_dim.month,
                    car_purchase.date_dim.day,
                    car_purchase.date_dim.week_day,
                    car_purchase.date_dim.oltp_id,
                    car_purchase.date_dim.fact_name,
                    car_purchase.seller_id,
                    car_purchase.location_id,
                    car_purchase.price,
                    car_purchase.car_years,
                    car_purchase.odometer,
                    car_purchase.condition,
                    car_purchase.employee_experience
                )
                for car_purchase in car_purchases
            ]
        else:
            query = """
                WITH insert_dim_car AS (
                    INSERT INTO dim_car(vin, manufacture_year, make, model, trim, body, transmission, color)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING vin
                ), insert_dim_date AS (
                    INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING date_id
                )

                INSERT INTO fact_car_purchase(
                    car_vin, seller_id, employee_id, location_id, date_id,
                    price, car_years, odometer, condition, employee_experience
                )
                VALUES
                    (
                        (SELECT vin FROM insert_dim_car),
                        (SELECT seller_id FROM dim_seller WHERE seller_oltp_id=%s),
                        (SELECT employee_id FROM dim_employee WHERE employee_oltp_id=%s AND is_valid = 1),
                        (SELECT location_id FROM dim_location WHERE address_oltp_id=%s AND is_valid = 1),
                        (SELECT date_id FROM insert_dim_date),
                        %s, %s, %s, %s, %s
                    );
        
                """
            data = [
                (
                    car_purchase.car_dim.vin,
                    car_purchase.car_dim.manufacture_year,
                    car_purchase.car_dim.make,
                    car_purchase.car_dim.model,
                    car_purchase.car_dim.trim,
                    car_purchase.car_dim.body_type,
                    car_purchase.car_dim.transmission,
                    car_purchase.car_dim.color,
                    car_purchase.date_dim.date,
                    car_purchase.date_dim.year,
                    car_purchase.date_dim.month,
                    car_purchase.date_dim.day,
                    car_purchase.date_dim.week_day,
                    car_purchase.date_dim.oltp_id,
                    car_purchase.date_dim.fact_name,
                    car_purchase.seller_id,
                    car_purchase.employee_dim.oltp_id,
                    car_purchase.location_id,
                    car_purchase.price,
                    car_purchase.car_years,
                    car_purchase.odometer,
                    car_purchase.condition,
                    car_purchase.employee_experience
                )
                for car_purchase in car_purchases
            ]
    else:
        print(f"fact_car_purchase incremental data loading")
        if insert_new_employee:
            query = """
                DO
                $$
                DECLARE
                    oltp_car_vin_exists BOOLEAN;
                BEGIN
                    -- Check if the record with the specified oltp_id exists
                    SELECT TRUE INTO oltp_car_vin_exists FROM fact_car_purchase WHERE car_vin = %s;

                    -- If the record exists, perform the update operation
                    IF oltp_car_vin_exists THEN
                        WITH insert_dim_employee AS (
                            INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING employee_id
                        ), update_dim_date AS (
                            UPDATE dim_date
                            SET date=%s, 
                            year=%s, 
                            month=%s, 
                            day=%s, 
                            week_day=%s
                            WHERE 
                                date_oltp_vin = %s 
                                AND fact_name = 'purchase'
                        )
                        UPDATE fact_car_purchase
                        SET employee_id=(SELECT employee_id FROM insert_dim_employee),
                            price = %s,
                            car_years = %s,
                            odometer = %s,
                            condition = %s,
                            employee_experience = %s
                        WHERE car_vin = %s;
                    ELSE
                        -- Otherwise, perform the insert operation
                        WITH insert_dim_employee AS (
                            INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING employee_id
                        ), insert_dim_date AS (
                            INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING date_id
                        )

                        INSERT INTO fact_car_purchase(
                            car_vin, seller_id, employee_id, location_id, date_id,
                            price, car_years, odometer, condition, employee_experience
                        )
                        VALUES
                            (
                                %s,
                                (SELECT seller_id FROM dim_seller WHERE seller_oltp_id=%s),
                                (SELECT employee_id FROM insert_dim_employee),
                                (SELECT location_id FROM dim_location WHERE address_oltp_id=%s AND is_valid = 1),
                                (SELECT date_id FROM insert_dim_date),
                                %s, %s, %s, %s, %s
                            );
                    END IF;
                END
                $$;
            """
            data = [
            (
                car_purchase.car_dim.vin,

                car_purchase.employee_dim.first_name,
                car_purchase.employee_dim.age,
                car_purchase.employee_dim.age_group,
                car_purchase.employee_dim.sex,
                car_purchase.employee_dim.salary,
                car_purchase.employee_dim.work_experience,
                car_purchase.employee_dim.oltp_id,

                car_purchase.date_dim.date,
                car_purchase.date_dim.year,
                car_purchase.date_dim.month,
                car_purchase.date_dim.day,
                car_purchase.date_dim.week_day,
                car_purchase.car_dim.vin,

                car_purchase.price,
                car_purchase.car_years,
                car_purchase.odometer,
                car_purchase.condition,
                car_purchase.employee_experience,
                car_purchase.car_dim.vin,

                car_purchase.employee_dim.first_name,
                car_purchase.employee_dim.age,
                car_purchase.employee_dim.age_group,
                car_purchase.employee_dim.sex,
                car_purchase.employee_dim.salary,
                car_purchase.employee_dim.work_experience,
                car_purchase.employee_dim.oltp_id,
                car_purchase.date_dim.date,
                car_purchase.date_dim.year,
                car_purchase.date_dim.month,
                car_purchase.date_dim.day,
                car_purchase.date_dim.week_day,
                car_purchase.date_dim.oltp_id,
                car_purchase.date_dim.fact_name,
                car_purchase.car_dim.vin,
                car_purchase.seller_id,
                car_purchase.location_id,
                car_purchase.price,
                car_purchase.car_years,
                car_purchase.odometer,
                car_purchase.condition,
                car_purchase.employee_experience
            )
            for car_purchase in car_purchases
        ]
        
        else:
            query = """
                DO
                $$
                DECLARE
                    oltp_car_vin_exists BOOLEAN;
                BEGIN
                    -- Check if the record with the specified oltp_id exists
                    SELECT TRUE INTO oltp_car_vin_exists FROM fact_car_purchase WHERE car_vin = %s;

                    -- If the record exists, perform the update operation
                    IF oltp_car_vin_exists THEN
                        WITH update_dim_date AS (
                            UPDATE dim_date
                            SET date=%s, 
                            year=%s, 
                            month=%s, 
                            day=%s, 
                            week_day=%s
                            WHERE 
                                date_oltp_vin = %s 
                                AND fact_name = 'purchase'
                        ) 
                        UPDATE fact_car_purchase
                        SET price = %s,
                            car_years = %s,
                            odometer = %s,
                            condition = %s,
                            employee_experience = %s
                        WHERE car_vin = %s;
                    ELSE
                        WITH insert_dim_date AS (
                            INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING date_id
                        )

                        INSERT INTO fact_car_purchase(
                            car_vin, seller_id, employee_id, location_id, date_id,
                            price, car_years, odometer, condition, employee_experience
                        )
                        VALUES
                            (
                                %s,
                                (SELECT seller_id FROM dim_seller WHERE seller_oltp_id=%s),
                                (SELECT employee_id FROM dim_employee WHERE employee_oltp_id=%s AND is_valid = 1),
                                (SELECT location_id FROM dim_location WHERE address_oltp_id=%s AND is_valid = 1),
                                (SELECT date_id FROM insert_dim_date),
                                %s, %s, %s, %s, %s
                            );
                    END IF;
                END
                $$;
            """
            data = [
                (
                    car_purchase.car_dim.vin,

                    car_purchase.date_dim.date,
                    car_purchase.date_dim.year,
                    car_purchase.date_dim.month,
                    car_purchase.date_dim.day,
                    car_purchase.date_dim.week_day,
                    car_purchase.car_dim.vin,

                    car_purchase.price,
                    car_purchase.car_years,
                    car_purchase.odometer,
                    car_purchase.condition,
                    car_purchase.employee_experience,
                    car_purchase.car_dim.vin,

                    car_purchase.date_dim.date,
                    car_purchase.date_dim.year,
                    car_purchase.date_dim.month,
                    car_purchase.date_dim.day,
                    car_purchase.date_dim.week_day,
                    car_purchase.date_dim.oltp_id,
                    car_purchase.date_dim.fact_name,
                    car_purchase.car_dim.vin,
                    car_purchase.seller_id,
                    car_purchase.employee_dim.oltp_id,
                    car_purchase.location_id,
                    car_purchase.price,
                    car_purchase.car_years,
                    car_purchase.odometer,
                    car_purchase.condition,
                    car_purchase.employee_experience
                )
                for car_purchase in car_purchases
            ]

    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'fact_car_purchase')
        

def load_fact_car_repair(conn, car_repairs, insert_new_employee, initial_data_loading):
    if initial_data_loading:
        if insert_new_employee:
            query = """
                WITH insert_dim_employee AS (
                    INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING employee_id
                ), insert_dim_location AS (
                    INSERT INTO dim_location(country, city, address_oltp_id)
                    VALUES
                        (%s, %s, %s)
                    RETURNING location_id
                ), insert_dim_date AS (
                    INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name, fact_oltp_id)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING date_id
                )

                INSERT INTO fact_car_repair(
                    car_vin, employee_id, location_id, date_id, repair_type_id,
                    cost, condition_delta, repair_oltp_id
                )
                VALUES
                    (
                        %s,
                        (SELECT employee_id FROM insert_dim_employee),
                        (SELECT location_id FROM insert_dim_location),
                        (SELECT date_id FROM insert_dim_date),
                        (SELECT repair_type_id FROM dim_car_repair_type WHERE repair_type = %s),
                        %s, %s, %s
                    );
            """
            data = [
                (
                    car_repair.employee_dim.first_name,
                    car_repair.employee_dim.age,
                    car_repair.employee_dim.age_group,
                    car_repair.employee_dim.sex,
                    car_repair.employee_dim.salary,
                    car_repair.employee_dim.work_experience,
                    car_repair.employee_dim.oltp_id,

                    car_repair.location_dim.country,
                    car_repair.location_dim.city,
                    car_repair.location_dim.oltp_id,

                    car_repair.date_dim.date,
                    car_repair.date_dim.year,
                    car_repair.date_dim.month,
                    car_repair.date_dim.day,
                    car_repair.date_dim.week_day,
                    car_repair.date_dim.oltp_id,
                    car_repair.date_dim.fact_name,
                    car_repair.oltp_id,

                    car_repair.car_vin,

                    car_repair.car_repair_type_dim.repair_type,

                    car_repair.cost,
                    car_repair.condition_delta,
                    car_repair.oltp_id
                )
                for car_repair in car_repairs
            ]
        else:
            query = """
                WITH insert_dim_location AS (
                    INSERT INTO dim_location(country, city, address_oltp_id)
                    VALUES
                        (%s, %s, %s)
                    RETURNING location_id
                ), insert_dim_date AS (
                    INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name, fact_oltp_id)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING date_id
                )

                INSERT INTO fact_car_repair(
                    car_vin, employee_id, location_id, date_id, repair_type_id,
                    cost, condition_delta, repair_oltp_id
                )
                VALUES
                    (
                        %s,
                        (SELECT employee_id FROM dim_employee WHERE employee_oltp_id=%s AND is_valid = 1),
                        (SELECT location_id FROM insert_dim_location),
                        (SELECT date_id FROM insert_dim_date),
                        (SELECT repair_type_id FROM dim_car_repair_type WHERE repair_type = %s),
                        %s, %s, %s
                    );
            """
            data = [
                (
                    car_repair.location_dim.country,
                    car_repair.location_dim.city,
                    car_repair.location_dim.oltp_id,

                    car_repair.date_dim.date,
                    car_repair.date_dim.year,
                    car_repair.date_dim.month,
                    car_repair.date_dim.day,
                    car_repair.date_dim.week_day,
                    car_repair.date_dim.oltp_id,
                    car_repair.date_dim.fact_name,
                    car_repair.oltp_id,

                    car_repair.car_vin,
                    car_repair.employee_dim.oltp_id,

                    car_repair.car_repair_type_dim.repair_type,

                    car_repair.cost,
                    car_repair.condition_delta,
                    car_repair.oltp_id
                )
                for car_repair in car_repairs
            ]
    else:
        print("fact_car_repair incremental data loading")
        if insert_new_employee:
            query = """
                DO
                $$
                DECLARE
                    oltp_car_vin_exists BOOLEAN;
                BEGIN
                    -- Check if the record with the specified oltp_id exists
                    SELECT TRUE INTO oltp_car_vin_exists FROM fact_car_repair WHERE car_vin = %s AND repair_oltp_id = %s;

                    -- If the record exists, perform the update operation
                    IF oltp_car_vin_exists THEN
                        WITH insert_dim_employee AS (
                            INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING employee_id
                        ), update_dim_date AS (
                            UPDATE dim_date
                            SET date=%s, 
                            year=%s, 
                            month=%s, 
                            day=%s, 
                            week_day=%s
                            WHERE 
                                date_oltp_vin = %s 
                                AND fact_name = 'repair'
                                AND fact_oltp_id = %s
                        )
                        UPDATE fact_car_repair
                        SET employee_id=(SELECT employee_id FROM insert_dim_employee),
                            cost=%s,
                            condition_delta=%s
                        WHERE 
                            car_vin = %s
                            AND repair_oltp_id = %s;
                    ELSE
                        -- Otherwise, perform the insert operation
                        WITH insert_dim_employee AS (
                            INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING employee_id
                        ), insert_dim_location AS (
                            INSERT INTO dim_location(country, city, address_oltp_id)
                            VALUES
                                (%s, %s, %s)
                            RETURNING location_id
                        ), insert_dim_date AS (
                            INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name, fact_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING date_id
                        )

                        INSERT INTO fact_car_repair(
                            car_vin, employee_id, location_id, date_id, repair_type_id,
                            cost, condition_delta,
                            repair_oltp_id
                        )
                        VALUES
                            (
                                %s,
                                (SELECT employee_id FROM insert_dim_employee),
                                (SELECT location_id FROM insert_dim_location),
                                (SELECT date_id FROM insert_dim_date),
                                (SELECT repair_type_id FROM dim_car_repair_type WHERE repair_type=%s),
                                %s, %s, %s
                            );
                    END IF;
                END
                $$;
            """
            data = [
                (
                    car_repair.car_vin,
                    car_repair.oltp_id,

                    car_repair.employee_dim.first_name,
                    car_repair.employee_dim.age,
                    car_repair.employee_dim.age_group,
                    car_repair.employee_dim.sex,
                    car_repair.employee_dim.salary,
                    car_repair.employee_dim.work_experience,
                    car_repair.employee_dim.oltp_id,

                    car_repair.date_dim.date,
                    car_repair.date_dim.year,
                    car_repair.date_dim.month,
                    car_repair.date_dim.day,
                    car_repair.date_dim.week_day,
                    car_repair.car_vin,
                    car_repair.oltp_id,

                    car_repair.cost,
                    car_repair.condition_delta,
                    car_repair.car_vin,
                    car_repair.oltp_id,

                    car_repair.employee_dim.first_name,
                    car_repair.employee_dim.age,
                    car_repair.employee_dim.age_group,
                    car_repair.employee_dim.sex,
                    car_repair.employee_dim.salary,
                    car_repair.employee_dim.work_experience,
                    car_repair.employee_dim.oltp_id,
                    car_repair.location_dim.country,
                    car_repair.location_dim.city,
                    car_repair.location_dim.oltp_id,
                    car_repair.date_dim.date,
                    car_repair.date_dim.year,
                    car_repair.date_dim.month,
                    car_repair.date_dim.day,
                    car_repair.date_dim.week_day,
                    car_repair.date_dim.oltp_id,
                    car_repair.date_dim.fact_name,
                    car_repair.oltp_id,

                    car_repair.car_vin,
                    car_repair.car_repair_type_dim.repair_type,
                    car_repair.cost,
                    car_repair.condition_delta,
                    car_repair.oltp_id
                )
                for car_repair in car_repairs
            ]
        
        else:
            query = """
                DO
                $$
                DECLARE
                    oltp_car_vin_exists BOOLEAN;
                BEGIN
                    -- Check if the record with the specified oltp_id exists
                    SELECT TRUE INTO oltp_car_vin_exists FROM fact_car_repair WHERE car_vin = %s AND repair_oltp_id = %s;

                    -- If the record exists, perform the update operation
                    IF oltp_car_vin_exists THEN
                        WITH update_dim_date AS (
                            UPDATE dim_date
                            SET date=%s, 
                            year=%s, 
                            month=%s, 
                            day=%s, 
                            week_day=%s
                            WHERE 
                                date_oltp_vin = %s 
                                AND fact_name = 'repair'
                                AND fact_oltp_id = %s
                        )
                        UPDATE fact_car_repair
                        SET
                            cost=%s,
                            condition_delta=%s
                        WHERE 
                            car_vin = %s
                            AND repair_oltp_id = %s;
                    ELSE
                        -- Otherwise, perform the insert operation
                        WITH insert_dim_location AS (
                            INSERT INTO dim_location(country, city, address_oltp_id)
                            VALUES
                                (%s, %s, %s)
                            RETURNING location_id
                        ),
                        insert_dim_date AS (
                            INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name, fact_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING date_id
                        )

                        INSERT INTO fact_car_repair(
                            car_vin, employee_id, location_id, date_id, repair_type_id,
                            cost, condition_delta, 
                            repair_oltp_id
                        )
                        VALUES
                            (
                                %s,
                                (SELECT employee_id FROM dim_employee WHERE employee_oltp_id=%s AND is_valid = 1),
                                (SELECT location_id FROM insert_dim_location),
                                (SELECT date_id FROM insert_dim_date),
                                (SELECT repair_type_id FROM dim_car_repair_type WHERE repair_type=%s),
                                %s, %s, %s
                            );
                    END IF;
                END
                $$;
            """
            data = [
                (
                    car_repair.car_vin,
                    car_repair.oltp_id,

                    car_repair.date_dim.date,
                    car_repair.date_dim.year,
                    car_repair.date_dim.month,
                    car_repair.date_dim.day,
                    car_repair.date_dim.week_day,
                    car_repair.car_vin,
                    car_repair.oltp_id,

                    car_repair.cost,
                    car_repair.condition_delta,
                    car_repair.car_vin,
                    car_repair.oltp_id,

                    car_repair.location_dim.country,
                    car_repair.location_dim.city,
                    car_repair.location_dim.oltp_id,

                    car_repair.date_dim.date,
                    car_repair.date_dim.year,
                    car_repair.date_dim.month,
                    car_repair.date_dim.day,
                    car_repair.date_dim.week_day,
                    car_repair.date_dim.oltp_id,
                    car_repair.date_dim.fact_name,
                    car_repair.oltp_id,

                    car_repair.car_vin,
                    car_repair.employee_dim.oltp_id,
                    car_repair.car_repair_type_dim.repair_type,
                    car_repair.cost,
                    car_repair.condition_delta,
                    car_repair.oltp_id
                )
                for car_repair in car_repairs
            ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'fact_car_repair')


def load_fact_car_sale(conn, car_sales, insert_new_employee, initial_data_loading):
    if initial_data_loading:
        if insert_new_employee:
            query = """
                WITH insert_dim_buyer AS (
                    INSERT INTO dim_buyer(first_name, age, age_group, sex, buyer_oltp_id)
                    VALUES
                        (%s, %s, %s, %s, %s)
                    RETURNING buyer_id
                ), insert_dim_employee AS (
                    INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING employee_id
                ), insert_dim_location AS (
                    INSERT INTO dim_location(country, city, address_oltp_id)
                    VALUES
                        (%s, %s, %s)
                    RETURNING location_id
                ), insert_dim_date AS (
                    INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING date_id
                )

                INSERT INTO fact_car_sale(
                    car_vin, buyer_id, employee_id, location_id, date_id,
                    price, gross_profit_amount, gross_profit_percentage, 
                    mmr, price_margin, 
                    car_years, odometer, condition, employee_experience,
                    service_time, service_cost
                )
                VALUES
                    (
                        %s,
                        (SELECT buyer_id FROM insert_dim_buyer),
                        (SELECT employee_id FROM insert_dim_employee),
                        (SELECT location_id FROM insert_dim_location),
                        (SELECT date_id FROM insert_dim_date),
                        %s, %s, %s, 
                        %s, %s,
                        %s, %s, %s, %s,
                        %s, %s
                    );
            """
            data = [
                (
                    car_sale.buyer_dim.first_name,
                    car_sale.buyer_dim.age,
                    car_sale.buyer_dim.age_group,
                    car_sale.buyer_dim.sex,
                    car_sale.buyer_dim.oltp_id,
                    
                    car_sale.employee_dim.first_name,
                    car_sale.employee_dim.age,
                    car_sale.employee_dim.age_group,
                    car_sale.employee_dim.sex,
                    car_sale.employee_dim.salary,
                    car_sale.employee_dim.work_experience,
                    car_sale.employee_dim.oltp_id,

                    car_sale.location_dim.country,
                    car_sale.location_dim.city,
                    car_sale.location_dim.oltp_id,

                    car_sale.date_dim.date,
                    car_sale.date_dim.year,
                    car_sale.date_dim.month,
                    car_sale.date_dim.day,
                    car_sale.date_dim.week_day,
                    car_sale.date_dim.oltp_id,
                    car_sale.date_dim.fact_name,

                    car_sale.car_vin,

                    car_sale.price,
                    car_sale.gross_profit_amount,
                    car_sale.gross_profit_percentage,
                    car_sale.mmr,
                    car_sale.price_margin,
                    car_sale.car_years,
                    car_sale.odometer,
                    car_sale.condition,
                    car_sale.employee_experience,
                    car_sale.service_time,
                    car_sale.service_cost
                )
                for car_sale in car_sales
            ]
        else:
            query = """
                WITH insert_dim_buyer AS (
                    INSERT INTO dim_buyer(first_name, age, age_group, sex, buyer_oltp_id)
                    VALUES
                        (%s, %s, %s, %s, %s)
                    RETURNING buyer_id
                ), insert_dim_location AS (
                    INSERT INTO dim_location(country, city, address_oltp_id)
                    VALUES
                        (%s, %s, %s)
                    RETURNING location_id
                ), insert_dim_date AS (
                    INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING date_id
                )

                INSERT INTO fact_car_sale(
                    car_vin, buyer_id, employee_id, location_id, date_id,
                    price, gross_profit_amount, gross_profit_percentage, 
                    mmr, price_margin, 
                    car_years, odometer, condition, employee_experience,
                    service_time, service_cost
                )
                VALUES
                    (
                        %s,
                        (SELECT buyer_id FROM insert_dim_buyer),
                        (SELECT employee_id FROM dim_employee WHERE employee_oltp_id=%s AND is_valid = 1),
                        (SELECT location_id FROM insert_dim_location),
                        (SELECT date_id FROM insert_dim_date),
                        %s, %s, %s, 
                        %s, %s,
                        %s, %s, %s, %s,
                        %s, %s
                    );
            """
            data = [
                (
                    car_sale.buyer_dim.first_name,
                    car_sale.buyer_dim.age,
                    car_sale.buyer_dim.age_group,
                    car_sale.buyer_dim.sex,
                    car_sale.buyer_dim.oltp_id,

                    car_sale.location_dim.country,
                    car_sale.location_dim.city,
                    car_sale.location_dim.oltp_id,

                    car_sale.date_dim.date,
                    car_sale.date_dim.year,
                    car_sale.date_dim.month,
                    car_sale.date_dim.day,
                    car_sale.date_dim.week_day,
                    car_sale.date_dim.oltp_id,
                    car_sale.date_dim.fact_name,

                    car_sale.car_vin,

                    car_sale.employee_dim.oltp_id,

                    car_sale.price,
                    car_sale.gross_profit_amount,
                    car_sale.gross_profit_percentage,
                    car_sale.mmr,
                    car_sale.price_margin,
                    car_sale.car_years,
                    car_sale.odometer,
                    car_sale.condition,
                    car_sale.employee_experience,
                    car_sale.service_time,
                    car_sale.service_cost
                )
                for car_sale in car_sales
            ]
    else:
        print(f"fact_car_sale incremental data loading")
        if insert_new_employee:
            print(f"fact_car_sale: insert new employee")
            query = """
                DO
                $$
                DECLARE
                    oltp_car_vin_exists BOOLEAN;
                BEGIN
                    -- Check if the record with the specified oltp_id exists
                    SELECT TRUE INTO oltp_car_vin_exists FROM fact_car_sale WHERE car_vin = %s;

                    -- If the record exists, perform the update operation
                    IF oltp_car_vin_exists THEN
                        WITH insert_dim_employee AS (
                            INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING employee_id
                        ), update_dim_date AS (
                            UPDATE dim_date
                            SET date=%s, 
                            year=%s, 
                            month=%s, 
                            day=%s, 
                            week_day=%s
                            WHERE 
                                date_oltp_vin = %s 
                                AND fact_name = 'sale'
                        )
                        UPDATE fact_car_sale
                        SET 
                            employee_id = (SELECT employee_id FROM insert_dim_employee),
                            service_cost = %s,
                            price = %s,
                            gross_profit_amount = %s,
                            gross_profit_percentage = %s,
                            mmr = %s,
                            price_margin = %s,
                            service_time = %s,
                            car_years = %s,
                            odometer = %s,
                            condition = %s,
                            employee_experience = %s
                        WHERE car_vin = %s;
                    ELSE
                        -- Otherwise, perform the insert operation
                        WITH insert_dim_employee AS (
                            INSERT INTO dim_employee(first_name, age, age_group, sex, salary, work_experience, employee_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING employee_id
                        ), insert_dim_buyer AS (
                            INSERT INTO dim_buyer(first_name, age, age_group, sex, buyer_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s)
                            RETURNING buyer_id
                        ), insert_dim_location AS (
                            INSERT INTO dim_location(country, city, address_oltp_id)
                            VALUES
                                (%s, %s, %s)
                            RETURNING location_id
                        ), insert_dim_date AS (
                            INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING date_id
                        )

                        INSERT INTO fact_car_sale(
                            car_vin, buyer_id, employee_id, location_id, date_id,
                            service_cost, price, gross_profit_amount, gross_profit_percentage,
                            mmr, price_margin, service_time,
                            car_years, odometer, condition, employee_experience
                        )
                        VALUES
                            (
                                %s,
                                (SELECT buyer_id FROM insert_dim_buyer),
                                (SELECT employee_id FROM insert_dim_employee),
                                (SELECT location_id FROM insert_dim_location),
                                (SELECT date_id FROM insert_dim_date),
                                %s, %s, %s, %s,
                                %s, %s, %s, %s, 
                                %s, %s, %s
                            );
                    END IF;
                END
                $$;
            """
            data = [
            (
                car_sale.car_vin,

                car_sale.employee_dim.first_name,
                car_sale.employee_dim.age,
                car_sale.employee_dim.age_group,
                car_sale.employee_dim.sex,
                car_sale.employee_dim.salary,
                car_sale.employee_dim.work_experience,
                car_sale.employee_dim.oltp_id,

                car_sale.date_dim.date,
                car_sale.date_dim.year,
                car_sale.date_dim.month,
                car_sale.date_dim.day,
                car_sale.date_dim.week_day,
                car_sale.car_vin,

                car_sale.service_cost,
                car_sale.price,
                car_sale.gross_profit_amount,
                car_sale.gross_profit_percentage,
                car_sale.mmr,
                car_sale.price_margin,
                car_sale.service_time,
                car_sale.car_years,
                car_sale.odometer,
                car_sale.condition,
                car_sale.employee_experience,
                car_sale.car_vin,

                car_sale.employee_dim.first_name,
                car_sale.employee_dim.age,
                car_sale.employee_dim.age_group,
                car_sale.employee_dim.sex,
                car_sale.employee_dim.salary,
                car_sale.employee_dim.work_experience,
                car_sale.employee_dim.oltp_id,
                car_sale.buyer_dim.first_name,
                car_sale.buyer_dim.age,
                car_sale.buyer_dim.age_group,
                car_sale.buyer_dim.sex,
                car_sale.buyer_dim.oltp_id,

                car_sale.location_dim.country,
                car_sale.location_dim.city,
                car_sale.location_dim.oltp_id,

                car_sale.date_dim.date,
                car_sale.date_dim.year,
                car_sale.date_dim.month,
                car_sale.date_dim.day,
                car_sale.date_dim.week_day,
                car_sale.date_dim.oltp_id,
                car_sale.date_dim.fact_name,

                car_sale.car_vin,

                car_sale.service_cost,
                car_sale.price,
                car_sale.gross_profit_amount,
                car_sale.gross_profit_percentage,
                car_sale.mmr,
                car_sale.price_margin,
                car_sale.service_time,
                car_sale.car_years,
                car_sale.odometer,
                car_sale.condition,
                car_sale.employee_experience 
            )
            for car_sale in car_sales
        ]
        
        else:
            query = """
                DO
                $$
                DECLARE
                    oltp_car_vin_exists BOOLEAN;
                BEGIN
                    -- Check if the record with the specified oltp_id exists
                    SELECT TRUE INTO oltp_car_vin_exists FROM fact_car_sale WHERE car_vin = %s;

                    -- If the record exists, perform the update operation
                    IF oltp_car_vin_exists THEN
                        WITH update_dim_date AS (
                            UPDATE dim_date
                            SET date=%s, 
                            year=%s, 
                            month=%s, 
                            day=%s, 
                            week_day=%s
                            WHERE 
                                date_oltp_vin = %s 
                                AND fact_name = 'sale'
                        )
                        UPDATE fact_car_sale
                        SET
                            service_cost = %s,
                            price = %s,
                            gross_profit_amount = %s,
                            gross_profit_percentage = %s,
                            mmr = %s,
                            price_margin = %s,
                            service_time = %s,
                            car_years = %s,
                            odometer = %s,
                            condition = %s,
                            employee_experience = %s
                        WHERE car_vin = %s;
                    ELSE
                        -- Otherwise, perform the insert operation
                        WITH insert_dim_buyer AS (
                            INSERT INTO dim_buyer(first_name, age, age_group, sex, buyer_oltp_id)
                            VALUES
                                (%s, %s, %s, %s, %s)
                            RETURNING buyer_id
                        ), insert_dim_location AS (
                            INSERT INTO dim_location(country, city, address_oltp_id)
                            VALUES
                                (%s, %s, %s)
                            RETURNING location_id
                        ), insert_dim_date AS (
                            INSERT INTO dim_date(date, year, month, day, week_day, date_oltp_vin, fact_name)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING date_id
                        )

                        INSERT INTO fact_car_sale(
                            car_vin, buyer_id, employee_id, location_id, date_id,
                            service_cost, price, gross_profit_amount, gross_profit_percentage,
                            mmr, price_margin, service_time,
                            car_years, odometer, condition, employee_experience
                        )
                        VALUES
                            (
                                %s,
                                (SELECT buyer_id FROM insert_dim_buyer),
                                (SELECT employee_id FROM dim_employee WHERE employee_oltp_id=%s AND is_valid = 1),
                                (SELECT location_id FROM insert_dim_location),
                                (SELECT date_id FROM insert_dim_date),
                                %s, %s, %s, %s,
                                %s, %s, %s, %s, 
                                %s, %s, %s
                            );
                    END IF;
                END
                $$;
            """
            data = [
            (
                car_sale.car_vin,

                car_sale.date_dim.date,
                car_sale.date_dim.year,
                car_sale.date_dim.month,
                car_sale.date_dim.day,
                car_sale.date_dim.week_day,
                car_sale.car_vin,

                car_sale.service_cost,
                car_sale.price,
                car_sale.gross_profit_amount,
                car_sale.gross_profit_percentage,
                car_sale.mmr,
                car_sale.price_margin,
                car_sale.service_time,
                car_sale.car_years,
                car_sale.odometer,
                car_sale.condition,
                car_sale.employee_experience,
                car_sale.car_vin,

                car_sale.buyer_dim.first_name,
                car_sale.buyer_dim.age,
                car_sale.buyer_dim.age_group,
                car_sale.buyer_dim.sex,
                car_sale.buyer_dim.oltp_id,

                car_sale.location_dim.country,
                car_sale.location_dim.city,
                car_sale.location_dim.oltp_id,

                car_sale.date_dim.date,
                car_sale.date_dim.year,
                car_sale.date_dim.month,
                car_sale.date_dim.day,
                car_sale.date_dim.week_day,
                car_sale.date_dim.oltp_id,
                car_sale.date_dim.fact_name,

                car_sale.car_vin,
                car_sale.employee_dim.oltp_id,

                car_sale.service_cost,
                car_sale.price,
                car_sale.gross_profit_amount,
                car_sale.gross_profit_percentage,
                car_sale.mmr,
                car_sale.price_margin,
                car_sale.service_time,
                car_sale.car_years,
                car_sale.odometer,
                car_sale.condition,
                car_sale.employee_experience 
            )
            for car_sale in car_sales
        ]

    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'fact_car_sale')