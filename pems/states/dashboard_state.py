from datetime import datetime
from dateutil.relativedelta import relativedelta
import reflex as rx
from pems.components.objects import Location, Asset, Station
from pems.helpers.database import db
from pems.helpers.oee_summariser import oee_summariser
# from pems.helpers.data_handler import csv_to_df
from pems.states.user_state import UserState
# from PIL import Image
# import pandas as pd

class DashboardState(UserState):
    # Define State Variables
    room_view: bool = True
    production_rooms: list[str] = []
    current_room: Location = Location("", "", False)
    weekly_view: bool = True
    monthly_view: bool = False
    yearly_view: bool = False
    start_date: datetime = datetime.today()
    end_date: datetime = datetime.today()

    # --- Dashboard State Variables ---
    @rx.var
    def connected(self) -> bool:
        return db.connection
    
    @rx.var
    def connection_check(self) -> str:
        return db.connection_status
    
    @rx.var
    def current_room_name(self) -> str:
        return self.current_room.name

    @rx.var
    def start_date_repr(self) -> str:
        return self.start_date.strftime("%Y-%m-%d")

    @rx.var
    def end_date_repr(self) -> str:
        return self.end_date.strftime("%Y-%m-%d")

    # --- State Functions ---
    def load(self):
        """Function for Loading the Dashboard"""
        # TODO: look into csv file loaded for upload, but none exist

        # Retrieve List of Production Rooms
        self.production_rooms = [area.name for area in db.locations]
        if len(self.production_rooms) == 0:
            self.current_room = Location("", "", False)
        else:
            self.current_room = [area for area in db.locations if "Nespresso" in area.name][0]

        # Reload New Entry Variables
        self.weekly_view = True
        self.monthly_view = False
        self.yearly_view = False
        self.start_date = datetime.today()
        self.end_date = datetime.today() + relativedelta(weeks=1)

    def is_valid_date(self, date: str, format: str):
        """Function for Checking if Date Representation is a Valid String"""
        try:
            return isinstance(datetime.strptime(date, format), datetime)
        except Exception:
            return False

    def set_date(self, start: bool):
        """Function for Setting either the Start or End Date"""
        if start:
            if self.weekly_view:
                self.end_date = self.start_date + relativedelta(weeks=1)
            elif self.monthly_view:
                self.end_date = self.start_date + relativedelta(months=1)
            elif self.yearly_view:
                self.end_date = self.start_date + relativedelta(years=1)
        else:
            if self.weekly_view:
                self.start_date = self.end_date + relativedelta(weeks=-1)
            elif self.monthly_view:
                self.start_date = self.end_date + relativedelta(months=-1)
            elif self.yearly_view:
                self.start_date = self.end_date + relativedelta(years=-1)

    # --- Dashboard Event Handlers --- 
    @rx.event
    def update_current_room(self, room: str):
        """Function for Updating the Current Room Selected"""
        self.current_room = [area for area in db.locations if area.name == room][0]

    @rx.event
    def update_timeframe(self, timeframe: str):
        """Function for Updating the Timeframe for OEE"""
        if timeframe == "weekly":
            self.weekly_view = True
            self.monthly_view = False
            self.yearly_view = False
            self.set_date(start=True)
        elif timeframe == "monthly":
            self.weekly_view = False
            self.monthly_view = True
            self.yearly_view = False
            self.set_date(start=True)
        elif timeframe == "yearly":
            self.weekly_view = False
            self.monthly_view = False
            self.yearly_view = True
            self.set_date(start=True)

    @rx.event
    def update_start_date(self, date: str):
        """Function for Updating the Start Date"""
        if self.is_valid_date(date, "%Y-%m-%d"):
            self.start_date = datetime.strptime(date, "%Y-%m-%d")
            self.set_date(start=True)

    @rx.event
    def update_end_date(self, date: str):
        """Function for Updating the End Date"""
        if self.is_valid_date(date, "%Y-%m-%d"):
            self.end_date = datetime.strptime(date, "%Y-%m-%d")
            self.set_date(start=False)
