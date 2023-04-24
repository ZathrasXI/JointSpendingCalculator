# JointSpendingCalclutor

To help with working out who owes whom what. Put bank statements formatted as .csv in a directory, and for each transaction in each statement the script will ask for
the name of the people who owe money. At the end, an HTML table is created displaying, who owes whom what.

Use `pytest` to run the tests.


## Made to solve the above problem, but also as an exercise in:
- TDD.
- Using PyTest for unit tests.
- Table Driven Development with PyTest.
- Trying pipeline testing using GitHub Actions.

## To setup:
1. Clone the repo.
2. Create a virtual environment, e.g. `python3 -m venv venv/`
3. Activate the virtual environment, `source venv/bin/activate`
4. Install packages `pip install -r requirements.txt`

## Usage:
1. Create a sub-directory and put statements formatted as .csv files in it.
2. run `python3 jointSpendingCalculator.py`.
3. Follow the instructions and open the HTML file in your browser at the end.

## Caveats:
1. Only supports .csv files from The Co-operative Bank and Monzo. To add another bank, update the `banks` dict on line 46.

