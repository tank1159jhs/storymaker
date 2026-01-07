import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    return {
        'youtube_api_key': os.getenv('YOUTUBE_API_KEY'),
        'huggingface_token': os.getenv('HUGGINGFACE_TOKEN'),
        'openai_api_key': os.getenv('OPENAI_API_KEY')  # 선택
    }
