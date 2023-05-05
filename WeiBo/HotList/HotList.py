import os
import re
from configparser import ConfigParser
from datetime import datetime

import pandas as pd
from requests_html import HTMLSession


def get_hot_search():
    session = HTMLSession()

    config = ConfigParser()
    config.read(os.path.join(os.getcwd(), "config.ini"), encoding="utf-8")

    sub = config["weibo"]["sub"]

    cookies = f"SUB={sub}"

    url = "https://s.weibo.com/top/summary?cate=realtimehot"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5",
        "dnt": "1",
        "origin": "https://s.weibo.com",
        "referer": "https://s.weibo.com/",
        "sec-ch-ua": "'Chromium';v='112', 'Microsoft Edge';v='112', 'Not:A-Brand';v='99'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "cookie": cookies
    }

    response = session.get(url, headers=headers)

    top_list = response.html.xpath("//*[@id='pl_top_realtimehot']/table/tbody/tr")

    link_list = []
    title_list = []
    hot_index_list = []

    for top in top_list:
        span_tag = top.find("span")
        if not (span_tag and span_tag[0].text):
            continue

        a_tag = top.find("a")[0]

        title_list.append(a_tag.text)
        link_list.append(a_tag.absolute_links.pop())
        hot_index_list.append(re.search(r"\d+", span_tag[0].text).group())

    return {"title": title_list,
            "index": hot_index_list,
            "link": link_list}


def get_hot_search_csv(hot_search: dict, fileName: str = None):
    now = datetime.now()
    timestamp = int(now.timestamp())
    date_and_time = now.strftime("%Y-%m-%d %H:%M:%S")
    date = now.strftime("%Y-%m-%d")

    if not fileName:
        fileName = f"{timestamp}.csv"

    output_folder_path = "output"
    daily_folder_path = os.path.join(output_folder_path, date)

    if not (os.path.exists(daily_folder_path) and os.path.isdir(daily_folder_path)):
        print(f"The folder {daily_folder_path} does not exist, creating the folder.")
        os.makedirs(daily_folder_path)
        print("Folder created successfully.")

    csv_path = os.path.join(daily_folder_path, fileName)

    data_frame = pd.DataFrame(hot_search)
    data_frame.index += 1
    data_frame.to_csv(csv_path, encoding="CP936")

    with open(csv_path, "r+", encoding="CP936") as file:
        content = file.read()
        file.seek(0, 0)
        file.write("date, " + date_and_time + "\n" + content)

    print(f"The hot search list has been saved to {csv_path}.")


if __name__ == "__main__":
    hot_search_dict = get_hot_search()
    get_hot_search_csv(hot_search_dict)
