from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.config import load_config

config = load_config()

def upload_to_youtube(video_path, title, description, tags):
    youtube = build('youtube', 'v3', developerKey=config['youtube_api_key'])
    
    request = youtube.videos().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': 'private'  # 테스트용
            }
        },
        media_body=MediaFileUpload(video_path)
    )
    response = request.execute()
    return response['id']
