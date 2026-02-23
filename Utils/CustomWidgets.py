from textual.widgets import Static
from textual.containers import Grid, Horizontal

class ExpenseRow(Horizontal):
    def __init__(self, name: str, amount: float):
        super().__init__()
        self.entry_name = name
        self.amount = amount

    def compose(self):
        DEFAULT_CSS = """
            ExpenseRow {
                width: 100%;
            }

            .expense-name {
                width: 1fr;
            }

            .expense-amount {
                width: auto;
                color: green;
                text-style: bold;
            }
        """

        yield Static(self.entry_name, classes="expense-name")
        yield Static(f"RM {self.amount:,.2f}", classes="expense-amount")


class EntryRow(Grid):
    DEFAULT_CSS = """ 
        EntryRow {
            width: 100%;
            grid-size: 3;
            grid-columns: 20% 1fr auto;
            padding: 0 1;
        }

        .expense-amount { 
            text-align: right;
            color: #FFFFFF;
            text-style: bold;
        } 
    """

    def __init__(self, date: str, amount: float, description: str):
        super().__init__()
        self.date = date
        self.amount = amount
        self.description = description

    def compose(self):
        yield Static(self.date)
        yield Static(self.description)
        yield Static(f"RM {self.amount:,.2f}", classes="expense-amount")
