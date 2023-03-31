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

@pytest.fixture
def remove_totals_spreadsheet(directory, totals_spreadsheet):
    filename = totals_spreadsheet
    os.remove(directory + filename)


class TestGetDetails:

    def test_which_folder_are_the_statements_in(self, directory):
        assert os.path.isdir(directory) is True
        assert directory[-1] == '/'


    def test_add_trailing_space(self, directory):
        folder_name = add_trailing_slash_if_needed(directory)
        assert folder_name[-1] == '/'


    def test_folder_contains_correct_statements(self, statements):
        statement_1 = 'expensive_statement.csv'
        statement_2 = 'cheaper_statement.csv'
        statement_3 = 'jans_coop_bank_statement.csv'
        assert statement_1 in statements
        assert statement_2 in statements
        assert statement_3 not in statements
        

    def test_create_totals_file(self, directory):
        with patch("builtins.input", return_value="totals"):
            spreadsheet = create_totals_file(directory)
        assert os.path.isfile(directory + spreadsheet) is True


    def test_whose_statement_is_this(self, statements):
        with patch("builtins.input", return_value="Sophie"):
            person = whose_statement(statements)
        assert person == "Sophie"
        assert person != "Tom"
    

class TestReadStatement:

    test_cases = [
        # Read Padme's statement - Jan pays for everything
        ( 
            "Padme",
            "cheaper_statement.csv",
            "Jan", 
            {
                "person_owed":"Padme",
                "Jan":90.0
            }
        ),

        # Read Reggie's statement - Jan and Sophie split everything
        ( 
            "Reggie", 
            "cheaper_statement.csv", 
            "Jan Sophie", 
            {
                "person_owed": "Reggie",
                "Jan": 45.0,
                "Sophie": 45.0                
            }
        ),

        # Read Jan's statement - Sophie, Jane, Sven split everything between them
        ( 
            "Jan",
            "cheaper_statement.csv",
            "Sophie Jane Sven",
            {
                "person_owed": "Jan",
                "Sophie": 30.0,
                "Jane": 30.0,
                "Sven": 30.0
            }
        ),
        # Read Sophie's statement - Sophie and Lou split everything between them
        (
            "Sophie",
            "expensive_statement.csv",
            "Sophie Lou Nai",
            {
                "person_owed": "Sophie",
                "Sophie": 0.0,
                "Lou": 136.67,
                "Nai": 136.67
            }
        )
    ]

    @pytest.mark.parametrize("statement_owner,statement,return_value,expected", test_cases)
    def test_read_statement(self, statement_owner, statement, return_value, expected, directory):
        with patch("builtins.input", return_value=return_value):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(statement, statement_owner, directory)
        
        people = return_value.split(' ')
        assert expected == owed_from_statement
        assert people.sort() == everyone_who_owes_from_this_statement.sort()


class TestReadThenMerge:
    '''Merge the values owed from a statement with the values in a totals spreadsheet'''
    test_cases = [
        # Can add values to an empty totals spreadsheet
        ( 
            "Denise",
            "cheaper_statement.csv",
            "Jan",
            "totals.csv",
            [
                {
                    "person_owed": "Denise",
                    "Jan": 90.0
                }
            ]
        ),
        # Can update values  names already in the totals spreadsheet
        (
            "Sophie",
            "cheaper_statement.csv",
            "Jan",
            "../prefilled_totals.csv",
            [
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
        ),
        # Can add new statement owner to the totals spreadsheet
        ( 
            "Martin",
            "expensive_statement.csv",
            "Petr Daniela Sophie Jan",
            "../prefilled_totals.csv",
            [
                {
                    "person_owed": "Sophie",
                    "Jan": 100.0,
                    "Sophie": 0.0
                },
                {
                    "person_owed": "Jan",
                    "Sophie": 10.0,
                    "Jan": 0.0
                },
                {
                    "person_owed": "Martin",
                    "Petr": 102.5,
                    "Daniela": 102.5,
                    "Jan": 102.5,
                    "Sophie": 102.5
                }
            ]
        )
    ]

    @pytest.mark.parametrize("statement_owner,statement,return_value,totals_statement,expected", test_cases)
    def test_can_merge_money_owed_with_values_in_totals_spreadsheet(self, statement_owner, statement, return_value, expected, directory, totals_statement, totals_spreadsheet):
        dir = directory
        if totals_statement == "totals.csv":
            totals = totals_spreadsheet
        else:
            totals = totals_statement

        with patch("builtins.input", return_value=return_value):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(statement, statement_owner, dir)
        updated_totals, _ = merge_owed_from_statement_with_totals(dir, everyone_who_owes_from_this_statement, statement_owner, totals, owed_from_statement)
        assert expected == updated_totals


class TestWriteTotalsSpreadsheet:
    test_cases = [
        (
            "Sophie",
            "Jan",
            "cheaper_statement.csv",
            "../prefilled_totals.csv",
            [
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
        )
    ]

    
    @pytest.mark.parametrize("statement_owner,return_value,statement,totals_statement,expected", test_cases)
    def test_can_write_to_totals_spreadsheet(self, statement_owner, return_value, statement, totals_statement, expected, totals_spreadsheet, directory):
        totals_sheet = totals_spreadsheet

        with patch("builtins.input", return_value=return_value):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(statement, statement_owner, directory)

        if totals_statement == '../prefilled_totals.csv':
            totals = totals_statement
        else:
            totals = totals_statement

        updated_totals, header = merge_owed_from_statement_with_totals(directory, everyone_who_owes_from_this_statement,statement_owner, totals, owed_from_statement)        
        write_to_totals_spreadsheet(directory, header, totals_sheet, updated_totals)

        with open(directory + totals_sheet, "r") as t:
            reader = csv.DictReader(t, fieldnames=header)
            print("FIELDNAMES", reader.fieldnames)
            list_of_rows = list(reader)
            assert expected == list_of_rows

