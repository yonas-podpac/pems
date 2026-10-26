import reflex as rx
from typing import Callable, Optional

def action_bar(
        is_admin: bool,
        title_block: rx.Component,
        login_block: rx.Component,
        admin_block: rx.Component = rx.fragment(),
        filter: bool = False,
        filter_bar: rx.Component = rx.fragment()
) -> rx.Component:
    """Render a Custom Action Bar"""
    return rx.vstack(
        # Top Row
        rx.hstack(
            # Title Block
            title_block,
            rx.spacer(),
            # Function Block
            rx.vstack(
                login_block,
                rx.cond(is_admin, admin_block, rx.fragment()),
                align="end"
            ),
            width="100%",
            padding_bottom="1rem",
            border_bottom="1px solid #e2e8f0",
            margin_bottom="1rem"
        ),
        # Second Row
        rx.cond(filter, filter_bar, rx.fragment()),
        width="100%"
    )

def title_block(title: str, subtitle: str, status: bool, block: rx.Component = rx.fragment()) -> rx.Component:
    """Render a Block with the Title of the Page"""
    return rx.vstack(
        rx.heading(title, size="8"),
        rx.text(subtitle, color_scheme="gray", size="2"),
        rx.cond(status, block, rx.fragment()),
        align_items="start"
    )

def redirect_title_block(
        title: str,
        subtitle: str,
        link: str,
) -> rx.Component:
    """Render a Block for Redirecting to Parent Page"""
    return rx.vstack(
        rx.heading(title, size="5"),
        rx.text(subtitle, color_scheme="gray", size="2"),
        rx.badge(
            rx.icon_button(
                "arrow_left_to_line",
                size="1",
                variant="soft",
                color_scheme="blue",
                on_click=rx.redirect(link)
            ),
            rx.text("Return", size="1", color_scheme="gray")
        ),
        align_items="start"
    )

def login_block(
        logged_in: bool, 
        username: str = "",
        redirect: str = "/",
        login: Optional[Callable] = lambda: None,
        logout: Callable[[str], None] = lambda: None,
) -> rx.Component:
    """Render a Block with login button or user info"""
    logged_in_var = rx.Var.create(logged_in)
    redirect_var = rx.Var.create(redirect)
    return rx.cond(
        logged_in_var,

        # Logged In Condition: Add username
        rx.hstack(
            rx.icon("circle_user_round", color="gray", size=16),
            rx.text(username, size="3", color_scheme="gray"),
            rx.button(
                "Log Out",
                variant="surface",
                color_scheme="sky",
                on_click=logout(redirect_var)
            ),
            align="center"
        ), # TODO: implement login details

        # Otherwise: Add login button
        rx.button("Log In", variant="surface", color_scheme="sky", on_click=login)
    )

def supabase_status_block(status: str, connected: bool) -> rx.Component:
    """Render a Block with Supabase Status"""
    return rx.text(
        f"System Status: ",
        rx.badge(
            status,
            color_scheme=rx.cond(connected, "green", "red")
        )
    )

def admin_control_block(
        can_add: bool = False,
        add_title: str = "",
        add: Callable = lambda: [],
        can_upload: bool = False,
        upload_title: str = "",
        pending: bool = False,
        is_processing: bool = False,
        filename: str = "",
        upload: Callable = lambda: [],
        clear: Callable = lambda: [],
        select: Callable[[list[rx.UploadFile]], None] = lambda _: None
) -> rx.Component:
    """Renders a Customisable Control Block for the Admin"""
    return rx.hstack(
        # Manage Upload Block
        rx.cond(
            can_upload,
            rx.cond(
                pending,
                rx.hstack(
                    rx.text(filename, size="1", color="green"),
                    rx.icon_button(
                        "upload",
                        color_scheme="green",
                        variant="ghost",
                        size="1",
                        on_click=upload
                    ),
                    rx.icon_button(
                        "trash-2",
                        color_scheme="red",
                        variant="ghost",
                        size="1",
                        on_click=clear
                    ),
                    align="center",
                    id="file_uploader",
                    border="2px dashed green",
                    padding="5px",
                    border_radius="8px",
                    width="100%",
                ),
                rx.upload(
                    rx.text(upload_title),
                    align="center",
                    id="file_uploader",
                    border="2px dashed #ccc",
                    padding="5px",
                    border_radius="8px",
                    width="100%",
                    on_drop=select(rx.upload_files(upload_id="file_uploader"))
                )
            ),
            rx.fragment()
        ),
        
        # Manage Add Block
        rx.cond(
            can_add,
            rx.button(
                add_title,
                icon="plus",
                color_scheme="blue",
                on_click=add
            ),
            rx.fragment()
        ),

        # Alignment
        align="center",
        spacing="3"
    )

