# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    before_count = len(df)
    df_cleaned = df.drop_duplicates()
    after_count = len(df_cleaned)
    logger.debug(f"Removed {before_count - after_count} duplicate rows.")
    return df_cleaned


def handle_missing(df, axis="rows"):
     if axis not in["rows", "columns"]:
        logger.error(f"Invalid axis value: {axis}. Must be 'rows' or 'columns'.")
        raise ValueError(f"Invalid axis value: {axis}. Must be 'rows' or 'columns'.")

     if axis == "rows":
        before_count = len(df)
        df_cleaned = df.dropna(axis=0)
        after_count = len(df_cleaned)
        logger.debug(f"Removed {before_count - after_count} rows with missing values.")
     else:
        before_count = len(df.columns)
        df_cleaned = df.dropna(axis=1)
        after_count = len(df_cleaned.columns)
        logger.debug(f"Removed {before_count - after_count} columns with missing values.")
     return df_cleaned


def remove_outliers(df, columns, method, threshold):
    if method not in ["iqr", "zscore"]:
        logger.error(f"Invalid method: {method}. Must be 'iqr' or 'zscore'.")
        raise ValueError(f"Invalid method: {method}. Must be 'iqr' or 'zscore'.")
    for column in columns:
        if column not in df.columns:
            logger.warning(f"Column is not found: {column} ")
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            logger.warning(f"Column is not numeric: {column}")
            continue
        before_count = len(df)
        if method == "iqr":
         q1 = df[column].quantile(0.25)
         q3 = df[column].quantile(0.75)
         iqr = q3 - q1
         lower_bound = q1 - threshold * iqr
         upper_bound = q3 + threshold * iqr
         df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        elif method == "zscore":
            mean = df[column].mean()
            std = df[column].std()

            if std == 0:
                continue

            z_scores = (df[column] - mean) / std
            df = df[abs(z_scores) <= threshold]
        
        logger.debug(f"{column}: method={method}, " 
        f"threshold={threshold}, "
        f"removed={before_count - len(df)} rows")

    return df


def process_data(df, config):
     processing = config["processing"]
     if processing.get("remove_duplicates"):
        df = remove_duplicates(df)
    
     if processing["missing"]["enabled"]:
        axis = processing["missing"]["axis"]
        df = handle_missing(df, axis)
    
     if processing["outliers"]["enabled"]:
        columns = processing["outliers"]["columns"]
        method = processing["outliers"]["method"]
        threshold = processing["outliers"]["threshold"]
        df = remove_outliers(df, columns, method, threshold)
   



     return df


def create_cleaning_report(df_before, df_after):
    report = {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": len(df_before.columns) - len(df_after.columns),
    }
    return report