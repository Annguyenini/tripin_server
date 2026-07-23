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

    def _device_push_token_validation(self, token: str) -> bool:
       if not token or not isinstance(token, str):
           return False
       if len(token) < 10 or len(token) > 512:
           return False
       # allow alphanumeric, dot, underscore, hyphen, and brackets (Expo push tokens: "ExponentPushToken[...]")
       check = re.match(r"^[a-zA-Z0-9._\-\[\]]+$", token)
       return True if check else False

    def _device_id_validation(self, device_id: str) -> bool:
       if not device_id or not isinstance(device_id, str):
           return False
       if len(device_id) < 5 or len(device_id) > 128:
           return False
       # allow alphanumeric, colon, space, parentheses, hyphen, underscore
       # (format: "Brand:Model (variant):uuid")
       # check = re.match(r"^[a-zA-Z0-9:\s()\-_]+$", device_id)
       return True
    def _platform_validation(self, platform: str) -> bool:
        ALLOWED_PLATFORM = {"ios", "android", "web",'ipados'}

        if not platform or not isinstance(platform, str):
            return False

        return platform.lower() in ALLOWED_PLATFORM

    def _lastseen_validation(self, lastseen: int) -> bool:
        if lastseen is None:
            return False

        if not isinstance(lastseen, int):
            return False

        # milliseconds timestamp should be positive
        if lastseen <= 0:
            return False

        return True
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

    def trip_privacy_validation(self,privacy:str):
        allow_privacy = ['private','public','friend']
        if privacy not in allow_privacy:
            raise ValueError(INPUT_ERROR.TRIP_PRIVACY)




class DeviceInputValidation(InputValidation):
    def __init__(self) -> None:
        super().__init__()

    def device_input_validation(
        self,
        device_id: str,
        platform: str,
        lastseen: int
    ) -> None:



        if not self._device_id_validation(device_id=device_id):
            raise ValueError(INPUT_ERROR.DEVICE_ID)

        if not self._platform_validation(platform=platform):
            raise ValueError(INPUT_ERROR.PLATFORM)

        if not self._lastseen_validation(lastseen=lastseen):
            raise ValueError(INPUT_ERROR.LASTSEEN)

    def push_token_input_validation(self,push_token:str):

        if not self._device_push_token_validation(token=push_token):
            raise ValueError(INPUT_ERROR.DEVICE_PUSH_TOKEN)
