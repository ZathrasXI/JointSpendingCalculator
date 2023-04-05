from fixtures import *
from jointSpendingCalculator import *

def test_2_other_people_split_first_file_statement_owner_pays_for_second(monkeypatch, directory, totals_spreadsheet):
    '''
    Two friends of the statement owner split the cost of all of the transactions in the first statement
    The statement owner of the 2nd statement pays for all of their transactions 
    '''
    inputs = iter([
        'test_data', 'totals', 
        'jan',
        'Padme Reggie', 'Padme Reggie', 'Padme Reggie',
        'Reggie',
        'Reggie', 'Reggie', 'Reggie'
        ])
    monkeypatch.setattr('builtins.input', lambda _:next(inputs))
    expected = [
        {
        'Padme': '205.0', 
        'Reggie': '205.0', 
        'jan': '0.0', 
        'owes': 'jan'
        }, 
        {
        'Padme': '0.0', 
        'Reggie': '0.0', 
        'jan': '0.0', 
        'owes': 'Reggie'
        }
    ]
    main()

    with open(directory + totals_spreadsheet, 'r') as t:
        t_s = csv.DictReader(t)
        #header = t_s.fieldnames
        totals_sheet = list(t_s)
        assert len(totals_sheet) == 2
        assert totals_sheet == expected