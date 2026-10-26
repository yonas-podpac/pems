import reflex as rx
import reflex_enterprise as rxe
from pems.components.template import PEMSTemplate
from pems.components.actions import *
from pems.components.dasboard import dashboard, new_entry_form
from pems.components.table import generic_table, generic_linked_table, analysis_table
from pems.components.form import *
from pems.components.calendar import calendar
from pems.components.work_orders import *
from pems.states.auth_state import AuthState
from pems.states.calendar_state import CalendarState
from pems.states.dashboard_state import DashboardState
from pems.states.asset_state import AssetState
from pems.states.extraction_state import ExtractionState
from pems.states.maintenance_state import MaintenanceState
from pems.states.oee_form_state import OEEFormState
from pems.states.preventative_state import PreventativeState
from pems.states.service_state import ServiceState
from pems.states.spare_state import SpareState
from pems.states.unplanned_state import UnplannedState

#  --- Define Page Views Using Template ---
def home_view() -> rx.Component:
    """Function for Creating the Home Page for PEMS"""
    # Render Supabase Status Block
    ssBlock = supabase_status_block(
        status=DashboardState.connection_check,
        connected=DashboardState.connected
    )

    # Render Title Block
    tBlock = title_block(
        title="PEMS Dashboard",
        subtitle="Computerised Maintenance Management System for Podpac",
        status=True,
        block=ssBlock
    )

    # Render Login Block
    lBlock = login_block(
        logged_in=AuthState.logged_in,
        username=AuthState.get_user_name,
        redirect="/",
        login=AuthState.toggle_login_form,
        logout=AuthState.logout
    )

    # Render Admin Block
    aBlock = admin_control_block(
        can_add=True,
        add_title="New Entry",
        add=OEEFormState.open
    ) # TODO: what does the home admin block require?

    return PEMSTemplate.layout(
        "Home",

        # 1. Action Bar
        action_bar(
            is_admin=AuthState.is_admin,
            title_block=tBlock,
            login_block=lBlock,
            admin_block=aBlock
        ),

        # 2. Dashboard Body
        dashboard(), # TODO: Build dashboard body

        # 3. Login Form
        login_form("/"),

        # 4. Sign Up Form
        signup_form(),

        # 5. New Entry Form
        new_entry_form(),

        load=DashboardState.load
    )

def reset_password_view() -> rx.Component:
    """Function for Reseting the Password Page"""
    return rx.form(
        rx.vstack(
            rx.cond(
                AuthState.error_message != "",
                rx.callout(
                    AuthState.error_message,
                    icon="triangle_alert",
                    color_scheme="amber",
                    role="alert",
                    width="100%"
                )
            ),

            rx.image(
                src="/pems-logo.png",
                width="200px",
                height="auto",
                border_radius="4px"
            ),

            rx.heading("Reset Password"),

            rx.spacer(),

            rx.vstack(
                rx.text("New Password", width="120px", font_weight="bold"),
                rx.input(
                    type="password",
                    placeholder="Enter a valid Password",
                    name="password",
                    width="500px",
                    on_change=AuthState.update_password
                ),
                rx.text(
                    "Confirm Password",
                    width="240px",
                    font_weight="bold"
                ),
                rx.input(
                    type="password",
                    placeholder="Re-enter your password",
                    name="confirm_password",
                    width="500px",
                    on_change=AuthState.update_confirm_password
                ),
                align="start"
            ),
            rx.divider(margin_y="2"),

            # 3. Email & Password Prompts
            rx.vstack(
                requirement_item("At least 11 characters long", AuthState.has_min_length),
                requirement_item("Includes a lowercase letter", AuthState.has_lowercase),
                requirement_item("Includes an uppercase letter", AuthState.has_uppercase),
                requirement_item("Includes a number", AuthState.has_number),
                requirement_item("Includes a special character (!@#$...)", AuthState.has_special),
                requirement_item("Passwords match", AuthState.passwords_match),
                align_items="start",
                spacing="1"
            ),

            rx.hstack(
                rx.button(
                    "Cancel",
                    variant="soft",
                    color_scheme="red",
                    type="button",
                    on_click=rx.redirect("/")
                ),

                # 3.b. Sign Up Button
                rx.button(
                    "Reset Password",
                    type="submit",
                    color_scheme="blue",
                ),
                justify="end",
                margin_top="1.5rem"
            ),
            align="center"
        ),
        align="center",
        spacing="3",
        on_submit=AuthState.handle_reset_password
    )

