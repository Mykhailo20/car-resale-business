def extract_employee_data(conn):
    # SQL query
    query = """
        SELECT 
            e.person_id, 
            e.first_name, e.last_name, e.middle_name,
            e.birth_date, e.sex, e.email, 
            p.name AS p_name, e.salary, e.hire_date 
        FROM 
            employee e
        JOIN 
            position p
        ON e.position_id = p.position_id;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        # Fetch the results
        data = cur.fetchall()
    return data


def extract_employee_updated_data(conn, last_etl_datetime):
    # SQL query
    query = """
        SELECT 
            e.person_id, 
            e.first_name, e.last_name, e.middle_name,
            e.birth_date, e.sex, e.email, 
            p.name AS p_name, e.salary, e.hire_date 
        FROM 
            employee e
        JOIN 
            position p
        ON e.position_id = p.position_id
        WHERE 
            e.updated_at >= %s
            OR p.updated_at >= %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (last_etl_datetime, last_etl_datetime))
        # Fetch the results
        data = cur.fetchall()
    return data


def extract_seller_data(conn, initial_data_loading, last_etl_datetime):
    if initial_data_loading:
        # SQL query
        query = """
            SELECT 
                s.seller_id, s.name, s.type, s.address_id, 
                country.name AS country_name,
                c.name AS city_name,
                addr.street,
                addr.postal_code
            FROM seller s
            JOIN address addr
            ON s.address_id = addr.address_id
            JOIN city c
            ON addr.city_id = c.city_id
            JOIN country
            ON c.country_id = country.country_id
        """
        with conn.cursor() as cur:
            cur.execute(query)
            # Fetch the results
            data = cur.fetchall()
    else:
        # SQL query
        query = """
            SELECT 
                s.seller_id, s.name, s.type, s.address_id, 
                country.name AS country_name,
                c.name AS city_name,
                addr.street,
                addr.postal_code
            FROM seller s
            JOIN address addr
            ON s.address_id = addr.address_id
            JOIN city c
            ON addr.city_id = c.city_id
            JOIN country
            ON c.country_id = country.country_id
            WHERE
                s.updated_at >= %s
        """
        with conn.cursor() as cur:
            cur.execute(query, (last_etl_datetime,))
            # Fetch the results
            data = cur.fetchall()

    return data


def extract_location_data(conn, initial_data_loading, last_etl_datetime):
    # SQL query
    query = """
        SELECT 
            address.address_id, 
            country.name AS country_name, 
            city.name AS city_name, 
            address.street,
            address.postal_code
        FROM address
        JOIN city ON address.city_id = city.city_id
        JOIN country ON city.country_id = country.country_id
        WHERE 
            city.updated_at >= %s
            OR country.updated_at >= %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (last_etl_datetime, last_etl_datetime))
        # Fetch the results
        data = cur.fetchall()
    return data
    

def extract_car_data(conn, limit_records=10):
    # SQL query
    query = """
        SELECT 
            c.vin, c.manufacture_year, cm.name AS make_name, c.model, c.trim, 
            cbt.name AS cbt_name, c.transmission, color.name AS color_name
        FROM car c
        JOIN car_make cm ON c.make_id = cm.car_make_id
        JOIN car_body_type cbt ON c.body_type_id = cbt.car_body_type_id
        JOIN color ON c.color_id = color.color_id
        LIMIT %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (limit_records,))
        # Fetch the results
        data = cur.fetchall()
    return data


def extract_car_repair_type_data(conn, initial_data_loading, last_etl_datetime):
    # SQL query
    query = """
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'repair_type_enum');
    """
    with conn.cursor() as cur:
        cur.execute(query)
        # Fetch the results
        data = cur.fetchall()
    return data
    

