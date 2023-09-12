from tecton import PushSource, HiveConfig
from tecton.types import String, Int64, Timestamp, Field

input_schema = [
    Field(name="USER_ID", dtype=String),
    Field(name="CHAT_MESSAGE_ID", dtype=String),
    Field(name="MESSAGE", dtype=String),
    Field(name="TIMESTAMP", dtype=Timestamp)
]

chat_message_eventsource = PushSource(
    name="chat_message_eventsource",
    schema=input_schema,
    batch_config=HiveConfig(
        database="chat_demo_data",
        table="chat_messages",
        timestamp_field="TIMESTAMP",
    ),
    description="Push Source for real-time chat messages",
    owner="nlee@tecton.ai",
    tags={"release": "production"},
)