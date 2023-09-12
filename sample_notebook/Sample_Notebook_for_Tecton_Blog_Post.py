# Databricks notebook source
# DBTITLE 1,Create a demo batch data source
import uuid 
Fake_Data = {"USER_ID": ["Bob123", "Sally123", "Mike555", "Joker574"],
            "CHAT_MESSAGE_ID": [str(uuid.uuid4()) for i in range(4)],
            "MESSAGE": ["I liked it a lot!", "I'm very disappointed in my last order :(", "Hi my name is Mike", "I enjoyed the product, thank you."],
            "TIMESTAMP": ["2023-08-06T22:15:14Z", "2023-08-07T18:15:14Z", "2023-08-08T12:15:14Z", "2023-08-09T20:15:14Z"]
}

# COMMAND ----------

# MAGIC %sql 
# MAGIC CREATE SCHEMA IF NOT EXISTS chat_demo_data;

# COMMAND ----------

import pandas as pd
df = spark.createDataFrame(pd.DataFrame.from_dict(Fake_Data))
df = df.withColumn("TIMESTAMP",df.TIMESTAMP.cast("timestamp"))
display(df)

# COMMAND ----------

(df.orderBy("TIMESTAMP")
 .write.mode('overwrite')
 .saveAsTable("chat_demo_data.chat_messages"))

# COMMAND ----------

display(spark.table("chat_demo_data.chat_messages"))

# COMMAND ----------

import tecton

#replace with your own token and tecton_url
token = dbutils.secrets.get(scope="nicklee", key="STAGING_TECTON_API_KEY") 
tecton_url = dbutils.secrets.get(scope="nicklee", key="STAGING_API_SERVICE")

tecton.set_credentials(token, tecton_url=tecton_url)
tecton.conf.set("TECTON_CLUSTER_NAME", "tecton-staging")
tecton.test_credentials()

ws = tecton.get_workspace("llm-demo-live") 

# COMMAND ----------

# DBTITLE 1,Streaming Chat Simulator
#Leave this code running to simulate a streaming data stream with Tecton's Ingest API 
import requests, json, uuid
import pandas as pd
from datetime import datetime
import time
import random

looping = True #Change to True if you want to kick off a constant stream of data to the Ingest API. Let code run in the background to simulate stream. 
verbose = True

def stream_a_chat(verbose = False): 
  current_timestamp_formatted = datetime.utcnow().strftime("%Y-%m-%d" + "T" + "%H:%M:%S" + "Z") #The expected Zulu Time format for Tecton

  random_message = random.choice(["I liked the color of the product.", 
                          "What shipping options do you offer?", 
                          "I will not be using your product ever again!",
                          "The product was terrible, garbage almost.", 
                          "Can you please solve my problem faster?",
                          "I'll tell my friends how great your product was!",
                          "I find this product incredibly hard to use.", 
                          "I liked the tool, but I would suggest adding more knobs for easier controls.",
                          "The product seems to fall apart after 10 uses. I would prefer a longer lasting solution."])
  
  random_user = random.choice(["Bob123", "Sally123", "Mike555", "Joker574"])

  data = {
    "workspace_name": "llm-demo-live", #replace with your workspace name 
    "dry_run": False,
    "records": {
      "chat_message_eventsource": [
        {
          "record": {
            "USER_ID": random_user,
            "CHAT_MESSAGE_ID": str(uuid.uuid4()),
            "MESSAGE": random_message,
            "TIMESTAMP": current_timestamp_formatted
          }
        }
      ]
    }
  }

  #replace this with your correct endpoint https://preview.<your_cluster>.tecton.ai/
  ingest_endpoint = 'https://preview.staging.tecton.ai/ingest' #this endpoint may change after Ingest API exits Preview.

  # This will only work for a live workspace
  r = requests.post(ingest_endpoint, data=json.dumps(data), headers={'Authorization': 'Tecton-key ' + token})  
  
  if verbose:
    print(json.dumps(data, indent=4))
    print(r.json())
  
  return data["records"]["chat_message_eventsource"][0]["record"] #so I can keep the event locally 

list_of_chat_events = []
while looping is True: 
  record = stream_a_chat(verbose = verbose)
  time.sleep(1) #sleep 1 second. Every 100 OpenAI inferences costs about 1 penny.
                #a 1 second sleep means every 5 minutes will cost about 3 cents   
  list_of_chat_events.append(record)

record = stream_a_chat(verbose=True)
list_of_chat_events.append(record) #keeping a list of all events for future use as a spine

# COMMAND ----------

#Here is a quick check of the Online Store; you can see features are being updated on-the-fly for each symbol as new data is streaming in from Ingest API. 
#Try submitting more data and re-running this code block to see the changes. 
chat_feature_service= ws.get_feature_service("live_sentiment_fs")

for user in ["Bob123", "Sally123", "Mike555", "Joker574"]: 
  online_features = chat_feature_service.get_online_features(join_keys={'USER_ID': user}).to_dict()
  formatted_output = json.dumps(online_features, indent=4)
  print(user + ": " + formatted_output)

# COMMAND ----------

# DBTITLE 1,Backfills also work for historic chats. 
chat_feature_view = ws.get_feature_view("live_sentiment_stats")
training_df = chat_feature_view.get_historical_features(start_time = datetime(2023, 8, 1), end_time = datetime(2023, 8, 10)).to_pandas()
display(training_df)

# COMMAND ----------

# DBTITLE 1,Sending a spine of chat events to Feature Service
spine = pd.DataFrame(list_of_chat_events)
spine["TIMESTAMP"] = pd.to_datetime(spine["TIMESTAMP"])

chat_feature_service = ws.get_feature_service("live_sentiment_fs")
display(chat_feature_service.get_historical_features(spine).to_spark())

# COMMAND ----------