def extract_purchase_data(conn, initial_data_loading, last_etl_datetime, limit_records=10):
    if initial_data_loading:
        # SQL query
        query = """
            SELECT 
                c.vin, c.manufacture_year, cm.name AS cm_name, 
                c.model, c.trim, cbt.name AS cbt_name, 
                c.transmission, color.name AS color_name,
                e.person_id AS e_oltp_id, e.first_name AS e_first_name, e.last_name AS e_last_name, e.middle_name AS e_middle_name, 
                e.birth_date, e.sex, e.email,
                pos.name AS e_position, e.salary, e.hire_date,
                s.seller_id AS seller_id, s.address_id AS seller_address,
                p.price, p.odometer, p.condition, p.purchase_date
            FROM purchase p

            JOIN car c ON p.car_vin = c.vin
            JOIN car_make AS cm ON c.make_id = cm.car_make_id
            JOIN car_body_type cbt ON c.body_type_id = cbt.car_body_type_id
            JOIN color ON c.color_id = color.color_id

            JOIN seller s ON p.seller_id = s.seller_id

            JOIN employee e ON p.employee_id = e.person_id
            JOIN position pos ON e.position_id = pos.position_id;
        """
        with conn.cursor() as cur:
            cur.execute(query)
            # Fetch the results
            data = cur.fetchall()
    else:
        # SQL query
        query = """
            SELECT 
                c.vin, c.manufacture_year, cm.name AS cm_name, 
                c.model, c.trim, cbt.name AS cbt_name, 
                c.transmission, color.name AS color_name,
                e.person_id AS e_oltp_id, e.first_name AS e_first_name, e.last_name AS e_last_name, e.middle_name AS e_middle_name, 
                e.birth_date, e.sex, e.email,
                pos.name AS e_position, e.salary, e.hire_date,
                s.seller_id AS seller_id, s.address_id AS seller_address,
                p.price, p.odometer, p.condition, p.purchase_date
            FROM purchase p

            JOIN car c ON p.car_vin = c.vin
            JOIN car_make AS cm ON c.make_id = cm.car_make_id
            JOIN car_body_type cbt ON c.body_type_id = cbt.car_body_type_id
            JOIN color ON c.color_id = color.color_id

            JOIN seller s ON p.seller_id = s.seller_id

            JOIN employee e ON p.employee_id = e.person_id
            JOIN position pos ON e.position_id = pos.position_id
            WHERE 
                p.updated_at >= %s
                OR c.updated_at >= %s
                OR e.updated_at >= %s;
        """
        with conn.cursor() as cur:
            cur.execute(query, (last_etl_datetime, last_etl_datetime, last_etl_datetime))
            # Fetch the results
            data = cur.fetchall()
        
    return data
    

def extract_repair_data(conn, initial_data_loading, last_etl_datetime, limit_records=10):
    # SQL query
    query = """
        SELECT 
            r.repair_id AS repair_oltp_id, 
            r.car_vin,
            e.person_id AS e_oltp_id, e.first_name AS e_first_name, e.last_name AS e_last_name, e.middle_name AS e_middle_name,
            e.birth_date, e.sex, 
            e.email, pos.name, e.salary, e.hire_date,
            r.address_id AS r_oltp_addr_id,
            country.name AS country_name, city.name AS city_name,
            addr.street, addr.postal_code, 
            r.repair_type, r.cost, p.condition AS p_condition, r.condition, r.repair_date
        FROM repair r

        JOIN employee e ON r.employee_id = e.person_id
        JOIN position pos ON e.position_id = pos.position_id

        JOIN address addr ON r.address_id = addr.address_id
        JOIN city ON addr.city_id = city.city_id
        JOIN country ON city.country_id = country.country_id

        JOIN purchase p ON r.car_vin = p.car_vin;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        # Fetch the results
        data = cur.fetchall()
    return data


def extract_sale_data(conn, initial_data_loading, last_etl_datetime, limit_records=10):
    # SQL query
    query = """
        SELECT 
            s.car_vin, c.manufacture_year,
            b.person_id AS b_oltp_id,
            b.first_name AS b_first_name, b.last_name AS b_last_name, b.middle_name AS b_middle_name,
            b.birth_date as b_birth_date, b.sex AS b_sex, b.email AS b_email,
            b.address_id AS b_addr_oltp_id,
            country.name AS b_country_name, city.name AS b_city_name,
            addr.street AS b_street, addr.postal_code AS b_postal_code,
            e.person_id AS e_oltp_id, 
            e.first_name AS e_first_name, e.last_name AS e_last_name, e.middle_name AS e_middle_name,
            e.birth_date, e.sex, 
            e.email, pos.name, e.salary, e.hire_date,
            s.mmr, s.price, s.odometer, s.condition, s.sale_date,
            COALESCE(total_repair_cost, 0) AS repair_cost,  -- Use COALESCE to return 0 if total_repair_cost is NULL
            p.price, p.purchase_date
        FROM sale s
        JOIN car c ON s.car_vin = c.vin
        JOIN buyer b ON s.buyer_id = b.person_id
        JOIN address addr ON b.address_id = addr.address_id
        JOIN city ON addr.city_id = city.city_id
        JOIN country ON city.country_id = country.country_id
        JOIN employee e ON s.employee_id = e.person_id
        JOIN position pos ON e.position_id = pos.position_id
        JOIN purchase p ON s.car_vin = p.car_vin
        LEFT JOIN (
            SELECT car_vin, SUM(cost) AS total_repair_cost
            FROM repair
            GROUP BY car_vin
        ) r ON s.car_vin = r.car_vin;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        # Fetch the results
        data = cur.fetchall()
    return data
