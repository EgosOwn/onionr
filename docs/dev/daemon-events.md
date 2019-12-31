# DaemonEvents

For things that need to be processed by the daemon

Observer pattern

Register listeners dynamically per event

Spawn new greenlets

-------------------

## Attributes

events: dict

schema:

{
        "event_id": dict{
                "event_name": string,
                "result_data": bytes,
                "started": epoch,
                "finished": epoch,
                "done": bool
        }
}


--------------------

MsgPack schema:

event_name: string
event_id: uuid4

