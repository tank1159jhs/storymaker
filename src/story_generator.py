# filepath: /Users/systemi/storymaker/src/story_generator.py
from transformers import pipeline
from src.config import load_config
from googleapiclient.discovery import build

config = load_config()

def generate_story(videos, format_type):
    # 요약 모델 추가하여 제대로 된 요약 생성
    combined_summary = " ".join([v['summary'] for v in videos])
    
    # 요약 모델 사용
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    summarized_text = summarizer(combined_summary, max_length=300, min_length=50, do_sample=False)[0]['summary_text']
    
    # 스토리 생성 (간단 프롬프트) - 영어로 변경하여 GPT-2 호환성 개선
    if format_type == "롱폼":
        length = 500  # 단어 수
        prompt = f"Based on the following summary about senior citizens' memories, write a completely new touching senior memory story in Japanese context. Structure: introduction, development, climax, conclusion, {length} words: {summarized_text}"
    else:  # 쇼츠
        length = 100
        prompt = f"Based on the following summary about senior citizens' memories, create a touching one-sentence summary of a senior memory in Japanese style: {summarized_text}"
    
    # AI 생성 (임시: Hugging Face 텍스트 생성 모델 사용)
    generator = pipeline("text-generation", model="gpt2")  # 무료 모델
    story = generator(prompt, max_length=length, num_return_sequences=1)[0]['generated_text']
    
    return story

def generate_script(video):
    # 선택한 동영상의 요약을 영어로 요약
    summary = video['summary']
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    try:
        english_summary = summarizer(summary, max_length=100, min_length=20, do_sample=False)[0]['summary_text']
    except:
        english_summary = summary  # 요약 실패 시 원본 사용
    
    # 키워드 추출 (영어 요약에서)
    keywords = " ".join(english_summary.split()[:10])
    
    # 대본 생성 프롬프트 - 챕터를 명시적으로 생성하도록
    prompt = f"Based on the keywords '{keywords}', create a new touching real-life story about senior citizens' memories. Write it as exactly 8 chapters, each formatted as 'Chapter X: [short text]'. Suitable for a 3-minute narration script (about 500 words total)."
    
    # AI 생성 - 더 강력한 모델 사용
    generator = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")  # 더 강력한 무료 모델
    full_script = generator(prompt, max_length=700, num_return_sequences=1, do_sample=True, temperature=0.7)[0]['generated_text']
    
    # 챕터 분리 - "Chapter X:" 패턴으로
    import re
    chapter_pattern = r"Chapter (\d+): (.+?)(?=Chapter \d+:|$)"
    matches = re.findall(chapter_pattern, full_script, re.DOTALL)
    chapters = [match[1].strip() for match in matches]
    
    # 부족한 챕터 채우기 또는 재분배
    if len(chapters) < 8:
        # 텍스트를 단어로 나누어 8개로 분배
        words = full_script.split()
        chunk_size = len(words) // 8
        chapters = [" ".join(words[i*chunk_size:(i+1)*chunk_size]) for i in range(8)]
    
    return chapters[:8]

def generate_draft(video):
    # 동영상 설명과 코멘트 가져오기
    summary = video['summary']
    video_id = video['url'].split('v=')[1]
    youtube = build('youtube', 'v3', developerKey=config['youtube_api_key'])
    
    # 코멘트 가져오기 (최대 5개)
    comments = []
    try:
        comment_request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=5
        )
        comment_response = comment_request.execute()
        for item in comment_response['items']:
            comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
    except:
        comments = ["코멘트 없음"]
    
    # 요약 모델 대신 API 데이터를 직접 결합하여 초안 생성
    draft = f"제목: {video['title']}\n\n설명: {summary}\n\n코멘트:\n" + "\n".join([f"- {comment}" for comment in comments])
    
    return draft[:500]  # 500자 제한

def generate_final_script(draft_text):
    # 수정된 초안을 기반으로 챕터 대본 생성
    prompt = f"このドラフトストーリーに基づいて、シニア市民の思い出についての感動的な実話を新しく作成してください。ちょうど8つのチャプターに構造化し、各チャプターは約100文字、合計約800文字。'Chapter X: [text]'として書いてください。: {draft_text}"
    
    generator = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")
    full_script = generator(prompt, max_length=900, num_return_sequences=1, do_sample=True, temperature=0.7)[0]['generated_text']
    
    # 챕터 분리
    import re
    chapter_pattern = r"Chapter (\d+): (.+?)(?=Chapter \d+:|$)"
    matches = re.findall(chapter_pattern, full_script, re.DOTALL)
    chapters = [match[1].strip() for match in matches]
    
    # 각 챕터 100자 정도로 조정
    chapters = [chapter[:100] for chapter in chapters]
    
    # 부족 시 채우기
    while len(chapters) < 8:
        chapters.append("追加 챕터 내용")
    
    return chapters[:8]
