from src.notification.push_notification_payload import PushNotificationPayload


def FRIEND_REQUEST_PUSH_NOTIFICATION_PAYLOAD(to: str, send_id: int, sender_name: str, avatar_url: str = None) -> PushNotificationPayload:
    payload = {
        "to": to,
        "title": f"{sender_name} wants to be your friend!! 👀",
        "body": f"{sender_name} slid into your friend requests. Accept before it gets awkward.",
        "data": {
            "type": "friend_request",
            "send_id": send_id
        },
        "sound": "default",
        "priority": "high",
        "channelId": "default"
    }
    if avatar_url:
        payload["richContent"] = {"image": avatar_url}
    return payload


def FRIEND_ACCEPT_PUSH_NOTIFICATION_PAYLOAD(to: str, send_id: int, sender_name: str, avatar_url: str = None) -> PushNotificationPayload:
    payload = {
        "to": to,
        "title": "AYYYYY! 🎉",
        "body": f"{sender_name} accepted your friend request. You're basically travel besties now.",
        "data": {
            "type": "friend_accept",
            "send_id": send_id
        },
        "sound": "default",
        "priority": "high",
        "channelId": "default"
    }
    if avatar_url:
        payload["richContent"] = {"image": avatar_url}
    return payload
