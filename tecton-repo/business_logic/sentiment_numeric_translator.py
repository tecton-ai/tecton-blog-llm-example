def sentiment_numeric_translator(sentiment_string):
    if sentiment_string == "Very Upset": return -2
    elif sentiment_string == "Upset": return -1
    elif sentiment_string == "Neutral": return 0
    elif sentiment_string == "Happy": return 1
    elif sentiment_string == "Very Happy": return 2
    else: return None
