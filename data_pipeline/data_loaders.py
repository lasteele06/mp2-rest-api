from pathlib import Path

import logging
import pandas as pd
import json
import yaml


# Do not call logging.basicConfig() here.
# Use the logging configuration from Part 1.
logger = logging.getLogger(__name__)


def load_csv(filepath):
    df = pd.read_csv(filepath)
    logger.info(f"Loaded CSV file: {filepath} ({len(df)} rows)")
    return df
    


def load_json(filepath):
    dj = json.load(open(filepath))
    logger.info(f"Loaded JSON file: {filepath}")
    return dj
    


def load_yaml(filepath):
    dy = yaml.safe_load(open(filepath))
    logger.info(f"Loaded YAML file: {filepath}")
    return dy
    


def load_data(filepath):
    path = Path(filepath)
    extension = path.suffix.lower()

    if extension == ".csv":
        return load_csv(path)
    elif extension == ".json":
        return load_json(path)
    elif extension == ".yaml":
        return load_yaml(path)
    else:
        logger.error(f"Unsupported file format: {extension}")
        raise ValueError(f"Unsupported file format: {extension}")
    
