import reflex as rx
from pems.components.sidebar import sidebar
from typing import Callable, Optional

PRINT_STYLES = """
html, body, #root {
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box;
}

@media print {
    @page {
        size: A4 portrait;
        margin: 15mm;
        
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 9pt;
            font-family: sans-serif;
            color: #555;
        }
    }

    html, body, #root, div {
        margin: 0 !important;
        padding: 0 !important;
        background: white !important;
        height: auto !important;
        min-height: 0 !important;
    }

    .no-print {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: fixed !important;
        top: -9999px !important;
    }

    .print-wrapper {
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        display: block !important;
    }

    .print-container {
        width: 100% !important;
        max-width: none !important;
        min-height: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        display: block !important;
    }

    /* Force table sections to repeat on each printed page */
    thead {
        display: table-header-group;
    }
    
    tfoot {
        display: table-footer-group;
    }

    tr, .print-block {
        page-break-inside: avoid;
    }
}
"""

ORIG_PRINT_STYLES = """
html, body, #root {
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box;
}

@media print {
    /* Reset page geometry and margins */
    @page {
        size: A4 portrait;
        margin: 15mm 15mm 15mm 15mm;
        
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 9pt;
            font-family: sans-serif;
            color: #555;
        }
    }

    /* Force all parent containers to zero out offsets */
    html, body, #root, div {
        margin: 0 !important;
        padding: 0 !important;
        background: white !important;
        height: auto !important;
        min-height: 0 !important;
    }

    /* Completely detach non-printable elements from document flow */
    .no-print {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: fixed !important;
        top: -9999px !important;
    }

    /* Reset wrapper padding */
    .print-wrapper {
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        display: block !important;
    }

    /* Standardize printable document container for page flow */
    .print-container {
        width: 100% !important;
        max-width: none !important;
        min-height: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        display: block !important;
    }

    /* Manage page breaks inside main body */
    .print-content {
        page-break-inside: auto;
    }
}
"""

class PEMSTemplate:
    """A reusable layout factory for PEMS pages"""

    @staticmethod
    def layout(
        page_title: str, 
        *content_nodes: rx.Component,
        load: Optional[Callable] = None
    ) -> rx.Component:
        """Wraps any page content with the standard system sidebar and layout bounds."""
        return rx.hstack(
            sidebar(page_title),
            rx.vstack(
                *content_nodes,
                padding="2em",
                width="100%",
                margin_left="260px",
            ),
            align="start",
            width="100%",
            on_mount=load
        )

    @staticmethod
    def preview(
        title: str,
        border_colour: str,
        maintenance_prefix: str, 
        maintenance_id: str,
        content: rx.Component
    ) -> rx.Component:
        return rx.box(
        rx.html(f"<style>{PRINT_STYLES}</style>"),

        # --- ACTION BAR (Screen Only) ---
        rx.hstack(
            rx.heading("Print Preview", size="3", color="gray"),
            rx.hstack(
                rx.link(rx.button("Back"), href="/schedule"),
                rx.button(
                    "Print / Export PDF", 
                    on_click=rx.call_script("window.print()"),
                    color_scheme="blue",
                    size="2"
                )
            ),
            class_name="no-print",
            width="100%",
            justify="between",
            align="center",
            padding_x="8",
            padding_y="4",
            bg="gray.100",
            border_bottom="1px solid #e2e8f0",
        ),

        # --- A4 MULTI-PAGE CONTAINER ---
        rx.center(
            rx.box(
                rx.el.table(
                    # Header: Repeats automatically on top of every printed sheet
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                rx.hstack(
                                    rx.image(
                                        src="/pems-logo.png",
                                        alt="Company Logo",
                                        height="40px",
                                        object_fit="contain",
                                    ),
                                    rx.heading(title, size="6", weight="bold"),
                                    width="100%",
                                    justify="between",
                                    align="center",
                                    border_bottom=f"4px solid {border_colour}",
                                    padding_bottom="3",
                                    margin_bottom="4",
                                ),
                                style={"font-weight": "normal", "text-align": "left"}
                            )
                        )
                    ),

                    # Footer: Repeats automatically at the bottom of every printed sheet
                    rx.el.tfoot(
                        rx.el.tr(
                            rx.el.td(
                                rx.hstack(
                                    rx.text(f"{maintenance_prefix}: {maintenance_id}", size="1", color="gray"),
                                    width="100%",
                                    justify="between",
                                    border_top=f"4px solid {border_colour}",
                                    padding_top="2",
                                    margin_top="4",
                                )
                            )
                        )
                    ),

                    # Body: Dynamically flows and splits across page boundaries
                    rx.el.tbody(
                        rx.el.tr(
                            rx.el.td(
                                rx.box(
                                    content,
                                    width="100%",
                                )
                            )
                        )
                    ),
                    style={"width": "100%", "border-collapse": "collapse"}
                ),
                class_name="print-container",
                width="210mm",
                min_width="210mm",
                min_height="297mm",
                padding="15mm",
                bg="white",
                box_shadow="0 4px 10px rgba(0, 0, 0, 0.15)",
                box_sizing="border-box",
            ),
            width="100%",
            padding_y="8",
            class_name="print-wrapper",
        ),

        width="100%",
        min_height="100vh",
        bg="gray.200",
        margin="0",
        padding="0",
    )

    @staticmethod
    def orig_preview(
        title: str,
        border_colour: str,
        maintenance_prefix: str, 
        maintenance_id: str,
        content: rx.Component
    ) -> rx.Component:
        return rx.box(
        # Outer wrapper centering the page
        rx.center(
            # The A4 Page Card
            rx.box(
                # Header
                rx.hstack(
                    rx.image(
                        src="/pems-logo.png",
                        alt="Company Logo",
                        height="40px",
                        object_fit="contain",
                    ),
                    rx.heading(title, size="6", weight="bold"),
                    width="100%",
                    justify="between",
                    align="center",
                    border_bottom=f"4px solid {border_colour}",
                    padding_bottom="3",
                    margin_bottom="4",
                ),

                # Middle Content Area
                rx.box(
                    content,
                    width="100%",
                    style={"flex": "1 1 auto"},  # Forces box to expand and fill available height
                ),

                # Footer
                rx.hstack(
                    rx.text(f"{maintenance_prefix}: {maintenance_id}", size="1", color="gray"),
                    width="100%",
                    justify="between",
                    border_top=f"4px solid {border_colour}",
                    padding_top="2",
                    style={"margin-top": "auto"},  # Anchors footer to bottom
                ),

                # Explicit A4 dimensions and Flexbox layout rules
                width="210mm",
                height="297mm",  # Explicit height enables flex space distribution
                padding="15mm",
                bg="white",
                box_shadow="0 4px 10px rgba(0, 0, 0, 0.15)",
                box_sizing="border-box",
                display="flex",
                flex_direction="column",
            ),
            width="100%",
            padding_y="8",
        ),
        width="100%",
        min_height="100vh",
        bg="gray.200",
    )
