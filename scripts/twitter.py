import requests
import time
from datetime import datetime
import pandas as pd

user_tweet_url = "https://twitter241.p.rapidapi.com/user-tweets"
user_url = "https://twitter241.p.rapidapi.com/user"

DATE_DEPTH = datetime(2022, 6, 1, 0, 0)
mounth_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
              "Nov": 11, "Dec": 12}

# kod cok temiz olmayabilir, kusura bakmayin
# buradaki username i kendinize gore degistirin, tek tek yapmak daha mantikli olabilir cunlu bir tane user icin bile buyuk ihtimalle 1 sene onceye gidene kadar patliyor
usernames = ["fiboo141425"]

# headers kismini kendiniz uye olduktan sonraki key ve host bilgileriyle degistirin
headers = {
	"X-RapidAPI-Key": "",
	"X-RapidAPI-Host": ""
}

def parse_date(date_str):
    tokens = date_str.split(" ")
    mounth = mounth_map[tokens[1]]
    day = int(tokens[2])
    hour_min = tokens[3]
    year = int(tokens[5])
    hour = int(hour_min.split(":")[0])
    minute = int(hour_min.split(":")[1])
    return datetime(year, mounth, day, hour, minute)


def is_date_eligible(compared_date):
    return compared_date > DATE_DEPTH


def get_user_tweets_one_batch(user_id, cursor=None, author=None):
    response = None
    querystring = {"user": user_id, "count": "20", "cursor": cursor}
    for i in range(3):
        try:
            response = requests.get(user_tweet_url, headers=headers, params=querystring, timeout=5)
            if response.status_code == 200 and response.json().get("error"):
                print("something went wrong, waiting for 60 seconds")
                time.sleep(60)
                continue
            break
        except:
            print("request failed", i+1, "times")
            if i == 2:
                return 1
        time.sleep(60)

    # response = requests.get(user_tweet_url, headers=headers, params=querystring)
    temp_result = []
    try:
        bottom_cursor = response.json()["cursor"]["bottom"]
    except:
        print("could not find the cursor")
        return 1
    try:
        temp_entries = response.json()["result"]["timeline"]["instructions"]
        for entry in temp_entries:
            tmp = entry if entry["type"] == "TimelineAddEntries" else None
        tweets = tmp['entries']
    except:
        return 0

    

    min_date = datetime.now()
    if tweets is not None:
        for index, tweet in enumerate(tweets):
            try:
                if tweets[index]["entryId"].split("-")[:2] == ["promoted", "tweet"]:
                    continue
                parent_temp_object = tweets[index]["content"]["itemContent"]['tweet_results']['result']
                temp_object = tweets[index]["content"]["itemContent"]['tweet_results']['result']['legacy']
            except:
                continue
            full_text = temp_object["full_text"]
            created_at = parse_date(temp_object["created_at"])
            favourite_count = int(temp_object["favorite_count"])
            try:
                view_count = int(parent_temp_object["views"]["count"])
            except:
                view_count = -1
            reply_count = int(temp_object["reply_count"])
            retweet_count = int(temp_object["retweet_count"])
            # quoted_tweet_text = temp_object["quoted_status_result"] if temp_object.get("quoted_status_result") else None
            temp_result.append({
                "full_text": full_text,
                "created_at": created_at,
                "favourite_count": favourite_count,
                "view_count":view_count,
                "reply_count": reply_count,
                "retweet_count": retweet_count,
                "author": author
                # "quoted_tweet_text":quoted_tweet_text
            })
            min_date = created_at if created_at < DATE_DEPTH else min_date
            print(min_date)
            print(temp_result[-1])
        
    return temp_result, bottom_cursor, is_date_eligible(min_date)


cursor_set = []


def get_all_user_tweets(user_id, author, cursor=None):
    result = []
    date_not_reached = True
    while date_not_reached:
        one_batch = get_user_tweets_one_batch(user_id, cursor, author)
        temp_result = None
        if one_batch == 1:
            break
        if one_batch == 0:
            continue
        temp_result, cursor, date_not_reached = one_batch
        if cursor in cursor_set:
            print("cursor is found before")
            break
        cursor_set.append(cursor)
        result.append(temp_result)
        time.sleep(3)
    return result


# get user id
user_ids = []
for username in usernames:
    username_query = {"username": username}
    response = requests.get(user_url, headers=headers, params=username_query)
    user_id = response.json()["data"]["user"]["result"]["rest_id"]
    user_ids.append((user_id, username))
    print(user_id)
    time.sleep(2)

df = pd.DataFrame()
for user_id, username in user_ids:
    result = get_all_user_tweets(user_id, username)
    for res in result:
        df = pd.concat([df, pd.DataFrame(res)])
    

#print(df)
print(cursor_set)
print("last cursor:", cursor_set[-1])

df.to_excel(f"{usernames[0]}.xlsx", index=False)
