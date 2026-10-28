import logging
logger = logging.getLogger(__name__)
class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df, filename):
        """Store a copy of the data and return a new integer ID."""
        self._counter += 1
        self._store[self._counter] = {
            "df": df.copy(),
            "filename": filename,
        }
        logger.debug(
            f"Stored dataset id = {self._counter}, rows = len[df]"
            )
        return self._counter
        
    def get(self, dataset_id):
        """Return a copy of the stored DataFrame, or None."""
        dataset = self._store.get(dataset_id)
        if dataset:
            return dataset["df"].copy()
        return None

    def get_metadata(self, dataset_id):
        """Return the dataset metadata, or None."""
        dataset = self._store.get(dataset_id)
        if dataset:
            df = dataset["df"]
            
            return {
            "id": dataset_id,
            "filename": dataset["filename"],
            "rows": len(df),
            "columns" : list(df.columns),
            "column_name": df.columns.tolist()
        }
        return None
    
    def update(self, dataset_id, df):
        """Replace an existing dataset; return True, or False if
missing."""
        dataset = self._store.get(dataset_id)
        if dataset:
            dataset["df"] = df.copy()
            return True
        return False
        