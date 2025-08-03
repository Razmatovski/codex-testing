import csv
import io
from typing import Iterable, List, Callable, Tuple, Any, Optional


def export_csv(query: Iterable, columns: List[Tuple[str, Callable[[Any], Any]]]) -> str:
    """Export iterable of objects to CSV string.

    Args:
        query: Iterable of objects to export.
        columns: List of tuples (header, getter) where getter takes an object
            and returns value for the column.

    Returns:
        CSV formatted string.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [header for header, _ in columns]
    writer.writerow(headers)
    for obj in query:
        writer.writerow([getter(obj) for _, getter in columns])
    return output.getvalue()


Validator = Callable[[List[str]], Optional[str]]
UpsertFn = Callable[[dict, int], Optional[str]]


def import_csv(
    stream: io.StringIO,
    validators: Iterable[Validator],
    upsert_fn: UpsertFn,
) -> List[str]:
    """Import data from CSV stream using validators and upsert function.

    Args:
        stream: Text stream containing CSV data.
        validators: Iterable of callables receiving fieldnames list and returning
            an error message or None.
        upsert_fn: Callable processing each row. It receives row dict and the
            current line number and returns optional error string.

    Returns:
        List of error messages collected during processing.
    """
    try:
        reader = csv.DictReader(stream)
    except Exception:
        return ["Invalid CSV"]

    errors: List[str] = []
    fieldnames = reader.fieldnames or []
    for validator in validators:
        err = validator(fieldnames)
        if err:
            errors.append(err)
    if errors:
        return errors

    for row in reader:
        err = upsert_fn(row, reader.line_num)
        if err:
            errors.append(err)
    return errors
