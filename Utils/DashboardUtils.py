from datetime import datetime

from textual import color
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import ListItem, ListView, Static
from textual_plotext import PlotextPlot

class DashboardDataRow(Horizontal):
    DEFAULT_CSS = """
        DashboardDataRow {
            height: auto;
        }

        Static {
            width: 1fr;
            padding-right: 2;
        }

        .dashboard-date {
            margin-left: 2;
        }

        .dashboard-balance {
            color: #FFFF00;
        }

        .dashboard-expense {
            color: #FF005F;
        }

        .dashboard-income {
            color: #87D700;
        }

        .dashboard-savings {
            color: #AF5FFF;
        }
    """

    def __init__(self, date: str, balance: float, expense: float, income: float, savings: float):
        super().__init__()
        self.date = date
        self.balance = balance
        self.expense = expense
        self.savings = savings
        self.income = income

    def compose(self) -> ComposeResult:
        yield Static(self.date, classes="dashboard-date")
        yield Static(f"RM {self.balance:,.2f}", classes="dashboard-balance")
        yield Static(f"RM {self.income:,.2f}", classes="dashboard-income")
        yield Static(f"RM {self.expense:,.2f}", classes="dashboard-expense")
        yield Static(f"RM {self.savings:,.2f}", classes="dashboard-savings")


class DashboardDataBox(VerticalScroll):
    DEFAULT_CSS = """
        DashboardDataBox {
            height: 45%;
            margin-top: 1;
            border: round #AFAFD7;
        }

        ListItem {
            padding-bottom: 1;
        }
    """

    def __init__(self, history_dataset: list):
        super().__init__()
        self.history_dataset = history_dataset[::-1] # Reverse the list; We want to display latest entry up top, and oldest down bottom
        self.list_view = ListView()

    def compose(self) -> ComposeResult:
        yield self.list_view

    def on_mount(self) -> None:
        for data in self.history_dataset:
            self.list_view.append(ListItem(DashboardDataRow(data['Date'], data['Balance'], data['Total Expenses'], data['Total Income'], data['Savings'])))

class DashboardScreen(Vertical):
    DEFAULT_CSS = """
        DashboardScreen {
            margin-top: 0;
        }

        DashboardDataBox {
            height: 50%;
            margin-top: 1;
            border: round #AFAFD7;
        }

        PlotextPlot {
            padding-left: 1;
            padding-right: 2;
        }
    """

    def __init__(self, balance: float, expense: float, savings: float, income: float, history_dataset: list) -> None:
        super().__init__()
        self.current_balance = balance
        self.current_expense = expense
        self.current_savings = savings
        self.current_income = income
        self.history_dataset = history_dataset

        # Add in current month info
        self.history_dataset.append({
            "Date": datetime.now().strftime("%b %Y"), # Current date in Month Year format, e.g., Feb 2026
            "Balance": self.current_balance,
            "Total Expenses": self.current_expense,
            "Total Income": self.current_income,
            "Savings": self.current_savings
        })

    def compose(self) -> ComposeResult:
        self.balance_plot = PlotextPlot(id="balance_plot")
        self.overview_table = DashboardDataBox(self.history_dataset)

        yield self.balance_plot
        yield self.overview_table

    def on_mount(self) -> None:
        plot_widget = self.query_one("#balance_plot")
        plt = plot_widget.plt

        x = list(range(len(self.history_dataset)))
        balances = [d["Balance"] for d in self.history_dataset]
        savings = [d["Savings"] for d in self.history_dataset]
        expenses = [d["Total Expenses"] for d in self.history_dataset]
        income = [d["Total Income"] for d in self.history_dataset]
        labels = [d["Date"] for d in self.history_dataset]

        plt.plot(x, balances, label="Balance", marker="braille", color=(255, 255, 0))
        plt.plot(x, income, label="Income", marker="braille", color="green")
        plt.plot(x, expenses, label="Expenses", marker="braille", color="red")
        plt.plot(x, savings, label="Savings", marker="braille", color="blue")

        plt.xticks(x, labels)
        plt.title("Financial Overview")
