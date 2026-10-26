import reflex as rx

def sidebar(active_page: str) -> rx.Component:
    # List of PEMS Modules
    nav_items = [
        ("Home", "/"),
        ("Asset Registrar", "/assets"),
        ("Spare Parts", "/parts"),
        ("Maintenance Schedule", "/schedule"),
        ("Extraction Analysis", "/extractions")
    ]

    return rx.vstack(
        # Logo
        rx.hstack(
            rx.image(
                src="/pems-logo.png",
                width="200px",
                height="auto",
                border_radius="4px"
            )
        ),

        # Dynamically Loop and build the layout
        *[
            rx.link(
                name, 
                href=url,
                width="100%",
                padding="0.6em 1em",
                border_radius="6px",
                font_weight="medium",
                # Highlight the active page in blue, others stay subtle
                background_color="#e0f2fe" if active_page == name else "transparent",
                color="#036a1" if active_page == name else "#4a5568",
                _hover={"background_color": "#f1f5f9", "color": "#1a202c"},
                transition="all 0.2s ease"
            )
            for name, url in nav_items
        ],

        position="fixed",
        padding="2em 1.5em",
        background_color="#f8fafc",
        height="100vh",
        width="260px",
        border_right="1px solid #e2e8f0",
        align_items="start",
        spacing="2",
    )