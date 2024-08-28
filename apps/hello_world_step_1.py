from simian.gui import Form, component, component_properties, utils

examples_url = "https://github.com/Simian-Web-Apps/simian-deploy-render"
hello_world_step = 1

# Run this file locally
if __name__ == "__main__":
    import simian.local

    simian.local.Uiformio(
        f"hello_world_step_{hello_world_step}",
        window_title=f"Simian: Hello World - Step {hello_world_step} !",
    )


def gui_init(meta_data: dict) -> dict:
    """Create a form and set a logo and title."""

    # Create form.
    form = Form()

    # Base payload
    payload = {
        "form": form,
        "navbar": {
            "title": (
                f'<a class="text-white" href="{examples_url}" target="_blank">'
                f'<i class="fa fa-github"></i></a>&nbsp;Hello World Step {hello_world_step} - from Simian!'
            )
        },
    }

    # Create a textfield.
    hello_text = component.TextField("helloKey", form)
    hello_text.label = "Enter first word"
    hello_text.defaultValue = "Hello"

    # Create a button.
    world_button = component.Button("buttonKey", form)
    world_button.label = "World!"
    world_button.disabled = True
    world_button.tooltip = (
        "Button disabled because no event and corresponding callback defined yet."
    )

    # Create a textfield.
    result_text = component.TextField("resultKey", form)
    result_text.label = "The result"
    result_text.placeholder = "Click button to display result ..."
    result_text.disabled = True

    return payload


def gui_event(meta_data: dict, payload: dict) -> dict:
    return payload
