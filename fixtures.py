import pytest
from jointSpendingCalculator import *
from unittest.mock import patch

@pytest.fixture
def directory():
    with patch('builtins.input', return_value='test_data'):
        DIRECTORY = find_folder()
    return DIRECTORY    

@pytest.fixture
def names():
    with patch("builtins.input", return_value="Jan Sophie"):
        NAMES = get_names()
    return NAMES

@pytest.fixture()
def totals_spreadsheet(directory):
    SPREADSHEET_NAME = "totals"
    with patch("builtins.input", return_value=SPREADSHEET_NAME):
        TOTALS_SPREADSHEET = create_totals_file(directory)
    yield TOTALS_SPREADSHEET
    os.remove(directory + TOTALS_SPREADSHEET)

@pytest.fixture
def statements(directory, totals_spreadsheet):
    totals_spreadsheet_name = totals_spreadsheet
    s = get_statements(directory, totals_spreadsheet_name)
    return s

