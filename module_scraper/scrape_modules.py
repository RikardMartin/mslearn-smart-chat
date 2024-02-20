#%%
import scrapy
from scrapy.crawler import CrawlerProcess

import os
import requests
import json

#%%
response = requests.get("https://learn.microsoft.com/api/catalog/?locale=en-en&type=modules")
content = response.json()
modules = content["modules"]

#%%
module_urls = []
for module in modules[:3]:
    module_urls.append(module["url"])
    
    folder = module["url"].split("/modules/")[1].split('/')[0]
    os.makedirs(os.path.join("module_data", folder), exist_ok=True)

    with open(os.path.join("module_data", folder, "metadata.json"), "w") as outfile: 
        json.dump(module, outfile)

#%%
class ModuleSpider(scrapy.Spider):
    name = "mslearn_module"

    def __init__(self, urls):
        super().__init__()
        self.module_urls = urls

    def start_requests(self):
        for url in self.module_urls:
            yield scrapy.Request(url=url, callback=self.get_module_pages)

    def get_module_pages(self, response):
        url_base = response.url.split("?")[0]

        pages = response.xpath("//ul[@id='unit-list']")[0]
        pages = pages.xpath("//a[@data-linktype='relative-path']")
        for page in pages:
            page_url = url_base + page.xpath("@href").get()
            yield scrapy.Request(url=page_url, callback=self.parse_page)

    def parse_page(self, response):
        page_text = response.xpath("//div[@id='unit-inner-section']//text()").getall()
        page_text = [line for line in page_text if not line.startswith("\n\t")]

        rel_path = response.url.split("/modules/")[1].split('/')
        folder = rel_path[0]
        filename = f"{rel_path[1]}.html"

        with open(os.path.join("module_data", folder, filename), 'w') as f: f.write(str(page_text))
        # Path(os.path.join(folder, filename)).write_bytes(response.body)
        self.log(f"Saved file {filename}")

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(ModuleSpider, urls=module_urls)
process.start()

#%%
process.stop()

# %%