def assets_views() -> rx.Component:
    """Function for Creating Asset Registrar Page"""
    # Initialise Lists
    tBlock = title_block(
        title="Asset Registrar",
        subtitle="Registry of all physical facility assets, HVAC, and machinery",
        status=False
    )

    lBlock = login_block(
        logged_in=AuthState.logged_in,
        username=AuthState.get_user_name,
        redirect="/assets",
        login=AuthState.toggle_login_form,
        logout=AuthState.logout
    )

    aBlock = admin_control_block(
        can_add=True,
        add_title="Add Asset",
        add=AssetState.handle_add_click
    )

    fBar = filter_bar(
        filters=AssetState.filter_options,
        params=AssetState.filter_params,
        current=AssetState.current_filters,
        set=AssetState.set_filter_value,
        apply=AssetState.apply_filter,
        delete=AssetState.delete_filter
    )
    return PEMSTemplate.layout(
        "Asset Registrar",

        # 1. Action Header Controls
        action_bar(
            is_admin=AuthState.is_admin,
            title_block=tBlock,
            login_block=lBlock,
            admin_block=aBlock,
            filter=True,
            filter_bar=fBar
        ),

        # 2. Main Generic Data Display Matrix
        generic_table(
            columns=AssetState.columns,
            data=AssetState.entries,
            can_edit=AuthState.is_admin,
            can_link=True,
            on_edit=AssetState.handle_edit_click,
            on_delete=AssetState.handle_delete_click,
            on_link=AssetState.link_data
        ),

        # 3. Login Form
        login_form("/assets"),

        # 4. Sign Up Form
        signup_form(),

        # 5. Build a New Entry Form
        generic_form(
            title="Asset Record Maintenance Setup",
            columns=AssetState.columns,
            options=AssetState.form_options,
            open=AssetState.is_new_entry_form_open,
            toggle=AssetState.toggle_new_entry_form,
            submit=AssetState.submit_new_entry_form,
            form_toggle_on_vals=AssetState.form_toggle_on_vals,
            form_toggle_off_vals=AssetState.form_toggle_off_vals,
            form_toggle_vals=AssetState.form_toggle_vals,
            form_toggle_bools=AssetState.form_toggles,
            handle_form_toggle=AssetState.handle_toggle
        ),

        # 6. Build a Current Entry Form
        generic_form(
            title="Asset Record Edit", # TODO: update with row value?
            columns=AssetState.columns,
            options=AssetState.form_options, # TODO: update with current entry options?
            open=AssetState.is_curr_entry_form_open,
            toggle=AssetState.toggle_curr_entry_form,
            submit=AssetState.submit_curr_entry_form,
            form_toggle_on_vals=AssetState.form_toggle_on_vals,
            form_toggle_off_vals=AssetState.form_toggle_off_vals,
            form_toggle_vals=AssetState.form_toggle_vals,
            form_toggle_bools=AssetState.form_toggles,
            handle_form_toggle=AssetState.handle_toggle,
            current=True,
            defaults=AssetState.default_options
        ),

        # 7. Delete Entry Window
        delete_entry_window(
            title=AssetState.asset_title,
            cancel=AssetState.cancel_delete_click,
            confirm=AssetState.confirm_delete_click,
            is_window_open=AssetState.is_delete_entry_window_open
        ),

        load=AssetState.load
    )

