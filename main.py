from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import pyperclip
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import os
import json

json_file_path = 'seo_results.json'

if not os.path.exists(json_file_path):
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump([], file)

def update_json_file(response_data, json_file_path):
    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = []

        data.append(response_data)

        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print("An error occurred while updating JSON file:", str(e))

class SEO:
    def __init__(self, extension_path):
        try:
            self.windows = {}
            self.extension_path = extension_path
            self.options = Options()
            self.options.add_argument('--disable-gpu')
            self.options.add_argument("--window-size=1280,720")
            self.options.add_argument('--no-sandbox')
            self.options.add_argument('--disable-dev-shm-usage')
            self.options.add_argument('--disable-translate')
            self.options.add_argument("--lang=de")
            self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
            self.options.add_experimental_option('useAutomationExtension', False)
            self.options.add_extension(self.extension_path)

            self.driver = webdriver.Chrome(options=self.options)
            self.wait = WebDriverWait(self.driver, 30, 1)
            self.driver.get("https://www.google.com")

            window_handles = self.driver.window_handles
            self.driver.switch_to.window(window_handles[0])

            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, f'// *[ @ id = "SIvCob"] / a[1]'))).click()

            input_search = self.wait.until(EC.presence_of_element_located((By.XPATH, f'// *[ @ id = "APjFqb"]')))
            input_search.send_keys("chat gpt")
            input_search.send_keys(Keys.ENTER)

        except Exception as e:
            print("An error occurred during initialization:", str(e))
            raise

    def run_search(self, search_query):
        try:
            print("Running search for", search_query)
            input_search = self.wait.until(EC.presence_of_element_located((By.XPATH, f'// *[ @ id = "APjFqb"]')))
            input_search.send_keys(search_query)
            input_search.send_keys(Keys.ENTER)

            time.sleep(3)

            input_search2 = self.wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="APjFqb"]')))
            input_search2.clear()
            input_search2.send_keys("search_query")
            input_search2.send_keys(Keys.ENTER)

            self.wait.until(EC.presence_of_element_located((By.XPATH,f'//*[@id="__ah__serp-side-panel__wrapper"]/div/div[2]/div/div[1]/div[2]/div[1]/button'))).click()
            time.sleep(1)
            keywords_ideas = pyperclip.paste()
            time.sleep(1)

            self.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 f'// *[ @ id = "__ah__serp-side-panel__wrapper"] / div / div[2] / div / div[1] / div[1] / div[2]'))).click()
            time.sleep(1)
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 f'//*[@id="__ah__serp-side-panel__wrapper"]/div/div[2]/div/div[1]/div[2]/div[1]/button'))).click()
            time.sleep(1)
            people_also_ask = pyperclip.paste()
            if "?" not in people_also_ask:
                people_also_ask = None

            return keywords_ideas, people_also_ask
        except Exception as e:
            print("An error occurred during search:", str(e))
            return None, None

    def close_driver(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print("An error occurred while closing the driver:", str(e))

# Wrap the main execution in a try-except block to handle exceptions
try:
    extension_path = "Ahrefs-SEO-Toolbar-On-Page-and-SERP-Tools.crx"
    df = pd.read_csv("slugs.csv")
    slugs = df["slug"].tolist()
    toolNames = df["toolName"].tolist()
    SEO_instance = SEO(extension_path)
    SEO_instance.wait.until(EC.presence_of_element_located((By.XPATH, f'// *[ @ id = "APjFqb"]')))

    for idx, slug in enumerate(slugs[:]):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                json_slugs = [item["slug"] for item in data]
                if slug in json_slugs:
                    print(f"{slug} was crawled!")
                    continue

            toolName = toolNames[idx]
            response_data = {"slug": slug, "toolName": toolName}
            search_queries_list = [f"{toolName}", f"{toolName} review", f"what is {toolName}?", f"how to use {toolName}?"]

            for idx, base_keyword in enumerate(search_queries_list):
                print(base_keyword)
                input_search = SEO_instance.wait.until(EC.presence_of_element_located((By.XPATH, f'// *[ @ id = "APjFqb"]')))
                input_search.clear()
                input_search.send_keys(base_keyword)
                input_search.send_keys(Keys.ENTER)

                SEO_instance.wait.until(EC.presence_of_element_located(
                    (By.XPATH, f'//*[@id="__ah__serp-side-panel__wrapper"]/div/div[2]/div/div[1]/div[2]/div[1]/button'))).click()
                keywords_ideas = pyperclip.paste()

                SEO_instance.wait.until(EC.presence_of_element_located(
                    (By.XPATH,f'// *[ @ id = "__ah__serp-side-panel__wrapper"] / div / div[2] / div / div[1] / div[1] / div[2]'))).click()
                SEO_instance.wait.until(EC.presence_of_element_located(
                    (By.XPATH,f'//*[@id="__ah__serp-side-panel__wrapper"]/div/div[2]/div/div[1]/div[2]/div[1]/button'))).click()
                people_also_ask = pyperclip.paste()
                if "?" not in people_also_ask:
                    people_also_ask = None

                response_data[f"search_query_{idx}"] = {"keywords_ideas": keywords_ideas, "people_also_ask": people_also_ask}

            update_json_file(response_data, json_file_path)

        except Exception as e:
            print(f"An error occurred for slug {slug}:", str(e))

finally:
    SEO_instance.close_driver()
