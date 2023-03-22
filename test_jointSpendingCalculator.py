import pytest
import unittest
from unittest.mock import patch
from jointSpendingCalculator import *
import os
import csv

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

@pytest.fixture
def totals_spreadsheet(directory):
    SPREADSHEET_NAME = "totals"
    with patch("builtins.input", return_value=SPREADSHEET_NAME):
        TOTALS_SPREADSHEET, HEADER = create_totals_file(directory)
    yield TOTALS_SPREADSHEET, HEADER
    os.remove(directory + TOTALS_SPREADSHEET)

@pytest.fixture
def statements(directory, totals_spreadsheet):
    totals_spreadsheet_name, _ = totals_spreadsheet
    s = get_statements(directory, totals_spreadsheet_name)
    return s

@pytest.fixture
def remove_totals_spreadsheet(directory, totals_spreadsheet):
    filename, _ = totals_spreadsheet
    os.remove(directory + filename)


class TestGetDetails:

    def test_which_folder_are_the_statements_in(self, directory):
        assert os.path.isdir(directory) is True
        assert directory[-1] == '/'


    def test_add_trailing_space(self, directory):
        folder_name = add_trailing_slash_if_needed(directory)
        assert folder_name[-1] == '/'


    def test_folder_contains_correct_statements(self, statements):
        statement_1 = 'jans_statement.csv'
        statement_2 = 'sophies_statement.csv'
        statement_3 = 'jans_coop_bank_statement.csv'
        assert statement_1 in statements
        assert statement_2 in statements
        assert statement_3 not in statements
        

    def test_create_totals_file(self, directory):
        with patch("builtins.input", return_value="totals"):
            spreadsheet, header = create_totals_file(directory)
        assert os.path.isfile(directory + spreadsheet) is True
        assert header == ['person_owed']


    def test_whose_statement_is_this(self, statements):
        with patch("builtins.input", return_value="Sophie"):
            person = whose_statement(statements)
        assert person == "Sophie"
        assert person != "Tom"
    

class TestReadStatement:

    def test_one_person_pays_for_all_transactions(self, directory):
        case = {   
                "statement_owner": "Sophie",
                "statement":"sophies_statement.csv",
                "return_value": "Jan",
                "expected": {
                    "person_owed":"Sophie",
                    "Jan":90.0
                }
            }
        with patch("builtins.input", return_value=case['return_value']):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(case["statement"], case['statement_owner'], directory)
        assert case['expected'] == owed_from_statement


    def test_2_people_go_halves_on_all_transactions(self, directory):
        case = {
                "statement_owner": "Sophie",
                "statement":"sophies_statement.csv",
                "return_value": "Jan James",
                "expected": {
                    "person_owed": "Sophie",
                    "Jan": 45.0,
                    "James": 45.0
                }
            }
        
        with patch("builtins.input", return_value=case['return_value']):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(case["statement"], case['statement_owner'], directory)
        assert case['expected'] == owed_from_statement


    def test_3_people_split_cost(self, directory):
        case = {   
                "statement_owner": "Jan",
                "statement":"sophies_statement.csv",
                "return_value": "Sophie Jane Sven",
                "expected": {
                    "person_owed": "Jan",
                    "Sophie": 30.0,
                    "Jane": 30.0,
                    "Sven": 30.0
                }
            }
        with patch("builtins.input", return_value=case['return_value']):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(case["statement"], case['statement_owner'], directory)
        assert case['expected'] == owed_from_statement


class TestMergeTotalsSpreadsheetWithOwedFromStatement:

    def test_can_merge_empty_totals_with_totals_from_statement(self, directory, totals_spreadsheet):
        totals, _ = totals_spreadsheet
        d = directory
        case = {
                "statement_owner": "Sophie",
                "return_value": "Jan",
                "statement": "sophies_statement.csv",
                "totals_spreadsheet": totals,
                "expected": {
                    "person_owed": "Sophie",
                    "Jan": 90.0,
                }
            }
        with patch("builtins.input", return_value=case['return_value']):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(case['statement'], case['statement_owner'], d)
        updated_totals, _ = merge_owed_from_statement_with_totals(d, everyone_who_owes_from_this_statement, case['statement_owner'], case['totals_spreadsheet'], owed_from_statement)
        assert case['expected'] == updated_totals[0]

    def test_can_update_prepopulated_totals_statement_one_person_paid_for_everything(self, directory):
        case = {
                "statement_owner": "Sophie",
                "return_value": "Jan",
                "statement": "sophies_statement.csv",
                "totals_spreadsheet": "../prefilled_totals.csv",
                "expected": [
                    {
                        "person_owed": "Sophie",
                        "Jan": 190.0,
                        "Sophie": 0.0
                    },
                    {
                        "person_owed": "Jan",
                        "Jan": 0.0,
                        "Sophie":10.0
                    }
                ]
            }
        with patch("builtins.input", return_value=case['return_value']):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(case['statement'], case['statement_owner'], directory)
    
        updated_totals, _ = merge_owed_from_statement_with_totals(directory, everyone_who_owes_from_this_statement,case['statement_owner'], case['totals_spreadsheet'], owed_from_statement)
        assert case['expected'][0] in updated_totals
        assert case['expected'][1] in updated_totals
        assert len(updated_totals) == 2


class TestWriteTotalsSpreadsheet:

    def test_can_write_to_totals_spreadsheet(self, totals_spreadsheet, directory):
        totals_sheet, header = totals_spreadsheet
        case = {
                "statement_owner": "Sophie",
                "return_value": "Jan",
                "statement": "sophies_statement.csv",
                "totals_spreadsheet": "../prefilled_totals.csv",
                "expected": [
                    {
                        'person_owed': 'person_owed', 
                        'Jan': 'Jan', 
                        'Sophie': 'Sophie'
                    },
                    {
                        "person_owed": "Sophie",
                        "Jan": "190.0",
                        "Sophie": "0.0"
                    },
                    {
                        "person_owed": "Jan",
                        "Jan": "0.0",
                        "Sophie":"10.0"
                    }
                ]
            }
        with patch("builtins.input", return_value=case['return_value']):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(case['statement'], case['statement_owner'], directory)
    
        updated_totals, header = merge_owed_from_statement_with_totals(directory, everyone_who_owes_from_this_statement,case['statement_owner'], case['totals_spreadsheet'], owed_from_statement)        
        write_to_totals_spreadsheet(directory, header, totals_sheet, updated_totals)

        with open(directory + totals_sheet, "r") as t:
            reader = csv.DictReader(t, fieldnames=header)
            print("FIELDNAMES", reader.fieldnames)
            list_of_rows = list(reader)
            assert case['expected'] == list_of_rows

