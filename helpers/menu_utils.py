from classes.state import State

def add_menu_command_with_hotkey(state: State, menu, label, command, hotkey=None):
    """
    Add a menu command and bind an optional hotkey (e.g. 'Control+z').

    Args:
        state (State):
        menu: which menu the butten will be bound to
        label: The label that will appear on the button
        command: The function or lambda function that will run when pressing the button
        hotkey: Will bind and display hotkey if set

    """
    display_label = f"{label} {hotkey}" if hotkey else label
    menu.add_command(label=display_label, command=command)
    if hotkey:
        tk_hotkey = f"<{hotkey.replace('+', '-')}>"
        state.canvas.bind_all(tk_hotkey, lambda _: command())