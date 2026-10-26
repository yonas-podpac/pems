import reflex as rx
import reflex_enterprise as rxe
from pems.states.calendar_state import CalendarState
from pems.states.preventative_state import PreventativeState
from pems.states.service_state import ServiceState
from pems.states.unplanned_state import UnplannedState
from typing import Optional, Callable

def calendar() -> rx.Component:
    """Function that Renders the Calendar View"""
    return rx.card(
        rx.vstack(
            # Calendar Controller
            rx.hstack(
                # Date Select
                rx.popover.root(
                    rx.popover.trigger(
                        rx.button(
                            rx.hstack(
                                rx.text(CalendarState.curr_repr),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                            ),
                            type="button",
                            bg="white",
                            color="black",
                        ),
                    ),
                    rx.popover.content(
                        date_select(),
                        # rx.vstack(
                        #     rx.hstack(
                        #         rx.text(CalendarState.curr_year),
                        #         rx.icon_button("arrow_up", bg="white", color="black", on_click=CalendarState.change_year(1)),
                        #         rx.icon_button("arrow_down", bg="white", color="black", on_click=CalendarState.change_year(-1)),
                        #         width="100%",
                        #         spacing="2",
                        #         align="center"
                        #     ),
                        #     rx.grid(
                        #         rx.foreach(
                        #             CalendarState.months,
                        #             lambda month_repr: rx.button(
                        #                 month_repr,
                        #                 type="button",
                        #                 bg=rx.cond(month_repr == CalendarState.curr_month, rx.color("blue", 5), "white"),
                        #                 color=rx.cond(month_repr == CalendarState.curr_month, "white", "black"),
                        #                 outline="none",
                        #                 border="none",
                        #                 on_click=CalendarState.set_month(month_repr),
                        #                 _focus={"outline": "none", "box_shadow": "none"},
                        #                 _hover={"background_color": rx.cond(month_repr == CalendarState.curr_month, rx.color("blue", 7), rx.color("gray", 3))}
                        #             )
                        #         ),
                        #         columns="4",
                        #         gap="2",
                        #         width="100%"
                        #     ),
                        #     spacing="2",
                        # ),
                        side="bottom",
                        align="start",
                        style={"width": rx.cond(CalendarState.month_view, "200px", "400px"), "padding": "12px"},
                    ),
                    open=CalendarState.date_select_open,
                    on_open_change=CalendarState.toggle_date_select,
                ),

                rx.hstack(
                    # View Select
                    rx.popover.root(
                        rx.popover.trigger(
                            rx.button(
                                rx.hstack(
                                    rx.cond(
                                        CalendarState.month_view, 
                                        rx.icon("calendar_days"), 
                                        rx.cond(
                                            CalendarState.week_view, 
                                            rx.icon("columns_4"), 
                                            rx.cond(
                                                CalendarState.day_view,
                                                rx.icon("panel_top"),
                                                rx.fragment()
                                            )
                                        )
                                    ),
                                    rx.cond(
                                        CalendarState.month_view,
                                        rx.text("Month"),
                                        rx.cond(
                                            CalendarState.week_view,
                                            rx.text("Week"),
                                            rx.cond(
                                                CalendarState.day_view,
                                                rx.text("Day"),
                                                rx.fragment()
                                            )
                                        )
                                    ),
                                    rx.icon("chevron-down"),
                                    spacing="2",
                                    align="center",
                                ),
                                type="button",
                                bg="white",
                                color="black",
                            ),
                        ),
                        rx.popover.content(
                            rx.vstack(
                                view_select_button("Day", "panel_top", CalendarState.set_day_view, show_check=CalendarState.day_view),
                                view_select_button("Week", "columns_4", CalendarState.set_week_view, show_check=CalendarState.week_view),
                                view_select_button("Month", "calendar_days", CalendarState.set_month_view, show_check=CalendarState.month_view),
                                spacing="2",
                            ),
                            side="bottom",
                            align="start",
                            style={"width": "150px", "padding": "12px"},
                        ),
                        open=CalendarState.view_select_open,
                        on_open_change=CalendarState.toggle_view_select,
                    ),

                    # Maintenance Entry Select
                    rx.popover.root(
                        rx.popover.trigger(
                            rx.button(
                                rx.hstack(
                                    rx.text("Maintenance Entry"),
                                    rx.icon("chevron-down"),
                                    spacing="2",
                                    align="center"
                                ),
                                type="button",
                                bg="#19B1E6",
                                color="white"
                            )
                        ),
                        rx.popover.content(
                            rx.vstack(
                                rx.button(
                                    "Schedule Service",
                                    color_scheme="green",
                                    variant="surface",
                                    width="100%",
                                    _hover={"background_color": rx.color("green", 7)},
                                    on_click=ServiceState.schedule_service
                                ),
                                rx.button(
                                    "Unplanned Maintenance",
                                    color_scheme="red",
                                    variant="surface",
                                    width="100%",
                                    _hover={"background_color": rx.color("red", 7)},
                                    on_click=UnplannedState.new_unplanned_maintenance
                                ),
                                spacing="2"
                            ),
                            side="bottom",
                            align="start",
                            style={"width": "300px", "padding": "12px"}
                        ),
                        open=CalendarState.maintenance_select_open,
                        on_open_change=CalendarState.toggle_maintenance_select
                    ),
                    spacing="2"
                ),
                width="100%",
                justify="between"
            ),

            rx.divider(margin_top="4"),
            rx.cond(
                CalendarState.month_view,
                month_view_grid(),
                rx.cond(
                    CalendarState.week_view,
                    week_view_grid(),
                    rx.cond(
                        CalendarState.day_view,
                        day_view_layout(),
                        rx.fragment()
                    )
                )
            ),
            width="100%"
        ),
        width="100%",
        padding="4"
    )

