from datetime import datetime
import reflex as rx
from typing import Callable, Optional
from pems.states.auth_state import AuthState
from pems.states.extraction_state import ExtractionState
from pems.states.maintenance_state import MaintenanceState
from pems.states.preventative_state import PreventativeState
from pems.states.service_state import ServiceState
from pems.states.unplanned_state import UnplannedState

def generic_form(
    title: str,
    columns: list[dict],
    options: dict[str, list[str]],
    open: bool,
    toggle: Optional[Callable],
    submit: Optional[Callable],
    # form_toggle_options: dict[str, list[str]] = {},
    form_toggle_on_vals: dict[str, str] = {},
    form_toggle_off_vals: dict[str, str] = {},
    form_toggle_vals: dict[str, str] = {},
    form_toggle_bools: dict[str, bool] = {},
    handle_form_toggle: Callable[[str], None] = lambda x: None,
    current: bool = False,
    defaults: dict[str, str] = {}
) -> rx.Component:
    """Renders a Dialog Box for a Generic Form"""
    options_var = rx.Var.create(options)
    defaults_var = rx.Var.create(defaults)
    toggled_var = rx.Var.create(form_toggle_bools)
    toggle_ons_var = rx.Var.create(form_toggle_on_vals)
    toggle_offs_var = rx.Var.create(form_toggle_off_vals)
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(title),
            rx.form(
                rx.table.root(
                    rx.table.body(
                        rx.foreach(
                            columns,
                            lambda col: rx.table.row(
                                rx.table.cell(
                                    rx.text(col["label"], font_weight="bold"),
                                    width="30%"
                                ),
                                rx.table.cell(
                                    rx.cond(
                                        col["type"] == "select",
                                        rx.cond(
                                            current,
                                            rx.select(
                                                options_var.get(col["key"].to(str)),
                                                value=defaults_var.get(col["key"].to(str)),
                                                name=col["key"],
                                                width="100%"
                                            ),
                                            rx.select(
                                                options_var.get(col["key"].to(str)),
                                                placeholder="Select an Option...",
                                                name=col["key"],
                                                width="100%"
                                            )
                                        ),
                                        rx.cond(
                                            col["type"] == "checkbox",
                                            build_toggle(
                                                toggled_var.get(col["key"].to(str)),
                                                toggle_on_val=toggle_ons_var[col["key"].to(str)],
                                                toggle_off_val=toggle_offs_var.get(col["key"].to(str)),
                                                toggle_key=col["key"],
                                                toggle=handle_form_toggle
                                            ),
                                            build_input(column=col, curr=current, default=defaults_var.get(col["key"].to(str)))
                                        )
                                        # build_input(column=col, width="100%")
                                    ),
                                    width="70%"
                                ),
                                width="100%"
                            )
                        ),
                        rx.table.row(
                            rx.table.cell(rx.dialog.close(rx.button(
                                "Cancel",
                                variant="surface",
                                color_scheme="red",
                                type="button",
                                on_click=toggle,
                                width="100%"
                            )), width="30%"),
                            rx.table.cell(rx.button(
                                "Save Record",
                                type="submit",
                                variant="surface",
                                color_scheme="blue",
                                width="100%"
                            ), width="70%")
                        )
                    )
                ),
                on_submit=submit
            ),
            max_width="480px"
        ),
        open=open
    )

def login_form(redirect: str) -> rx.Component:
    """Renders a Login Form for PEMS"""
    return rx.dialog.root(
        rx.dialog.content(
            # Login Window Title
            rx.dialog.title("PEMS Login"),

            # Close Dialog Button
            rx.dialog.close(
                rx.icon(
                    tag="x",
                    position="absolute",
                    top="12px",
                    right="12px",
                    cursor="pointer",
                    color="gray",
                    _hover={"color": "black"},
                    on_click=AuthState.toggle_login_form
                )
            ),

            # Error Message Callout
            rx.cond(
                AuthState.error_message != "",
                rx.callout(
                    AuthState.error_message,
                    icon="triangle_alert",
                    color_scheme="amber",
                    role="alert",
                    width="100%"
                ),
                rx.fragment()
            ),

            # Login Form
            rx.form(
                rx.vstack(
                    # Username Input
                    rx.text("Username", font_weight="bold", width="120px"),
                    rx.input(
                        placeholder="Username or Email",
                        name="username",
                        width="100%",
                        on_change=AuthState.update_username
                    ),

                    # Password Input
                    rx.text("Password", font_weight="bold", width="120px"),
                    rx.input(
                        placeholder="Enter your password",
                        type="password",
                        name="password",
                        width="100%",
                        on_change=AuthState.update_password
                    ),
                    rx.button(
                        "Forgot Password?",
                        variant="surface",
                        color_scheme="blue",
                        size="1",
                        type="button",
                        on_click=AuthState.reset_password
                    )
                ),

                # Login Form Buttons
                rx.vstack(
                    # Login Button
                    rx.button(
                        "Login",
                        type="submit",
                        color_scheme="green",
                        width="100%"
                    ),

                    # Sign Up Button
                    rx.hstack(
                        rx.text("New User? Create an Account", size="1", color_scheme="gray"),
                        rx.button(
                            "Sign Up",
                            type="button",
                            color_scheme="blue",
                            size="1",
                            on_click=AuthState.toggle_signup_form
                        ),
                        align="center"
                    ),

                    align="center",
                    width="100%",
                    margin_top="1.5em"
                ),
                spacing="3",
                on_submit=AuthState.login(redirect)
            )
        ),
        open=AuthState.is_login_form_open
    )

