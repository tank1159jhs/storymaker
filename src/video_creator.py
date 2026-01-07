# MoviePy 2.x: moviepy 패키지에서 직접 import
from moviepy import (
    VideoFileClip,
    ImageClip,
    TextClip,
    AudioFileClip,
    ColorClip,  # 배경용 추가
    concatenate_videoclips,
    concatenate_audioclips,  # 배경음악용 추가
    CompositeVideoClip,
    CompositeAudioClip  # 배경음악용 추가
)
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_subtitle_image(text, font_path, font_size, max_width, 
                          text_color=(255, 255, 255), 
                          stroke_color=(0, 0, 0),
                          stroke_width=3,
                          padding=20):
    """
    PIL로 자막 이미지 생성 (ImageMagick 우회, 글자 잘림 없음)
    
    Args:
        text: 자막 텍스트
        font_path: 폰트 파일 경로
        font_size: 폰트 크기
        max_width: 최대 너비 (자동 줄바꿈)
        text_color: 텍스트 색상 (R, G, B)
        stroke_color: 테두리 색상 (R, G, B)
        stroke_width: 테두리 두께
        padding: 텍스트 주변 여백
    
    Returns:
        numpy array (RGBA 이미지)
    """
    # 폰트 로드
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
    
    # 텍스트 줄바꿈 처리
    dummy_img = Image.new('RGBA', (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    
    words = list(text)  # 일본어/한국어는 글자 단위로 분리
    lines = []
    current_line = ""
    
    for char in text:
        test_line = current_line + char
        bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width - padding * 2:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char
    if current_line:
        lines.append(current_line)
    
    # 전체 텍스트 크기 계산
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = dummy_draw.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    
    total_height = sum(line_heights) + (len(lines) - 1) * 10  # 줄 간격 10px
    max_line_width = max(line_widths) if line_widths else 100
    
    # 이미지 크기 (패딩 + 테두리 두께 포함)
    # stroke가 양쪽으로 확장되므로 충분한 여백 확보
    img_width = max_line_width + padding * 2 + stroke_width * 4
    img_height = total_height + padding * 2 + stroke_width * 4
    
    # 이미지 생성 (RGBA - 완전 투명 배경)
    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 텍스트 그리기 (테두리 + 본문)
    # stroke가 글자 주변으로 확장되므로 여백을 충분히 확보
    y_offset = padding + stroke_width + 5  # 추가 여백 5px
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x_offset = (img_width - line_width) // 2  # 중앙 정렬
        
        # 테두리 효과 (stroke_width 사용)
        draw.text((x_offset, y_offset), line, font=font, fill=text_color,
                  stroke_width=stroke_width, stroke_fill=stroke_color)
        
        y_offset += line_heights[i] + 10
    
    # numpy 배열로 변환
    return np.array(img)

def add_background_music(video_clip, music_path, volume=0.15):
    """배경음악 추가 (나레이션보다 작은 볼륨)"""
    if not music_path or not os.path.exists(music_path):
        return video_clip
    
    try:
        print(f"🎵 배경음악 추가 중: {os.path.basename(music_path)}")
        narration = video_clip.audio
        music = AudioFileClip(music_path).with_volume_scaled(volume)
        
        # 음악을 비디오 길이에 맞춤 (루프 또는 자르기)
        if music.duration < video_clip.duration:
            repeats = int(video_clip.duration / music.duration) + 1
            music = concatenate_audioclips([music] * repeats)
        
        music = music.subclipped(0, video_clip.duration)
        composite_audio = CompositeAudioClip([narration, music])
        result = video_clip.with_audio(composite_audio)
        print(f"✅ 배경음악 추가 완료")
        return result
    
    except Exception as e:
        print(f"❌ 배경음악 추가 실패: {e}")
        return video_clip

def create_video(images, audio_path, subtitle_path, format_type):
    if format_type == "롱폼":
        # 이미지 슬라이드 + 오디오 + 자막 (MoviePy 2.x)
        clips = []
        for img in images:
            clip = ImageClip(img, duration=10)  # 10초 per 이미지
            clips.append(clip)
        video = concatenate_videoclips(clips)
        audio = AudioFileClip(audio_path)
        video = video.with_audio(audio)
        # 자막 추가 (간단)
        txt_clip = TextClip(text="자막 예시", font_size=70, color='white', duration=video.duration)
        txt_clip = txt_clip.with_position('bottom')
        video = CompositeVideoClip([video, txt_clip])
    else:  # 쇼츠
        # 1-2 이미지 + 오디오 요약
        clip = ImageClip(images[0], duration=30)
        # MoviePy 2.x: with_subclip -> subclipped
        audio = AudioFileClip(audio_path).subclipped(0, 30)
        video = clip.with_audio(audio)
    
    output_path = "/Users/systemi/storymaker/output/video.mp4"
    video.write_videofile(output_path, fps=24)
    return output_path

def merge_scenes_to_video(scenes, narrations, all_images, output_dir='output', subtitle_settings=None):
    """씬별 동영상을 합쳐서 최종 동영상 생성 (씬당 1개 이미지 + 나레이션 + 자막)
    
    Args:
        scenes: 씬 정보 리스트
        narrations: 나레이션 정보 리스트
        all_images: 이미지 정보 리스트
        output_dir: 출력 디렉토리 (기본값: 'output')
        subtitle_settings: 자막 설정 딕셔너리 (기본값: None)
    """
    # import는 이미 파일 상단에서 처리됨
    
    # 기본 자막 설정
    if subtitle_settings is None:
        subtitle_settings = {
            'font_size': 70,
            'font_color': 'white',
            'stroke_color': 'black',
            'stroke_width': 2,  # ⭐ 5 → 2 (글자 잘림 방지)
            'position_y': 960
        }
    
    scene_clips = []
    
    print(f"\n동영상 합성 시작: 총 {len(scenes)}개 씬")
    print(f"📁 출력 폴더: {output_dir}")
    print(f"🎨 자막 설정: 크기={subtitle_settings['font_size']}, 색상={subtitle_settings['font_color']}, 위치={subtitle_settings['position_y']}")
    
    for i, scene in enumerate(scenes):
        print(f"\n씬 {scene['scene_num']} 처리 중...")
        
        narration = narrations[i]
        scene_images = all_images[i]['images']  # 씬당 2개 이미지
        
        # 오디오 로드
        audio_clip = AudioFileClip(narration['audio'])
        duration = audio_clip.duration
        timings = narration['timings']
        
        print(f"  - 이미지 개수: {len(scene_images)}개")
        print(f"  - 오디오 길이: {duration:.2f}초")
        print(f"  - 자막 개수: {len(timings)}개")
        
        # ⭐ 씬당 5개 이미지를 오디오 길이에 맞게 균등 분할하여 표시
        # 이미지 크기: 1536x864 (16:9) → 1920x1080으로 업스케일
        num_images = len(scene_images)
        img_duration = duration / num_images
        img_clips = []
        
        VIDEO_WIDTH = 1920
        VIDEO_HEIGHT = 1080
        
        for img_idx, img_path in enumerate(scene_images):
            img_clip = ImageClip(img_path, duration=img_duration)
            
            # 비율 유지하면서 화면에 맞추기 (contain 방식)
            orig_w, orig_h = img_clip.size
            scale = min(VIDEO_WIDTH / orig_w, VIDEO_HEIGHT / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            
            img_clip = img_clip.resized((new_w, new_h))
            
            # 중앙 배치 (검은 배경 위에)
            x_offset = (VIDEO_WIDTH - new_w) // 2
            y_offset = (VIDEO_HEIGHT - new_h) // 2
            img_clip = img_clip.with_position((x_offset, y_offset)).with_start(img_idx * img_duration)
            
            img_clips.append(img_clip)
        
        # 검은 배경 클립
        bg_clip = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=duration)
        
        # 자막 클립들 생성
        subtitle_clips = []
        alignment = subtitle_settings.get('alignment', 'center')
        
        # macOS 한글/일본어/한자 완벽 지원 폰트 경로 (우선순위순)
        font_paths = [
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',  # ⭐ 한자 포함 모든 문자 지원
            '/System/Library/Fonts/Hiragino Sans GB.ttc',  # 히라기노 (일본어/한자 최적)
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf',  # 한글/일본어
            '/System/Library/Fonts/Supplemental/NotoSansGothic-Regular.ttf',
            'Arial-Unicode-MS'
        ]
        
        # 사용 가능한 폰트 찾기
        font_to_use = 'Arial'  # 기본값
        for font_path in font_paths:
            if '/' in font_path and os.path.exists(font_path):
                font_to_use = font_path
                print(f"  ✓ 폰트 발견: {font_path}")
                break
            elif '/' not in font_path:
                # 시스템 폰트 이름 (경로 없음)
                font_to_use = font_path
                print(f"  ✓ 시스템 폰트 사용: {font_path}")
                break
        
        print(f"  📝 사용할 폰트: {font_to_use}")
        print(f"  📝 자막 생성 시도: {len(timings)}개")
        
        for j, timing in enumerate(timings):
            start_time = timing['time']
            end_time = timings[j + 1]['time'] if j + 1 < len(timings) else duration
            subtitle_duration = end_time - start_time
            
            if subtitle_duration <= 0:
                continue
            
            try:
                # 자막 최대 너비 (화면의 90%)
                MAX_WIDTH = int(VIDEO_WIDTH * 0.9)  # 1728px
                
                # ⭐ PIL로 자막 이미지 생성 (ImageMagick 우회 - 글자 잘림 없음)
                subtitle_img = create_subtitle_image(
                    text=timing['text'],
                    font_path=font_to_use,
                    font_size=subtitle_settings['font_size'],
                    max_width=MAX_WIDTH,
                    text_color=(255, 255, 255),  # 흰색
                    stroke_color=(0, 0, 0),  # 검정 테두리
                    stroke_width=4,  # 테두리 두께 (가독성 확보)
                    padding=10
                )
                
                # numpy 배열을 ImageClip으로 변환
                txt_clip = ImageClip(subtitle_img, duration=subtitle_duration)
                
                # 텍스트 크기 가져오기
                text_height = subtitle_img.shape[0]
                
                # Y 좌표 계산 - 화면 하단 (이미지 영역 내)
                # 이미지: 1280x720, 화면: 1920x1080
                # 이미지 하단 = (1080-720)/2 + 720 = 900px
                IMAGE_BOTTOM = 900
                SUBTITLE_MARGIN = 80
                y_position = IMAGE_BOTTOM - text_height - SUBTITLE_MARGIN
                
                # 디버깅: 첫 번째 자막만 로그 출력
                if j == 0:
                    print(f"    📍 자막: y={y_position}, 높이={text_height}")
                
                # 위치 및 시작 시간 설정
                txt_clip = txt_clip.with_position(('center', y_position)).with_start(start_time)
                
                subtitle_clips.append(txt_clip)
                
            except Exception as e:
                print(f"    ✗ 자막 {j+1} 생성 실패: {e}")
        
        # 이미지 + 자막 합성 (배경 + 이미지 + 자막)
        print(f"  ✅ 자막 {len(subtitle_clips)}개 생성 완료")
        
        if subtitle_clips:
            scene_video = CompositeVideoClip([bg_clip] + img_clips + subtitle_clips, size=(1920, 1080))
        else:
            print(f"  ⚠ 자막 없이 이미지만 사용")
            scene_video = CompositeVideoClip([bg_clip] + img_clips, size=(1920, 1080))
        
        # 오디오 추가 (MoviePy 2.x에서는 with_audio)
        scene_video = scene_video.with_audio(audio_clip)
        
        # 배경음악 추가 (선택사항)
        background_music_path = scene.get('background_music', None)
        music_volume = scene.get('music_volume', 0.15)
        
        scene_video = add_background_music(scene_video, background_music_path, volume=music_volume)
        
        # ⭐ MoviePy 2.x: crossfadein/crossfadeout 제거됨
        # 씬 전환은 concatenate_videoclips에서 자동 처리
        
        scene_clips.append(scene_video)
        
        print(f"  ✅ 씬 {scene['scene_num']} 완료 (Ken Burns 효과 적용)")
    
    # 모든 씬 합치기
    print(f"\n🔗 모든 씬 합치는 중...")
    final_video = concatenate_videoclips(scene_clips, method="compose")
    
    output_path = f'{output_dir}/final_video.mp4'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🚀 최종 동영상 렌더링 중... (고속 인코딩 모드)")
    final_video.write_videofile(
        output_path, 
        fps=24, 
        codec='libx264', 
        audio_codec='aac',
        # 속도 최적화 설정
        threads=8,  # 스레드 수 증가
        preset='veryfast',  # 빠른 인코딩 (품질 유지)
        bitrate='5000k',  # 비트레이트로 품질 보장
        logger=None,  # 로그 간소화
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        audio_bitrate='192k'
    )
    
    print(f"\n✅ 최종 동영상 생성 완료: {output_path}")
    return output_path
