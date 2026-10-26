import reflex as rx
from pems.states.dashboard_state import DashboardState
from pems.states.oee_form_state import OEEFormState
from typing import Callable

def dashboard() -> rx.Component:
    """Function for Rendering the Dashboard"""
    return rx.vstack(
        # Build the Top Bar
        rx.hstack(
            production_filter(),
            timeframe(),
            date_range(),
            align_items="center",
            spacing="0",
            width="100%"
        ),
        width="100%",
        padding_bottom="1rem",
        border_bottom="1px solid #e2e8f0",
        margin_bottom="1rem"
    )

def production_filter() -> rx.Component:
    """Function for Rendering the Production Room Filter"""
    return rx.hstack(
        rx.text("Production Room:", font_weight="bold", width="30%"),
        rx.select(
            DashboardState.production_rooms,
            value=DashboardState.current_room_name,
            name="production_room_filter",
            width="70%",
            on_change=DashboardState.update_current_room
        ),
        align_items="center",
        spacing="0",
        width="33%",
        margin_right="3px"
    )

def timeframe() -> rx.Component:
    """Function for Rendering the Timeframe Selection"""
    return rx.hstack(
        rx.text("Timeframe:", font_weight="bold", width="40%"),
        toggle_button("Weekly", "weekly", "20%", DashboardState.weekly_view, DashboardState.update_timeframe),
        toggle_button("Monthly", "monthly", "20%", DashboardState.monthly_view, DashboardState.update_timeframe),
        toggle_button("Yearly", "yearly", "20%", DashboardState.yearly_view, DashboardState.update_timeframe),
        align_items="center",
        spacing="0",
        width="33%",
        margin_right="3px"
    )

def date_range() -> rx.Component:
    """Function for Rendering the Date Range"""
    return rx.hstack(
        rx.text("Date Range:", font_weight="bold", width="40%"),
        rx.input(
            type="date",
            value=DashboardState.start_date_repr,
            on_change=DashboardState.update_start_date
        ),
        rx.input(
            type="date",
            value=DashboardState.end_date_repr,
            on_change=DashboardState.update_end_date
        ),
        align_items="center",
        spacing="0",
        width="33%"
    )

# --- Form Fields
def new_entry_form() -> rx.Component:
    """Function that Renders a New OEE Submission Form"""
    return rx.dialog.root(
        rx.dialog.content(
            # Form Title
            rx.dialog.title("Production Files Submission Form"),
            rx.divider(
                color_scheme="blue",
                margin_top="4px",
                margin_bottom="16px",
                style={"height": "3px"}
            ),

            # Form Content
            rx.cond(
                OEEFormState.current_step == 0,
                parameters_page(),
                rx.cond(
                    OEEFormState.current_step == OEEFormState.total_steps - 1,
                    submission_page(),
                    file_upload_page(OEEFormState.current_key)
                )
            ),
            rx.divider(
                color_scheme="blue",
                margin_top="4px",
                margin_bottom="16px",
                style={"height": "3px"}
            ),

            # Footer
            form_footer(),
            max_width="21cm"
        ),
        open=OEEFormState.form_open
    )

def parameters_page() -> rx.Component:
    """Function that Renders the Parameter Page for the Form"""
    return rx.vstack(
        rx.heading("Parameter Settings", size="5"),
        rx.hstack(
            rx.text("Form Types:", width="25%"),
            toggle_button("Logs", "log", "25%", OEEFormState.is_logs, OEEFormState.update_form_type),
            toggle_button("Schedule", "schedule", "25%", OEEFormState.is_schedule, OEEFormState.update_form_type),
            toggle_button("Summary", "summary", "25%", OEEFormState.is_summary, OEEFormState.update_form_type),
            width="100%"
        ),
        rx.hstack(
            rx.text("Production Room:", width="25%"),
            rx.select(
                OEEFormState.production_rooms,
                placeholder="Select a Production Room",
                value=OEEFormState.production_room_repr,
                name="production_room",
                width="75%",
                on_change=OEEFormState.update_production_room
            ),
            width="100%"
        ),
        rx.hstack(
            rx.text("Date Range:", width="25%"),
            rx.input(
                value=OEEFormState.start_date_repr,
                name="start_date",
                type="date",
                width="37.5%"
            ),
            rx.input(
                value=OEEFormState.end_date_repr,
                name="end_date",
                type="date",
                width="37.5%"
            ),
            width="100%"
        ),
    )