def signup_form() -> rx.Component:
    """Renders a Sign Up Form"""
    return rx.dialog.root(
        rx.dialog.content(
            # Sign Up Window Title
            rx.dialog.title("Create a PEMS Account"),

            # Error Message Callout
            rx.cond(
                AuthState.error_message != "",
                rx.callout(
                    AuthState.error_message,
                    icon="triangle_alert",
                    color_scheme="amber",
                    role="alert",
                    width="100%"
                ),
                rx.fragment()
            ),

            # Generate Sign Up Form
            rx.form(
                rx.vstack(
                    # Username Input
                    rx.text("Username", font_weight="bold", width="120px"),
                    rx.input(
                        placeholder="Username",
                        name="username",
                        width="100%",
                        on_change=AuthState.update_username
                    ),
                    
                    # Email Address Input
                    rx.text("Email", font_weight="bold", width="120px"),
                    rx.input(
                        type="email",
                        placeholder="Email Address",
                        name="email",
                        width="100%",
                        on_change=AuthState.update_email
                    ),

                    # First Name Input
                    rx.text("First Name", font_weight="bold", width="120px"),
                    rx.input(
                        placeholder="First Name",
                        name="first_name",
                        width="100%",
                        on_change=AuthState.update_first_name
                    ),

                    # Last Name Input
                    rx.text("Last Name", font_weight="bold", width="120px"),
                    rx.input(
                        placeholder="Last Name",
                        name="last_name",
                        width="100%",
                        on_change=AuthState.update_last_name
                    ),

                    # Role Selectbox
                    rx.text("Role", font_weight="bold", width="120px"),
                    rx.select(
                        AuthState.roles,
                        placeholder="Select a role...",
                        name="role",
                        on_change=AuthState.update_role
                    ),

                    # Password Input
                    rx.text("Password", font_weight="bold", width="120px"),
                    rx.input(
                        type="password",
                        placeholder="Enter a valid Password",
                        name="password",
                        width="100%",
                        on_change=AuthState.update_password
                    ),

                    # Confirm Password Input
                    rx.text("Confirm Password", font_weight="bold", width="240px"),
                    rx.input(
                        type="password",
                        placeholder="Re-enter your password",
                        name="confirm_password",
                        width="100%",
                        on_change=AuthState.update_confirm_password
                    ),

                    rx.divider(margin_y="2"),

                    # Email & Password Prompts
                    rx.vstack(
                        requirement_item("Valid Podpac email address", AuthState.is_valid_email),
                        requirement_item("At least 11 characters long", AuthState.has_min_length),
                        requirement_item("Includes a lowercase letter", AuthState.has_lowercase),
                        requirement_item("Includes an uppercase letter", AuthState.has_uppercase),
                        requirement_item("Includes a number", AuthState.has_number),
                        requirement_item("Includes a special character (!@#$...)", AuthState.has_special),
                        requirement_item("Passwords match", AuthState.passwords_match),
                        align_items="start",
                        spacing="1",
                        width="100%"
                    ),

                    rx.divider(margin_y="2"),
                ),

                # Sign Up Form Buttons
                rx.hstack(
                    # Cancel Button
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            variant="soft",
                            color_scheme="red",
                            type="button",
                            on_click=AuthState.toggle_signup_form
                        )
                    ),

                    # 4.b. Sign Up Button
                    rx.button(
                        "Sign Up",
                        type="submit",
                        color_scheme="blue",
                    ),
                    justify="end",
                    width="100%",
                    margin_top="1.5rem"
                ),
                spacing="3",
                on_submit=AuthState.signup
            ),
        ),
        open=AuthState.is_signup_form_open
    )

def delete_entry_window(
        title: str,
        cancel: Optional[Callable],
        confirm: Optional[Callable],
        is_window_open: bool
) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Are you sure you want to delete {}?".format(title)),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    "Delete",
                    color_scheme="red",
                    variant="surface",
                    width="50%",
                    on_click=confirm
                ),
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        color_scheme="gray",
                        variant="surface",
                        width="100%",
                        on_click=cancel
                    ),
                    width="50%"
                ),
                width="100%"
            )
        ),
        open=is_window_open
    )

