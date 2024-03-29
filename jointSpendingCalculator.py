import os
import csv
import pandas
import re

def add_trailing_slash_if_needed(directory_name):
    folder = directory_name
    if folder[-1] != '/':
        folder += '/'
    return folder

def get_names():
    names_input = input('Enter your names seperated by a space. ')
    names_raw = names_input.split(' ')
    names = [ name.strip().capitalize() for name in names_raw if name != '']
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
    statements.sort()
    return statements

def create_totals_file(folder):
    name_input = input('What would you like the spreadsheet with the final calculations to be called? ')
    filename = name_input + '.csv'
    directory = add_trailing_slash_if_needed(folder)
    path_to_file = directory + filename
    with open(path_to_file, 'w') as totals:
        column_names = ["owes"] 
        csv_writer = csv.DictWriter(totals, fieldnames=column_names)
        csv_writer.writeheader()
    return filename


def whose_statement_and_which_bank(statement):
    name = input(f"Who does this statement belong to: '{statement}'? ")
    banks = {
        "Co-operative": " Money Out",
        "Monzo": "Amount"
    }
    print("Which bank is the statement from?")
    for bank in banks:
        print(f" - {bank}")
    bank_name = input("")
    while bank_name.strip().capitalize() not in banks:
        bank_name = input('Bank not found. Please try again: ')
    return name, banks[bank_name.strip().capitalize()]

def convert_all_values_to_floats(totals_spreadsheet):
    for row in totals_spreadsheet:
        for person in row:
            if person != "owes":
                try:
                    row[person] = float(row[person])
                except ValueError:
                    row[person] = 0.0
    return totals_spreadsheet

def triage_transactions(statement, outgoings_column_name, directory, statement_owner, totals_spreadsheet):
    owed_from_statement, names = read_statement(statement, outgoings_column_name, statement_owner, directory)
    new_total_owed, header = merge_owed_from_statement_with_totals(directory, names, statement_owner, totals_spreadsheet, owed_from_statement)
    write_to_totals_spreadsheet(directory, header, totals_spreadsheet, new_total_owed)


def read_statement(statement, outgoings_column_name, statement_owner, directory):
    everyone_from_statement = [statement_owner]

    with open(directory + statement, "r") as persons_statement:
        statement_reader = csv.DictReader(persons_statement)
        print(f"For each transaction in {statement} enter the name of everyone who should pay for this item. Remember to include your name.") 
        print("TYPE '*SKIP*' to skip a transaction.")
        owes_from_statement = {"owes": statement_owner, statement_owner: 0.0}
        for transaction in statement_reader:
            try:
                cost = float(transaction[outgoings_column_name])
                price = re.search("[0-9.]+", transaction[outgoings_column_name])
                cost = float(price.group())
            except TypeError and ValueError:
                continue
            print(f"\n{transaction}\n")
            ask_for_names_of_people = input("Including yourself, list the people who should pay for this transaction: ")
            if ask_for_names_of_people.strip() == '*SKIP*':
                continue 
            list_of_names_unformatted = ask_for_names_of_people.split(" ")
            people_who_owe = [person.capitalize() for person in list_of_names_unformatted if person != ""]
            how_much_each_person_owes = round(cost / len(people_who_owe), 2)

            for person in people_who_owe:
                if person not in owes_from_statement: owes_from_statement[person] = 0.0
                if person.lower() != statement_owner.lower():
                    owes_from_statement[person] = round(owes_from_statement[person] + how_much_each_person_owes, 2)
            everyone_from_statement += people_who_owe
    return owes_from_statement, everyone_from_statement


def merge_owed_from_statement_with_totals(directory, names_from_statement, statement_owner, name_of_totals_spreadsheet, owed_from_current_statement):
    header = []
    with open(directory + name_of_totals_spreadsheet, "r") as read_totals:
        totals_csv_object = csv.DictReader(read_totals)
        header = list(totals_csv_object.fieldnames)
        for name in names_from_statement:
            if name not in header:
                header.append(name)

        totals_spreadsheet = convert_all_values_to_floats(list(totals_csv_object))
        people_who_owe_from_statement = list(owed_from_current_statement.keys())
        people_who_owe_from_statement.remove("owes")
        people_already_owed = []
        
        for row in totals_spreadsheet:
            people_already_owed.append(row["owes"])
            for name in names_from_statement:
                if name not in row:
                    row[name] = 0.0
            if row['owes'] == statement_owner:
                for person in people_who_owe_from_statement:
                    try:
                        row[person] += float(owed_from_current_statement[person])
                    except ValueError:
                        row[person] += float(owed_from_current_statement[person])

        
        if statement_owner not in people_already_owed:
            for person in header:
                if person not in owed_from_current_statement and person != 'owes':
                    owed_from_current_statement[person] = 0.0
            totals_spreadsheet.append(owed_from_current_statement)
            
        return totals_spreadsheet, header


def write_to_totals_spreadsheet(directory, header, totals_spreadsheet, new_total_owed):
    with open(directory + totals_spreadsheet, "w") as t:
        writer = csv.DictWriter(t,fieldnames=header)
        writer.writeheader()
        for row in new_total_owed:
            writer.writerow(row)

def create_table_in_html_file(folder, new_totals_spreadsheet):
    totals_csv = pandas.read_csv(folder + new_totals_spreadsheet)
    name_of_html = new_totals_spreadsheet[:-3] + 'html'
    totals_csv.to_html(folder + name_of_html)
    return name_of_html


def main():
    folder = find_folder()
    new_totals_spreadsheet = create_totals_file(folder)
    statements = get_statements(folder, new_totals_spreadsheet)
    for statement in statements:
        if statement != new_totals_spreadsheet:
            person, outgoings_column_name = whose_statement_and_which_bank(statement)
            triage_transactions(statement, outgoings_column_name, folder, person, new_totals_spreadsheet)
    
    html_file = create_table_in_html_file(folder, new_totals_spreadsheet)
    print(f'You can view a table of who owes whom what, by opening {folder}{html_file} in a web browser.')

if __name__ == "__main__":
    main()