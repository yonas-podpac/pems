from datetime import datetime
import reflex as rx
from pems.states.maintenance_state import MaintenanceState
from pems.states.preventative_state import PreventativeState
from pems.states.service_state import ServiceState
from pems.states.unplanned_state import UnplannedState

from typing import Callable, Optional

def calendar() -> rx.Component:
    """Function that Renders the Calendar View"""
    day_header = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return rx.card(
        rx.vstack(
            # Calendar Controller
            rx.hstack(
                rx.hstack(
                    rx.button(
                        "<",
                        variant="surface",
                        color_scheme="gray",
                        on_click=MaintenanceState.change_month(-1)
                    ),
                    rx.text(MaintenanceState.month),
                    rx.button(
                        ">",
                        variant="surface",
                        color_scheme="gray",
                        on_click=MaintenanceState.change_month(1)
                    ),
                    width="15em",
                    justify="between",
                    align="center"
                ),
                rx.hstack(
                    rx.button(
                        "Schedule a Service",
                        variant="surface",
                        color_scheme="green",
                        on_click=ServiceState.schedule_service,
                        _hover={"background_color": rx.color("green", 7)}
                    ),
                    rx.button(
                        "Unplanned Maintenance",
                        variant="surface",
                        color_scheme="red",
                        on_click=UnplannedState.new_unplanned_maintenance,
                        _hover={"background_color": rx.color("red", 7)}
                    )
                ),
                width="100%",
                justify="between"
            ),
            rx.divider(margin_top="4"),

            # Days of the Week Header
            rx.grid(
                *[rx.center(rx.text(h, font_weight="bold", size="2")) for h in day_header],
                columns="7",
                width="100%",
                gap="2",
                margin_bottom="2"
            ),

            # Calendar Grid
            rx.grid(
                rx.foreach(
                    MaintenanceState.month_days,
                    lambda day_obj: day_box(
                        MaintenanceState.current_month, 
                        day_obj["day"], 
                        MaintenanceState.day_jobs[day_obj["month"]][day_obj["day"]], 
                        MaintenanceState.open_day_details
                    )
                ),
                columns="7",
                gap="2",
                width="100%"
            ),
            # rx.divider(margin_top="4"),
            width="100%"
        ),
        width="100%",
        padding="4"
    )

def day_box(
        current_month: bool,
        day: int,
        jobs: list[dict[str, str]],
        open_day_details: Callable[[int], None]
) -> rx.Component:
    """Function that Render the Day Boxes in the Calendar"""
    is_today = (day == datetime.now().day)
    return rx.cond(
        day == 0,
        rx.box(width="100%", asepect_ratio="1"),
        rx.box(
            rx.text(
                day.to(str),
                position="absolute",
                top="4px",
                left="8px",
                font_weight="bold",
                color=rx.cond(is_today & current_month, "blue.500", "gray.700"),
                font_size="0.9em"
            ),
            rx.vstack(
                rx.foreach(
                    jobs,
                    lambda job: rx.badge(
                        job["title"],
                        rx.cond(
                            job["complete"],
                            rx.icon(
                                tag="check",
                                position="absolute",
                                right="6px",
                                top="50%",
                                transform="translateY(-50%)",
                                size=14
                            ),
                            rx.fragment()
                        ),
                        font_size="0.7em",
                        color_scheme=job["colour"],
                        border_radius="md",
                        width="100%",
                        white_space="nowrap",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        position="relative",
                        _hover={
                            "background_color": rx.color(job["colour"], 10),
                            "color": rx.color(job["colour"], 3), 
                            "cursor": "pointer"
                        }
                    )
                ),
                margin_top="24px",
                spacing="1",
                width="100%",
                align="start"
            ),
            position="relative",
            width="100%",
            height="8em",
            aspect_ratio="1", # Keeps the calendar grid cells perfectly square
            border=rx.cond(is_today & current_month, "2px solid #3182ce", "1px solid #e2e8f0"),
            border_radius="md",
            padding="8px",
            bg=rx.cond(is_today & current_month, "blue.50", "white"),
            _hover={
                "background_color": rx.color("gray", 3),
                "cursor": "pointer"
            },
            on_click=open_day_details(day)
        )
    )
