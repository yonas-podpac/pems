import calendar as pycal
from datetime import datetime
from dateutil.relativedelta import relativedelta
import reflex as rx
from pems.helpers.calendar_handler import calendar_handler
from pems.states.user_state import UserState
from pems.states.preventative_state import PreventativeState
from pems.states.service_state import ServiceState
from pems.states.unplanned_state import UnplannedState

class CalendarState(UserState):
    # Calendar States
    today: datetime = datetime.today()
    selected_date: datetime = datetime.today()
    day_view: bool = False
    week_view: bool = False
    month_view: bool = True
    date_select_open: bool = False
    view_select_open: bool = False
    maintenance_select_open: bool = False
    day_key: str = ""
    day_tasks: dict[str, list[dict[str, str]]] = {}
    week_list: list[str] = []
    week_tasks: dict[str, dict[str, list[dict[str, str]]]] = {}
    month_list: list[str] = []
    weeks: list[list[str]] = []
    month_tasks: dict[str, dict[str, list[dict[str, str]]]] = {}
    
    @rx.var
    def curr_repr(self) -> str:
        if self.month_view:
            return self.selected_date.strftime("%B %Y")
        if self.week_view:
            week_idx = self.selected_date.weekday()
            print(week_idx)
            first_day = self.selected_date.day - week_idx
            print(first_day)
            last_day = self.selected_date.day + 6 - week_idx
            final_day = pycal.monthrange(self.selected_date.year, self.selected_date.month)[1]
            if first_day == 0:
                prev_month = self.selected_date + relativedelta(month=(self.selected_date.month - 1))
                final_day = pycal.monthrange(self.selected_date.year, prev_month.month)[1]
                return str(final_day) + " " + prev_month.strftime("%B") + " - " + str(last_day) + " " + self.selected_date.strftime("%B, %Y")
            elif first_day < 0:
                prev_day = (self.selected_date + relativedelta(day=(week_idx - 7))).strftime("%d %B")
                return prev_day + " - " + str(last_day) + self.selected_date.strftime("%B, %Y")
            elif last_day > final_day:
                next_day = (self.selected_date + relativedelta(day=(final_day - last_day))).strftime("%d %B, %Y")
                return str(first_day) + " " + self.selected_date.strftime("%B") + " - " + next_day
            else:
                return str(first_day) + " - " + str(last_day) + " " + self.selected_date.strftime("%B, %Y")
        if self.day_view:
            return self.selected_date.strftime("%d %B, %Y")

    @rx.var
    def day_view_repr(self) -> str:
        return self.selected_date.strftime("%A, %d %B")

    @rx.var
    def no_tasks(self) -> bool:
        if self.day_tasks.keys().__contains__("tasks"):
            return len(self.day_tasks["tasks"]) == 0
        return False

    @rx.var
    def curr_month(self) -> str:
        return self.selected_date.strftime("%b")

    @rx.var
    def full_month(self) -> str:
        return self.selected_date.strftime("%B")

    @rx.var
    def curr_year(self) -> str:
        return self.selected_date.strftime("%Y")

    @rx.var
    def months(self) -> list[str]:
        return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    @rx.var
    def weekdays(self) -> list[str]:
        return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # --- State Functions ---
    def load(self):
        """Function used to Load State Variables"""
        self.selected_date = datetime.today()
        self.day_view = False
        self.week_view = False
        self.month_view = True
        self.date_select_open = False
        self.view_select_open = False
        self.load_lists()

    def load_lists(self):
        """Function used to Load Day / Week / Month Lists"""
        self.day_key = calendar_handler.get_day_key(self.selected_date)
        self.day_tasks = calendar_handler.get_tasks(self.selected_date, self.day_key, self.day_key)[self.day_key]
        self.week_list = calendar_handler.get_week_list(self.selected_date)
        self.week_tasks = calendar_handler.get_tasks(self.selected_date, self.week_list[0], self.week_list[-1])
        self.month_list = calendar_handler.get_month_list(self.selected_date)
        self.weeks = [self.month_list[i:i + 7] for i in range(0, len(self.month_list), 7)]
        self.month_tasks = calendar_handler.get_tasks(self.selected_date, self.month_list[0], self.month_list[-1])

    # --- Calendar Controller Functions ---
    @rx.event
    def toggle_date_select(self):
        """Function for Toggling the Date Select"""
        self.date_select_open = not self.date_select_open

    @rx.event
    def toggle_view_select(self):
        """Function for Toggling the View Select"""
        self.view_select_open = not self.view_select_open

    @rx.event
    def toggle_maintenance_select(self):
        """Function for Toggling the Maintenance Select"""
        self.maintenance_select_open = not self.maintenance_select_open

    @rx.event
    def change_year(self, count: int):
        """Function for Incrementing / Decrementing Selected Year"""
        self.selected_date = self.selected_date + relativedelta(years=count)
        self.load_lists()

    @rx.event
    def change_month(self, count: int):
        """Function for Incrementing / Decrementing Selected Month"""
        self.selected_date = self.selected_date + relativedelta(months=count)
        self.load_lists()

    @rx.event
    def set_month(self, month_repr: str):
        """Function for Setting Selected Month"""
        self.selected_date = self.selected_date.replace(month=datetime.strptime(month_repr, "%b").month)
        self.date_select_open = False
        self.load_lists()

    @rx.event
    def select_day(self, day: str, month: str, year: str):
        """Function for Selecting the Day"""
        self.selected_date = self.selected_date.replace(day=int(day), month=int(month), year=int(year))
        self.day_view = True
        self.week_view = False
        self.month_view = False
        self.view_select_open = False
        self.load_lists()

    @rx.event
    def set_day_view(self):
        """Function for Setting Day View"""
        self.day_view = True
        self.week_view = False
        self.month_view = False
        self.view_select_open = False

    @rx.event
    def set_week_view(self):
        """Function for Setting Week View"""
        self.day_view = False
        self.week_view = True
        self.month_view = False
        self.view_select_open = False

    @rx.event
    def set_month_view(self):
        """Function for Setting Month View"""
        self.day_view = False
        self.week_view = False
        self.month_view = True
        self.view_select_open = False

    @rx.event
    def open_work_order(self, id: str, m_type: str, complete: bool):
        """Function for Opening a Work Order"""
        if m_type == "procedure" or m_type == "preventative":
            return PreventativeState.open_work_order_form(id=id, complete=complete)
        elif m_type == "service":
            return ServiceState.open_work_order_form(id=id, complete=complete)
        elif m_type == "unplanned":
            return UnplannedState.open_work_order_form(id=id, complete=complete)
