import pytest
from fixtures import *
from unittest.mock import patch
from jointSpendingCalculator import *
import os
import csv


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
        input_list = ['Sophie', 'Monzo']
        inputs = iter(input_list)
        with patch("builtins.input", side_effect=inputs):
            person, outgoings_column_name = whose_statement_and_which_bank(statements)
        assert person == "Sophie"
        assert outgoings_column_name == 'Amount'
    

class TestReadStatement:

    test_cases = [
        # Read Padme's statement - Jan pays for everything
        ( 
            "Padme",
            "cheaper_statement.csv",
            "Amount",
            "Jan", 
            {
                "owes":"Padme",
                "Jan":90.0,
                "Padme":0.0
            }
        ),

        # Read Reggie's statement - Jan and Sophie split everything
        ( 
            "Reggie", 
            "cheaper_statement.csv",
            "Amount", 
            "Jan Sophie", 
            {
                "owes": "Reggie",
                "Jan": 45.0,
                "Sophie": 45.0,
                "Reggie": 0.0                
            }
        ),

        # Read Jan's statement - Sophie, Jane, Sven split everything between them
        ( 
            "Jan",
            "cheaper_statement.csv",
            "Amount",
            "Sophie Jane Sven",
            {
                "owes": "Jan",
                "Sophie": 30.0,
                "Jane": 30.0,
                "Sven": 30.0,
                "Jan": 0.0
            }
        ),
        # Read Sophie's statement - Sophie and Lou split everything between them
        (
            "Sophie",
            "expensive_statement.csv",
            " Money Out",
            "Sophie Lou Nai",
            {
                "owes": "Sophie",
                "Sophie": 0.0,
                "Lou": 136.67,
                "Nai": 136.67
            }
        ),
        (
            "Sophie",
            "expensive_statement.csv",
            " Money Out",
            "*SKIP*",
            {
                "owes": "Sophie",
                "Sophie": 0.0
            }
        )
    ]

    @pytest.mark.parametrize("statement_owner,statement,outgoings_column,return_value,expected", test_cases)
    def test_read_statement(self, statement_owner, statement, outgoings_column, return_value, expected, directory):
        with patch("builtins.input", return_value=return_value):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(statement, outgoings_column, statement_owner, directory)
        
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
            "Amount",
            "Jan",
            "totals.csv",
            [
                {
                    "owes": "Denise",
                    "Jan": 90.0,
                    "Denise": 0.0
                }
            ]
        ),
        # Can update values  names already in the totals spreadsheet
        (
            "Sophie",
            "cheaper_statement.csv",
            "Amount",
            "Jan",
            "../prefilled_totals.csv",
            [
                {
                    "owes": "Sophie",
                    "Jan": 190.0,
                    "Sophie": 0.0
                },
                {
                    "owes": "Jan",
                    "Jan": 0.0,
                    "Sophie":10.0
                }
            ]
        ),
        # Can add new statement owner to the totals spreadsheet
        ( 
            "Martin",
            "expensive_statement.csv",
            " Money Out",
            "Petr Daniela Sophie Jan",
            "../prefilled_totals.csv",
            [
                {
                    "owes": "Sophie",
                    "Jan": 100.0,
                    "Sophie": 0.0,
                    "Petr": 0.0,
                    "Daniela": 0.0,
                    "Martin": 0.0
                },
                {
                    "owes": "Jan",
                    "Sophie": 10.0,
                    "Jan": 0.0,
                    "Petr": 0.0,
                    "Daniela": 0.0,
                    "Martin": 0.0
                },
                {
                    "owes": "Martin",
                    "Petr": 102.5,
                    "Daniela": 102.5,
                    "Jan": 102.5,
                    "Sophie": 102.5,
                    "Martin": 0.0
                }
            ]
        )
    ]

    @pytest.mark.parametrize("statement_owner,statement,outgoings_column,return_value,totals_statement,expected", test_cases)
    def test_can_merge_money_owed_with_values_in_totals_spreadsheet(self, statement_owner, statement, outgoings_column,return_value, expected, directory, totals_statement, totals_spreadsheet):
        dir = directory
        with patch("builtins.input", return_value=return_value):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(statement, outgoings_column, statement_owner, dir)
        updated_totals, _ = merge_owed_from_statement_with_totals(dir, everyone_who_owes_from_this_statement, statement_owner, totals_statement, owed_from_statement)
        assert expected == updated_totals


