import requests

def main():
    top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    item_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    try:
        ids = requests.get(top_url, timeout=10).json()
    except Exception as e:
        print(f"Error fetching top stories: {e}")
        return
    for i, item_id in enumerate(ids[:5], 1):
        try:
            item = requests.get(item_url.format(item_id), timeout=10).json()
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            print(f"{i}. {title}\n   {url}")
        except Exception as e:
            print(f"Error fetching item {item_id}: {e}")

if __name__ == "__main__":
    main()