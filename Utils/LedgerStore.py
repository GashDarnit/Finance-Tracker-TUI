import json
import os
import shutil
import glob
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List

class LedgerStore:
    HISTORY_PATH = "History"
    def __init__(self) -> None:
        self.current_month_json = "current_expenses.json"
        self.current_income_json= "current_income.json"
        self.current_balance_json = "current_balance.json"
        self.current_savings_json = "current_savings.json"

        self.check_first_time_loading() # If user has ran the application before, they'd have the json files, otherwise, create them

        self.current_expenses = self.load_current_expenses() if not self.is_json_file_empty(self.current_month_json) else {}
        self.current_income = self.load_current_income() if not self.is_json_file_empty(self.current_income_json) else {}
        self.current_balance = self.load_current_balance()
        self.current_savings = self.load_current_savings()

        self._check_new_month_from_entries() # Check if a new month or year has passed (Probably really only need to check month but ehh)

    def check_first_time_loading(self):
        """ Check if the user has the data files """

        if not os.path.exists(self.current_month_json):
            with open(self.current_month_json, "w") as file:
                json.dump({}, file, indent=4)
        
        if not os.path.exists(self.current_income_json):
            with open(self.current_income_json, "w") as file:
                json.dump({}, file, indent=4)

        if not os.path.exists(self.current_balance_json):
            with open(self.current_balance_json, "w") as file:
                json.dump({"Balance": 0}, file, indent=4)
        
        if not os.path.exists(self.current_savings_json):
            with open(self.current_savings_json, "w") as file:
                json.dump({"Savings": 0}, file, indent=4)



    def load_current_expenses(self) -> Dict:
        expenses = {}

        try:
            with open(self.current_month_json) as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

        with open(self.current_month_json) as file:
            data = json.load(file)

            for expense, instances in data.items():

                # Sort entries by date
                instances.sort( key=lambda x: datetime.strptime(x["payment_date"], "%d-%m-%Y") )

                cur_sum = sum(entry["value"] for entry in instances)

                expenses[expense] = {
                    "entries": instances,
                    "value": cur_sum,
                }

        return expenses

    def load_expense_history(self, filename: str) -> Dict:
        history_filename = os.path.join(self.HISTORY_PATH, filename)
        expenses = {}

        with open(history_filename) as file:
            data = json.load(file)['Expense']

            for expense, instances in data.items():

                # Sort entries by date
                instances.sort( key=lambda x: datetime.strptime(x["payment_date"], "%d-%m-%Y") )

                cur_sum = sum(entry["value"] for entry in instances)

                expenses[expense] = {
                    "entries": instances,
                    "value": cur_sum,
                }

        return expenses
    
    def load_income_history(self, filename: str) -> Dict:
        history_filename = os.path.join(self.HISTORY_PATH, filename)
        expenses = {}

        with open(history_filename) as file:
            data = json.load(file)['Income']

            for expense, instances in data.items():

                # Sort entries by date
                instances.sort( key=lambda x: datetime.strptime(x["payment_date"], "%d-%m-%Y") )

                cur_sum = sum(entry["value"] for entry in instances)

                expenses[expense] = {
                    "entries": instances,
                    "value": cur_sum,
                }

        return expenses
    
    def load_current_balance(self) -> float:
        try:
            with open(self.current_balance_json) as file:
                balance = json.load(file)['Balance']
        except Exception as e:
            print(f"Failed to load balance: {e}")
            balance = 0.0

        return balance
    
    def load_current_savings(self) -> float:
        try:
            with open(self.current_savings_json) as file:
                savings = json.load(file)['Savings']
        except Exception as e:
            print(f"Failed to load Savings: {e}")
            savings = 0.0

        return savings

    def load_current_income(self) -> Dict:
        expenses = {}

        try:
            with open(self.current_income_json) as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

        with open(self.current_income_json) as file:
            data = json.load(file)

            for expense, instances in data.items():
                # Sort entries by date
                instances.sort( key=lambda x: datetime.strptime(x["payment_date"], "%d-%m-%Y") )

                cur_sum = sum(entry["value"] for entry in instances)

                expenses[expense] = {
                    "entries": instances,
                    "value": cur_sum,
                }

        return expenses
    
    def save_current_balance(self) -> bool:
        try:
            with open(self.current_balance_json, "w") as file:
                json.dump({"Balance": self.current_balance}, file, indent=4)

        except Exception as e:
            print(f"Failed to save balance: {e}")
            return False
        
        return True
    
    def save_current_savings(self) -> bool:
        try:
            with open(self.current_savings_json, "w") as file:
                json.dump({"Savings": self.current_savings}, file, indent=4)

        except Exception as e:
            print(f"Failed to save savings: {e}")
            return False
        
        return True

    def save_current_expenses(self, is_history=False) -> bool:
        try:
            # Create a new dict in the original format
            data_to_save = {
                service: info["entries"] if isinstance(info, dict) else info
                for service, info in self.current_expenses.items()
            }

            if is_history:
                temp = data_to_save
                income = {
                    service: info["entries"] if isinstance(info, dict) else info
                    for service, info in self.current_income.items()
                }

                total_expenses = self.get_total_expenses()
                total_income = self.get_total_income()
                data_to_save = {
                    'Expense': temp,
                    'Income': income,
                    'Total Expenses': total_expenses,
                    'Total Income': total_income,
                    'Balance': self.current_balance,
                    'Savings': self.current_savings
                }

            with open(self.current_month_json, "w") as file:
                json.dump(data_to_save, file, indent=4)

        except Exception as e:
            print(f"Failed to save file: {e}")
            return False

        return True
    
    def save_current_income(self) -> bool:
        try:
            # Create a new dict in the original format
            data_to_save = {
                service: info["entries"] if isinstance(info, dict) else info
                for service, info in self.current_income.items()
            }
            with open(self.current_income_json, "w") as file:
                json.dump(data_to_save, file, indent=4)

        except Exception as e:
            print(f"Failed to save file: {e}")
            return False

        return True


    def get_current_expenses(self):
        return self.current_expenses
    
    def get_current_income(self):
        return self.current_income
    
    def get_current_balance(self):
        return self.current_balance
    
    def get_current_savings(self):
        return self.current_savings
    
    def get_expenses_history(self) -> List:
        entries = []
        for entry in glob.glob("History/*"): 
            entries.append(entry.split('/')[-1].split('.')[0].replace('_', ' ')) # This looks so chaotic lmao
        
        return entries

    def get_total_expenses(self) -> float:
        total = 0
        for _, content in self.current_expenses.items(): 
            total += content['value']

        return total
    
    def get_total_income(self) -> float:
        total = 0
        for _, content in self.current_income.items(): 
            total += content['value']

        return total

    def add_new_expense(self, expense) -> None:
        '''
        "Name": name,
        "Description": description,
        "Payment Date": date,
        "Amount": float(amount),

        '''
        name, description, date, amount = [item[1] for item in expense.items()]
        

        new_entry = {
            'description': description,
            'payment_date': date,
            'value': amount
        }

        if name in self.current_expenses:
            self.current_expenses[name]['entries'].append(new_entry)

            cur_sum = 0
            for entry in self.current_expenses[name]['entries']:
                cur_sum += entry['value']

            self.current_expenses[name]['value'] = cur_sum

        else:
            self.current_expenses[name] = {}
            self.current_expenses[name]['entries'] = [new_entry]
            self.current_expenses[name]['value'] = amount

        if name == "Savings": self.update_current_savings(new_entry['value'])

        self.save_current_expenses()
        self.update_current_balance(amount)

    def add_new_income(self, income) -> None:
        '''
        "Name": name,
        "Description": description,
        "Payment Date": date,
        "Amount": float(amount),

        '''
        name, description, date, amount = [item[1] for item in income.items()]
        

        new_entry = {
            'description': description,
            'payment_date': date,
            'value': amount
        }

        if name in self.current_income:
            self.current_income[name]['entries'].append(new_entry)

            cur_sum = 0
            for entry in self.current_income[name]['entries']:
                cur_sum += entry['value']

            self.current_income[name]['value'] = cur_sum

        else:
            self.current_income[name] = {}
            self.current_income[name]['entries'] = [new_entry]
            self.current_income[name]['value'] = amount

        # If income goes up, and it has something to do with savings, then it's most likely a savings withdrawal
        if "Savings" in name: self.update_current_savings(-amount)

        self.save_current_income()
        self.update_current_balance(-amount) # Negative here since we want balance to go up

    def add_new_expense_entry(self, title, new_entry) -> None:
        '''
        "Name": description,
        "Payment Date": date,
        "Amount": float(amount)
        '''
        self.current_expenses[title]['entries'].append(new_entry)

        # Sort list of entries in case the new entry is from an earlier date
        self.current_expenses[title]['entries'].sort( key=lambda x: datetime.strptime(x["payment_date"], "%d-%m-%Y") )

        # Running sum; Should be more accurate this way
        self.current_expenses[title]['value'] = sum( entry['value'] for entry in self.current_expenses[title]['entries'] )

        if title == "Savings": self.update_current_savings(new_entry['value'])

        self.save_current_expenses()
        self.update_current_balance(new_entry['value'])

    def add_new_income_entry(self, title, new_entry) -> None:
        '''
        "Name": description,
        "Payment Date": date,
        "Amount": float(amount)
        '''
        self.current_income[title]['entries'].append(new_entry)

        # Sort list of entries in case the new entry is from an earlier date
        self.current_income[title]['entries'].sort( key=lambda x: datetime.strptime(x["payment_date"], "%d-%m-%Y") )

        # Running sum; Should be more accurate this way
        self.current_income[title]['value'] = sum( entry['value'] for entry in self.current_income[title]['entries'] )

        self.save_current_income()
        self.update_current_balance(-new_entry['value']) # Negative since we want balance to go up
    
    def remove_expense(self, expense) -> None:
        expense_total = self._get_entry_total(self.current_expenses, expense)
        del self.current_expenses[expense]

        if expense == 'Savings': self.update_current_savings(-expense_total)
        self.save_current_expenses()
        self.update_current_balance(-expense_total) # Negative since we want balance to go up

    def remove_income(self, income) -> None:
        income_total = self._get_entry_total(self.current_income, income)
        del self.current_income[income]

        if "Savings" in income:
            self.update_current_savings(-income_total)

        self.save_current_income()
        self.update_current_balance(income_total) # Positive since we want balance to go down

    def load_past_expenses(self, filename) -> Dict:
        data = {}
        filename += ".json"
        try:
            with open(os.path.join("History", filename)) as file:
                data = json.load(file)

        except Exception as e:
            print(f"Failed to load {filename}: {e}")

        return data

    def load_past_income(self, filename) -> Dict:
        data = {}
        filename += ".json"
        try:
            with open(os.path.join("History", filename)) as file:
                data = json.load(file)

        except Exception as e:
            print(f"Failed to load {filename}: {e}")

        return data

    def update_current_balance(self, expense_cost) -> float:
        # Should work for both positive and negative values
        self.current_balance -= expense_cost
        self.save_current_balance()

        return self.current_balance

    def update_current_savings(self, savings_change) -> float:
        # Should work for both positive and negative values
        self.current_savings += savings_change
        self.save_current_savings()

        return self.current_savings
    
    def update_expense_entry(self, expense: str, index: int, updated_entry: dict) -> None:
        # Add old total to balance; We'll reduce it with new amount later
        old_total = self._get_entry_total(self.current_expenses, expense)
        self.update_current_balance(-old_total)

        # Update the entry
        self.current_expenses[expense]["entries"][index] = updated_entry
        self.current_expenses[expense]["entries"].sort( key=lambda x: datetime.strptime(x["payment_date"], "%d-%m-%Y") ) # Sort the entry since date could be updated too

        # Update the expense with new total
        new_total = self._get_entry_total(self.current_expenses, expense)
        self.update_current_balance(new_total)
        self.current_expenses[expense]["value"] = new_total

        self.save_current_expenses()

        # If the expense is Savings, we can simply just store the value since they should behave the same anyways
        if expense == 'Savings': 
            self.current_savings = new_total
            self.save_current_savings()

    def update_income_entry(self, income: str, index: int, updated_entry: dict) -> None:
        # Add old total to balance; We'll reduce it with new amount later
        old_total = self._get_entry_total(self.current_income, income)
        self.update_current_balance(-old_total)

        # Update the entry
        self.current_income[income]["entries"][index] = updated_entry
        self.current_income[income]["entries"].sort( key=lambda x: datetime.strptime(x["payment_date"], "%d-%m-%Y") ) # Sort the entry since date could be updated too

        # Update the income with new total
        new_total = self._get_entry_total(self.current_income, income)
        self.update_current_balance(new_total)
        self.current_income[income]["value"] = new_total

        self.save_current_income()


    def is_json_file_empty(self, json_file):
        return os.path.getsize(json_file) == 0
    
    def get_history_dataset(self):
        entries = []
        
        now = datetime.now()

        # Go back 11 months
        year = now.year
        month = now.month - 11
        while month <= 0:
            month += 12
            year -= 1
            
        cutoff_date = datetime(year, month, 1)

        for entry in glob.glob("History/*"):
            full_date = entry.split('/')[-1].split('.')[0]
            date_obj = datetime.strptime(full_date, "%B %Y")

            if date_obj >= cutoff_date:
                with open(entry) as file:
                    temp_data = json.load(file)

                entries.append({
                    "date_obj": date_obj,
                    "Date": date_obj.strftime("%b %Y"),
                    "Balance": temp_data["Balance"],
                    "Total Expenses": temp_data["Total Expenses"],
                    "Total Income": temp_data["Total Income"],
                    "Savings": temp_data["Savings"]
                })

        # Sort by date
        entries.sort(key=lambda x: x["date_obj"])

        # Remove helper key
        for e in entries:
            del e["date_obj"]

        return entries
    
    def _get_entry_total(self, entry_to_check, expense_name) -> float:
        current_sum = 0

        entries = entry_to_check[expense_name]["entries"]

        for entry in entries:
            current_sum += entry["value"]

        return current_sum

    def _check_new_month_from_entries(self):
        if not self.current_expenses:
            return
        
        today = datetime.today()
        current_month = today.month
        current_year = today.year

        # Find the earliest payment date across all categories
        earliest_payment = min( datetime.strptime(payments['entries'][0]["payment_date"], "%d-%m-%Y") for payments in self.current_expenses.values() if payments )

        # If the month or year is different from the current time, then we reset the Ledger; Time can only go forward after all
        if earliest_payment.month != current_month or earliest_payment.year != current_year:
            self._reset_ledger()

    def _reset_ledger(self):
        if self.current_expenses:
            self.save_current_expenses(is_history=True) # Optional flag that lets us store Balance and Savings

            today = datetime.today()
            last_month = today - relativedelta(months=1) # Get 1 month before
            history_filename = last_month.strftime("%B %Y") + ".json"

            try:
                os.rename(self.current_month_json, history_filename) # Rename old 'current_expenses.json' to '{Month} {Year}.json'
                shutil.move(history_filename, os.path.join(self.HISTORY_PATH, history_filename)) # Move the file to history folder
                self.current_expenses = {} # Reset current expenses
                self.current_income = {}
                self.save_current_expenses() # Save the empty dict

            except Exception as e:
                print(f"Something went wrong, general exception caught: {e}")


            