def orig_admin_control_block(
        pending: bool,
        is_processing: bool,
        filename: str,
        upload: Optional[Callable],
        clear: Optional[Callable],
        select: Optional[Callable],
        add: Optional[Callable]
) -> rx.Component:
    """Render a Block for Admin Control, such as CSV Dump, add entry"""
    return rx.hstack(
        # CSV Upload Field
        rx.cond(
            pending,

            # Condition 1: File ready for upload
            rx.vstack(
                rx.button(
                    "Upload File",
                    variant="surface",
                    color_scheme="green",
                    on_click=upload,
                    loading=is_processing
                ),
                rx.hstack(
                    rx.text(filename, size="1", color="green"),
                    rx.button(
                        rx.icon("trash-2"),
                        color_scheme="red",
                        variant="ghost",
                        size="1",
                        on_click=clear
                    ),
                    align="center"
                ),
                id="csv_uploader",
                border="2px dashed green",
                padding="5px",
                border_radius="8px",
                width="100%",
                align="center"
            ),

            # Condition 2: No File Present
            rx.upload(
                rx.vstack(
                    rx.button("Select File", color_scheme="blue", variant="surface"),
                    rx.text("Drag and drop your file here", size="1", color_scheme="gray"),
                    align="center"
                ),
                id="csv_uploader",
                border="2px dashed #ccc",
                padding="5px",
                border_radius="8px",
                width="100%",
                on_drop=select(rx.upload_files(upload_id="csv_uploader"))
            )
        ),

        # Add Entry Button
        rx.button(
            "Add Entry",
            icon="plus",
            color_scheme="blue",
            on_click=add
        ),
        align="center",
        spacing="3"
    )

def admin_simple_block(
        add: Optional[Callable]
) -> rx.Component:
    """Render a Simplified Block for Admin Control"""
    return rx.hstack(
        # Add Entry Button
        rx.button(
            "Add Entry",
            icon="plus",
            color_scheme="blue",
            on_click=add
        ),
        align="center",
        spacing="3"
    )

def filter_bar(
        filters: dict[str, list[str]],
        params: list[dict[str, str]],
        current: dict[str, str],
        set: Optional[Callable],
        apply: Optional[Callable],
        delete: Optional[Callable]
) -> rx.Component:
    """Render a Bar for Filters"""
    return rx.vstack(
        # Generate each filter select box
        rx.hstack(
            rx.foreach(
                params,
                lambda param: rx.vstack(
                    rx.text(param["label"], size="2", weight="bold"),
                    rx.select(
                        filters[param["key"].to(str)],
                        value=current[param["key"]],
                        name=param["key"],
                        on_change=lambda val, k=param["key"]: set(k, val),
                        width="120px"
                    )
                )
            ),
            justify="start",
            width="100%"
        ),
        rx.hstack(
            # Generate badges for each filter
            rx.foreach(
                current,
                lambda filt: rx.badge(
                    rx.text(filt[1], size="1", color_scheme="gray"),
                    rx.icon_button(
                        "trash-2",
                        size="1",
                        variant="soft",
                        color_scheme="red",
                        on_click=delete(filt[0])
                    )
                )
            ),

            # Generate Apply Filter button
            rx.button(
                "Apply Filter",
                type="submit",
                color_scheme="blue",
                on_click=apply
            ),
            justify="end",
            width="100%"
        ),
        width="100%"
    )
