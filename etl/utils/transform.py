import re
import pandas as pd

# Function to check if a string matches a given pattern
def check_format(data, pattern):
    return bool(re.match(pattern, data))


def check_null_values(df, important_columns, df_name):
    # Check for null values in important columns
    for column in important_columns:
        if df[column].isnull().any():
            raise ValueError(f"DataFrame {df_name} contains null values in the '{column}' column. ETL process stopped.")
    
    # Check for null values in other columns
    for column in df.columns:
        if df[column].isnull().any():
            num_missing = df[column].isnull().sum()
            print(f"Column '{column}' has {num_missing} missing values.")

    # If any missing values are found, print a message
    if df.isnull().values.any():
        print(f"Note: DataFrame {df_name} contains missing values in some columns. ETL process continues.")



def check_dataframe(df, important_columns, df_name):
    print(f"Checking the {df_name} dataframe:")
    check_null_values(df, important_columns, df_name)

    # Output data types of DataFrame columns
    print(f"Data types of {df_name} columns before types transformations:")
    print(df.dtypes)

    for column in df.columns:
        if 'condition' in column:
            df[column] = df[column].astype(float)
        elif 'date' in column:
            df[column] = pd.to_datetime(df[column])

    print(f"Data types of {df_name} columns after types transformations:")
    print(df.dtypes)
