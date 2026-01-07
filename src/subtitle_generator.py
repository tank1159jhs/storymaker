import srt
from datetime import timedelta

def generate_subtitles(story, audio_duration):
    # 간단 자막 생성 (텍스트를 문장 단위로 분할)
    sentences = story.split('. ')
    subs = []
    start_time = timedelta(seconds=0)
    duration_per_sentence = audio_duration / len(sentences)
    
    for i, sentence in enumerate(sentences):
        end_time = start_time + timedelta(seconds=duration_per_sentence)
        sub = srt.Subtitle(index=i+1, start=start_time, end=end_time, content=sentence)
        subs.append(sub)
        start_time = end_time
    
    output_path = "/Users/systemi/storymaker/output/subtitles.srt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt.compose(subs))
    return output_path