def extraction_analysis_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            # 1. Form Title
            rx.dialog.title("New Extraction Upload"),

            # 2. Build Table Layout
            rx.form(
                rx.table.root(
                    # 2.1. Research Type
                    rx.table.row(
                        rx.table.cell(
                            rx.text("Research ID", font_weight="bold"),
                            col_span=3
                        ),
                        rx.table.cell(
                            rx.text("Analysis Type", font_weight="bold"),
                            col_span=3
                        ),
                        width="100%"
                    ),
                    rx.table.row(
                        rx.table.cell(
                            rx.input(
                                placeholder="e.g. RD-26-007",
                                name="research_id",
                                width="100%",
                                on_change=ExtractionState.update_research_id
                            ),
                            col_span=3
                        ),
                        rx.table.cell(
                            rx.input(
                                rx.select(
                                    ExtractionState.analysis_options,
                                    value=ExtractionState.analysis_type,
                                    name="analysis_type",
                                    width="100%",
                                    on_change=ExtractionState.update_analysis_type
                                )
                            ),
                            col_span=3
                        ),
                        width="100%"
                    ),

                    # 2.2. Capsule / Lid Information
                    rx.table.row(
                        rx.table.cell(
                            rx.text("Capsule Type", font_weight="bold"),
                            col_span=2
                        ),
                        rx.table.cell(
                            rx.text("Lid Material", font_weight="bold"),
                            col_span=2
                        ),
                        rx.table.cell(
                            rx.text("Group Number", font_weight="bold"),
                            col_span=2
                        ),
                        width="100%"
                    ),
                    rx.table.row(
                        rx.table.cell(
                            rx.input(
                                placeholder="Enter capsule type...",
                                name="capsule_type",
                                width="100%",
                                on_change=ExtractionState.update_capsule_type
                            ),
                            col_span=2
                        ),
                        rx.table.cell(
                            rx.input(
                                placeholder="Enter lid material...",
                                name="lid_material",
                                width="100%",
                                on_change=ExtractionState.update_lid_material
                            ),
                            col_span=2
                        ),
                        rx.table.cell(
                            rx.input(
                                type="number",
                                placeholder="Enter test group number...",
                                step="1",
                                name="capsule_group",
                                width="100%",
                                on_change=ExtractionState.update_capsule_group
                            ),
                            col_span=2
                        ),
                        width="100%"
                    ),

                    # 2.3. Coffee Information Row
                    rx.table.row(
                        rx.table.cell(
                            rx.text("Coffee Profile", font_weight="bold"),
                            col_span=2
                        ),
                        rx.table.cell(
                            rx.text("Dose Weight (g)", font_weight="bold"),
                            col_span=2
                        ),
                        rx.table.cell(
                            rx.text("Grind Setting", font_weight="bold"),
                            col_span=2
                        ),
                        width="100%"
                    ),
                    rx.table.row(
                        rx.table.cell(
                            rx.input(
                                placeholder=rx.cond(ExtractionState.coffee_selected, "e.g. RC09", "No Coffee Selected"),
                                name="coffee_profile",
                                width="100%",
                                disabled=~ExtractionState.coffee_selected,
                                on_change=ExtractionState.update_coffee_profile
                            ),
                            col_span=2
                        ),
                        rx.table.cell(
                            rx.input(
                                type="number",
                                placeholder=rx.cond(ExtractionState.coffee_selected, "Enter dose weight...", "No Coffee Selected"),
                                name="dose_weight",
                                step="0.1",
                                width="100%",
                                disabled=~ExtractionState.coffee_selected,
                                on_change=ExtractionState.update_dose_weight
                            ),
                            col_span=2
                        ),
                        rx.table.cell(
                            rx.input(
                                type="number",
                                placeholder=rx.cond(ExtractionState.coffee_selected, "Enter grind setting...", "No Coffee Selected"),
                                name="grind_setting",
                                step="0.1",
                                width="100%",
                                disabled=~ExtractionState.coffee_selected,
                                on_change=ExtractionState.update_grind_setting
                            ),
                            col_span=2
                        ),
                        width="100%"
                    ),

                    # 2.4. Date Information Row
                    rx.table.row(
                        rx.table.cell(
                            rx.text("Pack Date", font_weight="bold"),
                            col_span=3
                        ),
                        rx.table.cell(
                            rx.text("Grind Date", font_weight="bold"),
                            col_span=3
                        ),
                        width="100%"
                    ),
                    rx.table.row(
                        rx.table.cell(
                            rx.input(
                                type="date",
                                name="pack_date",
                                width="100%",
                                on_change=ExtractionState.update_pack_date
                            ),
                            col_span=3
                        ),
                        rx.table.cell(
                            rx.input(
                                type="date",
                                name="grind_date",
                                width="100%",
                                disabled=~ExtractionState.coffee_selected,
                                on_change=ExtractionState.update_grind_date
                            ),
                            col_span=3
                        ),
                        width="100%"
                    ),

                    # 2.5. File Drop
                    rx.table.row(
                        rx.table.cell(
                            rx.cond(
                                ExtractionState.pending,
                                rx.hstack(
                                    rx.text(ExtractionState.filename, size="1", color="green"),
                                    rx.icon_button(
                                        "trash-2",
                                        type="button",
                                        color_scheme="red",
                                        variant="ghost",
                                        size="1",
                                        disabled=ExtractionState.is_processing,
                                        on_click=ExtractionState.delete_file
                                    ),
                                    id="csv_uploader",
                                    border="2px dashed green",
                                    padding="5px",
                                    border_radius="8px",
                                    width="100%",
                                    align="center"
                                ),
                                rx.upload(
                                    rx.text("Drag and drop file here", size="1", color_scheme="gray"),
                                    id="csv_uploader",
                                    border="2px dashed #ccc",
                                    padding="5px",
                                    border_radius="8px",
                                    width="100%",
                                    on_drop=ExtractionState.update_file(rx.upload_files(upload_id="csv_uploader"))
                                )
                            ),
                            col_span=6
                        ),
                        width="100%"
                    ),

                    # 2.6. Form Buttons
                    rx.table.row(
                        rx.table.cell(rx.button(
                            "Submit Analysis",
                            type="submit",
                            variant="surface",
                            color_scheme="blue",
                            width="100%",
                            disabled=~ExtractionState.form_complete,
                            loading=ExtractionState.is_processing,
                            _hover={"background_color", rx.cond(
                                ExtractionState.form_complete,
                                rx.color("blue", 7),
                                rx.color("blue", 1)
                            )}
                        ), col_span=3),
                        rx.table.cell(rx.dialog.close(rx.button(
                            "Cancel",
                            variant="surface",
                            color_scheme="red",
                            type="button",
                            disabled=ExtractionState.is_processing,
                            on_click=ExtractionState.toggle,
                            width="100%",
                            _hover={"background_color": rx.color("red", 7)}
                        )), col_span=3),
                        width="100%"
                    ),
                ),
                on_submit=ExtractionState.submit_form
            ),
            max_width="21cm"
        ),
        open=ExtractionState.is_extraction_form_open
    )

def day_jobs_window() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            # 1. Day Jobs Window Title
            rx.dialog.title(MaintenanceState.day_jobs_title),

            # 2. Close Dialog Box
            rx.dialog.close(
                rx.icon(
                    tag="x",
                    position="absolute",
                    top="12px",
                    right="12px",
                    cursor="pointer",
                    color="gray",
                    _hover={"color": "black"},
                    on_click=MaintenanceState.close_day_details
                )
            ),

            # 3. Add List of Jobs for Date
            rx.foreach(
                MaintenanceState.selected_day_jobs,
                lambda job: rx.badge(
                    job["title"],
                    font_size="0.7em",
                    color_scheme=job["colour"],
                    border_radius="md",
                    width="100%",
                    white_space="nowrap",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    _hover={
                        "background_color": rx.color(job["colour"], 10),
                        "color": rx.color(job["colour"], 3),
                        "cursor": "pointer"
                    },
                    on_click=rx.cond(
                        job["type"] == "preventative",
                        PreventativeState.open_work_order_form(job["id"], job["complete"]),
                        rx.cond(
                            job["type"] == "service",
                            ServiceState.open_work_order_form(job["id"], job["complete"]),
                            UnplannedState.open_work_order_form(job["id"], job["complete"])
                        )
                    )
                )
            )
        ),
        open=MaintenanceState.is_day_jobs_open
    )

