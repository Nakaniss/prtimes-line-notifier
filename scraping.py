import requests


class PressRelease:
    def __init__(self, id, title, url, company, updated_at, release_comple_date):
        self.id = id
        self.title = title
        self.url = url
        self.company = company
        self.updated_at = updated_at
        self.release_comple_date = release_comple_date


# APIのURLから、PressReleaseオブジェクトのリストを返す関数
def get_pr(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        pr_list = []
        for entry in data.get("data", []):
            # マッピング
            id = entry.get("id", "")
            title = entry.get("title", "").replace(",", "")
            url = "https://prtimes.jp" + entry.get("url", "")
            company = entry.get("company", "")
            updated_at = entry.get("updated_at", "")
            release_comple_date = entry.get("release_comple_date", "")
            press_release = PressRelease(id, title, url, company, updated_at, release_comple_date)

            pr_list.append(press_release)
        return pr_list
    else:
        print(f"Error fetching data from API. Status code: {response.status_code}")
        return []
