# %%
### Basic imports ###
import os
import re

from dotenv import load_dotenv

import streamlit as st

# %%
if __name__ == "__main__":

    st.title("Ask MSlearn")

    ### Get secrets for authentication ###

    #from notebookutils.mssparkutils.credentials import getSecret
    #KEYVAULT_ENDPOINT = "https://mslearn-bot.vault.azure.net/"
    load_dotenv()

    # Azure AI Search
    AI_SEARCH_NAME = "mslearn-aisearch"
    AI_SEARCH_ENDPOINT = "https://mslearn-aisearch.search.windows.net"
    AI_SEARCH_INDEX_NAME = "fabrichack-mslearn-index"
    AI_SEARCH_API_KEY = os.getenv("AI_SEARCH_API_KEY")

    # Azure OpenAI
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # %%
    ## Set up connection to Azure OpenAI ###

    from openai import AzureOpenAI

    deployment = "text-summarization-model"
    client = AzureOpenAI(
        base_url=f"{OPENAI_API_BASE}/openai/deployments/{deployment}/extensions",
        api_key=OPENAI_API_KEY,
        api_version="2023-08-01-preview",
    )

    # %%
    ### Set up RAG logic ###

    def prompt_mslearn(search_string: str):
        try:
            completion = client.chat.completions.create(
                model=deployment,
                messages=[
                    {
                        "role": "assistant",
                        "content": "You are a tech support assistant that helps people evaluate different tools and products. You compare different features of the tools in your data sources and make recommendations to the user depending on their needs and interests."
                    },
                    {
                        "role": "user",
                        "content": search_string,
                    },
                ],

                extra_body={
                    "dataSources": [
                        {
                            "type": "AzureCognitiveSearch",
                            "parameters": {
                                "endpoint": AI_SEARCH_ENDPOINT,
                                "key": AI_SEARCH_API_KEY,
                                "indexName": AI_SEARCH_INDEX_NAME,
                                "fieldsMapping": {
                                    "urlField": "url",
                                    "contentFieldsSeparator": "\n",
                                    "contentFields": [
                                        "content"
                                    ],
                                    "titleField": "title",
                                    "urlField": "url",
                                    "vectorFields": [
                                        "content_vector"
                                    ]
                                }
                            }
                        }
                    ]
                }
            )


            return completion
            # .model_dump_json(indent=2)
            # return completion.choices[0].message.content

        except Exception as e:
            print(f"An error occurred: {e}")
            # You can choose to return a default message or handle the error as needed
            return "Sorry, an error occurred while processing your request."

    # %%
    prompt = st.chat_input("Ask me about Microsoft cloud tools and services")
    if prompt:

        example_prompt = "I am a .NET developer interested in building secure solutions for sensitive customers. Which cloud services can i use to make my work more effective and robust against attacks?"

        answer = prompt_mslearn(prompt)

        st.write(answer.choices[0].message.content)

        content = answer.choices[0].message.context["messages"][0]["content"]
        match = re.search(r'https://learn.microsoft.com/en-us/training/modules/', content)
        url = content[match.start():match.end()+80].split('?')[0]
        st.write("More information:", url) # Currently only prints first url


