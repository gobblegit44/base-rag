import ollama

# Load the dataset

dataset = []
with open('dog-facts.txt', 'r') as file:
  dataset = file.readlines()
  print(f'Loaded {len(dataset)} entries')

# Implement the retrieval system

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

# Each element in the VECTOR_DB will be a tuple (chunk, embedding)
# The embedding is a list of floats, for example: [0.1, 0.04, -0.34, 0.21, ...]
VECTOR_DB = []

def add_chunk_to_database(chunk):
  embedding = ollama.embed(model=EMBEDDING_MODEL, input=chunk)['embeddings'][0]
  VECTOR_DB.append((chunk, embedding))

for i, chunk in enumerate(dataset):
  add_chunk_to_database(chunk)
  print(f'Added chunk {i+1}/{len(dataset)} to the database')

def cosine_similarity(a, b):
  dot_product = sum([x * y for x, y in zip(a, b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)

def retrieve(query, top_n=3):
  query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
  # temporary list to store (chunk, similarity) pairs
  similarities = []
  for chunk, embedding in VECTOR_DB:
    similarity = cosine_similarity(query_embedding, embedding)
    similarities.append((chunk, similarity))
  # sort by similarity in descending order, because higher similarity means more relevant chunks
  similarities.sort(key=lambda x: x[1], reverse=True)
  # finally, return the top N most relevant chunks
  return similarities[:top_n]


# Chatbot

input_query = input('Ask me a question: ')

# First, have the model identify distinct topics and generate search queries for each
topic_identification_prompt = '''You are a helpful assistant. Based on the user's question, identify the distinct topics/aspects that need to be addressed and generate a separate search query for each one. Format your response as a list of search queries, one per line. Only output the search queries, nothing else.'''

query_response = ollama.chat(
  model=LANGUAGE_MODEL,
  messages=[
    {'role': 'system', 'content': topic_identification_prompt},
    {'role': 'user', 'content': input_query},
  ]
)
search_queries = query_response['message']['content'].strip().split('\n')
print('\nGenerated search queries:')
for query in search_queries:
    print(f' - {query}')

# Retrieve knowledge for each search query
all_retrieved_knowledge = []
for query in search_queries:
    retrieved = retrieve(query)
    all_retrieved_knowledge.extend(retrieved)

# Remove duplicates while preserving order
seen = set()
unique_retrieved_knowledge = []
for chunk, similarity in all_retrieved_knowledge:
    if chunk not in seen:
        seen.add(chunk)
        unique_retrieved_knowledge.append((chunk, similarity))

print('\nRetrieved knowledge:')
for chunk, similarity in unique_retrieved_knowledge:
    print(f' - (similarity: {similarity:.2f}) {chunk}')

instruction_prompt = f'''You are a helpful chatbot.
Use only the following pieces of context to answer the question. Make sure to address all aspects of the question. Don't make up any new information:
{'\n'.join([f' - {chunk}' for chunk, similarity in unique_retrieved_knowledge])}
'''

stream = ollama.chat(
  model=LANGUAGE_MODEL,
  messages=[
    {'role': 'system', 'content': instruction_prompt},
    {'role': 'user', 'content': input_query},
  ],
  stream=True,
)

# print the response from the chatbot in real-time
print('\nChatbot response:')
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
