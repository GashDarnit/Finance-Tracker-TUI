import json
import os
import glob
from typing import Dict, List

class LedgerStore:
    HISTORY_PATH = "History"
    def __init__(self) -> None:
        self.current_month_json = "current_expenses.json"
        self.current_balance_json = "current_balance.json"
        self.current_savings_json = "current_savings.json"
        self.current_expenses = self.load_current_expenses() if not self.is_json_file_empty() else {}
        self.current_balance = self.load_current_balance()
        self.current_savings = self.load_current_savings()

    def load_current_expenses(self) -> Dict:
        expenses = {}
        with open(self.current_month_json) as file:
            data = json.load(file)

            for expense, instances in data.items():
                expenses[expense] = {'entries': instances, 'value': 0.0}
                cur_sum = 0
                for entry in instances:
                    cur_sum += entry['value']

                expenses[expense]['value'] = cur_sum
        
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

    def save_current_expenses(self) -> bool:
        try:
            # Create a new dict in the original format
            data_to_save = {
                service: info["entries"] if isinstance(info, dict) else info
                for service, info in self.current_expenses.items()
            }

            with open(self.current_month_json, "w") as file:
                json.dump(data_to_save, file, indent=4)

        except Exception as e:
            print(f"Failed to save file: {e}")
            return False

        return True


    def get_current_expenses(self):
        return self.current_expenses
    
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
        for _, content in self.current_expenses.items(): total += content['value']

        return total

    def add_new_expense(self, expense) -> None:
        '''
        "Name": name,
        "Payment Date": date,
        "Amount": float(amount),
        '''
        name, date, amount = [item[1] for item in expense.items()]
        new_entry = {
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


        print(f"[Ledger] New {name} amount: {self.current_expenses[name]['value']}")

        self.save_current_expenses()
        self.update_current_balance(amount)

    def add_new_expense_entry(self, title, new_entry) -> None:
        '''
        "Payment Date": date,
        "Amount": float(amount),
        '''
        self.current_expenses[title]['entries'].append(new_entry)
        self.current_expenses[title]['value'] += new_entry['value']

        self.save_current_expenses()
        self.update_current_balance(new_entry['value'])
    
    def remove_expense(self, expense) -> None:
        expense_total = self._get_entry_total(expense)
        del self.current_expenses[expense]

        self.save_current_expenses()
        self.update_current_balance(-expense_total) # Negative since we want balance to go up

    def update_current_expenses(self, expense, cost):
        self.current_expenses[expense] = cost

    def load_past_expenses(self, filename) -> Dict:
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
        self.current_savings -= savings_change
        self.save_current_savings()

        return self.current_savings

    def is_json_file_empty(self):
        return os.path.getsize(self.current_month_json) == 0
    
    def _get_entry_total(self, expense_name) -> float:
        current_sum = 0

        entries = self.current_expenses[expense_name]["entries"]

        for entry in entries:
            current_sum += entry["value"]

        return current_sum