def stations_view() -> rx.Component:
    """Function for Creating Machine Stations Page"""
    # Initialise Lists
    tBlock = redirect_title_block(
        title=AssetState.asset_title,
        subtitle=AssetState.asset_subtitle,
        link="/assets"
    )

    lBlock = login_block(
        logged_in=AuthState.logged_in,
        username=AuthState.get_user_name,
        redirect="/stations",
        login=AuthState.toggle_login_form,
        logout=AuthState.logout
    )

    aBlock = admin_control_block(
        can_add=True,
        add_title="Add Station",
        add=AssetState.handle_add_click
    )

    fBar = filter_bar(
        filters=AssetState.filter_options,
        params=AssetState.filter_params,
        current=AssetState.current_filters,
        set=AssetState.set_filter_value,
        apply=AssetState.apply_filter,
        delete=AssetState.delete_filter
    )
    return PEMSTemplate.layout(
        "Machine Stations",

        # 1. Action Header Controls
        action_bar(
            is_admin=AuthState.is_admin,
            title_block=tBlock,
            login_block=lBlock,
            admin_block=aBlock,
            filter=True,
            filter_bar=fBar
        ),

        # 2. Table displaying stations for selected Asset
        generic_table(
            columns=AssetState.asset_columns,
            data=AssetState.asset_entries,
            can_edit=AuthState.is_admin,
            on_edit=AssetState.handle_station_edit,
            on_delete=AssetState.handle_station_delete
        ),
        load=AssetState.load # TODO: check if this is acceptable
    )

def parts_view() -> rx.Component:
    return PEMSTemplate.layout(
        "Spare Parts",
        rx.heading("Spare Parts", size="8"),
        rx.text("Inventory Control, stock levels, and part-to-machine mapping"),
        load=SpareState.load
    )

def schedule_view() -> rx.Component:
    """Function for Creating Maintenance Schedule Page"""
    # Initialise Action Bar Components
    tBlock = title_block(
        title="Maintenance Schedule",
        subtitle="Calendar View for Preventative and Recurring Maintenance Schedules",
        status=False
    )

    lBlock = login_block(
        logged_in=AuthState.logged_in,
        username=AuthState.get_user_name,
        redirect="/schedule",
        login=AuthState.toggle_login_form,
        logout=AuthState.logout
    )

    aBlock = admin_control_block(
        can_add=True,
        add_title="Add Maintenance Procedure",
        add=PreventativeState.new_procedure
    )

    return PEMSTemplate.layout(
        "Maintenance Schedule",
        # 1. Action Bar
        action_bar(
            is_admin=AuthState.is_admin,
            title_block=tBlock,
            login_block=lBlock,
            admin_block=aBlock,
            filter=False
        ),

        # 2. Calendar View
        calendar(),
        day_jobs_window(),

        # 3. Login Forms
        login_form("/schedule"),
        signup_form(),

        # 5. Preventative Maintenance Forms
        new_maintenance_procedure(),
        preventative_work_order_form(),

        # 6. Service Maintenance Forms
        service_form(),

        # 7. Unplanned Maintenance Forms
        unplanned_maintenance_form()
    )

def preview_view() -> rx.Component:
    """Function for Creating the Print Preview Page"""
    return PEMSTemplate.preview(
        title=rx.cond(
            PreventativeState.print_preview,
            PreventativeState.title,
            rx.cond(
                ServiceState.print_preview,
                ServiceState.title,
                rx.cond(
                    UnplannedState.print_preview,
                    UnplannedState.title,
                    "Work Order Title"
                )
            )
        ),
        border_colour=rx.cond(
            PreventativeState.print_preview,
            "blue",
            rx.cond(
                ServiceState.print_preview,
                "green",
                rx.cond(
                    UnplannedState.print_preview,
                    "red",
                    "gray"
                )
            )
        ),
        maintenance_prefix=rx.cond(
            PreventativeState.print_preview,
            "PM ID",
            rx.cond(
                ServiceState.print_preview,
                "SM ID",
                rx.cond(
                    UnplannedState.print_preview,
                    "UM ID",
                    "ID"
                )
            )
        ),
        maintenance_id=rx.cond(
            PreventativeState.print_preview,
            PreventativeState.maintenance_id,
            rx.cond(
                ServiceState.print_preview,
                ServiceState.maintenance_id,
                rx.cond(
                    UnplannedState.print_preview,
                    UnplannedState.maintenance_id,
                    "M-103"
                )
            )
        ),
        content=rx.cond(
            PreventativeState.print_preview,
            preventative_work_order_print(),
            rx.cond(
                ServiceState.print_preview,
                rx.fragment(),
                rx.cond(
                    UnplannedState.print_preview,
                    rx.fragment(),
                    rx.fragment()
                )
            )
        )
    )

