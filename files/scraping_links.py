from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import json
import time
import asyncio
import os
import logging

url = "https://cse.lk/pages/financial-reports/financial-reports.component.html"

def get_links_in_titles(url, blob_name):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=50)
            page = browser.new_page()
            page.goto(url)
            time.sleep(100)

            link_locators = page.locator("div.financial-reports-block").locator("ul").locator("li").all()
            # .get_by_role("table").get_by_role("tbody").get_by_role("tr").all()

            for lc in link_locators:
                report_name = lc.locator("div.rules-block").locator("div.col-lg-8").locator("div.rule").inner_text()
                if blob_name.split(".")[0] in report_name.lower():
                    report_url = lc.locator("div.rules-block").locator("div.col-lg-3").locator("a").get_attribute("href")
                    
                    print(report_url)
                # else:
                #     logging.warning(f"No valid PDF reports found.")

        return "Annual reports uploaded to Azure Blob Storage."
                    
user_input = input("Enter the text: ")                    
get_links_in_titles(url, user_input)                  