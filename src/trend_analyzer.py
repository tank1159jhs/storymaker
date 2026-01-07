from googleapiclient.discovery import build
from src.config import load_config
import re

config = load_config()

def analyze_trends(subscriber_range, view_range, format_type, query):
    print("트렌드 분석 시작...")
    # YouTube API 설정 (일본 전제)
    youtube = build('youtube', 'v3', developerKey=config['youtube_api_key'])
    
    # 범위에 따른 필터 값 설정
    if subscriber_range == "1만-10만":
        min_sub = 10000
        max_sub = 100000
    elif subscriber_range == "10만-50만":
        min_sub = 100000
        max_sub = 500000
    else:  # 50만 이상
        min_sub = 500000
        max_sub = float('inf')
    
    if view_range == "10만 이상":
        min_view = 100000
    elif view_range == "50만 이상":
        min_view = 500000
    else:  # 100만 이상
        min_view = 1000000

    # 검색 쿼리 (사용자 입력)
    print(f"검색 쿼리: {query}")
    search_response = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        regionCode='JP',
        relevanceLanguage='ja',
        maxResults=50  # 더 많은 결과 가져오기
    ).execute()
    
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    print(f"검색 결과 수: {len(video_ids)}개")
    
    # 비디오 상세 정보 가져오기 (한 번에)
    videos_response = youtube.videos().list(
        part='snippet,statistics,contentDetails',
        id=','.join(video_ids)
    ).execute()
    
    filtered_videos = []
    
    for item in videos_response['items']:
        video_id = item['id']
        
        # 채널 정보 가져오기
        channel_id = item['snippet']['channelId']
        channel_response = youtube.channels().list(
            part='statistics',
            id=channel_id
        ).execute()
        
        subscriber_count = int(channel_response['items'][0]['statistics'].get('subscriberCount', 0))
        view_count = int(item['statistics'].get('viewCount', 0))
        
        # Duration 파싱
        duration = item['contentDetails']['duration']
        duration_seconds = 0
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            duration_seconds = hours * 3600 + minutes * 60 + seconds
        
        # 길이 표시 (분:초)
        display_minutes = duration_seconds // 60
        display_seconds = duration_seconds % 60
        duration_display = f"{display_minutes}분 {display_seconds}초"
        
        # 포맷에 따른 필터링
        if format_type == "쇼츠" and duration_seconds > 60:
            continue
        elif format_type == "롱폼" and duration_seconds <= 60:
            continue
        
        # 구독자 수와 조회수 필터링 (수정됨)
        if not (min_sub <= subscriber_count <= max_sub):
            print(f"  - {item['snippet']['title']}: 구독자 수 필터링 ({subscriber_count:,})")
            continue
        if view_count < min_view:
            print(f"  - {item['snippet']['title']}: 조회수 필터링 ({view_count:,})")
            continue
        
        print(f"  ✓ {item['snippet']['title']}: 구독자 {subscriber_count:,}, 조회수 {view_count:,}")
        
        filtered_videos.append({
            'title': item['snippet']['title'],
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'video_id': video_id,
            'summary': item['snippet']['description'][:150],
            'metadata': f'구독자: {subscriber_count:,}, 조회수: {view_count:,}, 길이: {duration_display}'
        })
    
    print(f"필터링 결과 수: {len(filtered_videos)}개")
    return filtered_videos[:10]  # 상위 10개
