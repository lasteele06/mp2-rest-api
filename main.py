import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import (
    DatasetInfo,
    DatasetStorage,
    HealthResponse,
    ProcessConfig,
    ProcessingReport,
    setup_logging,
    log_requests
)
from data_pipeline import (
    create_cleaning_report,
    process_data,
    validate_dataframe
)

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")

app.middleware("http")(log_requests)

storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""

    extension = Path(file.filename or "").suffix.lower()

    if extension != ".csv":
        logger.warning(f"Unsupported file format: {extension}")
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )

    # Read and parse CSV content into a DataFrame
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError
    ):
        logger.warning("Invalid CSV file")
        raise HTTPException(
            status_code=400,
            detail="Error reading CSV file"
        )

    # Save dataset to storage
    dataset_id = storage.save(df, file.filename)

    logger.info(
        f"Dataset saved with ID: {dataset_id}, "
        f"filename: {file.filename}, rows: {len(df)}"
    )

    return DatasetInfo(
        id=dataset_id,
        filename=file.filename,
        rows=len(df),
        columns=len(df.columns),
        column_names=df.columns.tolist()
    )

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""

    df = storage.get(dataset_id)

    if df is None:
        logger.warning(f"Dataset not found: {dataset_id}")
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )
    
    records = json.loads(df.head(limit).to_json(orient="records"))

    logger.info(
        f"Retrieved dataset: id={dataset_id}, "
        f"returned_rows={len(records)}"
    )

    return {
        "id": dataset_id,
        "data": records,
        "total_rows": len(df)
    }
@app.post(
    "/datasets/{dataset_id}/process",
    response_model=ProcessingReport
)
def process_dataset(dataset_id: int, config: ProcessConfig):
    """Validate and process a stored dataset using MP1 functions."""

    # 1. Retrieve dataset
    df = storage.get(dataset_id)

    if df is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # 2. Convert Pydantic model to dictionary
    config_dict = config.model_dump()

    # 3. Check numeric columns exist
    numeric_columns = config_dict["validation"]["numeric_columns"]

    for column in numeric_columns:
        if column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Numeric column not found: {column}"
            )

    try:
        # 4. Validate dataset
        original_rows = len(df)

        validated_df = validate_dataframe(
            df,
            config_dict["validation"]["required_columns"],
            numeric_columns
        )

        # 5. Count rows removed during validation
        validation_rows_removed = original_rows - len(validated_df)

        # Save copy before processing
        validated_copy = validated_df.copy()

        # 6. Process dataset using MP1
        processed_df = process_data(validated_df, config_dict)

        # 7. Generate cleaning report
        cleaning_report = create_cleaning_report(
            validated_copy,
            processed_df
        )

        # 8. Update the original stored dataset
        storage.update(dataset_id, processed_df)

        # 9. Log results
        logger.info(
            f"Dataset {dataset_id} processed: "
            f"validation removed {validation_rows_removed} rows, "
            f"cleaning report: {cleaning_report}"
        )

        # 10. Return response
        return {
            "id": dataset_id,
            "validation_rows_removed": validation_rows_removed,
            "cleaning_report": cleaning_report
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )