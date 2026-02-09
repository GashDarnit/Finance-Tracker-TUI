from textual.widgets import Static
from textual.containers import Horizontal

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

