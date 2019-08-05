from fuzzywuzzy import process
from fuzzywuzzy import fuzz


def match_country_by_name(target: str, countries: list) -> str:
    """
    Find closest matching string in `countries` to `target`. We use the "token set ratio",
    as we want (for example) "Bolivia (Plurinational State of)" to be recognised as "Bolivia"
    across datasets. See fuzzywuzzy documentation for more details.
    https://github.com/seatgeek/fuzzywuzzy
    """
    return process.extractOne(target, countries, scorer=fuzz.token_set_ratio)