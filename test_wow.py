import unittest
from unittest.mock import patch
from wow import *
import os
import csv


class TestGetInformation(unittest.TestCase):
    FOLDER_NAME = 'test_data'
    with patch('builtins.input', return_value=FOLDER_NAME):
        DIRECTORY = find_folder()
    
    with patch("builtins.input", return_value="Jan Sophie"):
        NAMES = get_names()

    SPREADSHEET_NAME = "totals"
    with patch("builtins.input", return_value=SPREADSHEET_NAME):
        TOTALS_SPREADSHEET, HEADER = create_totals_file(DIRECTORY, NAMES)

    STATEMENTS = get_statements(DIRECTORY, TOTALS_SPREADSHEET)
    HEADER = ["person_owed"] + NAMES

    def clear_totals_spreadsheet(self):
        with open(self.DIRECTORY + self.TOTALS_SPREADSHEET, "w") as t:
            clear_spreadsheet = csv.DictWriter(t, self.HEADER)
            clear_spreadsheet.writeheader()

    def test_get_names(self):
            assert 'Jan' in self.NAMES
            assert 'Sophie' in self.NAMES
            assert ' ' not in self.NAMES


    def test_which_folder_are_the_statements_in(self):
        assert os.path.isdir(self.DIRECTORY) is True
        assert self.DIRECTORY[-1] == '/'


    def test_add_trailing_space(self):
        folder_name = add_trailing_slash_if_needed(self.FOLDER_NAME)
        assert folder_name[-1] == '/'


    def test_folder_contains_correct_statements(self):
        statement_1 = 'jans_statement.csv'
        statement_2 = 'sophies_statement.csv'
        statement_3 = 'jans_coop_bank_statement.csv'
        assert statement_1 in self.STATEMENTS
        assert statement_2 in self.STATEMENTS
        assert statement_3 not in self.STATEMENTS
        

    def test_create_totals_file(self):
        with patch("builtins.input", return_value="totals"):
            spreadsheet, header = create_totals_file(self.DIRECTORY, self.NAMES)
        assert spreadsheet == self.SPREADSHEET_NAME + ".csv"
        assert header == ['person_owed'] + self.NAMES
        assert os.path.isfile(self.DIRECTORY + self.TOTALS_SPREADSHEET) is True
        with open(self.DIRECTORY + self.TOTALS_SPREADSHEET) as totals:
            reader = csv.DictReader(totals)
            file_header = reader.fieldnames
            assert header == file_header

        self.clear_totals_spreadsheet()

    def test_whose_statement_is_this(self):
        with patch("builtins.input", return_value="Sophie"):
            person = whose_statement(self.STATEMENTS[0], self.NAMES)

        assert person == "Sophie"
        assert person != "Michael"


    def test_can_skip_transaction(self):
        # with open(self.DIRECTORY+self.STATEMENTS[0]) as sophies_statement:
        #     totals_csv = csv.DictReader(sophies_statement)
        #     number_of_transactions = len(list(totals_csv)) - 1

        # with patch("builtins.input", return_value="skip"):
        #     _, _ = triage_transactions(self.STATEMENTS[0], self.DIRECTORY, self.NAMES[1], self.NAMES, self.TOTALS_SPREADSHEET)

        # with open(self.DIRECTORY+self.STATEMENTS[0]) as totals:
        #     reader = csv.DictReader(totals)
        #     number_of_rows_in_totals = len(list(reader)) - 1
        # assert number_of_rows_in_totals == 0
        pass

    def test_one_person_paid_for_all_transactions(self):
        self.clear_totals_spreadsheet()
        with patch("builtins.input", return_value="Jan"):
            triage_transactions(self.STATEMENTS[0], self.DIRECTORY, self.NAMES[1], self.NAMES, self.TOTALS_SPREADSHEET)
        with open(self.DIRECTORY + self.TOTALS_SPREADSHEET, 'r') as totals:
            totals_dict = csv.DictReader(totals)
            totals_list = list(totals_dict)
            sophie_is_owed = {
                "person_owed":"Sophie",
                "Jan":"90.0",
                "Sophie":""
            }
            assert len(totals_list) > 0
            assert sophie_is_owed in totals_list
       

    def test_both_people_split_everything(self):
        self.clear_totals_spreadsheet()
        with patch("builtins.input", return_value="Jan Sophie"):
            triage_transactions(self.STATEMENTS[0], self.DIRECTORY, self.NAMES[0], self.NAMES, self.TOTALS_SPREADSHEET)
        jan_is_owed = {
            "person_owed":"Jan",
            "Jan":"",
            "Sophie":"45.0"
        }
        with open(self.DIRECTORY + self.TOTALS_SPREADSHEET, 'r') as totals:
            totals_dict = csv.DictReader(totals)
            totals_list = list(totals_dict)
   
            assert len(totals_list) > 0
            assert jan_is_owed in totals_list

    def test_update_total_that_a_person_owes(self):
        self.clear_totals_spreadsheet()
        with patch("builtins.input", return_value="Jan"):
            triage_transactions(self.STATEMENTS[0], self.DIRECTORY, self.NAMES[1], self.NAMES, self.TOTALS_SPREADSHEET)
        with patch("builtins.input", return_value="Jan Sophie"):
            triage_transactions(self.STATEMENTS[0], self.DIRECTORY, self.NAMES[1], self.NAMES, self.TOTALS_SPREADSHEET)
        
        sophies_total_owed_after_statement_triaged_twice = {
            "person_owed":"Sophie",
            "Sophie":"",
            "Jan":"135.0"
        }
        with open(self.DIRECTORY + self.TOTALS_SPREADSHEET, "r") as t:
            totals_sheet = csv.DictReader(t, self.HEADER)
            list_of_rows_totals_sheet = list(totals_sheet)
            assert len(list_of_rows_totals_sheet) > 0
            assert sophies_total_owed_after_statement_triaged_twice in list_of_rows_totals_sheet

            count_how_many_sophies = 0
            for row in list_of_rows_totals_sheet:
                if row["person_owed"] == "Sophie":
                    count_how_many_sophies += 1
            assert count_how_many_sophies == 1


    def test_can_write_totals_for_statements_from_2_different_people(self):
        self.clear_totals_spreadsheet()

        with patch("builtins.input", return_value="Jan"):
            triage_transactions(self.STATEMENTS[0], self.DIRECTORY, self.NAMES[1], self.NAMES, self.TOTALS_SPREADSHEET)

        with patch("builtins.input", return_value="Sophie"):
            triage_transactions(self.STATEMENTS[1], self.DIRECTORY, self.NAMES[0], self.NAMES, self.TOTALS_SPREADSHEET)

        jan_is_owed = {
            "person_owed":"Jan",
            "Sophie":"410.0",
            "Jan":""
        }
        sophie_is_owed = {
            "person_owed":"Sophie",
            "Sophie":"",
            "Jan":"90.0"
        }
        with open(self.DIRECTORY + self.TOTALS_SPREADSHEET, "r") as totals:
            totals_reader = csv.DictReader(totals, self.HEADER)
            list_of_totals = list(totals_reader)
            assert len(list_of_totals) == 3
            assert list_of_totals == [jan_is_owed, sophie_is_owed]


    def test_read_statement(self):
        with patch("builtins.input", return_value="Jan"):
            owed_from_statement = read_statement(self.STATEMENTS[0], self.NAMES[1], self.DIRECTORY)
        sophie_is_owed = {
            "person_owed":"Sophie",
            "Jan": 90.0
        }
        assert sophie_is_owed == owed_from_statement


    def test_can_merge_total_owed_from_statement_with_empty_total_spreadsheet(self):
        with patch("builtins.input", return_value="Jan"):
            owed_from_statement = read_statement(self.STATEMENTS[0], self.NAMES[1], self.DIRECTORY)
        
        updated_totals = merge_owed_with_totals(self.DIRECTORY, self.NAMES[1], self.TOTALS_SPREADSHEET, owed_from_statement)
        sophies_new_total_owed = {
            "person_owed":"Sophie",
            "Jan": 90.0
        }
        assert updated_totals[0] == sophies_new_total_owed


    def test_write_new_total(self):
        owed_from_statement = []
        with patch("builtins.input", return_value="Jan"):
            owed_from_statement.append(read_statement(self.STATEMENTS[0], self.NAMES[1], self.DIRECTORY))

        write_to_spreadsheet_of_totals(self.DIRECTORY, self.NAMES, self.TOTALS_SPREADSHEET, owed_from_statement)

        with open(self.DIRECTORY + self.TOTALS_SPREADSHEET, "r") as t:
            header = ["person_owed"] + self.NAMES
            totals_spreadsheet = list(csv.DictReader(t, header))

        sophie_is_owed = {
            "person_owed":"Sophie",
            "Jan": "90.0",
            "Sophie": ""
        }
        assert len(totals_spreadsheet)
        assert sophie_is_owed in totals_spreadsheet




    @classmethod
    def tearDownClass(self) -> None:
        os.remove(self.DIRECTORY + self.TOTALS_SPREADSHEET)