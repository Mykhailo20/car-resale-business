from car_resale_business_project.databases.etl.etl_utils.extract import *

from car_resale_business_project.databases.etl.etl_utils.transform import *
from car_resale_business_project.databases.etl.etl_utils.create_OLTP_class_instances import *
from car_resale_business_project.databases.etl.etl_utils.OLTP_to_OLAP_mapper import *

from car_resale_business_project.databases.etl.etl_utils.load import *


def seller_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading, last_etl_datetime):

    oltp_db_conn = pg2.connect(database=oltp_config_dict['database'], user=oltp_config_dict['user'], password=oltp_config_dict['password'])

    print(f"\nSELLER EXTRACT")
    if initial_data_loading:
        print(f"Initial data loading.")
        seller_data = extract_seller_data(conn=oltp_db_conn, initial_data_loading=initial_data_loading, last_etl_datetime=last_etl_datetime)
    else:
        print(f"Incremental data loading.")
        seller_data = extract_seller_data(conn=oltp_db_conn, initial_data_loading=initial_data_loading, last_etl_datetime=last_etl_datetime)
        print(f"updated_seller_data = {seller_data}")

    oltp_db_conn.close()
    seller_columns = [
        's_oltp_id',
        's_name', 's_type',
        's_addr_oltp_id', 's_country', 's_city',
        's_street', 's_postal_code'
    ]
    seller_df = pd.DataFrame(seller_data, columns=seller_columns)

    print(f"\nSELLER TRANSFORM")
    check_dataframe(seller_df, important_columns=['s_oltp_id'], df_name='seller_df')

    # Create OLAP Seller + Location classes instances
    olap_sellers_list = []
    olap_sellers_locations_list = []
    for _, row in seller_df.iterrows():
        oltp_seller_obj = create_seller(row)

        olap_seller_obj = OLTP_to_OLAP_seller(oltp_seller=oltp_seller_obj, seller_metadata=metadata['dimensions']['dim_seller'])
        olap_sellers_list.append(olap_seller_obj)
        if initial_data_loading:
            olap_sellers_locations_obj = OLTP_to_OLAP_location(oltp_address=oltp_seller_obj.address, location_metadata=metadata['dimensions']['dim_location'])
            olap_sellers_locations_list.append(olap_sellers_locations_obj)
        
    print(f"\nSELLER LOAD")
    olap_db_conn = pg2.connect(database=olap_config_dict['database'], user=olap_config_dict['user'], password=olap_config_dict['password'])
    
    # INSERT DATA INTO dim_seller table
    batch_size = 10
    start_index = 0
    total_records = len(olap_sellers_list)

    data_insertion_start_time = time.time()
    while start_index < total_records:

        end_index = min(start_index + batch_size, total_records)
        seller_batch_data = olap_sellers_list[start_index:end_index]
        seller_location_batch_data = olap_sellers_locations_list[start_index:end_index]
        load_seller_dim(conn=olap_db_conn, seller_dims=seller_batch_data, initial_data_loading=initial_data_loading)
        print(f"load_seller_dim: len(seller_batch_data) = {len(seller_batch_data)}\nseller_batch_data = {seller_batch_data}")
        if initial_data_loading:
            print(f"\nload_seller_dim -> load_dim_location: len(seller_location_batch_data)={len(seller_location_batch_data)}\nseller_location_batch_data={seller_location_batch_data}")
            load_location_dim(conn=olap_db_conn, location_dims=seller_location_batch_data)

        start_index += batch_size
        break

    data_insertion_duration = time.time() - data_insertion_start_time
    print(f"Data insertion time: {data_insertion_duration // 60: .0f}m {data_insertion_duration % 60: .0f}s\n")
    olap_db_conn.close() 


