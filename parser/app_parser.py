import json
import os
import shutil
import threading
import requests
from bs4 import BeautifulSoup

DOM = 'https://play.google.com'
HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh;Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, likeGecko)"
                  "Chrome/90.0.4430.93 Safari/537.36"
}


class DataCollector(threading.Thread):

    def __init__(self, url, key_word, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.key_word = key_word
        self.data_list = []

    def run(self):
        req = requests.get(self.url, HEADERS)
        project_name = self.url.split(".")[-1]
        if os.path.exists(f"data/{project_name}"):
            project_name = project_name + str(1)
        with open(f"data/{project_name}.html", "w") as file:
            file.write(req.text)

        with open(f"data/{project_name}.html") as file:
            src = file.read()
        soup = BeautifulSoup(src, "lxml")
        project_data = soup.find("div", class_="JNury Ekdcne")
        try:
            additional_info = project_data.find("div", class_="IxB2fe").find_all("div", class_="hAyfc")
        except Exception:
            additional_info = None
        try:
            project_app_name = project_data.find("h1", class_="AHFaub").find("span").text
        except Exception:
            project_app_name = 'Not found'

        try:
            project_author = project_data.find("span", class_="T32cc UAO9ie").find("a", class_="hrTbp R8zArc").text
        except Exception:
            project_author = 'Not found'

        try:
            project_category = project_data.find_all("span", class_="T32cc UAO9ie")[-1].text
        except Exception:
            project_category = 'Not found'

        try:
            project_description = project_data.find("div", class_="DWPxHb").text
        except Exception:
            project_description = 'Not found'

        try:
            project_average_rating = project_data.find("div", class_="BHMmbe").text
        except Exception:
            project_average_rating = 'Not found'

        try:
            project_total_marks = \
                project_data.find("span", class_="AYi5wd TBRnV").text
        except Exception:
            project_total_marks = 'Not found'

        try:
            project_last_update = \
                additional_info[0].find("div", class_="IQ1z0d").find("span").text
        except Exception:
            project_last_update = 'Not found'

        if project_app_name.lower().find(self.key_word) == -1 \
                and project_description.lower().find(self.key_word) == -1:
            pass
        else:
            self.data_list.append(
                {
                    "Название": project_app_name,
                    "Url страницы приложения": self.url,
                    "Автор": project_author,
                    "Категория": project_category,
                    "Описание": project_description,
                    "Средняя оценка": project_average_rating,
                    "Количество оценок": project_total_marks,
                    "Последнее обновление": project_last_update
                }
            )


class ApplicationStoreParser:

    def __init__(self, key_word):
        self.key_word = key_word
        self.url = f'https://play.google.com/store/search?q={key_word}&c=apps'
        self.project_urls = []
        self.project_data_list = []

    def get_apps_list(self):
        req = requests.get(self.url, HEADERS)

        with open('../app_file.html', 'w') as file:
            file.write(req.text)

        with open('../app_file.html') as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        apps = soup.find_all("div", class_="ImZGtf mpg5gc")

        for app in apps:
            project_url = DOM + app.find("div", class_="wXUyZd").find("a").get("href")
            self.project_urls.append(project_url)

    def write_to_json_file(self):
        with open("../report/report_data.json", "w", encoding="utf-8") as file:
            json.dump(self.project_data_list, file, indent=4, ensure_ascii=False)
            print(f"Saved at {file.name}")

    def write_to_json_str(self):
        print(json.dumps(self.project_data_list, indent=4, ensure_ascii=False))

    def run(self):
        os.mkdir("data")
        if not os.path.exists("../report"):
            os.mkdir("../report")
        self.get_apps_list()
        collectors = []
        for num, project_url in enumerate(self.project_urls):
            collector = DataCollector(project_url, self.key_word)
            collectors.append(collector)
        for collector in collectors:
            collector.start()
        for collector in collectors:
            collector.join()
        for collector in collectors:
            self.project_data_list += collector.data_list
        self.write_to_json_file()
        self.write_to_json_str()
        shutil.rmtree("data")