def file_upload_page(key: str) -> rx.Component:
    """Function that Renders the File Upload Page for a given File key"""
    upload_id = f"upload_{key}"

    return rx.vstack(
        rx.heading(OEEFormState.key_titles[key], size="5"),

        # Upload Box
        rx.upload(
            rx.hstack(
                rx.icon("upload"),
                rx.text("Drag and drop file here"),
                justify_content="center"
            ),
            id=upload_id,
            padding="2em",
            border="2px dashed gray",
            border_radius="8px",
            width="100%",
            on_drop=OEEFormState.update_file(rx.upload_files(upload_id=upload_id))
        ),

        # File Statuses
        rx.vstack(
            rx.foreach(
                OEEFormState.file_indices[key],
                lambda idx: rx.cond(
                    OEEFormState.upload_status[key][idx],
                    rx.hstack(
                        rx.icon("circle_check", color="green"),
                        rx.text(OEEFormState.file_names[key][idx], color_scheme="green"),
                        rx.icon_button(
                            "trash-2",
                            type="button",
                            color_scheme="red",
                            variant="ghost",
                            on_click=lambda _: OEEFormState.delete_file(key, idx)
                        )
                    ),
                    rx.text(f"{OEEFormState.file_names[key][idx]} not uploaded", color_scheme="red")
                )
            )
        ),

        spacing="4",
        width="100%"
    )

def submission_page() -> rx.Component:
    """Function that Renders the Submission Page for the Form"""
    return rx.vstack(
        rx.heading("Submit Form", size="5"),
        rx.text(OEEFormState.status_repr),
        rx.foreach(
            OEEFormState.file_keys,
            lambda key: rx.vstack(
                rx.text(f"{key.upper()} Files:", font_weight="bold"),
                rx.foreach(
                    OEEFormState.file_indices[key],
                    lambda idx: rx.cond(
                        OEEFormState.upload_status[key][idx],
                        rx.hstack(
                            rx.icon("circle_check", color="green"),
                            rx.text(OEEFormState.file_names[key][idx], color_scheme="green"),
                            rx.icon_button(
                                "trash-2",
                                type="button",
                                color_scheme="red",
                                variant="ghost",
                                on_click=lambda _: OEEFormState.delete_file(key, idx)
                            )
                        ),
                        rx.text(f"{OEEFormState.file_names[key][idx]} not uploaded", color_scheme="red")
                    )
                )
            ),
        ),
        rx.hstack(
            rx.button(
                "Submit Form", 
                color_scheme="blue",
                variant="surface",
                disabled=~OEEFormState.upload_complete,
                loading=OEEFormState.submitting,
                on_click=OEEFormState.submit,
                align="center"
            ),
            rx.cond(
                OEEFormState.message != "",
                rx.callout(
                    OEEFormState.message,
                    size="1",
                    variant="outline",
                    color_scheme="gray",
                    high_contrast=False
                ),
                rx.fragment()
            )
        )
        # align="center"
    )

def form_footer() -> rx.Component:
    """Function that Renders the Footer for the Form"""
    return rx.hstack(
        # Controller
        rx.button(
            "Previous", 
            color_scheme=rx.cond(
                OEEFormState.current_step == 0,
                "gray",
                "blue"
            ),
            variant="surface",
            _hover={
                "background_color": rx.cond(
                    OEEFormState.current_step == 0,
                    rx.color("gray", 3),
                    rx.color("blue", 7)
                )
            },
            width="27%",
            disabled=OEEFormState.current_step == 0,
            on_click=OEEFormState.previous
        ),
        rx.button(
            "Next", 
            color_scheme=rx.cond(
                OEEFormState.current_step == OEEFormState.total_steps - 1,
                "gray",
                "blue"
            ),
            variant="surface",
            _hover={
                "background_color": rx.cond(
                    OEEFormState.current_step == OEEFormState.total_steps - 1,
                    rx.color("gray", 3),
                    rx.color("blue", 7)
                )
            },
            width="27%",
            disabled=(OEEFormState.current_step == OEEFormState.total_steps - 1), 
            on_click=OEEFormState.next
        ),
        rx.button(
            "Cancel",
            color_scheme="red",
            variant="surface",
            _hover={"background_color": rx.color("red", 7)},
            width="27%",
            on_click=OEEFormState.cancel
        ),

        # Page Numbers
        rx.text(f"Page {OEEFormState.current_step + 1} of {OEEFormState.total_steps}", width="19%", align_self="center")
    )

# --- Generic Rendered Components ---
def toggle_button(title: str, arg: str, width: str, active: bool, function: Callable[[str], None]) -> rx.Component:
    """Function that Renders a Toggle Button"""
    return rx.button(
        title,
        variant="surface",
        color_scheme=rx.cond(
            active,
            "blue",
            "gray"
        ),
        type="button",
        on_click=lambda _: function(arg),
        width=width,
        _hover={"background_color": rx.cond(
            active,
            rx.color("blue", 7),
            rx.color("gray", 7)
        )}
    )