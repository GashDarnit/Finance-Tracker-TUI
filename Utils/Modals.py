from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView, Static
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual import events

from Utils.CustomWidgets import EntryRow, ExpenseRow
from Utils.LedgerStore import LedgerStore

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
                self.date = Input(placeholder="Date (DD-MM-YYYY)", id="expense-date")
                self.description = self.amount = Input(placeholder="Description", id="expense-desc")
                self.amount = Input(placeholder="Amount", type="number", id="expense-amount")


                yield self.expense_name
                yield self.date
                yield self.description
                yield self.amount


    def on_mount(self):
        self.expense_name.focus()

    def on_input_submitted(self, event: Input.Submitted):
        if event.input is self.amount:
            self.submit()

    def submit(self):
        name = self.expense_name.value.strip()
        date = self.date.value.strip()
        description = self.description.value.strip()
        amount = self.amount.value.strip()

        if not name or not date or not amount:
            return  # later: show error

        self.dismiss({
            "Name": name,
            "Description": description,
            "Payment Date": date,
            "Amount": float(amount),
        })


class NewEntryModal(ModalScreen):
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
                yield Label("New Entry", id="dialog-title")

                self.date = Input(placeholder="Date (DD-MM-YYYY)", id="expense-date")
                self.description = self.amount = Input(placeholder="Description", id="expense-desc")
                self.amount = Input(placeholder="Amount", type="number", id="expense-amount")


                yield self.date
                yield self.description
                yield self.amount


    def on_mount(self):
        self.date.focus()

    def on_input_submitted(self, event: Input.Submitted):
        if event.input is self.amount:
            self.submit()

    def submit(self):
        date = self.date.value.strip()
        description = self.description.value.strip()
        amount = self.amount.value.strip()

        if not description or not date or not amount:
            return  # later: show error

        self.dismiss({
            "Description": description,
            "Payment Date": date,
            "Amount": float(amount),
        })



class ExpenseListModal(ModalScreen):
    DEFAULT_CSS = """
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
            height: 60%;
            max-width: 70;
            min-width: 40;
            padding: 1 2;
            border: round #AFAFD7;
        }

        #dialog-title {
            width: 100%;
            text-align: center;
            text-style: bold;
            color: #AFAFD7;
            margin-bottom: 1;
        }

        #instructions-footer {
            text-align: left;
            color: #AFAFD7;
            background: black;
            border-top: solid #AFAFD7;
            padding-top: 1;
        }

        ListItem {
            height: auto;
            margin-bottom: 1;
        }

        EntryRow {
            width: 100%;
            height: auto;
            padding: 0 1;
        }

        EntryRow > Static:first-child {
            width: 1fr;
        }

        EntryRow > Static:last-child {
            width: auto;
            text-align: right;
            padding-right: 2;
        }
    """

    BINDINGS = [
        ("escape", "dismiss", "Cancel"),
        ("n", "new_expense", "New Expense"),
        ("Enter", "edit_expense", "Edit Selected"),
        ("x", "delete_expense", "Delete Selected"),
    ]

    def __init__(self, title: str, expenses: list, ledger: LedgerStore):
        super().__init__()
        self.title = title
        self.expenses = expenses
        self.list_view = None
        self.ledger = ledger

    def compose(self):
        with Container():
            with Vertical(id="dialog"):
                yield Label(self.title, id="dialog-title")

                # Create empty ListView
                self.list_view = ListView()
                yield self.list_view

                # Footer instructions
                yield Static("\[N] New Expense  \[Enter] Edit  \[X] Delete", id="instructions-footer")

    async def on_mount(self):
        """Populate ListView after it's mounted."""
        await self.refresh_list()

    def action_new_expense(self):
        """Open a new expense dialog from within this modal."""
        self.app.push_screen(NewEntryModal(), self.on_new_expense_submitted)

    def action_delete_expense(self):
        """Triggered when user presses 'x'."""

        if not self.list_view.children:
            return

        selected_index = self.list_view.index
        entries = self.ledger.current_expenses[self.title]["entries"]

        if selected_index is None or selected_index >= len(entries):
            return

        selected_entry = entries[selected_index]
        display_name = f"{selected_entry['description']} worth {selected_entry['value']:.2f} from {selected_entry['payment_date']}"

        self.app.push_screen(
            ConfirmDeleteModal(display_name),
            lambda confirmed: self.on_delete_confirmed(confirmed, selected_index)
        )

    def on_new_expense_submitted(self, result):
        """Callback when NewExpenseModal is submitted."""
        if result is None:
            return

        new_entry = {
            'description': result["Description"],
            'payment_date': result["Payment Date"],
            'value': result["Amount"]
        }

        self.ledger.add_new_expense_entry(self.title, new_entry) # Add new entry to the ledger
        self.call_later(self.refresh_list) # Refresh the list view so that the content is date-sorted

    def on_delete_confirmed(self, confirmed: bool, index: int):
        if not confirmed:
            return

        entries = self.ledger.current_expenses[self.title]["entries"]

        if 0 <= index < len(entries):
            deleted_entry = entries.pop(index)

            # Recalculate total safely
            self.ledger.current_expenses[self.title]["value"] = sum(
                e["value"] for e in entries
            )

            # Persist changes
            self.ledger.save_current_expenses()
            self.ledger.update_current_balance(-deleted_entry["value"])

            if self.title == 'Savings': self.ledger.update_current_savings(-deleted_entry["value"])

        # Refresh UI
        self.call_later(self.refresh_list)

    async def refresh_list(self):
        self.list_view.clear()

        # Pull sorted entries from ledger
        entries = self.ledger.current_expenses[self.title]["entries"]

        for entry in entries:
            await self.list_view.append( ListItem(EntryRow(entry["payment_date"], entry["value"], entry["description"])) )

        if self.list_view.children:
            self.list_view.index = 0
            self.list_view.focus()

class ConfirmDeleteModal(ModalScreen[bool]):
    DEFAULT_CSS = """
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
            padding: 0 2;
            border: round #AFAFD7;
        }

        #dialog-title {
            text-style: bold;
            margin-bottom: 1;
            text-align: center;
        }
    """

    BINDINGS = [
        ("y", "confirm", "Yes"),
        ("enter", "confirm", "Yes"),
        ("n", "dismiss", "No"),
        ("escape", "dismiss", "Cancel"),
    ]

    def __init__(self, expense_name: str):
        super().__init__()
        self.expense_name = expense_name

    def compose(self):
        with Container():
            with Vertical(id="dialog"):
                yield Label("Confirm Deletion", id="dialog-title")
                yield Static(
                    f"Delete {self.expense_name}?\n\n"
                )
                yield Static("\[Enter] Yes\t\[Escape] No")

    def action_confirm(self):
        self.dismiss(True)

