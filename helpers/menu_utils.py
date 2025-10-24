from classes.state import State

def add_menu_command_with_hotkey(state: State, menu, label, command, hotkey=None):
    """Add a menu command and bind an optional hotkey (e.g. 'Control+z')."""
    display_label = f"{label} {hotkey}" if hotkey else label
    menu.add_command(label=display_label, command=command)
    if hotkey:
        tk_hotkey = f"<{hotkey.replace('+', '-')}>"
        state.canvas.bind_all(tk_hotkey, lambda _: command())

