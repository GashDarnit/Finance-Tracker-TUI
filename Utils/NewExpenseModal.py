from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Container, Vertical
from textual import events

class NewExpenseModal(ModalScreen):
    DEFAULT_CSS = """
        ModalScreen {
            background: transparent;
        }

        ModalScreen {
            background: transparent;
        }

        Container {
            width: 100%;
            height: 100%;
            background: transparent;
            align: center middle;
        }

        #dialog {
            width: 60%;
            height: auto;
            max-width: 70;
            min-width: 40;
            padding: 1 2;
            border: round #AFAFD7;
        }


        #dialog-title {
            text-style: bold;
            margin-bottom: 1;
            text-align: center;
        }
    """

    BINDINGS = [
        ("escape", "dismiss", "Cancel"),
    ]

    def compose(self):
        with Container():  # full-screen container
            with Vertical(id="dialog"):
                yield Label("New Expense", id="dialog-title")

                self.expense_name = Input(placeholder="Expense name", id="expense-name")
                self.date = Input(placeholder="Date (YYYY-MM-DD)", id="expense-date")
                self.amount = Input(placeholder="Amount", type="number", id="expense-amount")


                yield self.expense_name
                yield self.date
                yield self.amount


    def on_mount(self):
        self.expense_name.focus()

    def on_input_submitted(self, event: Input.Submitted):
        if event.input is self.amount:
            self.submit()

    def submit(self):
        name = self.expense_name.value.strip()
        date = self.date.value.strip()
        amount = self.amount.value.strip()

        if not name or not date or not amount:
            return  # later: show error

        self.dismiss({
            "Name": name,
            "Payment Date": date,
            "Amount": float(amount),
        })

