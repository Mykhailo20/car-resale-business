import pandas as pd

from car_resale_business_project.config.data_config import MIN_CAR_SALE_PRICE


def prepare_car_df(filepath, samples_no, oltp_logger):
    try:
        oltp_logger.info("\nStarting car_df preparation process...")
        
        car_df = pd.read_csv(filepath)
        car_df = car_df.sample(n=samples_no, random_state=42)

        # parse saledate columns
        car_df['sale_timestamp'] = pd.to_datetime(car_df['sale_timestamp'])
        car_df['sale_date'] = pd.to_datetime(car_df['sale_date'])
        car_df['sale_date_fake'] = pd.to_datetime(car_df['sale_date_fake'])
        
        if len(car_df[car_df['sale_date'].dt.year < car_df['year']]) != 0:
            oltp_logger.warning("Found invalid sale_date values with car.manufacture_year > sale.sale_date. These records will be rejected because they are incorrect from a business logic point of view. Example: %s. Number of discarded records: %s.", car_df[car_df['sale_date'].dt.year < car_df['year']].iloc[0], len(car_df[car_df['sale_date'].dt.year < car_df['year']]))

            car_df = car_df[car_df['sale_date'].dt.year >= car_df['year']]

        if len(car_df[car_df['sale_date_fake'].dt.year < car_df['year']]) != 0:
            oltp_logger.warning("Found invalid sale_date_fake values with car.manufacture_year > sale.sale_date_fake. These records will be rejected because they are incorrect from a business logic point of view. Example: %s. Number of discarded records: %s.", car_df[car_df['sale_date_fake'].dt.year < car_df['year']].iloc[0], len(car_df[car_df['sale_date_fake'].dt.year < car_df['year']]))

            car_df = car_df[car_df['sale_date_fake'].dt.year >= car_df['year']]

        duplicate_vins = car_df.groupby('vin').size()
        # Filter out VINs that have only one occurrence
        duplicate_vins = duplicate_vins[duplicate_vins > 1]
        if not duplicate_vins.empty:
            oltp_logger.warning("Duplicate car VINs found: %s. Duplicates will be deleted to ensure the correct operation of the program. Number of discarded records: %s.", duplicate_vins, len(duplicate_vins))
            car_df = car_df.drop_duplicates(subset='vin')

        if len(car_df[car_df['sellingprice'] < MIN_CAR_SALE_PRICE]) > 0:
            oltp_logger.warning("A car saleprice value less than MIN_CAR_SALE_PRICE = 4000 was found. These records will be discarded to ensure the correctness of the random data generation. Example: %s. Number of discarded records: %s.", car_df[car_df['sellingprice'] < MIN_CAR_SALE_PRICE].iloc[0], len(car_df[car_df['sellingprice'] < MIN_CAR_SALE_PRICE]))

            car_df[car_df['sellingprice'] >= MIN_CAR_SALE_PRICE]

        oltp_logger.info("Car_df preparation process completed successfully.")
        
    except Exception as e:
        oltp_logger.error("Error occurred while preparing car_df: %s", e, exc_info=True)
        raise

    return car_df