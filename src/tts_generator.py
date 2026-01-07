import re
import os
import asyncio
from gtts import gTTS
from deep_translator import GoogleTranslator

# Edge TTS 임포트
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("⚠️ Edge TTS 없음: pip install edge-tts")

def detect_language(text):
    """텍스트의 언어를 더 정확하게 감지 (한글, 일본어, 영어)"""
    # 한글 체크
    if re.search(r'[가-힣]', text):
        print("[detect_language] Detected: ko (한글)")
        return 'ko'
    # 일본어 체크 (히라가나, 카타카나, 한자)
    elif re.search(r'[ぁ-んァ-ン]', text):
        print("[detect_language] Detected: ja (히라가나/카타카나)")
        return 'ja'
    elif re.search(r'[一-龯々〆〤]', text):  # 일본어 한자 범위
        print("[detect_language] Detected: ja (한자)")
        return 'ja'
    # 영어 (기본값)
    elif re.search(r'[a-zA-Z]', text):
        print("[detect_language] Detected: en (영어)")
        return 'en'
    # 혼합/기타: 가장 많은 문자의 언어로 추정
    else:
        counts = {
            'ko': len(re.findall(r'[가-힣]', text)),
            'ja': len(re.findall(r'[ぁ-んァ-ン一-龯々〆〤]', text)),
            'en': len(re.findall(r'[a-zA-Z]', text)),
        }
        detected = max(counts, key=counts.get)
        print(f"[detect_language] Fallback detected: {detected} (counts: {counts})")
        return detected

def enhance_text_with_emotion(text):
    """텍스트를 자연스럽게 정리 (SSML 없이)
    
    Edge TTS는 기본적으로 SSML을 지원하지 않으므로,
    텍스트만 깔끔하게 정리하고 음성 파라미터로 감정 조절
    """
    # 특수 기호나 불필요한 공백 정리
    text = re.sub(r'\s+', ' ', text)  # 여러 공백을 하나로
    text = text.strip()
    
    # 읽기 어려운 기호 제거
    text = text.replace('⸻', '')
    text = text.replace('---', '')
    text = text.replace('🎬', '')
    
    # 구두점 정리 (자연스러운 휴지를 위해)
    text = text.replace('...', '…')
    text = text.replace('..', '…')
    
    return text

def translate_text(text, target_lang):
    """텍스트를 목표 언어로 번역"""
    source_lang = detect_language(text)
    
    if source_lang == target_lang:
        return text
    
    print(f"  🔄 자동 번역: {source_lang} → {target_lang}")
    
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"  ⚠️ 번역 실패: {e}")
        return text

async def generate_tts_edge(text, output_path, language='ja', voice=None, rate='+0%', pitch='+0Hz', volume='+0%'):
    """Edge TTS로 음성 생성 (무료, 고품질, 커스터마이징 가능)
    
    Args:
        text: 읽을 텍스트
        output_path: 저장 경로
        language: 언어 코드 ('ja', 'ko', 'en')
        voice: 음성 이름 (None이면 기본값 사용)
        rate: 말하기 속도 ('-50%' ~ '+100%')
        pitch: 음높이 ('-20Hz' ~ '+20Hz')
        volume: 볼륨 ('-50%' ~ '+50%')
    """
    # 언어별 기본 음성 (라디오 DJ 스타일 - 자연스럽고 친근함)
    default_voices = {
        'ja': 'ja-JP-KeitaNeural',      # 일본어 남성 (차분하고 깊이 있음)
        'ko': 'ko-KR-GookMinNeural',    # 한국어 남성 (캐주얼하고 편안함) ⭐ 변경
        'en': 'en-US-GuyNeural'         # 영어 남성 (따뜻하고 신뢰감 있음)
    }
    
    # 음성 선택 (직접 지정 또는 기본값)
    selected_voice = voice if voice else default_voices.get(language, default_voices['en'])
    
    # SSML로 감정 표현 강화
    text = enhance_text_with_emotion(text)
    
    # Edge TTS Communicate 객체 생성
    communicate = edge_tts.Communicate(
        text=text,
        voice=selected_voice,
        rate=rate,
        pitch=pitch,
        volume=volume
    )
    
    await communicate.save(output_path)

def generate_tts_gtts(text, output_path, language='ja'):
    """gTTS로 음성 생성 (폴백용)"""
    tts = gTTS(text, lang=language, slow=False)
    tts.save(output_path)

