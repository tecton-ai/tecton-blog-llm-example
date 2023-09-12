def sentiment_function(message_string, api_key):
    import time, random #As a Tecton requirement, I must import within the method
    import json
    import urllib.request
    import urllib.error

    save_money = False
    if save_money:
        time.sleep(1)  # simulate an inference lag time
        return random.choice(["Very Upset", "Upset", "Neutral", "Happy", "Very Happy"])
    else:
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }

        # prompt for our LLM
        json_data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'user',
                    'content': '''For the message below, classify sentiment as 
                    ["Very Upset", "Upset", "Neutral", "Happy", "Very Happy"]. 
                    If the message includes constructive product feedback, set "contains_feedback" to 1, otherwise set it to 0. 
                    Return JSON ONLY. No other text outside the JSON. JSON format: 
                    {"message_sentiment": <message sentiment>, 
                    "contains_feedback": <1 or 0>} 
                    Here is the message to classify: ''' + message_string
                }
            ],
            'temperature': 0.7
        }
        json_data = json.dumps(json_data).encode('utf-8')
        max_retries = 4
        retry_delay = 2  # seconds

        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(url, headers=headers, data=json_data)
                response = urllib.request.urlopen(req)
                response_data = response.read().decode('utf-8')
                response_json = json.loads(response_data)
                message_sentiment = json.loads(response_json['choices'][0]['message']['content'])['message_sentiment']
                contains_feedback = json.loads(response_json['choices'][0]['message']['content'])['contains_feedback']
                return message_sentiment, contains_feedback
            except urllib.error.HTTPError as e:
                if attempt < max_retries:
                    print(f"Received HTTPError {e.code}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to retrieve the response after {max_retries} tries: {e}")
                    return None
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
