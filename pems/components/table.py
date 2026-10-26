import reflex as rx
from typing import Optional, Callable
from PIL import Image

def generic_table(
        columns: list[dict], 
        data: list[dict], 
        can_edit: bool = False,
        can_link: bool = False,
        on_edit: Callable[[int], None] = lambda x: None, 
        on_delete: Callable[[int], None] = lambda x: None,
        on_link: Callable[[int], None] = lambda x: None
) -> rx.Component:
    """Generate a dynamic, styled management table based on provided column metadata"""
    return rx.table.root(
        # 1. Table Header Loop
        rx.table.header(
            rx.table.row(
                rx.foreach(
                    columns,
                    lambda col: rx.table.column_header_cell(col["label"])
                ),
                rx.cond(
                    can_edit | can_link,
                    rx.table.column_header_cell("Actions", text_align="right"),
                    rx.fragment()
                )
            )
        ),
        
        # 2. Table Body Nested Loop
        rx.table.body(
            rx.foreach(
                data,
                lambda row_data, index: rx.table.row(
                    rx.foreach(
                        columns,
                        lambda col: rx.table.cell(row_data[col["key"].to(str)])
                    ),
                    rx.cond(
                        can_edit | can_link,
                        rx.table.cell(
                            rx.hstack(
                                rx.cond(
                                    can_edit,
                                    rx.hstack(
                                        rx.icon_button(
                                            "pencil", 
                                            size="1", 
                                            variant="soft", 
                                            color_scheme="indigo",
                                            on_click=on_edit(index)
                                        ),
                                        rx.icon_button(
                                            "trash-2", 
                                            size="1", 
                                            variant="soft", 
                                            color_scheme="red",
                                            on_click=on_delete(index)
                                        )
                                    ),
                                    rx.fragment()
                                ),
                                rx.cond(
                                    can_link,
                                    rx.icon_button(
                                        "book_open_text", 
                                        size="1", 
                                        variant="soft", 
                                        color_scheme="green",
                                        on_click=on_link(index)
                                    )
                                ),
                                justify="end",
                                spacing="2"
                            )
                        ),
                        rx.fragment()
                    )
                )
            )
        ),
        width="100%",
        variant="surface"
    )

def generic_linked_table(columns: list[dict], data: list[dict], link_data) -> rx.Component:
    """"""
    return rx.table.root(
        # 1. Table Header Loop
        rx.table.header(
            rx.table.row(
                rx.foreach(
                    columns,
                    lambda col: rx.table.column_header_cell(col["label"])
                ),
                rx.table.column_header_cell("Actions", text_align="right")
            )
        ),
        
        # 2. Table Body Nested Loop
        rx.table.body(
            rx.foreach(
                data,
                lambda row_data, index: rx.table.row(
                    # FIX: Force the key to evaluate as a client-side string lookup
                    rx.foreach(
                        columns,
                        lambda col: rx.table.cell(row_data[col["key"].to(str)])
                    ),
                    # Action Buttons Column
                    rx.table.cell(
                        rx.hstack(
                            rx.icon_button(
                                "book_open_text", 
                                size="1", 
                                variant="soft", 
                                color_scheme="green",
                                on_click=link_data(index)
                            ),
                            justify="center"
                        )
                    )
                )
            )
        ),
        width="100%",
        variant="surface"
    )

def analysis_table(columns: list[dict], data: list[dict], img: Image.Image, img_label: str, display_plot, display_full_plot) -> rx.Component:
    return rx.hstack(
        # Analysis Table
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.foreach(
                        columns,
                        lambda col: rx.table.column_header_cell(col["label"])
                    ),
                    rx.table.column_header_cell("Capsule Plot", text_align="right")
                )
            ),
            rx.table.body(
                rx.foreach(
                    data,
                    lambda row_data, index: rx.table.row(
                        rx.foreach(
                            columns,
                            lambda col: rx.table.cell(row_data[col["key"].to(str)])
                        ), 
                        rx.table.cell(
                            rx.icon_button(
                                "image",
                                size="1",
                                variant="soft",
                                color_scheme="green",
                                on_click=display_plot(index)
                            ),
                            align="center"
                        )
                    )
                )
            ),
            width="100%",
            variant="surface"
        ),
        # Display Table
        rx.table.root(
            rx.table.body(
                rx.table.row(
                    rx.table.cell(
                        rx.image(
                            src=img,
                            width="800px",
                            height="auto"
                        ),
                        align="center"
                    )
                ),
                rx.table.row(
                    rx.table.cell(
                        rx.text(img_label, size="2"),
                        align="center"
                    )
                ),
                rx.table.row(
                    rx.table.cell(
                        rx.badge(
                            rx.text("Full Plot", size="2", color_scheme="gray"),
                            rx.icon_button(
                                "image_upscale",
                                size="2",
                                variant="soft",
                                color_scheme="blue",
                                on_click=display_full_plot
                            )
                        ),
                        align="center"
                    )
                )
            )
        )
    )