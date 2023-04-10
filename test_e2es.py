from fixtures import *
from jointSpendingCalculator import *

def test_2_other_people_split_first_file_statement_owner_pays_for_second(monkeypatch, directory, totals_spreadsheet):
    '''
    Two friends of the statement owner split the cost of all of the transactions in the first statement
    The statement owner of the 2nd statement pays for all of their transactions 
    '''
    mocked_input = iter([
        'test_data', 'totals', 
        'Jan',
        'Co-operative',
        'Padme Reggie', 'Padme Reggie', 'Padme Reggie',
        'Reggie',
        'Monzo',
        'Reggie', 'Reggie', 'Reggie'
        ])
    monkeypatch.setattr('builtins.input', lambda _:next(mocked_input))
    expected = [
        {
        'Padme': '205.0', 
        'Reggie': '205.0', 
        'Jan': '0.0', 
        'owes': 'Jan'
        }, 
        {
        'Padme': '0.0', 
        'Reggie': '0.0', 
        'Jan': '0.0', 
        'owes': 'Reggie'
        }
    ]
    main()

    with open(directory + totals_spreadsheet, 'r') as t:
        t_s = csv.DictReader(t)
        totals_sheet = list(t_s)
        assert totals_sheet == expected


def test_SO_and_4_friends_split_first_transaction_and_a_few_pay_for_last_statement(monkeypatch, directory, totals_spreadsheet):
    '''
    The statement owner and 4 friends split each transaction in the first statement
    Different people pay for the transactions in the 2nd statement
    '''
    mocked_input = iter([
        'test_data', 'totals', 
        'Jan',
        'Co-operative',
        'Jan Padme Reggie Sophie Lou', 'Jan Lou Sophie Padme Reggie', 'Padme Sophie Lou Jan Reggie',
        'Reggie',
        'Monzo',
        'Albert John', 'Thomas Reggie', 'Reggie Padme'
        ])
    monkeypatch.setattr('builtins.input', lambda _:next(mocked_input))
    expected = [
        {
        'Albert':'0.0',
        'Jan': '0.0',
        'John':'0.0',
        'Lou':'82.0',
        'Padme': '82.0', 
        'Sophie':'82.0',
        'Reggie': '82.0', 
        'Thomas':'0.0',
        'owes': 'Jan'
        }, 
        {
        'Albert':'7.5',
        'Jan': '0.0',
        'John':'7.5',
        'Lou':'0.0',
        'Padme': '27.5', 
        'Reggie': '0.0', 
        'Sophie':'0.0',
        'Thomas':'10.0',
        'owes': 'Reggie'
        }
    ]
    main()

    with open(directory + totals_spreadsheet, 'r') as t:
        t_s = csv.DictReader(t)
        totals_sheet = list(t_s)
        assert totals_sheet == expected


def test_2_statements_from_the_same_person(monkeypatch, directory, totals_spreadsheet):
    '''
    The same statement owner for 2 separate statements
    '''
    mocked_input = iter([
        'test_data', 'totals', 
        'Jan',
        'Co-operative',
        'Jan Padme Reggie Sophie Lou', 'Jan Lou Sophie Padme Reggie', 'Padme Sophie Lou Jan Reggie',
        'Jan',
        'Monzo',
        'Albert John', 'Thomas Reggie', 'Reggie Padme'
        ])
    monkeypatch.setattr('builtins.input', lambda _:next(mocked_input))
    expected = [
        {
        'Albert':'7.5',
        'Jan': '0.0',
        'John':'7.5',
        'Lou':'82.0',
        'Padme': '109.5', 
        'Sophie':'82.0',
        'Reggie': '119.5', 
        'Thomas':'10.0',
        'owes': 'Jan'
        }
    ]
    main()

    with open(directory + totals_spreadsheet, 'r') as t:
        t_s = csv.DictReader(t)
        totals_sheet = list(t_s)
        assert totals_sheet == expected