from types import SimpleNamespace
ERROR_KEYS=SimpleNamespace(
    NOPERMISSION='not_authorize',
    FAILED='failed'
)



ERROR_MESSAGE=SimpleNamespace(
    NOPERMISSION='You dont have permission!',
    SERVER_FAILED='Server failed to conplete the request'
)

INPUT_ERROR =SimpleNamespace(
    USERNAME ='Username must between 3-15 letter, Must containt 1 Upper case and starting with a word',
    PASSWORD ='Password must contain at least 1 upper case,1 sepecial char, 1 degit, and start with a word. Between 8-12 letters',
    DISPLAY_NAME='Display name must contain upper case letter, no special char. Between 5-10 letters',
    EMAIL ='Email invalid',
    TRIP_NAME ='Trip name must have no special char and start with word. Between 5-10 words ',
    VERIFY_CODE ='Only containt 6 digits',
)