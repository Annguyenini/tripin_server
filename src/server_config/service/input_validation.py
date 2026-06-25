import re
import unicodedata

from src.error_code.error_code import INPUT_ERROR


class InputValidation:
    def _username_validation(self, username: str) -> bool:
        # length between 3-20
        if not username:
            return False
        if len(username) < 3 or len(username) > 15:
            return False
        # must contain upper case letter, no special char and start with word
        check = re.match(r"^(?=.*[A-Z])[a-zA-Z]\w+$", username)
        return True if check else False

    def _password_validation(self, password: str) -> bool:
        if not password:
            return False
        if len(password) < 8 or len(password) > 15:
            return False
        # must contain at least 1upper case,1 sepecial char, 1 degit, and start with word
        check = re.match(r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[a-zA-Z]", password)
        return True if check else False

    def _displayname_validation(self, display_name: str) -> bool:
        s = display_name.strip()
        if not (2 <= len(s) <= 32):
            return False
        return all(
            unicodedata.category(c) in ("Ll", "Lu", "Lt", "Lm", "Lo", "Nd", "Zs")
            or c == " "
            for c in s
        )

    def _email_validation(self, email: str) -> bool:
        if not email:
            return False
        # if doesnt have the @ dont bother care
        check = re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
        return True if check else False

    def _verify_code_validation(self, code: str) -> bool:
        if not code:
            return False
        # only digits, 6 digits
        check = re.match(r"^\d{6}$", code)
        return True if check else False

    def _validate_provider(self, provider: str):
        ALLOWED_PROVIDERS = {"google"}
        if not provider or not provider.strip():
            return False
        if provider.strip() not in ALLOWED_PROVIDERS:
            return False
        return True

    def _validate_provider_id(self, provider_id: str):
        if not provider_id or not provider_id.strip():
            return False
        return True

    def _trip_name_validation(self, trip_name: str) -> bool:
        if not trip_name:
            return False

        if len(trip_name) < 5 or len(trip_name) > 40:
            return False

        return trip_name[0].isalnum() and all(
            c.isalnum() or c == " " for c in trip_name
        )

    def _trip_image_validation(self, image_path: str):
        pattern = r"^trips/\d+/cover\.jpg$"
        return bool(re.match(pattern, image_path))


class CredentialInputValidation(InputValidation):
    def __init__(self) -> None:
        super().__init__()

    def login_input_validation(self, **kwargs):
        username = kwargs.get("username")
        password = kwargs.get("password")
        email = kwargs.get("email")
        if username:
            if not self._username_validation(username=username):
                raise ValueError(INPUT_ERROR.USERNAME)
        elif email:
            if not self._email_validation(email=email):
                raise ValueError(INPUT_ERROR.EMAIL)
        if not self._password_validation(password=password):
            raise ValueError(INPUT_ERROR.PASSWORD)

    def signup_input_validation(
        self, username: str, password: str, email: str, display_name: str
    ) -> None:

        if not self._username_validation(username=username):
            raise ValueError(INPUT_ERROR.USERNAME)
        if not self._email_validation(email=email):
            raise ValueError(INPUT_ERROR.EMAIL)
        if not self._password_validation(password=password):
            raise ValueError(INPUT_ERROR.PASSWORD)
        if not self._displayname_validation(display_name=display_name):
            raise ValueError(INPUT_ERROR.DISPLAY_NAME)

    def verify_code_input_validation(self, email: str, code: str) -> None:
        if not self._email_validation(email=email):
            raise ValueError(INPUT_ERROR.EMAIL)
        if not self._verify_code_validation(code=str(code)):
            raise ValueError(INPUT_ERROR.VERIFY_CODE)

    def provider_input_validation(self, provider: str, protiver_id: str) -> None:
        if not self._validate_provider(provider=provider):
            raise ValueError(INPUT_ERROR.PROVIDER)
        if not self._validate_provider_id(provider_id=protiver_id):
            raise ValueError(INPUT_ERROR.PROVIDER_ID)

    def provider_complete_signup_inputs_validation(
        self, username: str, password: str, display_name: str
    ) -> None:
        if not self._username_validation(username=username):
            raise ValueError(INPUT_ERROR.USERNAME)

        if not self._password_validation(password=password):
            raise ValueError(INPUT_ERROR.PASSWORD)
        if not self._displayname_validation(display_name=display_name):
            raise ValueError(INPUT_ERROR.DISPLAY_NAME)

    def email_validation(self, email: str):
        if not self._email_validation(email=email):
            raise ValueError(INPUT_ERROR.EMAIL)

    def password_validation(self, password: str):
        if not self._password_validation(password=password):
            raise ValueError(INPUT_ERROR.PASSWORD)


class TripInputValidation(InputValidation):
    def __init__(self) -> None:
        super().__init__()

    def trip_name_validation(self, trip_name: str):
        if not self._trip_name_validation(trip_name=trip_name):
            raise ValueError(INPUT_ERROR.TRIP_NAME)

    def trip_image_validation(self, image_path: str):
        if not self._trip_image_validation(image_path=image_path):
            print(image_path)
            raise ValueError(INPUT_ERROR.TRIP_IMAGE)
