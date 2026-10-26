import calendar as pycal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pems.helpers.database import db
import time

class CalendarHandler:
    def __init__(self):
        self.__maintenance_frequencies = db.maintenance_frequencies
        self.__maintenance_procedures = db.maintenance_procedures
        self.__maintenance_types = db.maintenance_types
        self.__preventative_maintenance = db.preventative_maintenance
        self.__service_maintenance = db.service_maintenance
        self.__unplanned_events = db.unplanned_events
        self.__unplanned_maintenance = db.unplanned_maintenance
        self.__work_order_statuses = db.work_order_statuses
        self.__work_orders = db.work_orders

    def get_day_key(self, curr: datetime) -> str:
        """Function for Retrieving the Day List for Day View"""
        return curr.strftime("%d-%m-%Y")

    def get_week_list(self, curr: datetime) -> list[str]:
        """Function for Retrieving the Day List for Week View"""
        # Generate Day List
        arr = []
        w_idx = curr.weekday()
        first_day = curr + relativedelta(days=(-1 * w_idx))
        last_day = curr + relativedelta(days=(6 - w_idx))

        # Iterate from First to Last Day
        step = timedelta(days=1)
        day = first_day
        while day <= last_day:
            arr.append(day.strftime("%d-%m-%Y"))
            day += step

        return arr

    def get_month_list(self, curr: datetime) -> list[str]:
        """Function for Retrieving the Day List for Month View"""
        # Generate Day List
        arr = []
        first_day = datetime.strptime(f"1-{curr.month}-{curr.year}", "%d-%m-%Y").weekday()
        last_day_num = pycal.monthrange(curr.year, curr.month)[1]
        last_day = datetime.strptime(f"{last_day_num}-{curr.month}-{curr.year}", "%d-%m-%Y").weekday()

        # Retrieve Previous Month Final Days
        if first_day > 0:
            prev_last_day_num = pycal.monthrange(curr.year if curr.month >= 1 else curr.year - 1, curr.month - 1 if curr.month > 1 else 12)[1]
            for x in range(first_day):
                d = (curr + relativedelta(months=-1)).replace(day=(prev_last_day_num - first_day + x + 1))
                arr.append(d.strftime("%d-%m-%Y"))

        # Fill Month Days
        for d in pycal.Calendar(firstweekday=0).itermonthdays(curr.year, curr.month):
            if d > 0:
                md = curr.replace(day=d)
                arr.append(md.strftime("%d-%m-%Y"))

        # Retrieve Next Month First Days
        if last_day < 6:
            for x in range(6 - last_day):
                nd = (curr + relativedelta(months=1)).replace(day=(x + 1))
                arr.append(nd.strftime("%d-%m-%Y"))
        
        return arr

    def get_tasks(self, current: datetime, start_repr: str, end_repr: str) -> dict[str, dict[str, list[dict[str, str]]]]:
        """Function for Getting Tasks between given Dates"""
        # Initialise Dictionary
        task_list = {}
        step = timedelta(days=1)
        
        curr = datetime.strptime(start_repr, "%d-%m-%Y")
        start = datetime.strptime(start_repr, "%d-%m-%Y")
        end = datetime.strptime(end_repr, "%d-%m-%Y")
        current_bd = current.strftime("%d-%m-%Y").split("-")
        t_bd = ["day", "month", "year"]

        # Itereate through Dates and Initialise Task Lists
        while curr <= end:
            repr = curr.strftime("%d-%m-%Y")
            repr_bd = repr.split("-")
            task_list[repr] = {
                "breakdown": [{"day": repr_bd[0], "month": repr_bd[1], "year": repr_bd[2]}],
                "current": [{t_bd[i]: "yes" if repr_bd[i] == current_bd[i] else "no"} for i in range(3)],
                "tasks": []
            }
            curr += step

        # Add Procedures to List
        for key, value in self.__get_procedures_within_range(start, end).items():
            for task in value:
                if task_list.keys().__contains__(key):
                    task_list[key]["tasks"].append(task)

        # Add Preventative Maintenance Tasks to List
        for key, value in self.__get_preventative_within_range(start, end).items():
            for task in value:
                if task_list.keys().__contains__(key):
                    task_list[key]["tasks"].append(task)

        # Add Services to List
        for key, value in self.__get_service_within_range(start, end).items():
            for task in value:
                if task_list.keys().__contains__(key):
                    task_list[key]["tasks"].append(task)

        # Add Unplanned Events to List
        for key, value in self.__get_unplanned_within_range(start, end).items():
            for task in value:
                if task_list.keys().__contains__(key):
                    task_list[key]["tasks"].append(task)

        return task_list

    def __get_procedures_within_range(self, first_date: datetime, last_date: datetime) -> dict[str, list[dict[str, str]]]:
        """Private Function for Retrieving all Maintenance Procedures Within a Date Range"""
        results = {}
        for procedure in self.__maintenance_procedures:
            frequency = self.__get_referenced_value(procedure.frequency_id, "maintenance_frequencies", "id", "frequency")
            weekday = time.strptime(procedure.repeats_on["weekday"], "%A").tm_wday
            ordinal = int(procedure.repeats_on["ordinal"][0]) - 1 # 1st in array is 0, not 1

            # Handle Weekly Procedures
            if frequency == "weekly":
                curr = first_date
                step = timedelta(days=1)
                while curr <= last_date:
                    if curr.weekday() == weekday:
                        date_key = curr.strftime("%d-%m-%Y")
                        if results.keys().__contains__(date_key):
                            results[date_key].append({
                                "id": procedure.procedure,
                                "title": procedure.procedure + ": " + procedure.title,
                                "type": "procedure",
                                "complete": "no",  # TODO: distinguish procedures that have been done for that time period
                                "colour": "blue"
                            })
                        else:
                            results[date_key] = [{
                                "id": procedure.procedure,
                                "title": procedure.procedure + ": " + procedure.title,
                                "type": "procedure",
                                "complete": "no",  # TODO: distinguish procedures that have been done for that time period
                                "colour": "blue"
                            }]
                    curr += step

            # Handle Monthly Procedures
            if frequency == "monthly":
                month = (first_date + relativedelta(weeks=1)).month
                year = first_date.year
                days = [datetime(y, m, d) for y, m, d, wd in pycal.Calendar().itermonthdays4(year, month) if m == month and wd == weekday]
                date_key = days[ordinal].strftime("%d-%m-%Y")
                if results.keys().__contains__(date_key):
                    results[date_key].append({
                        "id": procedure.procedure,
                        "title": procedure.procedure + ": " + procedure.title,
                        "type": "procedure",
                        "complete": "no",  # TODO: distinguish procedures that have been done for that time period
                        "colour": "blue"
                    })
                else:
                    results[date_key] = [{
                        "id": procedure.procedure,
                        "title": procedure.procedure + ": " + procedure.title,
                        "type": "procedure",
                        "complete": "no",  # TODO: distinguish procedures that have been done for that time period
                        "colour": "blue"
                    }]

            # Handle Quarterly Procedures
            if frequency == "quarterly":
                pass

            # Handle Annual Procedures
            if frequency == "annually":
                pass

        return results

    def __get_preventative_within_range(self, first_date: datetime, last_date: datetime) -> dict[str, list[dict[str, str]]]:
        """Private Function for Retrieving all Preventative Maintenance Jobs Within a Date Range"""
        # Initialise Results Dictionary
        results = {}

        # Iterate over Work Orders
        for wo in self.__work_orders:
            # Initialise Created Date and only process Preventative Work Orders in Date Range
            created_at =  datetime.strptime(wo.created_at, "%Y-%m-%d")
            if created_at >= first_date and created_at <= last_date and self.__get_referenced_value(wo.type_id, "maintenance_types", "id", "type") == "preventative":
                pm = [p for p in self.__preventative_maintenance if p.work_order_id == wo.id][0]
                procedure_title = [procedure.title for procedure in self.__maintenance_procedures if procedure.id == pm.procedure_id][0]
                date_key = created_at.strftime("%d-%m-%Y")

                # Add Preventative Maintenance to Results
                if results.keys().__contains__(date_key):
                    results[date_key].append({
                        "id": pm.preventative_id,
                        "title": pm.preventative_id + ": " + procedure_title,
                        "type": "preventative",
                        "complete": "yes" if self.__get_referenced_value(wo.status_id, "work_order_statuses", "id", "status") == "complete" else "no",
                        "colour": "indigo"
                    })
                else:
                    results[date_key] = [{
                        "id": pm.preventative_id,
                        "title": pm.preventative_id + ": " + procedure_title,
                        "type": "preventative",
                        "complete": "yes" if self.__get_referenced_value(wo.status_id, "work_order_statuses", "id", "status") == "complete" else "no",
                        "colour": "indigo"
                    }]

        return results

    def __get_service_within_range(self, first_date: datetime, last_date: datetime) -> dict[str, list[dict[str, str]]]:
        """Private Function for Retrieving all Service Maintenance Jobs Within a Date Range"""
        # Initialise Results Dictionary
        results = {}

        # Iterate over Work Orders
        for wo in self.__work_orders:
            # Initialise Created Date and only process Service Work Orders in Date Range
            created_at = datetime.strptime(wo.created_at, "%Y-%m-%d")
            if created_at >= first_date and created_at <= last_date and self.__get_referenced_value(wo.type_id, "maintenance_types", "id", "type") == "service":
                sm = [s for s in self.__service_maintenance if s.work_order_id == wo.id][0]
                date_key = created_at.strftime("%d-%m-%Y")

                # Add Service Maintenance to Results
                if results.keys().__contains__(date_key):
                    results[date_key].append({
                        "id": sm.service_id,
                        "title": sm.service_id + ": " + sm.title,
                        "type": "service",
                        "complete": "yes" if self.__get_referenced_value(wo.status_id, "work_order_statuses", "id", "status") == "complete" else "no",
                        "colour": "green"
                    })
                else:
                    results[date_key] = [{
                        "id": sm.service_id,
                        "title": sm.service_id + ": " + sm.title,
                        "type": "service",
                        "complete": "yes" if self.__get_referenced_value(wo.status_id, "work_order_statuses", "id", "status") == "complete" else "no",
                        "colour": "green"
                    }]

        return results

    def __get_unplanned_within_range(self, first_date: datetime, last_date: datetime) -> dict[str, list[dict[str, str]]]:
        """Private Function for Retrieving all Unplanned Maintenance Jobs Within a Date Range"""
        # Initialise Results Dictionary
        results = {}

        # Iterate over Unplanned Events
        for ue in self.__unplanned_events:
            # Initialise Created Date and only process Unplanned Events in Date Range
            incident_date = datetime.strptime(ue.date, "%Y-%m-%d")
            if incident_date >= first_date and incident_date <= last_date:
                # Find Associated Work Orders and Unplanned Maintenance
                um = [u for u in self.__unplanned_maintenance if u.id == ue.unplanned_id][0]
                wo = [w for w in self.__work_orders if w.id == um.work_order_id][0]
                date_key = incident_date.strftime("%d-%m-%Y")

                # Add Unplanned Maintenance to Results
                if results.keys().__contains__(date_key):
                    results[date_key].append({
                        "id": um.unplanned_id,
                        "title": um.unplanned_id + ": " + um.title,
                        "type": "unplanned",
                        "complete": "yes" if self.__get_referenced_value(wo.status_id, "work_order_statuses", "id", "status") == "complete" else "no",
                        "colour": "red"
                    })
                else:
                    results[date_key] = [{
                        "id": um.unplanned_id,
                        "title": um.unplanned_id + ": " + um.title,
                        "type": "unplanned",
                        "complete": "yes" if self.__get_referenced_value(wo.status_id, "work_order_statuses", "id", "status") == "complete" else "no",
                        "colour": "red"
                    }]

        return results

    def __get_referenced_value(self, ref_val: str, xref_table: str, xref_column: str, desired_column: str) -> str:
        """Private Function that Retrieves Referenced Values from other Tables"""
        if xref_table == "maintenance_frequencies":
            return [freq[desired_column] for freq in self.__maintenance_frequencies if freq[xref_column] == ref_val][0]
        if xref_table == "maintenance_types":
            return [mt[desired_column] for mt in self.__maintenance_types if mt[xref_column] == ref_val][0]
        if xref_table == "work_order_statuses":
            return [state[desired_column] for state in self.__work_order_statuses if state[xref_column] == ref_val][0]

calendar_handler = CalendarHandler()
