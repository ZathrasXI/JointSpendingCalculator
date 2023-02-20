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
    new_total_owed = merge_owed_with_totals(directory, statement_owner, totals_spreadsheet, owed_from_statement)
    print("NEW TOTAL", new_total_owed)
    write_to_spreadsheet_of_totals(directory, names, totals_spreadsheet, new_total_owed)


def read_statement(statement, statement_owner, directory):
    with open(directory + statement, "r") as persons_statement:
        statement_reader = csv.DictReader(persons_statement)
        print(f"For each transaction in {statement} enter the name of everyone who should pay for this item. Remember to include yourself...") # ..."by typing me." ?
        owed_from_current_statement = {"person_owed": statement_owner}
        for transaction in statement_reader:
            try:
                cost = float(transaction[" Money Out"])
            except TypeError and ValueError:
                continue
            print('__'*50)
            print(transaction)
            input_people_who_owe = input("Including yourself, list the people who should pay for this transaction: ")
            unformatted_list_of_people = input_people_who_owe.split(" ")
            people_who_owe = [person for person in unformatted_list_of_people if person != ""]
            how_much_each_person_owes = cost / len(people_who_owe)
            for person in people_who_owe:
                if person.lower() != statement_owner.lower():
                    if person not in owed_from_current_statement.keys():
                        owed_from_current_statement[person] = 0
                    owed_from_current_statement[person] += how_much_each_person_owes
    return owed_from_current_statement


def merge_owed_with_totals(directory, statement_owner, totals_csv, owed_from_current_statement):
    with open(directory + totals_csv, "r") as read_totals:
        totals_csv_object = csv.DictReader(read_totals)
        current_totals = list(totals_csv_object)
        people_currently_owed = [person["person_owed"] for person in current_totals if person["person_owed"] != statement_owner]
        print("PEOPLE CURRENTLY OWED", people_currently_owed)
        if current_totals:
            for person_owed in current_totals:
                if person_owed["person_owed"] == statement_owner:
                    for debtor in owed_from_current_statement.keys():
                        if debtor in person_owed.keys() and debtor != "person_owed":
                            debtor_currently_owes_total_sheet = float(person_owed[debtor])
                            person_owed[debtor] = debtor_currently_owes_total_sheet + owed_from_current_statement[debtor]
                elif statement_owner not in people_currently_owed:
                    current_totals.append(owed_from_current_statement)
        elif owed_from_current_statement:
            current_totals.append(owed_from_current_statement)
    print("CURRENT TOTALS", current_totals)
    return current_totals


def write_to_spreadsheet_of_totals(directory, names, totals_spreadsheet, totals):
    totals_header = ["person_owed"] + names
    with open(directory + totals_spreadsheet, "w") as ut:
        write_totals = csv.DictWriter(ut, fieldnames=totals_header)
        write_totals.writeheader()
        for person in totals:
            write_totals.writerow(person)





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