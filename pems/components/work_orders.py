import reflex as rx
from pems.components.form import build_toggle
from pems.states.preventative_state import PreventativeState
from pems.states.service_state import ServiceState
from pems.states.unplanned_state import UnplannedState

def preventative_work_order_form() -> rx.Component:
    """Renders a Digital Preventative Maintenance Work Order"""
    return rx.dialog.root(
        rx.dialog.content(
            # 1. Title & IDs Associated with Work Order
            rx.dialog.title(PreventativeState.title),
            rx.hstack(
                rx.text("Work Order ID", font_weight="bold", width="33.3%"),
                rx.text("Maintenance ID", font_weight="bold", width="33.3%"),
                rx.text("Procedure ID", font_weight="bold", width="33.4%"),
                spacing="0"
            ),
            rx.hstack(
                rx.badge(
                    PreventativeState.work_order_id,
                    color_scheme="gray",
                    border_radius="md",
                    font_size="1",
                    align_items="center",
                    justify_content="center",
                    width="33.3%"
                ),
                rx.badge(
                    PreventativeState.preventative_id,
                    color_scheme="indigo",
                    border_radius="md",
                    font_size="1",
                    align_items="center",
                    justify_content="center",
                    width="33.3%"
                ),
                rx.badge(
                    PreventativeState.procedure_id,
                    color_scheme="blue",
                    border_radius="md",
                    font_size="1",
                    align_items="center",
                    justify_content="center",
                    width="33.4%"
                ),
                spacing="0"
            ),
            rx.divider(
                color_scheme="blue",
                margin_top="4px",
                margin_bottom="16px",
                style={"height": "3px"}
            ),

            rx.form(
            # 2. Employee Working on WO & Date of Work
                rx.hstack(
                    rx.text("Name:", font_weight="bold", width="15%"),
                    rx.cond(
                        PreventativeState.editable,
                        rx.input(
                            placeholder="Enter Employee's Name",
                            value=PreventativeState.name,
                            width="35%",
                            on_change=PreventativeState.update_name
                        ),
                        rx.text(PreventativeState.name, width="35%")
                    ),
                    rx.text("Date:", font_weight="bold", width="15%"),
                    rx.cond(
                        PreventativeState.editable,
                        rx.input(
                            type="date",
                            value=PreventativeState.date_repr,
                            width="35%",
                            on_change=PreventativeState.update_date
                        )
                    )
                ),
                rx.divider(
                    color_scheme="blue",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 3. Preventative Maintenance Tasks
                rx.table.root(
                    # 3.1. Location Row
                    rx.table.row(
                        rx.table.row_header_cell(PreventativeState.location, color="white", col_span=4),
                        background_color="navy"
                    ),

                    # 3.2. Asset Rows
                    rx.foreach(
                        PreventativeState.wo_assets,
                        lambda asset: rx.fragment(
                            # 3.2.1. Asset Row
                            rx.table.row(
                                rx.table.row_header_cell(asset, col_span=4),
                                background_color=rx.color("blue", 7)
                            ),

                            # 3.2.2. Task Header Row
                            rx.table.row(
                                rx.table.row_header_cell("Task ID", width="10%"),
                                rx.table.row_header_cell("Job", width="30%"),
                                rx.table.row_header_cell("Complete", width="20%"),
                                rx.table.row_header_cell("Notes", width="40%"),
                                background_color="gray"
                            ),

                            # 3.2.3. Task Rows
                            rx.foreach(
                                PreventativeState.tasks[asset],
                                lambda task: rx.table.row(
                                    rx.table.cell(task["id"], width="10%"),
                                    rx.table.cell(task["job"], width="30%"),
                                    rx.table.cell(
                                        rx.cond(
                                            PreventativeState.editable,
                                            build_toggle(
                                                PreventativeState.task_completed[task["id"]], 
                                                "Yes", 
                                                "No", 
                                                task["id"] + "_complete", 
                                                lambda val: PreventativeState.update_task_complete(task["id"], val),
                                                width="100%"
                                            ),
                                            rx.cond(
                                                PreventativeState.maintenance_complete,
                                                rx.cond(
                                                    PreventativeState.task_completed[task["id"]],
                                                    rx.fragment(
                                                        rx.text("Y / "),
                                                        rx.text("N", text_decoration="line-through"),
                                                        rx.text(" / "),
                                                        rx.text("N/A", text_decoration="line-through")
                                                    ),
                                                    rx.fragment(
                                                        rx.text("Y", text_decoration="line-through"),
                                                        rx.text(" / N / "),
                                                        rx.text("N/A", text_decoration="line-through")
                                                    )
                                                ),
                                                rx.text("Y / N / N/A")
                                            )
                                        ), 
                                        width="20%"
                                    ),
                                    rx.table.cell(
                                        rx.cond(
                                            PreventativeState.editable,
                                            rx.text_area(
                                                value=PreventativeState.task_notes[task["id"]],
                                                name=task["id"] + "_note",
                                                width="100%",
                                                on_change=lambda val: PreventativeState.update_task_notes(task["id"], val)
                                            ),
                                            rx.text(PreventativeState.task_notes[task["id"]])
                                        ), 
                                        width="40%"
                                    )
                                )
                            )
                        )
                    )
                ),
                rx.divider(
                    color_scheme="blue",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 4. Additional Notes
                rx.text("Notes:", font_weight="bold"),
                rx.cond(
                    PreventativeState.editable,
                    rx.text_area(
                        placeholder="Enter notes for the procedure here",
                        value=PreventativeState.additional_notes,
                        width="100%",
                        on_change=PreventativeState.update_additional_notes
                    ),
                    rx.text(PreventativeState.additional_notes, width="100%")
                ),
                rx.divider(
                    color_scheme="blue",
                    margin_top="4px",
                    margin_bottom="16px",
                    style={"height": "3px"}
                ),

                # 5. Form Buttons
                rx.hstack(
                    rx.cond(
                        PreventativeState.editable,
                        rx.button(
                            "Submit Work Order",
                            type="submit",
                            variant="surface",
                            color_scheme="blue",
                            width="33%",
                            disabled=~PreventativeState.work_order_complete,
                            loading=PreventativeState.submitting,
                            _hover={"background_color": rx.cond(
                                PreventativeState.form_complete,
                                rx.color("blue", 7),
                                rx.color("blue", 1)
                            )}
                        ),
                        rx.button(
                            "Edit Work Order",
                            variant="surface",
                            color_scheme="green",
                            type="button",
                            on_click=PreventativeState.edit,
                            width="33%",
                            _hover={"background_color": rx.color("green", 7)}
                        )
                    ),
                    rx.button(
                        "Print",
                        variant="surface",
                        color_scheme="gray",
                        type="button",
                        on_click=PreventativeState.print_work_order,
                        width="33%",
                        _hover={"background_color": rx.color("gray", 7)}
                    ),
                    rx.dialog.close(rx.button(
                        "Cancel",
                        variant="surface",
                        color_scheme="red",
                        type="button",
                        on_click=PreventativeState.cancel,
                        width="33%",
                        _hover={"background_color": rx.color("red", 7)}
                    ), width="34%"),
                    spacing="0"
                ),
                on_submit=PreventativeState.work_order_submit
            ),
            max_width="21cm"
        ),
        open=PreventativeState.work_order_form_open
    )

def preventative_work_order_print() -> rx.Component:
    """Renders a Printable Preventative Maintenance Work Order"""
    return rx.vstack(
        # Name & Date of Completion
        rx.cond(
            PreventativeState.work_order_complete,

            # Employee Assigned WO & Date of Completion
            rx.hstack(
                rx.text("Name:", font_weight="bold", width="25%"),
                rx.text(PreventativeState.name, width="25%"),
                rx.text("Date:", font_weight="bold", width="25%"),
                rx.text(PreventativeState.date, width="25%"),
                width="100%",
                spacing="0"
            ),

            # Blank Line for Printed Incomplete Form
            rx.hstack(
                rx.hstack(
                    rx.text("Name:", font_weight="bold"),
                    rx.box(border_bottom="1px solid black", width="250px"),
                    align="baseline",
                    spacing="2"
                ),
                rx.hstack(
                    rx.text("Date:", font_weight="bold"),
                    rx.box(border_bottom="1px solid black", width="250px"),
                    align="baseline",
                    spacing="2"
                ),
                spacing="6",
                margin_bottom="4"
            )
        ),

        # Maintenance Tasks to be Completed
        rx.table.root(
            rx.table.body(
                # Label the Production Room
                rx.table.row(
                    rx.table.cell(
                        rx.text(PreventativeState.location, font_weight="bold", color="white"),
                        background_color=rx.color("blue", 9),
                        border="1px solid gray",
                        col_span=4
                    ),
                    width="100%"
                ),

                # Iterate Over Assets
                rx.foreach(
                    PreventativeState.wo_assets,
                    lambda asset: rx.fragment(
                        # Label the Asset
                        rx.table.row(
                            rx.table.cell(
                                rx.text(asset, font_weight="bold"),
                                background_color="blue",
                                border="1px solid gray",
                                col_span=4
                            ),
                            width="100%"
                        ),

                        # Task Headers
                        rx.table.row(
                            rx.table.cell(
                                rx.text("Task ID", font_weight="bold"),
                                background_color="gray",
                                border="1px solid gray",
                                width="20%",
                            ),
                            rx.table.cell(
                                rx.text("Job", font_weight="bold"),
                                background_color="gray",
                                border="1px solid gray",
                                width="30%",
                            ),
                            rx.table.cell(
                                rx.text("Complete", font_weight="bold"),
                                background_color="gray",
                                border="1px solid gray",
                                width="20%",
                            ),
                            rx.table.cell(
                                rx.text("Notes", font_weight="bold"),
                                background_color="gray",
                                border="1px solid gray",
                                width="30%",
                            ),
                            width="100%"
                        ),

                        # Iterate over Maintenance Tasks
                        rx.foreach(
                            PreventativeState.tasks[asset],
                            lambda task: rx.table.row(
                                # Task ID Cell
                                rx.table.cell(
                                    rx.text(task["id"]),
                                    border="1px solid gray",
                                    width="20%"
                                ),

                                # Job Cell
                                rx.table.cell(
                                    rx.text(task["job"]),
                                    border="1px solid gray",
                                    width="30%"
                                ),

                                # Task Complete
                                rx.table.cell(
                                    rx.cond(
                                        PreventativeState.work_order_complete,
                                        rx.hstack(
                                            rx.text("Y / "),
                                            rx.text("N", text_decoration="line-through"),
                                            rx.text(" / "),
                                            rx.text("N/A", text_decoration="line-through"),
                                            align="center"
                                        ),
                                        rx.hstack(
                                            rx.text("Y", text_decoration="line-through"),
                                            rx.text(" / N / "),
                                            rx.text("N/A", text_decoration="line-through"),
                                            align="center"
                                        )
                                    ),
                                    border="1px solid gray",
                                    width="20%"
                                ),

                                # Parts Used  / Notes Cell
                                rx.table.cell(
                                    rx.text(task["notes"]),
                                    border="1px solid gray",
                                    width="30%"
                                ),

                                width="100%"
                            ),
                        ),
                    )
                ),

                # Label Final Notes
                rx.table.row(
                    rx.table.cell(
                        rx.text("Notes:", font_weight="bold"),
                        background_color="gray",
                        border="1px solid gray",
                        col_span=4
                    ),
                ),

                # Notes Row
                rx.table.row(
                    rx.table.cell(
                        # rx.text(PreventativeState.notes[field]),
                        border="1px solid gray",
                        col_span=4
                    )
                ),
            ),
            width="100%"
        ),

        width="100%"
    )