def new_maintenance_procedure() -> rx.Component:
    """Function that Renders a New Preventative Maintenance Procedure Form"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                # 1. ID & Title Block
                # 1.1. Form Title Row
                rx.dialog.title("New Preventative Maintenance Procedure Form"),

                # 1.2. ID Row
                rx.hstack(
                    rx.text("Maintenance Procedure ID", font_weight="bold", width="50%"),
                    rx.badge(
                        PreventativeState.maintenance_id,
                        color_scheme="blue",
                        border_radius="md",
                        font_size="1",
                        align_items="center",
                        justify_content="center",
                        width="50%"
                    ),
                    align_items="center",
                    spacing="0"
                ),

                # 1.3. Maintenance Procedure Title
                rx.hstack(
                    rx.text("Title", font_weight="bold", width="25%"),
                    rx.input(
                        placeholder="e.g. Annual K-fee Maintenance Procedures",
                        value=PreventativeState.title,
                        name="title",
                        width="75%",
                        on_change=PreventativeState.update_title
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),
                rx.divider(
                    color_scheme="blue",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 2. Procedure Location & Frequency Details
                rx.text("Section 1. Procedure Location & Frequency Details", font_weight="bold"),

                # 2.1. Production Room Selection
                rx.hstack(
                    rx.text("Production Room", font_weight="bold", width="50%"),
                    rx.select(
                        PreventativeState.locations,
                        placeholder="Choose a Production Area",
                        name="location",
                        width="50%",
                        on_change=PreventativeState.update_location
                    ),
                    align_items="center",
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 2.2. Estimated Duration Selection
                rx.hstack(
                    rx.text("Estimated Duration (mins)", font_weight="bold", width="50%"),
                    rx.input(
                        placeholder="e.g. 10 minutes",
                        type="number",
                        step="1",
                        name="estimated_duration",
                        width="50%",
                        on_change=PreventativeState.update_estimated_duration
                    ),
                    align_items="center",
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 2.3. Frequency Details Selection
                rx.hstack(
                    rx.text("Repeats", font_weight="bold", width="25%"),
                    rx.select(
                        PreventativeState.frequencies,
                        placeholder="e.g. Weekly, Monthly, etc.",
                        name="frequency",
                        width="25%",
                        on_change=PreventativeState.update_frequency
                    ),
                    align_items="center",
                    spacing="0",
                    padding_top="0.5em"
                ),
                rx.hstack(
                    rx.text("On the ", font_weight="bold", width="10%"),
                    rx.select(
                        PreventativeState.ordinals,
                        placeholder="e.g. 1st, 2nd, etc.",
                        width="20%",
                        on_change=PreventativeState.update_ordinal
                    ),
                    rx.select(
                        PreventativeState.weekdays,
                        placeholder="Monday, Tuesday, etc.",
                        width="20%",
                        on_change=PreventativeState.update_weekday
                    ),
                    align_items="center",
                    spacing="0",
                    padding_top="0.5em"
                ),
                rx.hstack(
                    rx.text("Start Date: ", font_weight="bold"),
                    rx.text(PreventativeState.day_of_month),
                    rx.select(
                        PreventativeState.months,
                        value=PreventativeState.selected_month,
                        name="start_month",
                        width="20%",
                        on_change=PreventativeState.update_month
                    ),
                    rx.text(PreventativeState.year),
                    align="center"
                ),
                rx.divider(
                    color_scheme="blue",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 3. Asset & Task Details
                rx.table.root(
                    rx.table.body(
                        rx.foreach(
                            PreventativeState.asset_fields,
                            lambda field: rx.fragment(
                                # 3.3. Asset Selection Row
                                rx.table.row(
                                    rx.table.row_header_cell(
                                        rx.text("Asset", font_weight="bold"),
                                        rx.select(
                                            PreventativeState.assets,
                                            placeholder="Select an Asset...",
                                            name=field,
                                            disabled=~PreventativeState.location_selected,
                                            width="100%",
                                            on_change=lambda val: PreventativeState.update_asset(field, val)
                                        ),
                                        rx.cond(
                                            field == "asset_0",
                                            rx.fragment(),
                                            rx.icon_button(
                                                "trash-2",
                                                size="1",
                                                type="button",
                                                variant="soft",
                                                color_scheme="red",
                                                on_click=PreventativeState.delete_asset_field(field)
                                            )
                                        ),
                                        col_span=2
                                    )
                                ),

                                # 3.4. Task Header Row
                                rx.table.row(
                                    rx.table.row_header_cell(rx.text("Station", font_weight="bold"), width="50%"),
                                    rx.table.row_header_cell(rx.text("Job", font_weight="bold"), width="50%"),
                                ),

                                # 3.5. Station & Task Selection
                                rx.foreach(
                                    PreventativeState.station_fields[field],
                                    lambda station: rx.table.row(
                                        rx.table.cell(
                                            rx.cond(
                                                PreventativeState.station_available[field],
                                                rx.select(
                                                    PreventativeState.stations[field],
                                                    placeholder="Selected a Station...",
                                                    name=station,
                                                    width="100%",
                                                    on_change=lambda val: PreventativeState.update_station(field, station, val)
                                                ),
                                                rx.text("No Stations Available for Asset")
                                            ),
                                            width="50%"
                                        ),
                                        rx.table.cell(
                                            rx.text_area(
                                                placeholder="Enter Task Description...",
                                                name=station + "_task",
                                                width=rx.cond(station == "station_0", "100%", "80%"),
                                                on_change=lambda val: PreventativeState.update_task(field, station, val)
                                            ),
                                            rx.cond(
                                                station == "station_0",
                                                rx.fragment(),
                                                rx.icon_button(
                                                    "trash-2",
                                                    size="1",
                                                    type="button",
                                                    variant="soft",
                                                    color_scheme="red",
                                                    on_click=PreventativeState.delete_station_field(field, station)
                                                )
                                            ),
                                        )
                                    ),
                                ),

                                # 3.6. Add Station Button Row
                                rx.table.row(
                                    rx.table.cell(
                                        rx.button(
                                            "+ Add Station", 
                                            type="button",
                                            variant="surface",
                                            color_scheme="blue",
                                            on_click=PreventativeState.add_station_field(field),
                                            width="100%",
                                            _hover={"background_color": rx.color("blue", 7)}
                                        ),
                                        col_span=2
                                    ),
                                ),
                            ),
                        ),

                        # 3.7. Add Asset Row
                        rx.table.row(
                            rx.table.cell(
                                rx.button(
                                    "+ Add Asset",
                                    type="button",
                                    variant="surface",
                                    color_scheme="blue",
                                    width="100%",
                                    on_click=PreventativeState.add_asset_field,
                                    _hover={"background_color": rx.color("blue", 7)}
                                ),
                                col_span=2
                            ),
                        )
                    ),
                ),
                rx.divider(
                    color_scheme="blue",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 4. Form Buttons
                rx.hstack(
                    rx.button(
                        "Submit Maintenance Procedure",
                        type="submit",
                        variant="surface",
                        color_scheme="blue",
                        width="50%",
                        disabled=~PreventativeState.form_complete,
                        loading=PreventativeState.submitting,
                        _hover={"background_color": rx.cond(
                            PreventativeState.form_complete,
                            rx.color("blue", 7),
                            rx.color("blue", 1)
                        )}
                    ),
                    rx.dialog.close(rx.button(
                        "Cancel",
                        variant="surface",
                        color_scheme="red",
                        type="button",
                        on_click=PreventativeState.toggle,
                        width="100%",
                        _hover={"background_color": rx.color("red", 7)}
                    ), width="50%")
                ),

                on_submit=PreventativeState.submit
            ),
            max_width="21cm"
        ),
        open=PreventativeState.new_procedure_form_open
    )

def service_form() -> rx.Component:
    """Render a Service Scheduling Form"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                # 1. ID & Title Block
                # 1.1. Form Title Row
                rx.dialog.title("Service Scheduling & Summary Form"),

                # 1.2. ID Rows
                rx.hstack(
                    rx.text("Work Order ID", font_weight="bold", width="25%"),
                    rx.badge(
                        ServiceState.work_order_id,
                        color_scheme="gray",
                        border_radius="md",
                        font_size="1",
                        align_items="center",
                        justify_content="center",
                        width="25%"
                    ),
                    rx.text("Service ID", font_weight="bold", width="25%"),
                    rx.badge(
                        ServiceState.maintenance_id,
                        color_scheme="green",
                        border_radius="md",
                        font_size="1",
                        align_items="center",
                        justify_content="center",
                        width="25%"
                    ),
                    align_items="center",
                    spacing="0"
                ),

                rx.hstack(
                    rx.text("Title", font_weight="bold", width="20%"),
                    rx.input(
                        placeholder="Select a Title for the Service...",
                        value=ServiceState.title,
                        name="title",
                        width="80%",
                        on_change=ServiceState.update_title
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),
                rx.divider(
                    color_scheme="green",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 2. Assignment Block
                rx.text("Section 1: Reporting & Service Assignment Details", font_weight="bold"),

                # 2.1. Reporting
                rx.hstack(
                    rx.text("Scheduled By", font_weight="bold", width="50%"),
                    rx.text("Service Date", font_weight="bold", width="50%"),
                    spacing="0",
                    padding_top="0.5em"
                ),

                rx.hstack(
                    rx.input(
                        placeholder="Enter Employee's Name",
                        value=ServiceState.reported_by,
                        name="reported_by",
                        width="50%",
                        on_change=ServiceState.update_reported_by
                    ),
                    rx.input(
                        type="date",
                        value=ServiceState.scheduled_date,
                        width="33.3%",
                        on_change=ServiceState.update_created_at
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 2.2. Assignment
                rx.hstack(
                    rx.text("Internal / External?", font_weight="bold", width="25%"),
                    build_toggle(ServiceState.external, "External", "Internal", "external", ServiceState.update_external, width="25%"),
                    spacing="0",
                    padding_top="0.5em"
                ),

                rx.hstack(
                    rx.text(
                        rx.cond(ServiceState.external, "Service Provider", "Assigned To"),
                        font_weight="bold",
                        width="25%"
                    ),
                    rx.input(
                        placeholder=rx.cond(ServiceState.external, "Enter Service Provider' Name", "Enter Employee's Name"),
                        value=ServiceState.assigned_to,
                        name="assigned_to",
                        width="25%",
                        on_change=ServiceState.update_assigned_to
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),
                rx.divider(
                    color_scheme="green",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 3. Serviced Assets Block
                rx.text("Section 2: Assets to be Serviced", font_weight="bold"),

                # 3.1. One Production Area Toggle
                rx.hstack(
                    rx.text("One Production Area?", font_weight="bold", width="25%"),
                    build_toggle(ServiceState.one_area, "Yes", "No", "one_area", ServiceState.update_one_area, width="25%"),
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 3.2. Location & Asset Selection
                rx.foreach(
                    ServiceState.asset_fields,
                    lambda field: rx.vstack(
                        rx.hstack(
                            rx.text("Production Area:", width="25%", align_self="center"),
                            rx.cond(
                                field == "asset_0",
                                rx.select(
                                    ServiceState.locations,
                                    placeholder="Select Production Area",
                                    value=ServiceState.services[field]["location"],
                                    name=field + "_location",
                                    width="25%",
                                    on_change=lambda val: ServiceState.update_service_location(field, val)
                                ),
                                rx.cond(
                                    ServiceState.one_area,
                                    rx.text(ServiceState.services[field]["location"], width="25%", align_self="center"),
                                    rx.select(
                                        ServiceState.locations,
                                        placeholder="Select Production Area",
                                        value=ServiceState.services[field]["location"],
                                        name=field + "_location",
                                        width="25%",
                                        on_change=lambda val: ServiceState.update_service_location(field, val)
                                    )
                                )
                            ),
                            width="100%",
                            padding="0"
                        ),
                        rx.hstack(
                            rx.text("Asset:", width="25%", align_self="center"),
                            rx.select(
                                ServiceState.assets[field],
                                placeholder="Select Asset",
                                value=ServiceState.services[field]["asset"],
                                name=field + "_asset",
                                width="25%",
                                on_change=lambda val: ServiceState.update_service_asset(field, val)
                            ),
                            width="100%",
                            padding="0"
                        ),
                        rx.hstack(
                            rx.text("Notes:", width="25%", align_self="center"),
                            rx.text_area(
                                placeholder="Notes for Asset",
                                value=ServiceState.services[field]["notes"],
                                name=field + "_notes",
                                width="75%",
                                on_change=lambda val: ServiceState.update_service_note(field, val)
                            ),
                            width="100%",
                            padding="0"
                        ),
                    ),
                ),
                rx.button(
                    "+ Add Another Asset to be Serviced",
                    type="button",
                    variant="surface",
                    color_scheme="gray",
                    on_click=ServiceState.add_field,
                    width="100%",
                    _hover={"background_color": rx.color("gray", 7)}
                ),

                # 3.3. Additional Notes
                rx.hstack(
                    rx.text("Additional Notes:", font_weight="bold", width="25%", align_self="center"),
                    rx.text_area(
                        placeholder="Services Notes...",
                        value=ServiceState.additional_notes,
                        width="75%",
                        on_change=ServiceState.update_additional_notes
                    ),
                    width="100%",
                    padding_top="0.5em"
                ),

                rx.divider(
                    color_scheme="green",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 4. Completion Summary
                rx.text("Section 3: Completion Summary", font_weight="bold"),

                # 4.1. Complete Toggle & Date Select
                rx.hstack(
                    rx.text("Complete?", font_weight="bold", width="25%"),
                    build_toggle(ServiceState.service_complete, "Yes", "No", "service_complete", ServiceState.update_complete_service, width="25%"),
                    rx.text("Completion Date:", font_weight="bold", width="25%"),
                    rx.input(
                        type="date",
                        name="completed_at",
                        disabld=~ServiceState.service_complete,
                        on_change=ServiceState.update_completed_at
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 4.2. Service Metrics
                rx.hstack(
                    rx.text("Total Downtime (hrs)", font_weight="bold", width="50%"),
                    rx.text("Total Cost ($)", font_weight="bold", width="50%"),
                    spacing="0"
                ),
                rx.hstack(
                    rx.input(
                        placeholder="Enter downtime...",
                        value=ServiceState.downtime,
                        type="number",
                        step="0.01",
                        name="downtime",
                        width="50%",
                        on_change=ServiceState.update_downtime
                    ),
                    rx.input(
                        placeholder="Enter cost...",
                        value=ServiceState.cost,
                        type="number",
                        step="0.01",
                        name="cost",
                        width="50%",
                        on_change=ServiceState.update_cost
                    ),
                    spacing="0"
                ),

                rx.divider(
                    color_scheme="green",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 5. Form Buttons
                rx.hstack(
                    rx.button(
                        rx.cond(
                            ServiceState.service_complete,
                            "Submit Service",
                            "Schedule Service"
                        ),
                        type="submit",
                        variant="surface",
                        color_scheme="blue",
                        width="50%",
                        disabled=~ServiceState.form_complete,
                        loading=ServiceState.submitting,
                        _hover={"background_color": rx.cond(
                            ServiceState.form_complete,
                            rx.color("blue", 7),
                            rx.color("blue", 1)
                        )}
                    ),
                    rx.dialog.close(rx.button(
                        "Cancel",
                        variant="surface",
                        color_scheme="red",
                        type="button",
                        on_click=ServiceState.toggle,
                        width="100%",
                        _hover={"background_color": rx.color("red", 7)}
                    ), width="100%"),
                    spacing="0"
                ),

                on_submit=ServiceState.submit
            ),
            max_width="21cm"
        ),
        open=ServiceState.service_form_open
    )

def unplanned_maintenance_form() -> rx.Component:
    """Render an Unplanned Maintenance Form"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                # 1. ID & TItle Block
                # 1.1. Form Title Row
                rx.dialog.title("Unplanned Maintenance Entry Form"),

                # 1.2. ID Rows
                rx.hstack(
                    rx.text("Work Order ID", font_weight="bold", width="25%"),
                    rx.badge(
                        UnplannedState.work_order_id,
                        color_scheme="gray",
                        border_radius="md",
                        font_size="1",
                        align_items="center",
                        justify_content="center",
                        width="25%"
                    ),
                    rx.text("Unplanned ID", font_weight="bold", width="25%"),
                    rx.badge(
                        UnplannedState.maintenance_id,
                        color_scheme="red",
                        border_radius="md",
                        font_size="1",
                        align_items="center",
                        justify_content="center",
                        width="25%"
                    ),
                    align_items="center",
                    spacing="0"
                ),

                rx.hstack(
                    rx.text("Title", font_weight="bold", width="20%"),
                    rx.input(
                        placeholder="Select a Title for the Issue...",
                        value=UnplannedState.title,
                        name="title",
                        width="80%",
                        on_change=UnplannedState.update_title
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),
                rx.divider(
                    color_scheme="red",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 2. Initial Report Block
                # 2.1. Location & Asset Identification
                rx.text("Section 1: Location & Asset", font_weight="bold"),
                rx.hstack(
                    rx.text("Production Room", font_weight="bold", width="25%"),
                    rx.select(
                        UnplannedState.locations,
                        placeholder="Select an Area...",
                        value=UnplannedState.location,
                        name="location",
                        width="75%",
                        on_change=UnplannedState.update_location
                    ),
                    spacing="0",
                    # padding_top="0.5em"
                ),
                rx.hstack(
                    rx.text("Asset", font_weight="bold", width="25%"),
                    rx.select(
                        UnplannedState.assets,
                        placeholder="Select an Asset...",
                        value=UnplannedState.asset,
                        name="asset",
                        width="75%",
                        disabled=~UnplannedState.location_selected,
                        on_change=UnplannedState.update_asset
                    ),
                    spacing="0"
                ),
                rx.hstack(
                    rx.text("Station", font_weight="bold", width="25%"),
                    rx.select(
                        UnplannedState.stations,
                        placholer=rx.cond(
                            UnplannedState.stations_available,
                            "No Stations Available",
                            "Select a Station..."
                        ),
                        value=UnplannedState.station,
                        name="station",
                        width="75%",
                        disabled=~UnplannedState.stations_available,
                        on_change=UnplannedState.update_station
                    ),
                    spacing="0",

                ),

                # 2.2. UM History
                rx.hstack(
                    rx.button(
                        rx.cond(UnplannedState.show_past, "-", "+"),
                        type="button",
                        color="maroon",
                        background_color="inherit",
                        on_click=UnplannedState.expand_issues,
                        border="none",
                        width="2em"
                    ),
                    rx.text("Past Unplanned Issues:", font_weight="bold", color="maroon"),
                    background_color=rx.color("red", 3),
                    align="center",
                    width="100%"
                ),
                rx.cond(
                    UnplannedState.show_past,
                    rx.select(
                        UnplannedState.past_ums,
                        on_change=UnplannedState.update_past_um,
                        width="100%"
                    ),
                    rx.fragment()
                ),

                rx.divider(
                    color_scheme="red",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 3. Reporting & Initial Failure Details
                rx.text("Section 2: Reporting & Initial Failure Details", font_weight="bold"),

                # 3.1. Reporting
                rx.hstack(
                    rx.text("Reported By", font_weight="bold", width="33.3%"),
                    rx.text("Assigned To", font_weight="bold", width="33.3%"),
                    rx.text("Initial Failure Date", font_weight="bold", width="33.3%"),
                    spacing="0",
                    padding_top="0.5em"
                ),

                rx.hstack(
                    rx.input(
                        placeholder="Enter Employee's Name",
                        value=UnplannedState.reported_by,
                        name="reported_by",
                        width="33.3%",
                        on_change=UnplannedState.update_reported_by
                    ),
                    rx.input(
                        placeholder="Enter Employee's Name",
                        value=UnplannedState.assigned_to,
                        name="assigned_to",
                        width="33.3%",
                        on_change=UnplannedState.update_assigned_to
                    ),
                    rx.input(
                        type="date",
                        value=UnplannedState.failure_date,
                        name="created_at",
                        width="33.3%",
                        on_change=UnplannedState.update_failure_date
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 3.2. Classification
                rx.hstack(
                    rx.text("Failure Type", font_weight="bold", width="50%"),
                    rx.text("Severity", font_weight="bold", width="50%"),
                    spacing="0",
                    padding_top="0.5em"
                ),

                rx.hstack(
                    rx.select(
                        UnplannedState.failure_types,
                        placeholder="Select a Failure Type",
                        value=UnplannedState.failure_type,
                        name="failure_type",
                        width="50%",
                        on_change=UnplannedState.update_failure_type
                    ),
                    rx.select(
                        UnplannedState.severities,
                        placeholder="Minor / Major",
                        value=UnplannedState.severity,
                        name="severity",
                        width="50%",
                        on_change=UnplannedState.update_severity
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 3.3. Description of Event
                rx.hstack(
                    rx.text("Description", font_weight="bold", width="20%"),
                    rx.text_area(
                        placeholder="Enter a description of the failure...",
                        value=UnplannedState.description,
                        name="description",
                        width="80%",
                        on_change=UnplannedState.update_description
                    ),
                    padding_top="0.5em"
                ),
                rx.divider(
                    color_scheme="red",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 4. Downtime Log Block
                rx.text("Section 3: Incidents & Action Logs", font_weight="bold"),
                rx.foreach(
                    UnplannedState.action_fields,
                    lambda field: rx.vstack(
                        rx.text(UnplannedState.incident_titles[field]),
                        rx.hstack(
                            rx.text("Start: ", width="12.5%", align_self="center"),
                            rx.input(
                                type="date",
                                value=UnplannedState.events[field]["event_date"],
                                name=field + "_event_date",
                                width="25%",
                                on_change=lambda val: UnplannedState.update_event_date(field, val)
                            ),
                            rx.input(
                                type="time",
                                value=UnplannedState.events[field]["event_time"],
                                name=field + "_event_time",
                                width="25%",
                                on_change=lambda val: UnplannedState.update_event_time(field, val)
                            ),
                            rx.text("Duration: ", width="12.5%", align_self="center"),
                            rx.input(
                                placeholder="Enter duration...",
                                value=UnplannedState.events[field]["duration"],
                                type="number",
                                step="0.1",
                                name=field + "_duration",
                                width="25%",
                                on_change=lambda val: UnplannedState.update_event_duration(field, val)
                            ),
                            width="100%",
                            padding="0"
                        ),
                        rx.hstack(
                            rx.text("Action Taken: ", width="25%"),
                            rx.text_area(
                                placeholder="Enter an action taken...",
                                value=UnplannedState.events[field]["action_taken"],
                                name=field + "_action_taken",
                                width="75%",
                                on_change=lambda val: UnplannedState.update_event_action(field, val)
                            ),
                            width="100%",
                            padding="0"
                        ),
                        rx.hstack(
                            rx.text("Parts Used (if any): ", width="25%", align_self="center"),
                            rx.select(
                                UnplannedState.spare_parts,
                                placeholder="Select a part used...",
                                value=UnplannedState.events[field]["spare_part"],
                                name=field + "_spare_part",
                                width="50%",
                                on_change=lambda val: UnplannedState.update_event_spare(field, val)
                            ),
                            rx.hstack(
                                rx.input(
                                    placeholder="Number of Parts Used...",
                                    value=UnplannedState.events[field]["quantity"],
                                    type="number",
                                    step="1",
                                    name=field + "_quantity",
                                    width=rx.cond(field == "action_0", "100%", "90%"),
                                    on_change=lambda val: UnplannedState.update_event_quantity(field, val)
                                ),
                                rx.cond(
                                    field == "action_0",
                                    rx.fragment(),
                                    rx.icon_button(
                                        "trash-2",
                                        size="1",
                                        type="button",
                                        variant="soft",
                                        color_scheme="red",
                                        on_click=UnplannedState.delete_action_field(field)
                                    )
                                ),
                            ),
                            width="100%",
                            padding="0"
                        ),
                    )
                ),
                rx.button(
                    "+ Add Another Event",
                    type="button",
                    variant="surface",
                    color_scheme="gray",
                    on_click=UnplannedState.add_action_field,
                    width="100%",
                    _hover={"background_color": rx.color("gray", 7)}
                ),
                rx.divider(
                    color_scheme="red",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 5. Status Block
                rx.text("Section 4: Resolution & Totals", font_weight="bold"),

                # 5.1. Resolution
                rx.hstack(
                    rx.text("Resolved?", font_weight="bold", width="25%"),
                    build_toggle(UnplannedState.resolved, "Resolved", "Unresolved", "resolved", UnplannedState.update_resolved, width="25%"),
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 5.2. Resolution Date & Root Cause
                rx.hstack(
                    rx.text("Resolution Date", font_weight="bold", width="50%"),
                    rx.text("Root Cause", font_weight="bold", width="50%"),
                    spacing="0",
                    padding_top="0.5em"
                ),

                rx.hstack(
                    rx.input(
                        type="date",
                        value=UnplannedState.resolution_date,
                        name="completed_at",
                        width="50%",
                        on_change=UnplannedState.update_resolution_date
                    ),
                    rx.select(
                        UnplannedState.root_causes,
                        placeholder="Select a Cause...",
                        value=UnplannedState.root_cause,
                        name="root_cause",
                        width="50%",
                        on_change=UnplannedState.update_root_cause
                    ),
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 5.3. Follow Up?
                rx.hstack(
                    rx.text("Follow Up Required?", font_weight="bold", width="25%"),
                    build_toggle(UnplannedState.follow_up_required, "Required", "Not Required", "follow_up", UnplannedState.update_follow_up, width="25%"),
                    spacing="0",
                    padding_top="0.5em"
                ),

                # 5.4. Aggregate Metrics
                rx.hstack(
                    rx.text("Total Estimated Downtime", font_weight="bold", width="50%"),
                    rx.text("Total Cost ($)", font_weight="bold", width="50%"),
                    spacing="0"
                ),
                rx.hstack(
                    rx.text(UnplannedState.downtime, width="50%"),
                    rx.input(
                        placeholder="Additional Costs ($)",
                        value=UnplannedState.additional_costs,
                        type="number",
                        step="0.01",
                        name="additional_cost",
                        width="25%",
                        on_change=UnplannedState.update_cost
                    ),
                    rx.text(UnplannedState.cost_repr, width="25%")
                ),            
                rx.divider(
                    color_scheme="red",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 6. Form Buttons
                rx.hstack(
                    rx.button(
                        "Submit Unplanned Maintenance",
                        type="submit",
                        variant="surface",
                        color_scheme="blue",
                        width="50%",
                        disabled=~UnplannedState.form_complete,
                        loading=UnplannedState.submitting,
                        _hover={"background_color": rx.cond(
                            UnplannedState.form_complete,
                            rx.color("blue", 7),
                            rx.color("blue", 1)
                        )}
                    ),
                    rx.dialog.close(rx.button(
                        "Cancel",
                        variant="surface",
                        color_scheme="red",
                        type="button",
                        on_click=UnplannedState.toggle,
                        width="100%",
                        _hover={"background_color": rx.color("red", 7)}
                    ), width="100%"),
                    spacing="0"
                ),
                on_submit=UnplannedState.submit
            ),
            max_width="21cm"
        ),
        open=UnplannedState.unplanned_form_open
    )

def requirement_item(label: str, condition: bool) -> rx.Component:
    """Renders a single checklist row that adapts to a condition status"""
    return rx.hstack(
        rx.cond(
            condition,
            rx.icon("check_circle", color="green", size=16),
            rx.icon("circle", color="gray", size=16)
        ), 
        rx.text(
            label,
            color=rx.cond(condition, "green", "gray"),
            size="2"
        ),
        align="center",
        spacing="2"
    )

# def build_input(column: rx.Var, options: rx.Var) -> rx.Component:
def build_input(column: rx.Var, curr: bool, default: any) -> rx.Component:
    """Generate an input for the form given set of parameters"""
    return rx.cond(
        curr,
        rx.match(
            column["type"],
            ("text", rx.input(
                default_value=default,
                name=column["key"],
                width="100%"
            )),
            ("number", rx.input(
                type=column["type"],
                default_value=default,
                name=column["key"],
                step=column["step"],
                width="100%"
            )),
            ("date", rx.input(
                type=column["type"],
                name=column["key"],
                default_value=default
            )),
            rx.input(default_value=default)
        ),
        rx.match(
            column["type"],
            ("text", rx.input(
                placeholder= column["placeholder"],
                name=column["key"],
                width="100%"
            )),
            ("number", rx.input(
                type=column["type"],
                placeholder=column["placeholder"],
                name=column["key"],
                step=column["step"],
                width="100%"
            )),
            ("date", rx.input(
                type=column["type"],
                name=column["key"],
            )),
            rx.input(placeholder=column["placeholder"])
        )
    )

def build_toggle(
        toggled: bool,
        toggle_on_val: str,
        toggle_off_val: str,
        toggle_key: str,
        toggle: Callable[[str], None] = lambda x: None,
        width: str = "100%"
) -> rx.Component:
    """Function that Builds a Text Toggle"""
    return rx.box(
        rx.box(
            # Text inside the Toggle
            rx.text(
                rx.cond(toggled, toggle_on_val, toggle_off_val),
                font_size="10px",
                font_weight="bold",
                color="white",
                # Padding moves text left/right
                # padding_left=rx.cond(toggled, "3px", "24px"),
                # padding_right=rx.cond(toggled, "24px", "3px"),
                transition="all 0.2s ease-in-out"
            ),
            # Knob that toggles
            rx.box(
                width="32px",
                height="16px",
                bg="white",
                border_radius="8px",
                position="absolute",
                top="4px",
                # Slides the knob horizontally based on state
                left=rx.cond(toggled, "80%", "4px"),
                transition="all 0.2s ease-in-out",
                box_shadow="md"
            ),
            width="100%",
            height="24px",
            # Smoothly Changes track colour from gray to green
            bg=rx.cond(toggled, "var(--green-9)", "var(--gray-8)"),
            border_radius="12px",
            position="relative",
            display="flex",
            align_items="center",
            justify_content="center",
            cursor="pointer",
            transition="background-color 0.2s"
        ),
        on_click=toggle(toggle_key),
        width=width
    )
