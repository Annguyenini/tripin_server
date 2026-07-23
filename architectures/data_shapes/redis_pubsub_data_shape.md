# Redis WebSocket Event Payload

The payload published to Redis for WebSocket notifications follows this structure:

```json
{
  "room_id": "user:[user_id]",
  "event_type": "[event_type]",
  "data": {
    "...": "..."
  }
}
room_id - unique id for each user
event-type - see web_socket/event_types.md
data - json object of data shape
