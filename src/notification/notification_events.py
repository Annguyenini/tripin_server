from types import SimpleNamespace


EVENT_TYPES = SimpleNamespace(
    FRIENDSHIP_EVENTS = SimpleNamespace(
        FRIEND_REQUEST = 'friend_request',
        FRIEND_REMOVED = 'friend_removed',
        FRIEND_REJECT = 'friend_reject',
        FRIEND_CANCEL = 'friend_cancel',
        FRIEND_ACCEPT = 'friend_accept'
    )
)
