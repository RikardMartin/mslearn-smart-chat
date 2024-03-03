## RAG-learn
This is the repo for our contribution to the Microsoft Fabric community AI hack competition.
The authors are Pankaj Mandania, Richard Martin, Mårten Sjö.

## Introduction
Our idea for this competition was to provide an interactive chat-interface to the articles on [mslearn](https://learn.microsoft.com). The mslearn database is a vast resource with information on many different Microsoft products and tools. It is navigable through tags and collections like *modules* and *learning paths*, but it can still be tricky to find just the article you need in a particular situation since they overlap on certain topics. We wanted to make it easier to filter through the modules in the mslearn library, and we wanted to extend the functionality from just finding and reading up on certain topics, to being able to automatically find **all** modules related to some topic, so that it's easier to compare the different tools, products and methods. We do this by creating an interactive chat-like experience where you explain your problem/situation to an AI and get recommendations based on the knowledge in mslearn.
Examples of use-cases:
* Post your resume to get suggestions of tools and products that you might be interested in
* Describe a workflow and get suggestions for tools and products that might help you get the work done

## Implementation
### 1. ETL
We utilized the open [API](https://learn.microsoft.com/en-us/training/support/catalog-api) to Microsoft learn to collect metadata about all the available modules. With this metadata we then crawled the [mslearn website](https://learn.microsoft.com) and downloaded the text content of each module. We note that a more sophisticated approach would be to download the structured markdown content along with figures, but that was not possible within the time frame of this project.
The code for this was done in Fabric notebooks in our project workspace. The data was stored as files in a lakehouse.

### 2. Indexing
We then set up a search index in Azure AI Search. For this implementation we choose a few categorical fields and a few text fields. We note that this index can be further refined in the future to allow better search results, but again, it was not feasible within the time frame. Furthermore we calculated a vector field with embeddings of the text content in the modules and added to the index. This was done with Azure OpenAI ada-002.
The code for this step was also a Fabric notebook. Reading data from our lakehouse and pushing it to our Azure AI Search resource.

### 3. Chat interface with Retrieval Augmented Generation (RAG)
The final step was to connect our smart database (with our Azure AI Search index) to a chat GPT-like interface where the user could ask questions.
