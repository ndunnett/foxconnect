import pickle
from collections.abc import Iterator
from pathlib import Path

from utils import gc_disabled

from .models import Data
from .parsing import generate_data


def initialise_data(data_pickle_path: Path, dump_file_glob: Iterator[Path]) -> Data:
    """Load pickled data if it exists otherwise generate and pickle data."""
    with gc_disabled():
        if data_pickle_path.is_file():
            with open(data_pickle_path, mode="rb") as file:
                data = pickle.load(file)  # noqa: S301

        else:
            data = generate_data(dump_file_glob)
            data_pickle_path.parent.resolve().mkdir(parents=True, exist_ok=True)

            with open(data_pickle_path, mode="wb") as file:
                pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

    return data
