# src/data_validator.py
import logging
import pandas as pd
logger = logging.getLogger(__name__)
def validate_dataframe(df, required_columns, numeric_columns):
#Validate the DataFrame and return valid data.
    rows_before = len(df)

    for col in required_columns:
        if col not in df.columns:
            logger.error(f"Missing required column: {col}")
            raise ValueError(f"Missing required column: {col}")
        
    # check that all the required columns exist
    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    logger.warning(f"Invalid numeric value in column '{col}' at row {i}: {value}")
                    invalid_rows.append(i)
        df = df.drop(index=invalid_rows)
        df[col] = pd.to_numeric(df[col])

    rows_after = len(df)

    logger.debug(
    f"Validation: {rows_before} rows before, "
    f"{rows_after} rows after validation."
)
                    


    return df