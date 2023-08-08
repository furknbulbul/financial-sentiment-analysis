import json
import pandas as pd
import datetime
from playwright.sync_api import sync_playwright
from openpyxl import load_workbook

def parse_thread(data):
    caption_data = data.get("caption", {})
    text = caption_data.get("text") if isinstance(caption_data, dict) else None

    shared_at = data.get("shared_at", data.get("taken_at"))
    if shared_at:
        shared_datetime = datetime.datetime.fromtimestamp(shared_at / 1000)
        published_date = shared_datetime.date()
        published_time = shared_datetime.time()
    else:
        published_date = None
        published_time = None

    return {
        "text": text,
        "published_on_date": published_date,
        "published_on_time": published_time,
        "username": data.get("user", {}).get("username"),
        "like_count": data.get("like_count")
    }

def traverse_json(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "threads":
                yield v
            elif isinstance(v, (dict, list)):
                yield from traverse_json(v)
    elif isinstance(data, list):
        for item in data:
            yield from traverse_json(item)

def scrape_threads(url):
    _xhr_calls = []

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page.on("response", intercept_response)
        page.goto(url)
        page.wait_for_selector("[data-pressable-container=true]")

        gql_calls = [f for f in _xhr_calls if "/api/graphql" in f.url]
        parsed_posts = []
        for xhr in gql_calls:
            data = json.loads(xhr.text())
            for thread_data in traverse_json(data):
                if isinstance(thread_data, list):
                    for thread in thread_data:
                        post = thread["thread_items"][0]["post"]
                        parsed_posts.append(parse_thread(post))
                else:
                    post = thread_data["thread_items"][0]["post"]
                    parsed_posts.append(parse_thread(post))

    return pd.DataFrame(parsed_posts)

def main():
    urls = [
    "https://www.threads.net/@erenkru?igshid=NTc4MTIwNjQ2YQ%3D%3D",
    "https://www.threads.net/@mehmetakifozen?igshid=NTc4MTIwNjQ2YQ%3D%3D",
    "https://www.threads.net/@cozdegerleme?igshid=NTc4MTIwNjQ2YQ%3D%3D",
    "https://www.threads.net/@xanthos_027?igshid=NTc4MTIwNjQ2YQ%3D%3D",
    "https://www.threads.net/@derya_hkm?igshid=NTc4MTIwNjQ2YQ%3D%3D",
    "https://www.threads.net/@fiyathedef?igshid=NTc4MTIwNjQ2YQ%3D%3D",
    "https://www.threads.net/@cozdegerleme?igshid=NTc4MTIwNjQ2YQ%3D%3D",
    "https://www.threads.net/@dr_arslan_smmm?igshid=NTc4MTIwNjQ2YQ%3D%3D"
    
    # Add more URLs here for multiple links
 ]

    all_dfs = [scrape_threads(url) for url in urls]
    combined_df = pd.concat(all_dfs, ignore_index=True).dropna(subset=["text"])

    output_file = "combined_threads_data.xlsx"
    combined_df.to_excel(output_file, index=False)

    print("Data from all links combined and saved to", output_file)

if __name__ == "__main__":
    main()