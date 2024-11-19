import os
from dotenv import load_dotenv
import requests
import tiktoken
from bs4 import BeautifulSoup
from langchain_openai.chat_models.azure import AzureChatOpenAI

# Load variables from .env file
load_dotenv()

# Function to count tokens
def count_tokens(text, model="gpt-4"):
    tokenizer = tiktoken.encoding_for_model(model)
    return len(tokenizer.encode(text))

# Function to extract text from URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            texto = soup.get_text(separator=' ')
            # Clean the text
            lines = (line.strip() for line in texto.splitlines())
            parts = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(part for part in parts if part)
            return clean_text
        else:
            print(f"Failed to fetch the URL. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



# Request to Azure Open AI
client = AzureChatOpenAI(
    azure_endpoint="https://openai-dio-bootcamp-translator.openai.azure.com/",
    api_key=os.getenv("AZURE_API_KEY"),  
    api_version="2024-02-15-preview",
    deployment_name="gpt-4o-mini",
    max_retries=0
)

# Function to translate an article and convert to Markdown
def translate_article(text, lang, max_tokens=500):
    total_tokens = count_tokens(text)
    print(f"Total tokens in input text: {total_tokens}")

    if total_tokens > max_tokens:
        print(f"Text exceeds {max_tokens} tokens.")
        truncated_text = text[:max_tokens]
    else:
        truncated_text = text
    messages = [
        {"role": "system", "content": "Você atua como tradutor de textos"},
        {"role": "user", "content": f"Traduza o seguinte texto para o idioma {lang} e responda em markdown:\n\n{truncated_text}"}
    ]

    try:
        response = client(messages=messages,max_tokens=max_tokens)  
        # Access content based on response structure
        translation = response['choices'][0]['message']['content']
        return translation
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        return None




url = 'https://edition.cnn.com/2024/11/12/tech/ai-deepfake-porn-advice-terms-of-service-wellness/index.html'

text = extract_text_from_url(url)
if text:
    article = translate_article(text, "pt-br", max_tokens=500)  
    print(article)

