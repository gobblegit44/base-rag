## Python implementation of RAG equipped to handle singular topic (base_rag.py) 
and another equipped to handle multiple topics (multiQ_rag.py) discussed in the User question.

To run the models, we will use ollama, a command line tool that allows us to run models from Hugging Face. With ollama, you don't need to have access to a server or cloud service to run the models. You can run the models directly on your computer.

For the models, let's use the following:

Embedding model: hf.co/CompendiumLabs/bge-base-en-v1.5-gguf
Language model: hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF

And for the dataset, we will use a simple list of facts about cats and dogs extracted from web/wiki (extract_content.py). Each fact will be considered as a chunk in the indexing phrase.

First, let's start by installing ollama from project's website: ollama.com

After installation, open a terminal and run the following command to download the required models:

ollama pull hf.co/CompendiumLabs/bge-base-en-v1.5-gguf
ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF

If you see the following output, it means the models are successfully downloaded:

pulling manifest /n
... /n
writing manifest /n
success/n

Before continuing, to use ollama in python, let's also install the ollama package:

pip install ollama

Next, create a python script and load the dataset cat-facts.txt or dog-facts into memory. The dataset contains a list of cat/dog facts that will be used as chunks in the indexing phrase.

Now, let's implement the vector database.

We will use the embedding model from ollama to convert each chunk into an embedding vector, then store the chunk and its corresponding vector in a list.

Next, let's implement the retrieval function that takes a query and returns the top N most relevant chunks based on cosine similarity. We can imagine that the higher the cosine similarity between the two vectors, the "closer" they are in the vector space. This means they are more similar in terms of meaning.

In the next step of Generation phrase, the chatbot will generate a response based on the retrieved knowledge from the step above. This is done by simply add the chunks into the prompt that will be taken as input for the chatbot. We then use the ollama to generate the response. 

You can find the final code in base_rag.py and multiQ_rag.py file. 

You can now ask the chatbot questions, and it will generate responses based on the retrieved knowledge from the dataset.

Ask me a question: tell me about cat speed /n
Retrieved chunks: ... /n
Chatbot response: /n
According to the given context, cats can travel at approximately 31 mph (49 km) over a short distance. This is their top speed.
