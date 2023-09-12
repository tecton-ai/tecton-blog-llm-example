from datetime import datetime, timedelta
from tecton import stream_feature_view, Aggregation, FilteredSource, BatchTriggerType
from entities import user
from data_sources.chat_message_eventsource import chat_message_eventsource
from tecton.types import Field, Timestamp, Int64, String
from tecton.aggregation_functions import last

output_schema = [
    Field(name="USER_ID", dtype=String),
    Field(name="SENTIMENT", dtype=String),
    Field(name="SENTIMENT_NUMERIC", dtype=Int64),
    Field(name="CONTAINS_FEEDBACK", dtype=Int64),
    Field(name="CHAT_MESSAGE_ID", dtype=String),
    Field(name="TIMESTAMP", dtype=Timestamp)
]

from api_key_llm import api_key
from business_logic.sentiment_function import sentiment_function
from business_logic.sentiment_numeric_translator import sentiment_numeric_translator
@stream_feature_view(
    name="live_sentiment_stats",
    source=FilteredSource(chat_message_eventsource),
    entities=[user],
    online=True,
    offline=True,
    feature_start_time=datetime(2023, 8, 1),
    batch_schedule = timedelta(days=1),
    manual_trigger_backfill_end_time=datetime(2023, 9, 5),
    batch_trigger=BatchTriggerType.MANUAL,
    aggregations=[
        Aggregation(column="SENTIMENT_NUMERIC", function="min", time_window=timedelta(minutes=120)),
        Aggregation(column="SENTIMENT_NUMERIC", function="max", time_window=timedelta(minutes=120)),
        Aggregation(column="SENTIMENT_NUMERIC", function="mean", time_window=timedelta(minutes=120)),
        Aggregation(column="SENTIMENT_NUMERIC", function="mean", time_window=timedelta(days=3)),
        Aggregation(column="CONTAINS_FEEDBACK", function="sum", time_window=timedelta(days=3)),
        Aggregation(column="SENTIMENT", function=last(10), time_window=timedelta(days=1)),
        Aggregation(column="CHAT_MESSAGE_ID", function=last(10), time_window=timedelta(days=1))
    ],
    tags={"release": "production"},
    owner="nlee@tecton.ai",
    description="analysis of a customer's recent sentiment",
    mode="python",
    schema=output_schema,
)
def live_sentiment_stats(chat_message_eventsource):
    chat_message_eventsource["SENTIMENT"], chat_message_eventsource["CONTAINS_FEEDBACK"] = sentiment_function(chat_message_eventsource["MESSAGE"], api_key)
    chat_message_eventsource["SENTIMENT_NUMERIC"] = sentiment_numeric_translator(chat_message_eventsource["SENTIMENT"])
    return chat_message_eventsource