def extraction_view() -> rx.Component:
    """Function for Creating the Extraction Analysis History Page"""
    # Initialise Blocks
    tBlock = title_block(
        title="Capsule Extraction Analysis",
        subtitle="Tool for analysing the performance of capsule extractions as recorded by the Testo 549i",
        status=False
    )

    lBlock = login_block(
        logged_in=AuthState.logged_in,
        username=AuthState.get_user_name,
        redirect="/extractions",
        login=AuthState.toggle_login_form,
        logout=AuthState.logout
    )

    aBlock = admin_control_block(
        can_add=True,
        add_title="Add Extraction Data",
        add=ExtractionState.open_extraction_form
    )

    fBar = filter_bar(
        filters=ExtractionState.filter_options,
        params=ExtractionState.filter_params,
        current=ExtractionState.current_filters,
        set=ExtractionState.set_filter_value,
        apply=ExtractionState.apply_filter,
        delete=ExtractionState.delete_filter
    )
    return PEMSTemplate.layout(
        "Extraction Analysis",

        # 1. Action Header Controls
        action_bar(
            is_admin=AuthState.is_admin,
            title_block=tBlock,
            login_block=lBlock,
            admin_block=aBlock,
            filter=True,
            filter_bar=fBar
        ),

        # 2. Analysis Summary Table
        generic_table(
            columns=ExtractionState.columns,
            data=ExtractionState.entries,
            can_edit=False,
            can_link=True,
            on_link=ExtractionState.link_data
        ),

        # 3. Login Forms
        login_form("/extractions"),
        signup_form(),
        
        # 5. Extraction Analysis Form
        extraction_analysis_form()
    )

def analysis_view() -> rx.Component:
    """Function for Creating the Analysis Page for a Trial Group"""
    # Initialise Blocks
    tBlock = title_block(
        title=ExtractionState.analysis_title,
        subtitle="Capsule Analysis Data",
        status= False
    )

    lBlock = login_block(
        logged_in=AuthState.logged_in,
        username=AuthState.get_user_name,
        redirect="/extractions",
        login=AuthState.toggle_login_form,
        logout=AuthState.logout
    )

    return PEMSTemplate.layout(
        "Analysis Group",

        # 1. Create return bar
        action_bar(
            is_admin=AuthState.is_admin,
            title_block=tBlock,
            login_block=lBlock
        ),

        # 2. Analysis Table
        analysis_table(
            columns=ExtractionState.analysis_columns,
            data=ExtractionState.analysis_entries,
            img=ExtractionState.img,
            img_label=ExtractionState.img_label,
            display_plot=ExtractionState.display_plot,
            display_full_plot=ExtractionState.display_full_plot
        ),
        load=ExtractionState.load # TODO: is this acceptable?
    )

# --- Initialise and Route the Application
app = rxe.App()
app.add_page(home_view, route="/", on_load=[AuthState.load, DashboardState.load, OEEFormState.load])
app.add_page(reset_password_view, route="/reset-password")
app.add_page(assets_views, route="/assets", on_load=[AuthState.load, AssetState.load])
app.add_page(stations_view, route="/stations")
app.add_page(parts_view, route="/parts")
app.add_page(schedule_view, route="/schedule", on_load=[AuthState.load, CalendarState.load, MaintenanceState.load, PreventativeState.load, ServiceState.load, UnplannedState.load])
app.add_page(extraction_view, route="/extractions", on_load=[AuthState.load, ExtractionState.load])
app.add_page(analysis_view, route="/analysis")
app.add_page(preview_view, route="/preview")