def car_repair_type_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading, last_etl_datetime):
    oltp_db_conn = pg2.connect(database=oltp_config_dict['database'], user=oltp_config_dict['user'], password=oltp_config_dict['password'])

    print(f"\nCAR REPAIR TYPE EXTRACT")
    car_repair_type_data = extract_car_repair_type_data(oltp_db_conn, initial_data_loading, last_etl_datetime=last_etl_datetime)
    print(f"car_repair_type_data = {car_repair_type_data}")

    oltp_db_conn.close()
    car_repair_fact_columns = [
        'c_repair_type'
    ]
    car_repair_type_df = pd.DataFrame(car_repair_type_data, columns=car_repair_fact_columns)

    print(f"\nCAR REPAIR TYPE TRANSFORM")
    check_dataframe(car_repair_type_df, important_columns=[], df_name='car_repair_type_df')
    
    olap_repair_types_list = []
    for _, row in car_repair_type_df.iterrows():

        olap_repair_type_obj = OLTP_to_OLAP_repair_type(row, car_repair_type_metadata=metadata['dimensions']['dim_car_repair_type'])
        olap_repair_types_list.append(olap_repair_type_obj)
    
    print(f"olap_repair_type_list = {olap_repair_types_list}")
    print(f"\nCAR REPAIR TYPE LOAD")
    olap_db_conn = pg2.connect(database=olap_config_dict['database'], user=olap_config_dict['user'], password=olap_config_dict['password'])
    
    # INSERT DATA INTO dim_seller table
    batch_size = 1000
    start_index = 0
    total_records = len(olap_repair_types_list)

    data_insertion_start_time = time.time()
    while start_index < total_records:

        end_index = min(start_index + batch_size, total_records)
        repair_type_batch_data = olap_repair_types_list[start_index:end_index]
        print(f"load_car_repair_type_dim")
        load_car_repair_type_dim(conn=olap_db_conn, repair_types=repair_type_batch_data, initial_data_loading=initial_data_loading)

        start_index += batch_size

    data_insertion_duration = time.time() - data_insertion_start_time
    print(f"Data insertion time: {data_insertion_duration // 60: .0f}m {data_insertion_duration % 60: .0f}s\n")
    olap_db_conn.close() 


def location_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading, last_etl_datetime):
    oltp_db_conn = pg2.connect(database=oltp_config_dict['database'], user=oltp_config_dict['user'], password=oltp_config_dict['password'])

    print(f"\nLOCATION EXTRACT")
    location_data = extract_location_data(conn=oltp_db_conn, initial_data_loading=initial_data_loading, last_etl_datetime=last_etl_datetime)

    if not initial_data_loading:
        print(f"Incremental data loading.")
        print(f"updated_location_data = {location_data}")
        print(f"len(updated_location_data) = {len(location_data)}")
    oltp_db_conn.close()

    location_columns = [
        'l_addr_oltp_id',
        'l_country', 'l_city',
        'l_street', 'l_postal_code'
    ]
    location_df = pd.DataFrame(location_data, columns=location_columns)

    print(f"\nLOCATION TRANSFORM")
    check_dataframe(location_df, important_columns=['l_addr_oltp_id'], df_name='location_df')

    # Create OLAP Location class instances
    olap_locations_list = []
    for _, row in location_df.iterrows():
        oltp_location_obj = create_address(row, prefix='l')

        olap_location_obj = OLTP_to_OLAP_location(oltp_location_obj, location_metadata=metadata['dimensions']['dim_location'])
        olap_locations_list.append(olap_location_obj)

    print(f"\nLOCATION LOAD")
    olap_db_conn = pg2.connect(database=olap_config_dict['database'], user=olap_config_dict['user'], password=olap_config_dict['password'])
    
    # INSERT DATA INTO dim_location table
    batch_size = 1000
    start_index = 0
    total_records = len(olap_locations_list)

    data_insertion_start_time = time.time()
    while start_index < total_records:

        end_index = min(start_index + batch_size, total_records)
        location_batch_data = olap_locations_list[start_index:end_index]
        load_location_dim(conn=olap_db_conn, location_dims=location_batch_data)

        start_index += batch_size

    data_insertion_duration = time.time() - data_insertion_start_time
    print(f"Data insertion time: {data_insertion_duration // 60: .0f}m {data_insertion_duration % 60: .0f}s\n")
    olap_db_conn.close()


