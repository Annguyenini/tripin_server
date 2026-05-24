from types import SimpleNamespace

USERAUDIT = SimpleNamespace(
    ACTIONS=SimpleNamespace(
        RESET_PASSWORD="reset_password",
        CHANGE_AVATAR="change_avatar",
        CHANGE_DISPLAY_NAME="change_displayname",
    ),
)
