#%%
import scrapy
from scrapy.crawler import CrawlerProcess

import os
import requests
import json

import numpy as np

from dotenv import load_dotenv
load_dotenv("/home/ricmartin/projekt/fhack/module_scraper/.env")

#%%
class ModuleSpider(scrapy.Spider):
    name = "mslearn_module"

    def __init__(self, urls):
        super().__init__()
        self.module_urls = urls
        # self.start_requests()

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
        filename = f"{rel_path[1]}.txt"

        print(filename)
        with open(os.path.join("module_data", folder, filename), 'w') as f:
            f.write(str(page_text))
        # Path(os.path.join(folder, filename)).write_bytes(response.body)
        self.log(f"Saved file {filename}")


#%%
response = requests.get("https://learn.microsoft.com/api/catalog/?locale=en-en&type=modules")
content = response.json()
modules = content["modules"]

#%%
module_urls = []
for module in modules[:3]:
    module_urls.append(module["url"])
    
    folder = module["url"].split("/modules/")[1].split('/')[0]
    path = os.path.join("module_data", folder)
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "metadata.json"), 'w') as outfile:
        json.dump(module, outfile)

#%%
process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
process.crawl(ModuleSpider, urls=module_urls)
process.start()

#%%
process.stop()

#%%
from openai import AzureOpenAI
from openai.types import CreateEmbeddingResponse, Embedding

key = os.getenv("OPENAI_API_KEY")
base = os.getenv("OPENAI_API_BASE")
client = AzureOpenAI(api_version="2023-07-01-preview", azure_endpoint=base, api_key=key)

#%%
embedding_model = "text-embedding-model"

def get_embedding(text):

    result = client.embeddings.create(
      model=embedding_model,
      input=text
    )
    # result = np.array(result["data"][0]["embedding"])
    result = result.data[0].embedding
    return result

get_embedding("hej san på dejsan")

#%%

folders = os.listdir("module_data")
folders = [file for file in folders if not '.' in file]
for folder in folders:
    path = os.path.join("module_data", folder)
    files = os.listdir(path)
    files.sort(key=lambda x: x[0])
    files = files[:-1]

    lessons = []
    for filename in files:
        print(filename)
        with open(os.path.join(path, filename), 'r') as doc:
            lessons.append(doc.read())
            os.remove(doc.name)

    with open(os.path.join(path, "metadata.json"), 'r') as metadata:
        data = json.load(metadata)

        data["content"] = str(lessons)
        data["content_vector"] = get_embedding(data["content"])
        
        with open(path+".json", 'w') as outfile:
            json.dump(data, outfile)

        # os.remove(metadata.name)
    # os.removedirs(path)
# %%