def purchase_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading, last_etl_datetime):

    oltp_db_conn = pg2.connect(database=oltp_config_dict['database'], user=oltp_config_dict['user'], password=oltp_config_dict['password'])
    print(f"\nPURCHASE EXTRACT")
    
    purchase_data = extract_purchase_data(conn=oltp_db_conn, initial_data_loading=initial_data_loading, last_etl_datetime=last_etl_datetime, limit_records=100)
    """
    if not initial_data_loading:
        print(f"updated_fact_car_purchase_data: {purchase_data}")
        """
    oltp_db_conn.close()

    purchase_columns = [
        'c_vin', 'c_manufacture_year', 'c_make_name', 
        'c_model', 'c_trim', 'c_cbt_name', 
        'c_transmission', 'c_color_name',
        'e_oltp_id', 'e_first_name', 'e_last_name', 'e_middle_name',
        'e_birth_date', 'e_sex', 'e_email', 'e_position', 'e_salary', 'e_hire_date',
        's_id', 'p_address_id', 
        'p_price', 'p_odometer', 'p_condition', 'p_purchase_date'
    ]

    purchase_df = pd.DataFrame(purchase_data, columns=purchase_columns)

    print(f"\nPURCHASE TRANSFORM")
    check_dataframe(purchase_df, important_columns=['c_vin', 'e_oltp_id', 's_id', 'p_address_id'], df_name='purchase_df')

    purchase_df['p_purchase_month'] = purchase_df['p_purchase_date'].dt.month
    purchase_df['p_purchase_year'] = purchase_df['p_purchase_date'].dt.year

    purchase_df = purchase_df.sort_values(by=['e_oltp_id', 'p_purchase_date'])

    
    unique_employee_oltp_ids = set(purchase_df['e_oltp_id'].to_list())
    
    print(f"\nPURCHASE LOAD")
    olap_db_conn = pg2.connect(database=olap_config_dict['database'], user=olap_config_dict['user'], password=olap_config_dict['password'])
    print(f"len(unique_employee_oltp_ids) = {len(unique_employee_oltp_ids)}")
    print(f"unique_employee_oltp_ids = {unique_employee_oltp_ids}")

    # Create OLAP fact_car_purchase + dim_employee + dim_car + dim_date classes instances
    data_insertion_start_time = time.time()
    for employee_oltp_id in unique_employee_oltp_ids:
        employee_purchases_df = purchase_df[purchase_df['e_oltp_id'] == employee_oltp_id]
        # print(f"\nPurchases of employee with employee_oltp_id={employee_oltp_id} = \n{employee_purchases_df}")
        index = 0
        prev_year = None
        prev_month = None
        for  _, row in employee_purchases_df.iterrows():
            olap_purchase_obj = OLTP_to_OLAP_purchase_df(row, metadata=metadata)
            
            if index == 0:
                if initial_data_loading:
                    # print(f"fact_car_purchase initial data loading")

                    # Insert the first record into dim_emloyee table and other tables
                    load_fact_car_purchase(olap_db_conn, [olap_purchase_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)

                else:
                    """
                        It is necessary to understand whether to insert a new record in the dim_employee table or not in case of new records in the fact_car_purchase table:
                        1) If an employee with the specified employee_oltp_id already exists in the dim_employee table and his experience matches the work experience (fact_car_purchase.employee_experience) in the current fact_car_purchase object, then there is no need to insert a new record into the dim_employee table.
                        2) Otherwise (if there are no records in the dim_employee table with the specified employee_oltp_id or his experience is different, then we need to insert a new record in the dim_employee table).
                    """
                    query = """
                        DO
                        $$
                        DECLARE
                            employee_exists BOOLEAN;
                            employee_id_local INT;
                        BEGIN
                            DROP TABLE IF EXISTS temp_table;
                            -- Check if the record with the specified employee_oltp_id exists
                            SELECT EXISTS(SELECT 1 FROM dim_employee WHERE employee_oltp_id = %s) INTO employee_exists;

                            -- If the record exists, retrieve the corresponding employee_id
                            IF employee_exists THEN
                                SELECT employee_id INTO employee_id_local FROM dim_employee 
                                WHERE employee_oltp_id = %s AND is_valid = 1;
                                
                                CREATE TEMPORARY TABLE temp_table AS
                                -- Select the employee_experience from the fact_car_purchase table
                                SELECT employee_experience FROM fact_car_purchase 
                                WHERE employee_id = employee_id_local;
                            ELSE
                                CREATE TEMPORARY TABLE temp_table AS
                                SELECT -1;
                            END IF;  
                        END
                        $$;

                        SELECT * FROM temp_table;
                    """
                    with olap_db_conn.cursor() as cur:
                        cur.execute(query, (olap_purchase_obj.employee_dim.oltp_id, olap_purchase_obj.employee_dim.oltp_id))
                        # Fetch the results
                        data = cur.fetchall()
                    
                    prev_work_experience = data[0][0]

                    if prev_work_experience != olap_purchase_obj.employee_dim.work_experience:
                        load_fact_car_purchase(olap_db_conn, [olap_purchase_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)

            elif (prev_year != row['p_purchase_year']) or (prev_month != row['p_purchase_month']):
                load_fact_car_purchase(olap_db_conn, [olap_purchase_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)
            else:
                load_fact_car_purchase(olap_db_conn, [olap_purchase_obj], insert_new_employee=False, initial_data_loading=initial_data_loading)

            # print(f"olap_purchase_obj = {olap_purchase_obj}\n")
            prev_year = row['p_purchase_year']
            prev_month = row['p_purchase_month']
            index += 1
    data_insertion_duration = time.time() - data_insertion_start_time
    print(f"Data insertion time: {data_insertion_duration // 60: .0f}m {data_insertion_duration % 60: .0f}s\n")  
    olap_db_conn.close()  
    

def repair_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading, last_etl_datetime):
    oltp_db_conn = pg2.connect(database=oltp_config_dict['database'], user=oltp_config_dict['user'], password=oltp_config_dict['password'])
    print(f"\nREPAIR EXTRACT")
    
    repair_data = extract_repair_data(conn=oltp_db_conn, initial_data_loading=initial_data_loading, last_etl_datetime=last_etl_datetime, limit_records=10)
    """
    if not initial_data_loading:
        print(f"updated_fact_car_repair_data: {repair_data}")
        """
    oltp_db_conn.close()
    print(f"len(repair_data) = {len(repair_data)}")
    # print(f"repair_data = {repair_data}")

    repair_columns = [
        'r_oltp_id', 'c_vin',
        'e_oltp_id', 'e_first_name', 'e_last_name', 'e_middle_name',
        'e_birth_date', 'e_sex', 'e_email', 'e_position', 'e_salary', 'e_hire_date',
        'r_addr_oltp_id', 'r_country', 'r_city', 'r_street', 'r_postal_code', 
        'r_repair_type', 'r_cost', 'p_condition', 'r_condition', 'r_repair_date' 
    ]

    repair_df = pd.DataFrame(repair_data, columns=repair_columns)

    print(f"\nREPAIR TRANSFORM")
    check_dataframe(repair_df, important_columns=['r_oltp_id', 'c_vin', 'e_oltp_id', 'r_addr_oltp_id'], df_name='repair_df')

    repair_df['r_repair_month'] = repair_df['r_repair_date'].dt.month
    repair_df['r_repair_year'] = repair_df['r_repair_date'].dt.year

    repair_df = repair_df.sort_values(by=['e_oltp_id', 'r_repair_date'])
    print(f"repair_df.head(5) = \n{repair_df.head(5)}")
    
    unique_employee_oltp_ids = set(repair_df['e_oltp_id'].to_list())
    print(f"unique_employee_oltp_ids = {unique_employee_oltp_ids}")

    print(f"\nREPAIR LOAD")
    olap_db_conn = pg2.connect(database=olap_config_dict['database'], user=olap_config_dict['user'], password=olap_config_dict['password'])

    data_insertion_start_time = time.time()
    for employee_oltp_id in unique_employee_oltp_ids:
        employee_repairs_df = repair_df[repair_df['e_oltp_id'] == employee_oltp_id]
        index = 0
        prev_year = None
        prev_month = None
        for  _, row in employee_repairs_df.iterrows():

            olap_repair_obj = OLTP_to_OLAP_repair_df(row, metadata)
            if index == 0:
                if initial_data_loading:
                    # print(f"fact_car_repair initial data loading")

                    # Insert the first record into dim_emloyee table and other tables
                    load_fact_car_repair(olap_db_conn, [olap_repair_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)

                else:
                    """
                        It is necessary to understand whether to insert a new record in the dim_employee table or not in case of new records in the fact_car_purchase table:
                        1) If an employee with the specified employee_oltp_id already exists in the dim_employee table and his experience matches the work experience (fact_car_purchase.employee_experience) in the current fact_car_purchase object, then there is no need to insert a new record into the dim_employee table.
                        2) Otherwise (if there are no records in the dim_employee table with the specified employee_oltp_id or his experience is different, then we need to insert a new record in the dim_employee table).
                    """
                    query = """
                        DO
                        $$
                        DECLARE
                            employee_exists BOOLEAN;
                            employee_id_local INT;
                        BEGIN
                            DROP TABLE IF EXISTS temp_table;
                            -- Check if the record with the specified employee_oltp_id exists
                            SELECT EXISTS(SELECT 1 FROM dim_employee WHERE employee_oltp_id = %s) INTO employee_exists;

                            -- If the record exists, retrieve the corresponding employee_id
                            IF employee_exists THEN
                                SELECT employee_id INTO employee_id_local FROM dim_employee 
                                WHERE employee_oltp_id = %s AND is_valid = 1;
                                
                                CREATE TEMPORARY TABLE temp_table AS
                                -- Select the employee_experience from the fact_car_purchase table
                                SELECT employee_experience FROM fact_car_purchase 
                                WHERE employee_id = employee_id_local;
                            ELSE
                                CREATE TEMPORARY TABLE temp_table AS
                                SELECT -1;
                            END IF;  
                        END
                        $$;

                        SELECT * FROM temp_table;
                    """
                    """
                    with olap_db_conn.cursor() as cur:
                        cur.execute(query, (olap_repair_obj.employee_dim.oltp_id, olap_repair_obj.employee_dim.oltp_id))
                        # Fetch the results
                        data = cur.fetchall()
                    
                    prev_work_experience = data[0][0]
                    print(f"fact_car_purchase incremental data loading: data (employee work_experience) = {data}")
                    print(f"work_experience = {prev_work_experience}")
                    print(f"current work_experience = {olap_repair_obj.employee_dim.work_experience}")

                    if prev_work_experience != olap_repair_obj.employee_dim.work_experience:
                        print(f"{prev_work_experience} != {olap_repair_obj.employee_dim.work_experience}")
                        # Temporary condition
                        if prev_work_experience != -1:
                            load_fact_car_purchase(olap_db_conn, [olap_repair_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)
                """
            elif (prev_year != row['r_repair_year']) or (prev_month != row['r_repair_month']):
                load_fact_car_repair(olap_db_conn, [olap_repair_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)
            else:
                load_fact_car_repair(olap_db_conn, [olap_repair_obj], insert_new_employee=False, initial_data_loading=initial_data_loading)

            # print(f"olap_purchase_obj = {olap_purchase_obj}\n")
            prev_year = row['r_repair_year']
            prev_month = row['r_repair_month']
            index += 1
    data_insertion_duration = time.time() - data_insertion_start_time
    print(f"Data insertion time: {data_insertion_duration // 60: .0f}m {data_insertion_duration % 60: .0f}s\n")        
    olap_db_conn.close() 


def sale_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading, last_etl_datetime):
    oltp_db_conn = pg2.connect(database=oltp_config_dict['database'], user=oltp_config_dict['user'], password=oltp_config_dict['password'])
    print(f"\nSALE EXTRACT")
    
    sale_data = extract_sale_data(conn=oltp_db_conn, initial_data_loading=initial_data_loading, last_etl_datetime=last_etl_datetime, limit_records=10)
    """
    if not initial_data_loading:
        print(f"updated_fact_car_sale_data: {sale_data}")
    """
    oltp_db_conn.close()
    
    sale_columns = [
        'c_vin', 'c_manufacture_year',
        'b_oltp_id', 'b_first_name', 'b_last_name', 'b_middle_name',
        'b_birth_date', 'b_sex', 'b_email',
        's_addr_oltp_id', 's_country', 's_city', 's_street', 's_postal_code', 
        'e_oltp_id', 'e_first_name', 'e_last_name', 'e_middle_name',
        'e_birth_date', 'e_sex', 'e_email', 'e_position', 'e_salary', 'e_hire_date',
        's_mmr', 's_price', 's_odometer', 's_condition', 's_sale_date',
        'r_cost', 'p_price', 'p_purchase_date'
    ]

    sale_df = pd.DataFrame(sale_data, columns=sale_columns)

    print(f"\nSALE TRANSFORM")
    print(f"len(sale_df) = {len(sale_df)}")
    sale_df['r_cost'] = sale_df['r_cost'].fillna(0)
    check_dataframe(sale_df, important_columns=['c_vin', 'b_oltp_id', 's_addr_oltp_id', 'e_oltp_id'], df_name='sale_df')

    sale_df['s_sale_month'] = sale_df['s_sale_date'].dt.month
    sale_df['s_sale_year'] = sale_df['s_sale_date'].dt.year

    sale_df = sale_df.sort_values(by=['e_oltp_id', 's_sale_date'])
    print(f"sale_df.head(5) = \n{sale_df.head(5)}")
    
    unique_employee_oltp_ids = set(sale_df['e_oltp_id'].to_list())
    print(f"unique_employee_oltp_ids = {unique_employee_oltp_ids}")

    print(f"\nSALE LOAD")
    olap_db_conn = pg2.connect(database=olap_config_dict['database'], user=olap_config_dict['user'], password=olap_config_dict['password'])

    data_insertion_start_time = time.time()
    for employee_oltp_id in unique_employee_oltp_ids:
        employee_sales_df = sale_df[sale_df['e_oltp_id'] == employee_oltp_id]
        index = 0
        prev_year = None
        prev_month = None
        for  _, row in employee_sales_df.iterrows():

            olap_sale_obj = OLTP_to_OLAP_sale_df(row, metadata)

            if index == 0:
                if initial_data_loading:
                    print(f"fact_car_sale initial data loading")

                    # Insert the first record into dim_emloyee table and other tables
                    load_fact_car_sale(olap_db_conn, [olap_sale_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)
                else:
                    """
                        It is necessary to understand whether to insert a new record in the dim_employee table or not in case of new records in the fact_car_purchase table:
                        1) If an employee with the specified employee_oltp_id already exists in the dim_employee table and his experience matches the work experience (fact_car_purchase.employee_experience) in the current fact_car_purchase object, then there is no need to insert a new record into the dim_employee table.
                        2) Otherwise (if there are no records in the dim_employee table with the specified employee_oltp_id or his experience is different, then we need to insert a new record in the dim_employee table).
                    """
                    query = """
                        DO
                        $$
                        DECLARE
                            employee_exists BOOLEAN;
                            employee_id_local INT;
                        BEGIN
                            DROP TABLE IF EXISTS temp_table;
                            -- Check if the record with the specified employee_oltp_id exists
                            SELECT EXISTS(SELECT 1 FROM dim_employee WHERE employee_oltp_id = %s) INTO employee_exists;

                            -- If the record exists, retrieve the corresponding employee_id
                            IF employee_exists THEN
                                SELECT employee_id INTO employee_id_local FROM dim_employee 
                                WHERE employee_oltp_id = %s AND is_valid = 1;
                                
                                CREATE TEMPORARY TABLE temp_table AS
                                -- Select the employee_experience from the fact_car_purchase table
                                SELECT employee_experience FROM fact_car_purchase 
                                WHERE employee_id = employee_id_local;
                            ELSE
                                CREATE TEMPORARY TABLE temp_table AS
                                SELECT -1;
                            END IF;  
                        END
                        $$;

                        SELECT * FROM temp_table;
                    """
                    """
                    with olap_db_conn.cursor() as cur:
                        cur.execute(query, (olap_repair_obj.employee_dim.oltp_id, olap_repair_obj.employee_dim.oltp_id))
                        # Fetch the results
                        data = cur.fetchall()
                    
                    prev_work_experience = data[0][0]
                    print(f"fact_car_purchase incremental data loading: data (employee work_experience) = {data}")
                    print(f"work_experience = {prev_work_experience}")
                    print(f"current work_experience = {olap_repair_obj.employee_dim.work_experience}")

                    if prev_work_experience != olap_repair_obj.employee_dim.work_experience:
                        print(f"{prev_work_experience} != {olap_repair_obj.employee_dim.work_experience}")
                        # Temporary condition
                        if prev_work_experience != -1:
                            load_fact_car_purchase(olap_db_conn, [olap_repair_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)
                """

            elif (prev_year != row['s_sale_year']) or (prev_month != row['s_sale_month']):
                load_fact_car_sale(olap_db_conn, [olap_sale_obj], insert_new_employee=True, initial_data_loading=initial_data_loading)

            else:
                load_fact_car_sale(olap_db_conn, [olap_sale_obj], insert_new_employee=False, initial_data_loading=initial_data_loading)

            # print(f"olap_purchase_obj = {olap_purchase_obj}\n")
            prev_year = row['s_sale_year']
            prev_month = row['s_sale_month']
            index += 1
    
    data_insertion_duration = time.time() - data_insertion_start_time
    print(f"Data insertion time: {data_insertion_duration // 60: .0f}m {data_insertion_duration % 60: .0f}s\n")        
    olap_db_conn.close() 

