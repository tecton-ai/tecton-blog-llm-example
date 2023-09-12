from tecton import FeatureService

from features.streaming_features.live_sentiment_stats import live_sentiment_stats

live_sentiment_fs = FeatureService(
    name="live_sentiment_fs",
    online_serving_enabled=True,
    features=[
        live_sentiment_stats
    ],
)