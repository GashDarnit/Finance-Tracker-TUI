from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalScroll, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, ListView, ListItem, Static

from Utils.LedgerStore import LedgerStore
from Utils.LeftPanes import HeaderBox, OptionsList, BalanceBox, SavingsBox
from Utils.CustomWidgets import ExpenseRow
from Utils.Modals import NewExpenseModal, ExpenseListModal


finance_ledger = LedgerStore()

class RightPanel(Vertical):
    DEFAULT_CSS = """
    ListView, ListItem, Static {
        background: transparent;
    }

    RightPanel {
        width: 70%;
        height: 100%;
        background: #080808;
        border: round #AFAFD7;
        margin: 0 0;
        padding-left: 1;
    }

    ListItem {
        height: auto;
        margin-bottom: 1;
    }

    ExpenseRow {
        width: 100%;
        height: auto;
        padding: 0 1;
    }

    ExpenseRow > Static:first-child {
        width: 1fr;
    }

    ExpenseRow > Static:last-child {
        width: auto;
        text-align: right;
        color: #AFAFD7;
        padding-right: 2;
    }

    #right-content {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: #AFAFD7;
        border-bottom: solid #AFAFD7;
        margin-bottom: 1;
    }

    #right-scroll {
        height: 1fr;
    }

    #instructions-footer {
        text-align: left;
        color: #AFAFD7;
        background: black;
        border-top: solid #AFAFD7;
        padding: 1 1;
    }

    """

    def compose(self) -> ComposeResult:
        self.current_title = None

        with VerticalScroll(id="right-scroll"):
            yield Static("Right Panel - Dynamic Content Here", id="right-content")

            self.list_view = ListView()
            yield self.list_view

        self.total_expense = Static("Total: ", id="expense-total")
        self.instructions = Static("[N] New Expense\t\t[Enter] Select Expense", id="instructions-footer", markup=False)
        yield self.total_expense
        yield self.instructions

    def update_content(self, title, items):
        """Replace right panel content dynamically."""
        # Update the top Static
        right_content = self.query_one("#right-content", Static)
        right_content.update(f"{title}")
        self.current_title = title

        # Clear previous list items
        self.list_view.clear()

        # Add new items
        if title == 'Current Expenses':
            self.instructions.display = True
            for name, content in items.items(): 
                self.list_view.append( ListItem(ExpenseRow(name, content['value'])) )

            self.query_one("#expense-total", Static).update(f"Total:\tRM {finance_ledger.get_total_expenses():.2f}")

        else:
            self.instructions.display = False
            for item in items: self.list_view.append(ListItem(Static(item)))