def date_select() -> rx.Component:
    """Function that Renders a Date Select Tool"""
    return rx.cond(
        CalendarState.month_view,
        month_select(),
        rx.hstack(
            day_select(),
            month_select(),
            width="100%"
        )
    )

def day_select() -> rx.Component:
    """Function that Renders a Day Select Tool"""
    return rx.vstack(
        # Build the Month Selector
        rx.hstack(
            rx.text(CalendarState.full_month),
            rx.icon_button("arrow_up", bg="white", color="black", on_click=CalendarState.change_month(-1)),
            rx.icon_button("arrow_down", bg="white", color="black", on_click=CalendarState.change_month(1)),
            width="100%",
            spacing="2",
            align="center"
        ),
        # Build Weekday Header
        rx.grid(
            rx.foreach(CalendarState.weekdays, lambda w: rx.text(w[0], font_weight="bold", text_align="center")),
            columns="7",
            gap="2",
            width="100%"
        ),
        # Build Grid Select
        rx.grid(
            rx.cond(
                CalendarState.week_view,
                rx.foreach(
                    CalendarState.weeks,
                    lambda week: rx.box(
                        rx.hstack(
                            rx.foreach(
                                week,
                                lambda day: rx.text(
                                    day[:2],
                                    width="2rem",
                                    text_align="center"
                                )
                            ),
                            spacing="4",
                            justify="between"
                        )
                    )
                ),
                rx.cond(
                    CalendarState.day_view,
                    rx.foreach(
                        CalendarState.month_list,
                        lambda day: rx.center(
                            CalendarState.month_tasks[day]["breakdown"][0]["day"],                     
                            width="2em",
                            height="2em",
                            border_radius="100%",
                            background_color=rx.cond(
                                (CalendarState.month_tasks[day]["current"][0]["day"] == "yes") & (CalendarState.month_tasks[day]["current"][1]["month"] == "yes"),
                                rx.color("blue", 5),
                                rx.color("white", 7)
                            ),
                            color=rx.cond(
                                CalendarState.month_tasks[day]["current"][1]["month"] == "yes",
                                "black",
                                rx.color("gray", 5)
                            ),
                            _hover={
                                "background_color": rx.cond(
                                    (CalendarState.month_tasks[day]["current"][0]["day"] == "yes") & (CalendarState.month_tasks[day]["current"][1]["month"] == "yes"),
                                    rx.color("blue", 7),
                                    rx.color("gray", 5)
                                ),
                                "cursor": "pointer"
                            },
                            font_size="1em",
                            on_click=CalendarState.select_day(CalendarState.month_tasks[day]["breakdown"][0]["day"], CalendarState.month_tasks[day]["breakdown"][0]["month"], CalendarState.month_tasks[day]["breakdown"][0]["year"])
                        )
                    ),
                    rx.fragment()
                )
            ),
            columns=rx.cond(CalendarState.week_view, "1", "7"),
            gap="2",
            width="100%"
        ),
        width="50%"
    )

