import os
import csv

def add_trailing_slash_if_needed(directory_name):
    folder = directory_name
    if folder[-1] != '/':
        folder += '/'
    return folder

def get_names():
    names_input = input('Enter your names seperated by a space. ')
    names = names_input.split(' ')
    return names

def find_folder():
    folder = input('What is the name of the folder your statements are in? ')
    directory_name = add_trailing_slash_if_needed(folder)
    if os.path.isdir(directory_name):
        return directory_name
    else:
        print('Folder not found.')

def get_statements(folder, totals_spreadsheet):
    statements = os.listdir(folder)
    statements.remove(totals_spreadsheet)
    return statements

def create_totals_file(folder, names):
    name_input = input('What would you like the spreadsheet with the final calculations to be called? ')
    filename = name_input + '.csv'
    directory = add_trailing_slash_if_needed(folder)
    path_to_file = directory + filename
    with open(path_to_file, 'w') as totals:
        column_names = ["person_owed"] + names
        csv_writer = csv.DictWriter(totals, fieldnames=column_names)
        csv_writer.writeheader()
    return filename, column_names

def whose_statement(statement, people):
    name = ""
    while name not in people:
        name = input(f"Who does this statement belong to: '{statement}'? ")
    return name


def triage_transactions(statement, directory, statement_owner, names, totals_spreadsheet):
    owed_from_statement = read_statement(statement, statement_owner, directory)
    new_total_owed = merge_owed_from_statement_with_totals(directory, statement_owner, totals_spreadsheet, owed_from_statement)


def read_statement(statement, statement_owner, directory):
    with open(directory + statement, "r") as persons_statement:
        statement_reader = csv.DictReader(persons_statement)
        print(f"For each transaction in {statement} enter the name of everyone who should pay for this item. Remember to include yourself...") # ..."by typing me." ?
        owes_from_statement = {"person_owed": statement_owner}
        for transaction in statement_reader:
            try:
                cost = float(transaction[" Money Out"])
            except TypeError and ValueError:
                continue
            print('__'*50)
            print(transaction)
            ask_for_names_of_people = input("Including yourself, list the people who should pay for this transaction: ")
            list_of_names_needs_empty_spaces_removed = ask_for_names_of_people.split(" ")
            people_who_owe = [person for person in list_of_names_needs_empty_spaces_removed if person != ""]
            how_much_each_person_owes = cost / len(people_who_owe)
            for person in people_who_owe:
                if person not in owes_from_statement: owes_from_statement[person] = 0.0
                if person.lower() != statement_owner.lower():
                    owes_from_statement[person] += how_much_each_person_owes
    return owes_from_statement


def merge_owed_from_statement_with_totals(directory, statement_owner, name_of_totals_spreadsheet, owed_from_current_statement):
    with open(directory + name_of_totals_spreadsheet, "r") as read_totals:
        totals_csv_object = csv.DictReader(read_totals)
        totals_spreadsheet_values_are_strings = list(totals_csv_object)
        print("AS STRINGS", totals_spreadsheet_values_are_strings)
        totals_spreadsheet = convert_all_values_to_floats(statement_owner, totals_spreadsheet_values_are_strings)
        print("AS FLOATS", totals_spreadsheet)
        statement = owed_from_current_statement
        people_who_owe_statement_owner_from_this_statement = list(statement.keys())
        people_who_owe_statement_owner_from_this_statement.remove("person_owed")
        people_owed_in_totals_spreadsheet = [person["person_owed"] for person in totals_spreadsheet if person["person_owed"] != statement_owner]
        # If statement owner already has a row in totals spreadsheet
        for row in totals_spreadsheet:
            if row["person_owed"] == statement_owner:
                    for person in people_who_owe_statement_owner_from_this_statement:
                        try:
                            row[person] = float(row[person]) + statement[person]
                        except KeyError:
                            row.update({
                                person: row[person]
                            })
        # If statement owner doesn't have a row in totals spreadsheet
        if statement_owner not in people_owed_in_totals_spreadsheet:
            totals_spreadsheet.append(statement)
    return totals_spreadsheet

def convert_all_values_to_floats(statement_owner, totals_spreadsheet):
    for row in totals_spreadsheet:
        for person in row:
            if person != "person_owed":
                try:
                    row[person] = float(row[person])
                except ValueError:
                    row[person] = 0.0
    return totals_spreadsheet


def main():
    names = get_names()
    folder = find_folder()
    new_totals_spreadsheet, spreadsheet_header = create_totals_file(folder, names)
    statements = get_statements(folder, new_totals_spreadsheet)
    for statement in statements:
        if statement != new_totals_spreadsheet:
            person = whose_statement(statement, names)
            triage_result = triage_transactions(statement, folder, person, names, new_totals_spreadsheet)
    
if __name__ == "__main__":
    main()