class FinanceTracker(Screen):
    BINDINGS = [
        # Vim-style keybinds
        ("h", "focus_left", "Focus left panel"),
        ("l", "focus_right", "Focus right panel"),
        ("j", "move_down", "Move selection down"),
        ("k", "move_up", "Move selection up"),

        # Arrow keys
        ("left", "focus_left", "Focus left panel"),
        ("right", "focus_right", "Focus right panel"),
        ("down", "move_down", "Move selection down"),
        ("up", "move_up", "Move selection up"),

        ("n", "new_expense", "New Expense"),
    ]

    def action_focus_left(self):
        """Move focus to left options list."""
        self.options_list.focus()

    def action_focus_right(self):
        """Move focus to right panel list, if there are items."""
        if self.right_panel.list_view.children:
            self.right_panel.list_view.index = 0
            self.right_panel.list_view.focus()

    def action_move_down(self):
        focused = self.focused
        if isinstance(focused, ListView) and focused.children:

            if focused.index is None:
                focused.index = 0
            else:
                focused.index = min(focused.index + 1, len(focused.children) - 1)

    def action_move_up(self):
        focused = self.focused
        if isinstance(focused, ListView) and focused.children:
            if focused.index is None:
                focused.index = 0
            else:
                focused.index = max(focused.index - 1, 0)

    def action_new_expense(self):
        focused = self.focused

        # Must be focused on the right panel ListView
        if focused is not self.right_panel.list_view:
            return

        # Must be showing Current Expenses
        if self.right_panel.current_title != "Current Expenses": 
            return

        self.open_new_expense_dialog()

    def open_new_expense_dialog(self):
        self.app.push_screen(NewExpenseModal(), self.on_new_expense_submitted)

    def on_new_expense_submitted(self, result):
        if result is None: return
        
        finance_ledger.add_new_expense(result) # Add new entry to ledger
        self.right_panel.update_content('Current Expenses', finance_ledger.get_current_expenses()) # Update content


    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical():
                self.options_list = OptionsList()
                self.balance = BalanceBox()
                self.savings = SavingsBox()

                yield HeaderBox()
                yield self.options_list

                with Horizontal():
                    yield self.balance
                    yield self.savings

            # Right column
            self.right_panel = RightPanel()
            yield self.right_panel
    
    def on_mount(self) -> None:
        self.options_list.index = 0

        self.query_one("#balance-value", Static).update(f"RM {finance_ledger.get_current_balance():.2f}")
        self.query_one("#savings-value", Static).update(f"RM {finance_ledger.get_current_savings():.2f}")

        self.options_list.focus()
        selected_item = self.options_list.children[0]
        option_text = selected_item.children[0].render()
        right_content = self.right_panel.query_one("#right-content", Static)
        right_content.update(f"{option_text}")

    async def on_list_view_highlighted(self, event: ListView.Highlighted):
        """Update right panel dynamically only when the left options are highlighted."""
        # Only respond if the event is from the left panel
        if event.list_view is not self.options_list:
            return

        list_item = event.item

        # Safe access: Static inside ListItem
        static_widgets = list_item.query(Static)
        if not static_widgets:
            return

        option_text = static_widgets[0].render()

        if option_text == 'Current Expenses':
            items = finance_ledger.get_current_expenses()
        elif option_text == 'Expenses History':
            items = finance_ledger.get_expenses_history()
        else:
            items = []

        self.right_panel.update_content(option_text, items)


    async def on_list_view_selected(self, event: ListView.Selected):
        """Called when an item is 'activated' (Enter pressed)."""

        # =============== LEFT PANEL selection logic ===============
        if event.list_view is self.options_list:
            list_item = event.item
            static_widgets = list_item.query(Static)
            if not static_widgets: return
            option_text = static_widgets[0].render()

            if self.right_panel.list_view.children and option_text != 'Dashboard':
                # Focus on the first item in the right panel
                self.right_panel.list_view.index = 0
                self.right_panel.list_view.focus()
            return  # done

        # =============== RIGHT PANEL selection logic ===============
        if event.list_view is self.right_panel.list_view:
            # Only show modal if we're in 'Current Expenses' mode
            if self.right_panel.current_title != "Current Expenses":
                return

            # Get selected item
            selected_index = self.right_panel.list_view.index
            if selected_index is None:
                return

            selected_item = self.right_panel.list_view.children[selected_index]
            static_widgets = selected_item.query(Static)
            current_expense = static_widgets[0].render()
            expense_entries = finance_ledger.get_current_expenses()[current_expense]['entries']

            # Push the modal
            self.app.push_screen( 
                ExpenseListModal(title=current_expense, expenses=expense_entries, ledger=finance_ledger), 
                self.on_new_expense_entry_submitted
            )

    def on_new_expense_entry_submitted(self, _):
        # Select the first option in the list
        self.right_panel.list_view.index = 0
        self.right_panel.list_view.focus()
        
        self.right_panel.update_content('Current Expenses', finance_ledger.get_current_expenses()) # Update content


class FinanceTrackerApp(App):
    def on_ready(self) -> None:
        self.push_screen(FinanceTracker())


if __name__ == "__main__":
    FinanceTrackerApp().run()
