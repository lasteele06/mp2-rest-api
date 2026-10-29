import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )


def validate_input(filepath):
    path = Path(filepath)

    if not path.is_file():
        logger.error(f"Input file {filepath} does not exist.")
        return False

    logger.info(f"Input file validated: {filepath}")
    return True