def generate_single_tts(text, output_path, language='ja', voice=None, rate='+0%', pitch='+0Hz', volume='+0%'):
    """단일 텍스트를 TTS로 변환 (Edge TTS 우선, gTTS 폴백)
    
    Args:
        text: 읽을 텍스트
        output_path: 저장 경로
        language: 언어 코드 ('ja', 'ko', 'en')
        voice: 음성 이름 (None이면 기본값)
        rate: 말하기 속도
        pitch: 음높이
        volume: 볼륨
    """
    
    # 1순위: Edge TTS (무료, 고품질)
    if EDGE_TTS_AVAILABLE:
        try:
            asyncio.run(generate_tts_edge(text, output_path, language, voice, rate, pitch, volume))
            return True
        except Exception as e:
            print(f"    ⚠️ Edge TTS 실패: {e}")
    
    # 2순위: gTTS (폴백)
    try:
        generate_tts_gtts(text, output_path, language)
        return True
    except Exception as e:
        print(f"    ⚠️ gTTS 실패: {e}")
        return False

def generate_tts_with_timestamps(script, scene_num, language='ja', auto_translate=True, voice=None, rate='-15%', pitch='-8Hz', volume='+0%', output_dir='output'):
    """타임스탬프 포함 대본에서 나레이션 생성 및 타이밍 추출
    
    라디오 DJ 스타일 - 인간미 있고 자연스러운 톤
    
    Args:
        script: 대본 텍스트 (타임스탬프 포함/미포함 모두 가능)
        scene_num: 씬 번호
        language: TTS 언어 ('ja', 'ko', 'en' 등)
        auto_translate: 자동 번역 활성화 여부 (기본값: True)
        voice: 음성 이름 (None이면 기본값)
        rate: 말하기 속도 (기본값: -15% - 더 느리게, 자연스럽게) ⭐ 변경
        pitch: 음높이 (기본값: -8Hz - 더 낮게, 깊이감) ⭐ 변경
        volume: 볼륨 (기본값: +0% - 자연스러운 볼륨)
        output_dir: 출력 디렉토리 (기본값: 'output')
    """
    print(f"[TTS DEBUG] generate_tts_with_timestamps 파라미터:")
    print(f"  language: {language}")
    print(f"  voice: {voice}")
    print(f"  rate: {rate}")
    print(f"  pitch: {pitch}")
    print(f"  volume: {volume}")
    print(f"  output_dir: {output_dir}")
    print(f"  script(앞 100자): {script[:100]}")
    print(f"  auto_translate: {auto_translate}")
    
    lines = script.strip().split('\n')
    text_segments = []  # 실제 읽을 텍스트만 저장
    
    lang_names = {'ja': '일본어', 'ko': '한국어', 'en': '영어'}
    lang_name = lang_names.get(language, language)
    
    print(f"\n🎤 나레이션 생성 - 씬 {scene_num} ({lang_name})")
    print(f"📁 출력 폴더: {output_dir}")
    
    # 디버그: 대본을 파일로 저장
    os.makedirs(output_dir, exist_ok=True)
    debug_path = f'{output_dir}/debug_script_scene_{scene_num}.txt'
    with open(debug_path, 'w', encoding='utf-8') as f:
        f.write(script)
    print(f"📝 디버그: 대본 저장 → {debug_path}")
    
    # 타임스탬프와 구분선 제거하고 실제 텍스트만 추출
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 타임스탬프 라인은 건너뛰기
        if re.match(r'^\[\d+:\d+\]$', line):
            continue
        
        # 구분선 건너뛰기
        if line.startswith('⸻') or line.startswith('---') or line.startswith('🎬'):
            continue
        
        # 타임스탬프가 포함된 라인에서 텍스트만 추출
        timestamp_match = re.match(r'\[(\d+):(\d+)\]\s*(.+)', line)
        if timestamp_match:
            text = timestamp_match.group(3).strip()
            if text:
                text_segments.append(text)
        else:
            # 일반 텍스트 라인
            if line and not line.startswith('('):  # 괄호로 시작하는 설명 제외
                text_segments.append(line)
    
    if not text_segments:
        raise ValueError(f"씬 {scene_num}에 읽을 텍스트가 없습니다. 대본을 확인해주세요.")
    
    print(f"📊 총 {len(text_segments)}개 문장 추출")
    
    # 자동 번역 적용 (개별 문장별로)
    if auto_translate:
        original_lang = detect_language(' '.join(text_segments[:3]))  # 처음 3문장으로 언어 감지
        print(f"🌍 감지된 원본 언어: {original_lang}, 목표 언어: {language}")
        
        if original_lang != language:
            print(f"🔄 자동 번역 시작: {original_lang} → {language}")
            translated_segments = []
            for i, text in enumerate(text_segments):
                translated = translate_text(text, language)
                translated_segments.append(translated)
                if i < 3:  # 처음 3개만 출력
                    print(f"  ✓ [{i+1}] {text[:30]}... → {translated[:30]}...")
            text_segments = translated_segments
            print(f"✅ 전체 {len(text_segments)}개 문장 번역 완료")
        else:
            print(f"✓ 언어 일치 - 번역 불필요")
    
    # ===== 각 문장을 개별 TTS 생성 후 합치기 (정확한 타이밍) =====
    voice_desc = voice if voice else f"기본 {language} 음성"
    print(f"\n🎙️ Edge TTS로 고품질 나레이션 생성 중...")
    print(f"   음성: {voice_desc}")
    print(f"   속도: {rate}, 음높이: {pitch}, 볼륨: {volume}")
    
    audio_segments = []
    timings = []
    current_time = 0.0
    
    temp_dir = f'{output_dir}/temp_scene_{scene_num}'
    os.makedirs(temp_dir, exist_ok=True)
    
    from moviepy import AudioFileClip, concatenate_audioclips
    
    for i, text in enumerate(text_segments):
        print(f"[TTS DEBUG] Edge TTS 요청 {i+1}/{len(text_segments)}:")
        print(f"  text: {text[:80]}")
        print(f"  language: {language}")
        print(f"  voice: {voice}")
        print(f"  rate: {rate}")
        print(f"  pitch: {pitch}")
        print(f"  volume: {volume}")
        
        try:
            # 개별 문장 TTS 생성 (Edge TTS → gTTS 폴백)
            temp_audio_path = f'{temp_dir}/segment_{i}.mp3'
            
            print(f"  [{i+1}/{len(text_segments)}] {text[:40]}...")
            
            # TTS 생성 (음성 옵션 적용)
            if not generate_single_tts(text, temp_audio_path, language, voice, rate, pitch, volume):
                print(f"    ⚠️ TTS 생성 실패, 건너뜀")
                continue
            
            # 실제 오디오 길이 측정
            audio_clip = AudioFileClip(temp_audio_path)
            segment_duration = audio_clip.duration
            
            # ✅ 타이밍 정확도 개선: 실제 오디오 길이 그대로 사용
            timings.append({
                'time': current_time,
                'text': text
            })
            
            audio_segments.append(audio_clip)
            
            print(f"  ✓ [{i+1}/{len(text_segments)}] {current_time:.2f}초 ({segment_duration:.2f}초) - {text[:40]}...")
            
            current_time += segment_duration
            
            # ✅ 호흡 시간 제거 - 싱크 문제 해결
            # 문장 사이 쉼은 TTS 자체에서 자연스럽게 처리됨
            
        except Exception as e:
            print(f"  ⚠️ 문장 {i+1} TTS 생성 실패: {e}")
            # 실패한 경우 평균 길이로 추정 (3초)
            timings.append({
                'time': current_time,
                'text': text
            })
            current_time += 3.0
    
    # 모든 오디오 세그먼트 합치기
    print(f"\n🔗 {len(audio_segments)}개 오디오 세그먼트 합치는 중...")
    
    # 🎭 호흡은 타이밍 계산에만 반영 (실제 무음 추가는 복잡하므로 생략)
    # 대신 문장 사이 시간 간격으로 자연스러움 표현
    final_audio = concatenate_audioclips(audio_segments)
    
    audio_path = f'{output_dir}/narration_scene_{scene_num}_{language}.mp3'
    final_audio.write_audiofile(audio_path, logger=None)
    
    # 리소스 정리
    for clip in audio_segments:
        clip.close()
    final_audio.close()
    
    # 임시 파일 삭제
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"✅ 나레이션 저장 완료: {audio_path}")
    print(f"⏱️ 총 오디오 길이: {current_time:.2f}초")
    print(f"📊 자막 개수: {len(timings)}개")
    
    # 타이밍 정보 출력
    print(f"\n📍 정확한 자막 타이밍:")
    for i, timing in enumerate(timings[:5]):  # 처음 5개만 출력
        print(f"  {i+1}. {timing['time']:.2f}초 - {timing['text'][:40]}...")
    if len(timings) > 5:
        print(f"  ... 외 {len(timings)-5}개")
    
    # 최종 사용된 스크립트 (문장 합치기)
    final_script = '\n'.join(text_segments)
    return audio_path, timings, final_script
