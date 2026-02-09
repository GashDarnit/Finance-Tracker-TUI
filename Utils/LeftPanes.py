from typing import Container
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import ListItem, ListView, Static

class HeaderBox(VerticalScroll):
    DEFAULT_CSS = """
    HeaderBox {
        width: 100%;
        height: 10%;
        border: solid;
        border: round #AFAFD7;
        margin: 0 0;
    }

    #header-box {
        width: 100%;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Finance Tracker", id="header-box")

class OptionsList(ListView):
    DEFAULT_CSS = """
    OptionsList {
        height: 79%;
        background: black 100%;
        border: solid;
        border: round #AFAFD7;
        margin: 0 0;
    }
    """

    def __init__(self):
        options = [ListItem(Static(f"Current Expenses")), ListItem(Static(f"Expenses History")), ListItem(Static(f"Dashboard"))]
        super().__init__(*options)
        self.border_title = "Options"
        self.border_title_align = "center"


class BalanceBox(Horizontal):
    DEFAULT_CSS = """
    BalanceBox {
        width: 50%;
        height: 100%;
        border: round #AFAFD7;
        margin: 0 0;
        align: center middle;
    }

    #balance-value {
        width: 100%;
        text-align: center;
        text-style: bold;
    }
    """

    def __init__(self):
        super().__init__()
        self.border_title = "Balance"
        self.border_title_align = "bottom"

    def compose(self) -> ComposeResult:
        yield Static("RM 0.00", id="balance-value")

class SavingsBox(Horizontal):
    DEFAULT_CSS = """
    SavingsBox {
        width: 50%;
        height: 100%;
        border: round #AFAFD7;
        margin: 0 0;
        align: center middle;
    }

    #savings-value {
        width: 100%;
        text-align: center;
        text-style: bold;
    }
    """

    def __init__(self):
        super().__init__()
        self.border_title = "Savings"
        self.border_title_align = "bottom"

    def compose(self) -> ComposeResult:
        yield Static("RM 0.00", id="savings-value")