class TestWriteTotalsSpreadsheet:
    test_cases = [
        # Can read a statement, 1 person pays for everything
        # Can update values for names already in pre-populated totals statement
        # Can re-write spreadsheet with updated values
        (
            "Sophie",
            "cheaper_statement.csv",
            "Amount",
            "Jan",
            "../prefilled_totals.csv",
            [
                {
                    'owes': 'owes', 
                    'Jan': 'Jan', 
                    'Sophie': 'Sophie'
                },
                {
                    "owes": "Sophie",
                    "Jan": "190.0",
                    "Sophie": "0.0"
                },
                {
                    "owes": "Jan",
                    "Jan": "0.0",
                    "Sophie":"10.0"
                }
            ]
        ),
        # Can read a spreadsheet, 3 people split cost
        # Can merge with prefilled totals spreadsheet
        # Can write to totals statement
        (
            "Sophie",
            "cheaper_statement.csv",
            "Amount",
            "Jan Finn Lou",
            "../prefilled_totals.csv",
            [
                {
                    'owes': 'owes', 
                    'Jan': 'Jan', 
                    'Sophie': 'Sophie',
                    'Finn': 'Finn',
                    'Lou': 'Lou'
                },
                {
                    "owes": "Sophie",
                    "Jan": "130.0",
                    "Sophie": "0.0",
                    "Lou": "30.0",
                    "Finn": "30.0"
                },
                {
                    "owes": "Jan",
                    "Jan": "0.0",
                    "Sophie":"10.0",
                    "Finn":"0.0",
                    "Lou": "0.0"
                }
            ]
        ),
        # When statement owner pays for everything, 
        # then names already in the totals spreadsheet get value 0.0
        (
            "Lou",
            "cheaper_statement.csv",
            "Amount",
            "Lou",
            "../prefilled_totals.csv",
            [
                {
                    'owes': 'owes', 
                    'Jan': 'Jan', 
                    'Sophie': 'Sophie',
                    'Lou': 'Lou'
                },
                {
                    "owes": "Sophie",
                    "Jan": "100.0",
                    "Sophie": "0.0",
                    "Lou": "0.0"
                },
                {
                    "owes": "Jan",
                    "Jan": "0.0",
                    "Sophie":"10.0",
                    "Lou": "0.0"
                },
                {
                    "owes": "Lou",
                    "Jan": "0.0",
                    "Sophie": "0.0",
                    "Lou": "0.0"
                }
            ]
        )
    ]


    @pytest.mark.parametrize("statement_owner,statement,outgoings_column,return_value,totals_statement,expected", test_cases)
    def test_can_write_to_totals_spreadsheet(self, statement_owner, statement, outgoings_column, return_value, totals_statement, expected, totals_spreadsheet, directory):
        totals_sheet = totals_spreadsheet

        with patch("builtins.input", return_value=return_value):
            owed_from_statement, everyone_who_owes_from_this_statement = read_statement(statement, outgoings_column, statement_owner, directory)

        updated_totals, header = merge_owed_from_statement_with_totals(directory, everyone_who_owes_from_this_statement,statement_owner, totals_statement, owed_from_statement)        
        write_to_totals_spreadsheet(directory, header, totals_sheet, updated_totals)

        with open(directory + totals_sheet, "r") as t:
            reader = csv.DictReader(t, fieldnames=header)
            newly_written_totals_sheet = list(reader)
            assert newly_written_totals_sheet == expected 
    
        

    