def month_select() -> rx.Component:
    """Function that Renders a Month Select Tool"""
    return rx.vstack(
        # Build the Year Selector
        rx.hstack(
            rx.text(CalendarState.curr_year),
            rx.icon_button("arrow_up", bg="white", color="black", on_click=CalendarState.change_year(1)),
            rx.icon_button("arrow_down", bg="white", color="black", on_click=CalendarState.change_year(-1)),
            width="100%",
            spacing="2",
            align="center"
        ),
        # Build the Month Selector Grid
        rx.grid(
            rx.foreach(
                CalendarState.months,
                lambda month_repr: rx.button(
                    month_repr,
                    type="button",
                    bg=rx.cond(month_repr == CalendarState.curr_month, rx.color("blue", 5), "white"),
                    color=rx.cond(month_repr == CalendarState.curr_month, "white", "black"),
                    outline="none",
                    border="none",
                    on_click=CalendarState.set_month(month_repr),
                    _focus={"outline": "none", "box_shadow": "none"},
                    _hover={"background_color": rx.cond(month_repr == CalendarState.curr_month, rx.color("blue", 7), rx.color("gray", 3))}
                )
            ),
            columns="4",
            gap="2",
            width="100%"
        ),
        spacing="2",
    )

def view_select_button(text: str, icon: str, callback: Optional[Callable], show_check: bool = False):
    """Function for Rendering a View Select Button"""
    return rx.button(
        rx.hstack(
            # Fixed 24px width box keeps text aligned across all buttons
            rx.box(
                rx.cond(show_check, rx.icon("check", size=18), None),
                width="24px",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.icon(icon),
            rx.text(text),
            spacing="2",
            align="center",
        ),
        on_click=callback,
        bg="white",
        color="black",
        width="120px",
        # variant="outline",
        _hover={"outline": "1px solid black"}
    )

def day_view_layout() -> rx.Component:
    """Function that Renders a Day View Layout for the Calendar"""
    return rx.hstack(
        rx.vstack(
            rx.text(
                CalendarState.curr_repr,
                position="absoute",
                top="4px",
                left="8px",
                font_weight="bold",
                color=rx.color("blue", 7),
                font_size="0.9em"
            ),
            rx.foreach(
                CalendarState.day_tasks["tasks"],
                lambda task: calendar_entry(task)
            ),
            width="50%",
            height="100%"
        ),
        rx.vstack(
            day_view_calendar_grid(),
            rx.divider(width="90%"),
            rx.text(CalendarState.day_view_repr, font_weight="bold", width="100%", margin_left="5%"),
            rx.divider(width="90%"),
            rx.cond(
                CalendarState.no_tasks,
                rx.text("No Maintenance Tasks", color="gray", width="100%", margin_left="5%"),
                rx.fragment(), # TODO: Detailed list display of tasks
            ),
            background_color=rx.color("gray", 2),
            align_items="center",
            width="50%",
            height="100%"
        ),
        width="100%",
        height="75vh"
    )

def week_view_grid() -> rx.Component:
    """Function that Renders a Week Grid View for the Calendar"""
    return rx.vstack(
        rx.grid(
            rx.foreach(CalendarState.weekdays, lambda w: rx.text(w, font_weight="bold")),
            columns="7",
            gap="2",
            width="100%"
        ),
        rx.grid(
            rx.foreach(
                CalendarState.week_list,
                lambda day: day_box(CalendarState.week_tasks[day], month_view=False)
            ),
            columns="7",
            gap="2",
            width="100%"
        ),
        height="75vh",
        width="100%"
    )

def month_view_grid() -> rx.Component:
    """Function that Renders a Month Grid View for the Calendar"""
    return rx.vstack(
        rx.grid(
            rx.foreach(CalendarState.weekdays, lambda w: rx.text(w, font_weight="bold")),
            columns="7",
            gap="2",
            width="100%"
        ),
        rx.grid(
            rx.foreach(
                CalendarState.month_list,
                lambda day: day_box(CalendarState.month_tasks[day])
            ),
            columns="7",
            gap="2",
            width="100%"
        ),
        width="100%"
    )

def day_view_calendar_grid() -> rx.Component:
    """Function that Renders a Mini Calendar for the Day View Layout"""
    return rx.vstack(
        rx.grid(
            rx.foreach(CalendarState.weekdays, lambda w: rx.text(w[0], font_weight="bold", text_align="center")),
            columns="7",
            gap="2",
            width="100%"
        ),
        rx.grid(
            rx.foreach(
                CalendarState.month_list,
                lambda day: rx.center(
                    CalendarState.month_tasks[day]["breakdown"][0]["day"],                     
                    width="2em",
                    height="2em",
                    border_radius="100%",
                    background_color=rx.cond(
                        (CalendarState.month_tasks[day]["current"][0]["day"] == "yes") & (CalendarState.month_tasks[day]["current"][1]["month"] == "yes"),
                        rx.color("blue", 5),
                        rx.color("white", 7)
                    ),
                    color=rx.cond(
                        CalendarState.month_tasks[day]["current"][1]["month"] == "yes",
                        "black",
                        rx.color("gray", 5)
                    ),
                    _hover={
                        "background_color": rx.cond(
                            (CalendarState.month_tasks[day]["current"][0]["day"] == "yes") & (CalendarState.month_tasks[day]["current"][1]["month"] == "yes"),
                            rx.color("blue", 7),
                            rx.color("gray", 5)
                        ),
                        "cursor": "pointer"
                    },
                    font_size="1em",
                    on_click=CalendarState.select_day(CalendarState.month_tasks[day]["breakdown"][0]["day"], CalendarState.month_tasks[day]["breakdown"][0]["month"], CalendarState.month_tasks[day]["breakdown"][0]["year"])
                )
            ),
            columns="7",
            gap="2",
            width="100%"
        ),
        width="15em"
    )

def date_select_calendar_grid() -> rx.Component:
    """Function that Renders a Date Select Calendar for either Week or Day Views"""
    return rx.vstack()

def day_box(entry: dict[str, list[str]], month_view: bool = True) -> rx.Component:
    """Function that Renders a Day Box on the Calendar Month View"""
    is_today = (entry["current"][0]["day"] == "yes")
    this_month = (entry["current"][1]["month"] == "yes")
    # return rxe.dnd.drop_target (
    #     rx.box(
    #         rx.text(
    #             entry["breakdown"][0]["day"],
    #             position="absolute",
    #             top="4px",
    #             left="8px",
    #             font_weight="bold",
    #             color=rx.cond(is_today & this_month, rx.color("blue", 7), "gray"),
    #             font_size="0.9em"
    #         ),
    #         rx.vstack(
    #             rx.foreach(
    #                 entry["tasks"],
    #                 lambda task: calendar_entry(task)
    #             ),
    #             margin_top="24px",
    #             spacing="1",
    #             width="100%",
    #             align="start"
    #         ),
    #         position="relative",
    #         width="100%",
    #         height="8em",
    #         aspect_ratio="1",
    #         border=rx.cond(is_today & this_month, "2px solid #3182ce", "1px solid #e2e8f0"),
    #         border_radius="md",
    #         padding="8px",
    #         bg=rx.cond(
    #             is_today & this_month,
    #             "blue.50",
    #             rx.cond(
    #                 this_month,
    #                 "white",
    #                 rx.color("gray", 5)
    #             )
    #         ),
    #         _hover={
    #             "background_color": rx.cond(
    #                 this_month,
    #                 rx.color("gray", 3),
    #                 rx.color("gray", 7)
    #             ),
    #             "cursor": "pointer"
    #         }
    #         # on_click= # TODO: set day_view = True
    #     )
    #     # TODO: complete drop item requirements
    #     # TODO: refer to: https://reflex.dev/docs/enterprise/drag-and-drop/
    # )
    return rx.box(
        rx.text(
            entry["breakdown"][0]["day"],
            position="absolute",
            top="4px",
            left="8px",
            font_weight="bold",
            color=rx.cond(is_today & this_month, rx.color("blue", 7), "gray"),
            font_size="0.9em"
        ),
        rx.vstack(
            rx.foreach(
                entry["tasks"],
                lambda task: calendar_entry(task)
            ),
            margin_top="24px",
            spacing="1",
            width="100%",
            align="start"
        ),
        position="relative",
        width="100%",
        height=rx.cond(month_view, "8em", "70vh"),
        aspect_ratio="1",
        border=rx.cond(is_today & this_month, "2px solid #3182ce", "1px solid #e2e8f0"),
        border_radius="md",
        padding="8px",
        bg=rx.cond(
            is_today & this_month,
            "blue.50",
            rx.cond(
                this_month,
                "white",
                rx.color("gray", 5)
            )
        ),
        _hover={
            "background_color": rx.cond(
                this_month,
                rx.color("gray", 3),
                rx.color("gray", 7)
            ),
            "cursor": "pointer"
        },
        on_click=CalendarState.select_day(entry["breakdown"][0]["day"], entry["breakdown"][0]["month"], entry["breakdown"][0]["year"])
    )

def calendar_entry(task: dict[str, str]) -> rx.Component:
    """Function that Renders a Movable Calendar Entry"""
    # return rxe.dnd.draggable(
    #     rx.badge(
    #         task["title"],
    #         rx.cond(
    #             task["complete"] == "yes",
    #             rx.icon(
    #                 tag="check",
    #                 position="absolute",
    #                 right="6px",
    #                 top="50%",
    #                 transform="translateY(-50%)",
    #                 size=14
    #             ),
    #             rx.fragment()
    #         ),
    #         font_size="0.7em",
    #         color_scheme=task["colour"],
    #         border_radius="md",
    #         width="100%",
    #         white_space="nowrap",
    #         overflow="hidden",
    #         text_overflow="ellipsis",
    #         position="relative",
    #         # on_click= # TODO: handle this based on task["type"]
    #         _hover={
    #             "background_color": rx.color(task["colour"], 10),
    #             "color": rx.color(task["colour"], 3), 
    #             "cursor": "pointer"
    #         }
    #     )
    #     # TODO: complete drag item requirements
    #     # TODO: refer to: https://reflex.dev/docs/enterprise/drag-and-drop/
    # )
    return rx.badge(
        task["title"],
        rx.cond(
            task["complete"] == "yes",
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
        color_scheme=task["colour"],
        border_radius="md",
        width="100%",
        white_space="nowrap",
        overflow="hidden",
        text_overflow="ellipsis",
        position="relative",
        on_click=lambda x: CalendarState.open_work_order(id=task["id"], m_type=task["type"], complete=(task["complete"] == "yes")),
        _hover={
            "background_color": rx.color(task["colour"], 10),
            "color": rx.color(task["colour"], 3), 
            "cursor": "pointer"
        }
    )
