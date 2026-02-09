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
        data = {}
        with open(self.current_month_json) as file:
            data = json.load(file)
        
        return data
    
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
            with open(self.current_balance_json) as file:
                savings = json.load(file)['Savings']
        except Exception as e:
            print(f"Failed to load Savings: {e}")
            savings = 0.0

        return savings

    def save_current_expenses(self) -> bool:
        try:
            with open(self.current_month_json, "w") as file:
                json.dump(self.current_expenses, file, indent=4)

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

    def is_json_file_empty(self):
        return os.path.getsize(self.current_month_json) == 0
