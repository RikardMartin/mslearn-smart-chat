#%%
import requests
import json

#%%
response = requests.get("https://learn.microsoft.com/api/catalog/")
content = response.json()

#%%
content.keys()
#%%
len(content["modules"])

#%%
modules = content["modules"]
modules[0].keys()
# %%
url = modules[0]["url"]

#%%
url
        



# %%
