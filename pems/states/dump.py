import reflex as rx


class FormState(rx.State):
    # Dynamic list of file keys (can be updated dynamically)
    file_keys: list[str] = ["File A", "File B", "File C"]

    # Parameter settings state
    param_1: str = ""
    param_2: str = ""

    # Current page index (0 = Parameters, 1..N = Files, Last = Submit)
    current_step: int = 0

    @rx.var
    def total_steps(self) -> int:
        # 1 page for parameters + N pages for files + 1 submission page
        return len(self.file_keys) + 2

    def next_page(self):
        if self.current_step < self.total_steps - 1:
            self.current_step += 1

    def prev_page(self):
        if self.current_step > 0:
            self.current_step -= 1

    def handle_submit(self):
        # Final form submission logic
        return rx.window_alert("Form Submitted Successfully!")


# --- PAGE 1: PARAMETER SETTING ---
def parameter_page() -> rx.Component:
    return rx.vstack(
        rx.heading("Step 1: Parameter Settings", size="5"),
        rx.input(
            placeholder="Parameter 1",
            value=FormState.param_1,
            on_change=FormState.set_param_1,
        ),
        rx.input(
            placeholder="Parameter 2",
            value=FormState.param_2,
            on_change=FormState.set_param_2,
        ),
        spacing="4",
        width="100%",
    )


# --- DYNAMIC INTERMEDIATE PAGES: SINGLE CSV FILE UPLOAD ---
def file_upload_page(key_name: str) -> rx.Component:
    upload_id = f"upload_{key_name}"

    return rx.vstack(
        rx.heading(f"Upload CSV for: {key_name}", size="5"),
        rx.upload(
            rx.vstack(
                rx.text(f"Drag and drop CSV for {key_name}"),
                rx.button("Select File", type_="button"),
                align="center",
            ),
            id=upload_id,
            accept={"text/csv": [".csv"]},
            padding="2em",
            border="2px dashed gray",
            border_radius="8px",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


# --- LAST PAGE: FINAL SUBMISSION ---
def submission_page() -> rx.Component:
    return rx.vstack(
        rx.heading("Final Step: Submit Form", size="5"),
        rx.text("Review your settings and click Submit to process all files."),
        rx.button(
            "Submit Form",
            color_scheme="green",
            size="3",
            on_click=FormState.handle_submit,
        ),
        spacing="4",
        width="100%",
    )


# --- LAYOUT HANDLER ---
def form_layout() -> rx.Component:
    return rx.vstack(
        # Header / Progress Indicator
        rx.text(
            f"Step {FormState.current_step + 1} of {FormState.total_steps}",
            weight="bold",
        ),
        rx.divider(),
        # Conditional view based on step index
        rx.cond(
            FormState.current_step == 0,
            parameter_page(),
            rx.cond(
                FormState.current_step == FormState.total_steps - 1,
                submission_page(),
                # Match the current step index to the dynamic file key list
                file_upload_page(
                    FormState.file_keys[FormState.current_step - 1]
                ),
            ),
        ),
        rx.divider(),
        # Navigation Controls
        rx.hstack(
            rx.button(
                "Previous",
                on_click=FormState.prev_page,
                disabled=FormState.current_step == 0,
            ),
            rx.button(
                "Next",
                on_click=FormState.next_page,
                disabled=FormState.current_step == FormState.total_steps - 1,
            ),
            justify="between",
            width="100%",
        ),
        padding="2em",
        max_width="500px",
        border="1px solid #E2E8F0",
        border_radius="12px",
    )


def index():
    return rx.center(form_layout(), height="100vh")