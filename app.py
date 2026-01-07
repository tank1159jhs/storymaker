import streamlit as st
import time
import os
from datetime import datetime
from src.config import load_config
from src.trend_analyzer import analyze_trends
from src.subtitle_settings import SUBTITLE_PRESETS, COLOR_OPTIONS, AVAILABLE_FONTS, DEFAULT_SUBTITLE_SETTINGS

config = load_config()

# 🆔 간단한 타임스탬프 폴더 (매번 새로 생성)
if 'output_dir' not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state['output_dir'] = f"output/{timestamp}"
    os.makedirs(st.session_state['output_dir'], exist_ok=True)
    print(f"✅ 출력 폴더 생성: {st.session_state['output_dir']}")

# 자막 설정 초기화
if 'subtitle_settings' not in st.session_state:
    st.session_state['subtitle_settings'] = DEFAULT_SUBTITLE_SETTINGS.copy()
    # 안전한 기본값으로 덮어쓰기
    st.session_state['subtitle_settings']['position_y'] = 850

st.title("유튜브 스토리 동영상 자동 생성기")

# ===== 📁 사이드바: 간단 정보 =====
with st.sidebar:
    st.header("📁 현재 작업")
    st.info(f"**출력 폴더**\n\n📂 {st.session_state['output_dir']}")
    
    # 새 작업 시작
    if st.button("🔄 새 작업 시작", use_container_width=True):
        # 세션 초기화
        for key in list(st.session_state.keys()):
            if key != 'output_dir':
                del st.session_state[key]
        # 새 폴더 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state['output_dir'] = f"output/{timestamp}"
        os.makedirs(st.session_state['output_dir'], exist_ok=True)
        st.rerun()

# 1단계: 트렌드 분석 (참고용)
st.header("1. 트렌드 분석 (선택)")
st.write("참고할 트렌드 동영상을 검색합니다.")
query = st.text_input("검색 키워드", "老人 思い出")
subscriber_range = st.selectbox("구독자 수 범위", ["1만-10만", "10만-50만", "50만 이상"])
view_range = st.selectbox("조회수 범위", ["10만 이상", "50만 이상", "100만 이상"])
format_type = st.radio("포맷 선택", ["롱폼", "쇼츠"])

if st.button("트렌드 분석 시작"):
    with st.spinner("분석 중..."):
        try:
            videos = analyze_trends(subscriber_range, view_range, format_type, query)
            st.session_state['videos'] = videos
            st.success(f"분석 완료! {len(videos)}개 동영상 발견")
        except Exception as e:
            st.error(f"오류: {e}")

if 'videos' in st.session_state:
    st.write("필터링된 동영상:")
    for video in st.session_state['videos']:
        st.write(f"- **{video['title']}**")
        st.write(f"  URL: {video['url']}")
        st.write(f"  {video['metadata']}")
        st.write("---")

# 2단계: 씬별 대본 입력
st.header("2. 씬별 대본 입력")
st.write("ChatGPT에서 생성한 대본을 씬별로 입력하세요 (최대 8씬).")
st.info("💡 팁: 타임스탬프 형식 [0:00] 텍스트 또는 일반 텍스트 모두 가능합니다.")

num_scenes = st.number_input("씬 개수", min_value=1, max_value=8, value=1)

scenes = []
for i in range(num_scenes):
    st.subheader(f"씬 {i+1}")
    scene_script = st.text_area(
        f"씬 {i+1} 대본", 
        placeholder="예시:\n[0:00] 昔々、ある小さな村に一人の老人が住んでいました。\n[0:05] 彼の人生は決して平坦ではありませんでした。",
        height=150, 
        key=f"scene_{i}"
    )
    if scene_script.strip():
        scenes.append({'scene_num': i+1, 'script': scene_script})

# 현재 입력된 씬 개수 표시
st.write(f"📝 현재 입력된 씬: **{len(scenes)}개** / {num_scenes}개")

if st.button("대본 확정"):
    if len(scenes) > 0:
        st.session_state['scenes'] = scenes
        st.success(f"✅ {len(scenes)}개 씬 대본이 확정되었습니다!")
        st.balloons()
    else:
        st.error("⚠️ 최소 1개 씬을 입력해주세요.")

# 3단계: 씬별 이미지 생성 또는 업로드
if 'scenes' in st.session_state:
    st.header("3. 이미지 준비")
    
    # 이미지 소스 선택
    image_source = st.radio(
        "이미지 준비 방법 선택",
        options=["🎨 AI로 자동 생성", "📁 직접 업로드"],
        horizontal=True,
        help="AI 생성은 시간이 걸리지만 자동으로 생성됩니다. 업로드는 빠르지만 이미지를 직접 준비해야 합니다."
    )
    
    if image_source == "📁 직접 업로드":
        # 이미지 업로드 모드
        st.info(f"📌 확정된 씬: **{len(st.session_state['scenes'])}개** (각 씬당 3개 이미지 필요)")
        st.write("💡 각 씬당 3개의 이미지를 업로드하세요 (배경/오브젝트 중심, 인물 제외)")
        
        uploaded_images = {}
        all_images_ready = True
        
        for scene in st.session_state['scenes']:
            scene_num = scene['scene_num']
            st.subheader(f"씬 {scene_num} 이미지 업로드")
            
            cols = st.columns(3)
            part_names = [f"그룹 {i+1}" for i in range(3)]
            scene_uploads = []
            
            for idx, part_name in enumerate(part_names, start=1):
                with cols[idx - 1]:
                    img = st.file_uploader(
                        f"그룹 {idx}",
                        type=['jpg', 'jpeg', 'png'],
                        key=f"upload_scene_{scene_num}_group{idx}"
                    )
                    if img:
                        st.image(img, caption=part_name, use_container_width=True)
                        scene_uploads.append(img)
                    else:
                        scene_uploads.append(None)
            
            if all(scene_uploads):
                uploaded_images[scene_num] = scene_uploads
            else:
                all_images_ready = False
        
        if st.button("✅ 업로드 이미지 확정"):
            if all_images_ready and len(uploaded_images) == len(st.session_state['scenes']):
                # 업로드된 이미지를 output 폴더에 저장
                import os
                from PIL import Image
                
                os.makedirs('output', exist_ok=True)
                all_images = []
                
                with st.spinner("이미지 저장 중..."):
                    for scene in st.session_state['scenes']:
                        scene_num = scene['scene_num']
                        images = []
                        
                        for part_num, uploaded_file in enumerate(uploaded_images[scene_num], start=1):
                            # 이미지 저장
                            img = Image.open(uploaded_file)
                            img_path = f'output/scene_{scene_num}_part{part_num}.jpg'
                            
                            # 1920x1080으로 리사이즈 (필요시)
                            if img.size != (1920, 1080):
                                img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                            
                            img.save(img_path, 'JPEG', quality=95)
                            images.append(img_path)
                        
                        all_images.append({
                            'scene_num': scene_num,
                            'images': images
                        })
                
                st.session_state['all_images'] = all_images
                st.success(f"✅ {len(all_images)}개 씬 × 3개 이미지 저장 완료!")
                st.balloons()
            else:
                st.error("⚠️ 모든 씬의 이미지를 업로드해주세요 (각 씬당 3개)")
    
    else:
        # AI 이미지 생성 모드
        st.write(f"대본에 맞는 AI 이미지를 자동으로 생성합니다 (Pollinations API - 무료 무제한).")
        st.info(f"📌 확정된 씬: **{len(st.session_state['scenes'])}개** (각 씬당 3개 이미지)")
        st.success("✅ Pollinations API: 무료 무제한, Flux 모델 사용, 5-10초/이미지")
        
        # 이미지 스타일 및 고급 설정
        col1, col2 = st.columns([2, 1])
        with col1:
            image_style = st.selectbox(
                "🎨 이미지 스타일 선택",
                options=["realistic", "cinematic", "anime", "semi-realistic"],
                format_func=lambda x: {
                    "realistic": "📷 실사 (Realistic) - 사진 같은 현실적 이미지",
                    "cinematic": "🎬 시네마틱 (Cinematic) - 영화 같은 극적인 이미지",
                    "anime": "🎌 애니메이션 (Anime) - 일본 애니메이션 스타일",
                    "semi-realistic": "🎨 세미 실사 (Semi-Realistic) - 회화적이고 부드러운 느낌"
                }[x],
                index=0,
                help="이미지의 전체적인 느낌을 결정합니다"
            )
        with col2:
            st.write("")  # 레이아웃 정렬용
            st.caption("💡 **추천**: 시네마틱 또는 실사 스타일")
        
        # 고급 설정 (접을 수 있는 expander)
        with st.expander("⚙️ 고급 설정 (SD WebUI API)"):
            col1, col2, col3 = st.columns(3)
            with col1:
                sampling_steps = st.slider(
                    "🎚️ Sampling Steps",
                    min_value=10,
                    max_value=50,
                    value=20,
                    step=5,
                    help="높을수록 품질 향상, 생성 시간 증가 (기본: 20)"
                )
            with col2:
                sampler_name = st.selectbox(
                    "🔧 Sampler",
                    options=["DPM++ 2M", "DPM++ 2M Karras", "Euler a", "DDIM", "LMS"],
                    index=0,
                    help="샘플링 알고리즘 (기본: DPM++ 2M)"
                )
            with col3:
                cfg_scale = st.slider(
                    "🎛️ CFG Scale",
                    min_value=1.0,
                    max_value=15.0,
                    value=7.0,
                    step=0.5,
                    help="프롬프트 일치도 (기본: 7.0)"
                )
            st.caption("""
                💡 **팁**: 기본값(Steps=20, Sampler=DPM++ 2M, CFG=7.0)이 대부분의 경우 최적입니다.
                - Steps ↑ → 품질 향상, 시간 증가
                - CFG Scale ↑ → 프롬프트 정확도 향상, 과도하면 과포화
            """)
    
    if image_source == "🎨 AI로 자동 생성" and st.button("🎨 모든 씬 이미지 생성 시작"):
        # 🔍 선택된 스타일 확인
        st.info(f"🎨 선택된 이미지 스타일: **{image_style}**")
        
        # ⚠️ SD WebUI 실행 확인
        import requests
        try:
            response = requests.get("http://127.0.0.1:7861/sdapi/v1/sd-models", timeout=5)
            if response.status_code != 200:
                st.error("⚠️ SD WebUI가 실행 중이지만 응답이 올바르지 않습니다.")
                st.stop()
        except requests.exceptions.ConnectionError:
            st.error("❌ SD WebUI가 실행되지 않았습니다!")
            st.warning("""
            ### SD WebUI 실행 방법:
            1. 터미널에서 다음 명령 실행:
            ```bash
            cd /Users/systemi/stable-diffusion-webui
            ./webui.sh --api --listen --port 7861
            ```
            2. SD WebUI가 완전히 로드될 때까지 기다린 후 다시 시도하세요.
            """)
            st.stop()
        except Exception as e:
            st.error(f"❌ SD WebUI 연결 오류: {e}")
            st.stop()
        
        st.success("✅ SD WebUI 연결 확인됨")
        
        with st.spinner("이미지 생성 중... (씬당 약 10-30초 소요)"):
            from src.image_generator import generate_images_from_script_only
            
            all_images = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for scene_idx, scene in enumerate(st.session_state['scenes']):
                status_text.text(f"🎨 씬 {scene['scene_num']}/{len(st.session_state['scenes'])} 이미지 생성 중...")

                # 항상 'final_scripts' 사용, 없으면 원본
                if 'final_scripts' in st.session_state and scene_idx < len(st.session_state['final_scripts']):
                    script_to_use = st.session_state['final_scripts'][scene_idx]
                else:
                    script_to_use = scene['script']

                images = generate_images_from_script_only(
                    script_to_use, 
                    scene['scene_num'],
                    output_dir=st.session_state['output_dir'],
                    image_style=image_style,
                    num_images=3,
                    steps=sampling_steps,
                    sampler_name=sampler_name,
                    cfg_scale=cfg_scale
                )
                
                all_images.append({'scene_num': scene['scene_num'], 'images': images})
                st.write(f"✓ 씬 {scene['scene_num']}: 이미지 생성 완료")
                
                # 씬 간 API 안정화 대기 (마지막 씬이 아니면)
                if scene_idx < len(st.session_state['scenes']) - 1:
                    time.sleep(3)
                
                # 생성된 이미지 즉시 표시 (씬당 3개)
                cols = st.columns(3)
                for part_idx, img in enumerate(images, start=1):
                    with cols[part_idx - 1]:
                        st.image(img, caption=f"그룹 {part_idx}", use_container_width=True)
                        st.caption(f"📁 씬{scene['scene_num']}-그룹{part_idx}")
                
                # 프로그레스 바: 씬 단위로 업데이트 (0.0 ~ 1.0)
                progress_bar.progress((scene_idx + 1) / len(st.session_state['scenes']))
            
            st.session_state['all_images'] = all_images
            status_text.empty()
            progress_bar.empty()
            st.success(f"🎉 모든 이미지 생성 완료! 총 {len(st.session_state['scenes'])}개 씬 × 3개 이미지 = {len(st.session_state['scenes']) * 3}개")
            st.balloons()

# 이미지 생성 후 확인
if 'all_images' in st.session_state:
    st.subheader("📸 생성된 이미지 확인")
    st.write(f"총 {len(st.session_state['all_images'])}개 씬 × 3개 이미지 = {len(st.session_state['all_images']) * 3}개")
    if st.checkbox("생성된 이미지 보기"):
        for img_group in st.session_state['all_images']:
            st.write(f"**씬 {img_group['scene_num']}**")
            # 씬당 3개의 이미지 표시
            cols = st.columns(3)
            # 취사선택: 체크박스 제공
            selected = st.multiselect(
                f"사용할 이미지를 선택하세요 (씬 {img_group['scene_num']})",
                options=[f"그룹 {i+1}" for i in range(3)],
                default=[f"그룹 {i+1}" for i in range(3)]
            )
            for idx, img_path in enumerate(img_group['images']):
                with cols[idx]:
                    st.image(img_path, caption=f"그룹 {idx+1}", use_container_width=True)
                    if f"그룹 {idx+1}" in selected:
                        st.caption("✅ 사용")
                    else:
                        st.caption("❌ 제외")
            st.divider()
    
    # 🔍 프리뷰 기능 추가
    with st.expander("🔍 씬별 프리뷰 (이미지 + 대본)", expanded=False):
        st.info("💡 각 씬의 이미지와 대본을 미리 확인하세요. 동영상 생성 전 확인하면 좋습니다!")
        
        for idx, scene in enumerate(st.session_state['scenes']):
            scene_num = scene['scene_num']
            img_group = st.session_state['all_images'][idx]
            
            st.subheader(f"씬 {scene_num}")
            
            # 이미지 3개를 나란히 표시
            cols = st.columns(3)
            part_names = ["시작", "중간", "끝"]
            for idx, img_path in enumerate(img_group['images']):
                with cols[idx]:
                    st.image(img_path, caption=part_names[idx], use_container_width=True)
            
            # 대본 표시
            st.markdown("**📝 대본:**")
            st.text_area(
                label=f"씬 {scene_num} 대본",
                value=scene['script'],
                height=150,
                disabled=True,
                key=f"preview_script_{scene_num}",
                label_visibility="collapsed"
            )
            
            # 예상 자막 미리보기
            lines = scene['script'].strip().split('\n')
            subtitles = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith('('):
                    # 타임스탬프 제거
                    import re
                    text = re.sub(r'\[\d+:\d+\]\s*', '', line)
                    if text:
                        subtitles.append(text)
            
            if subtitles:
                st.markdown("**💬 예상 자막:**")
                for i, sub in enumerate(subtitles[:3], 1):  # 처음 3개만
                    st.caption(f"{i}. {sub}")
                if len(subtitles) > 3:
                    st.caption(f"... 외 {len(subtitles)-3}개")
            
            st.divider()
    
    st.write("---")

    # 3.5. 최종 대본 검토 및 수정 (이미지 생성 후 항상 표시)
    st.header("3.5. 최종 대본 검토 및 수정")
    st.info("💡 이미지 생성이 완료되었습니다! 이제 나레이션에 사용될 최종 대본을 확인하고 수정할 수 있습니다.")
    
    # 언어 코드 매핑
    lang_map = {
        "일본어 (Japanese)": "ja",
        "한국어 (Korean)": "ko",
        "영어 (English)": "en"
    }
    
    # 나레이션 생성 전에만 대본 편집 가능
    if 'narrations' not in st.session_state:
        # 목표 언어 선택
        target_language = st.selectbox(
            "🌍 최종 대본 언어 (나레이션 언어)",
            options=["일본어 (Japanese)", "한국어 (Korean)", "영어 (English)"],
            index=0,
            help="이 언어로 자동 번역되며, 직접 수정할 수 있습니다."
        )
        selected_lang = lang_map[target_language]
        
        st.write("---")
        st.subheader("📝 씬별 최종 대본")
        st.caption(f"원본 대본을 **{target_language}**로 자동 번역합니다. 필요시 직접 수정하세요.")
        
        # 자동 번역 및 편집
        translated_scripts = []
        from src.tts_generator import translate_text, detect_language
        
        for idx, scene in enumerate(st.session_state['scenes']):
            scene_num = scene['scene_num']
            original_script = scene['script']
            
            # 기존 final_scripts가 있으면 그것을 기본값으로 사용
            if 'final_scripts' in st.session_state and idx < len(st.session_state['final_scripts']):
                default_value = st.session_state['final_scripts'][idx]
            else:
                # 자동 번역
                original_lang = detect_language(original_script)
                if original_lang != selected_lang:
                    default_value = translate_text(original_script, selected_lang)
                    st.caption(f"씬 {scene_num}: {original_lang} → {selected_lang} 자동 번역됨")
                else:
                    default_value = original_script
                    st.caption(f"씬 {scene_num}: 이미 {selected_lang}로 작성됨")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                edited = st.text_area(
                    f"씬 {scene_num} 최종 대본 ({target_language})", 
                    value=default_value, 
                    height=150, 
                    key=f"edit_final_{scene_num}"
                )
            with col2:
                st.caption("**원본 대본:**")
                st.text_area(
                    f"씬 {scene_num} 원본", 
                    value=original_script, 
                    height=150, 
                    disabled=True,
                    key=f"original_{scene_num}"
                )
            
            translated_scripts.append(edited)
            st.write("---")
        
        # 확정 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ 최종 대본 확정 및 나레이션 생성으로 이동", use_container_width=True):
                st.session_state['final_scripts'] = translated_scripts
                st.session_state['final_scripts_language'] = selected_lang
                st.success(f"✅ 최종 대본이 확정되었습니다! ({target_language})")
                st.info("👇 아래 '4. 씬별 나레이션 생성'으로 이동하세요.")
                st.balloons()
                st.rerun()
    else:
        # 나레이션 생성 후에는 편집 불가
        st.warning("⚠️ 나레이션이 이미 생성되었습니다. 대본을 수정하려면 나레이션을 다시 생성해야 합니다.")
        st.caption("💡 팁: 사이드바의 '🔄 새 작업 시작' 버튼을 눌러 처음부터 다시 시작할 수 있습니다.")
        
        # 현재 사용된 최종 대본 표시
        if 'final_scripts' in st.session_state:
            with st.expander("📄 현재 사용 중인 최종 대본 보기"):
                for idx, script in enumerate(st.session_state['final_scripts']):
                    st.text_area(f"씬 {idx+1}", value=script, height=100, disabled=True, key=f"readonly_final_{idx}")

# 4단계: 씬별 나레이션 생성 (이미지 다음)
if 'all_images' in st.session_state:
    st.header("4. 씬별 나레이션 생성")
    st.write("대본을 읽는 음성을 생성합니다 (Edge TTS - Microsoft 무료 고품질)")
    st.info("⚡️ 번역본 검토/수정 단계에서 확정한 최종 대본이 항상 사용됩니다. (자동 번역 옵션 없음)")
    
    # 언어 선택
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tts_language = st.selectbox(
            "🌍 나레이션 언어 선택",
            options=["일본어 (Japanese)", "한국어 (Korean)", "영어 (English)"],
            index=0,
            help="TTS(텍스트 음성 변환)에 사용할 언어를 선택하세요"
        )
    # (자동 번역 체크박스 완전 제거)
    # 언어 코드 매핑
    lang_map = {
        "일본어 (Japanese)": "ja",
        "한국어 (Korean)": "ko",
        "영어 (English)": "en"
    }
    selected_lang = lang_map[tts_language]
    
    # 음성 선택 (인기 있는 3개씩)
    st.subheader("🎙️ 음성 설정")
    voice_options = {
        "ja": {
            "Keita (남성, 친근하고 따뜻함) ⭐": "ja-JP-KeitaNeural",
            "Nanami (여성, 부드럽고 감성적)": "ja-JP-NanamiNeural",
            "Daichi (남성, 깊이 있고 차분함)": "ja-JP-DaichiNeural"
        },
        "ko": {
            "Hyunsu (남성, 따뜻하고 친근함) ⭐": "ko-KR-HyunsuNeural",
            "SunHi (여성, 밝고 친근함)": "ko-KR-SunHiNeural",
            "InJoon (남성, 차분하고 감성적)": "ko-KR-InJoonNeural"
        },
        "en": {
            "Guy (남성, 따뜻하고 신뢰감) ⭐": "en-US-GuyNeural",
            "Jenny (여성, 친근하고 밝음)": "en-US-JennyNeural",
            "Christopher (남성, 캐주얼)": "en-US-ChristopherNeural"
        }
    }
    sample_texts = {
        "ja": "こんにちは。今日は特別なお話をお届けします。",
        "ko": "안녕하세요. 오늘은 특별한 이야기를 들려드리겠습니다.",
        "en": "Hello. Today, I will share a special story with you."
    }
    speed_options = {
        "느리게 (감정 표현)": "-15%",
        "보통 (기본)": "+0%",
        "빠르게": "+15%"
    }
    col1, col2 = st.columns(2)
    with col1:
        selected_voice_desc = st.radio(
            "🗣️ 음성 선택",
            options=list(voice_options[selected_lang].keys()),
            help="각 음성을 미리 들어보고 선택하세요"
        )
        selected_voice = voice_options[selected_lang][selected_voice_desc]
        if st.button(f"🔊 {selected_voice_desc.split('(')[0].strip()} 미리듣기"):
            with st.spinner("샘플 음성 생성 중..."):
                try:
                    from src.tts_generator import generate_single_tts
                    import os
                    sample_path = f"output/sample_{selected_voice.replace('-', '_')}.mp3"
                    os.makedirs('output', exist_ok=True)
                    success = generate_single_tts(
                        text=sample_texts[selected_lang],
                        output_path=sample_path,
                        language=selected_lang,
                        voice=selected_voice,
                        rate='-15%',
                        pitch='-8Hz',
                        volume='+0%'
                    )
                    if success and os.path.exists(sample_path):
                        st.audio(sample_path, format='audio/mp3')
                        st.success("✅ 샘플 음성 재생!")
                    else:
                        st.error("❌ 샘플 생성 실패")
                except Exception as e:
                    st.error(f"오류: {e}")
    with col2:
        selected_speed_desc = st.radio(
            "⚡ 말하기 속도",
            options=list(speed_options.keys()),
            index=1,
            help="음성의 속도를 조절합니다"
        )
        voice_speed = speed_options[selected_speed_desc]
    st.caption(f"✅ 선택: **{selected_voice_desc}** | 속도: **{selected_speed_desc}**")
    # 안내 메시지: 항상 최종 대본 사용
    if 'final_scripts' in st.session_state:
        st.success(f"✅ **{tts_language}** 선택됨 | 3.5단계에서 확정한 최종 대본이 사용됩니다.")
        st.caption("💡 3.5단계 '최종 대본 검토 및 수정'에서 입력한 대본이 그대로 나레이션 및 자막에 반영됩니다!")
    else:
        st.warning("⚠️ 최종 대본이 확정되지 않았습니다. 3.5단계로 돌아가서 최종 대본을 확정하세요.")
        st.stop()
    
    if st.button("🎙️ 모든 씬 나레이션 생성 시작"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_narrations = []
        from src.tts_generator import generate_tts_with_timestamps
        
        for i, scene in enumerate(st.session_state['scenes']):
            status_text.text(f"🎙️ 씬 {scene['scene_num']} 나레이션 생성 중... ({i+1}/{len(st.session_state['scenes'])})")
            
            # 최종 확정된 대본 사용
            final_script = st.session_state['final_scripts'][i]
            
            # 💡 반환값 개수 수정: generate_tts_with_timestamps는 3개 값을 반환
            try:
                audio_path, timings, processed_script = generate_tts_with_timestamps(
                    script=final_script,
                    scene_num=scene['scene_num'],
                    language=selected_lang,
                    voice=selected_voice,
                    rate=voice_speed,  # 사용자가 선택한 속도 (-15%, +0%, +15%)
                    pitch='-8Hz',      # 감성적인 톤을 위해 약간 낮게 고정
                    output_dir=st.session_state['output_dir']
                )
                
                narration_data = {
                    'audio': audio_path,
                    'audio_path': audio_path,
                    'timings': timings,
                    'script': processed_script
                }
                
                all_narrations.append(narration_data)
                st.audio(audio_path)
                
            except Exception as e:
                st.error(f"❌ 씬 {scene['scene_num']} 나레이션 생성 실패: {e}")
                import traceback
                print(f"나레이션 생성 에러:\n{traceback.format_exc()}")
            
            progress_bar.progress((i + 1) / len(st.session_state['scenes']))
        
        st.session_state['narrations'] = all_narrations
        status_text.empty()
        progress_bar.empty()
        st.success("🎉 모든 나레이션 생성 완료!")
        st.balloons()

# 5단계: 씬 합치기 및 최종 동영상 생성 (이미지 + 자막 + 나레이션)
if 'narrations' in st.session_state:
    st.header("5. 최종 동영상 생성")
    st.write("이미지 + 자막 + 나레이션을 합쳐서 최종 동영상을 만듭니다.")
    
    # 🎨 자막 스타일 설정
    st.subheader("🎨 자막 스타일")
    
    # 프리셋 선택
    preset_name = st.selectbox(
        "스타일 프리셋",
        options=["커스텀"] + list(SUBTITLE_PRESETS.keys()),
        index=1,  # YouTube 기본을 기본값으로
        key="subtitle_preset"
    )
    
    # 프리셋 변경 시 설정 업데이트
    if preset_name != "커스텀":
        # 프리셋 설정 적용 (key 없이 직접 업데이트)
        st.session_state['subtitle_settings'] = SUBTITLE_PRESETS[preset_name].copy()
        st.success(f"✅ {preset_name} 적용됨")
    
    # 현재 설정 해시 (변경 감지용)
    current_settings_hash = f"{st.session_state['subtitle_settings']['font_size']}_{st.session_state['subtitle_settings'].get('subtitle_margin', 40)}_{st.session_state['subtitle_settings']['stroke_width']}_{st.session_state['subtitle_settings']['font_color']}"
    
    # 실제 이미지에 자막 미리보기
    if 'all_images' in st.session_state and len(st.session_state['all_images']) > 0:
        st.markdown("#### 🎬 자막 미리보기 (첫 번째 이미지)")
        first_image_path = st.session_state['all_images'][0]['images'][0]
        col_preview1, col_preview2 = st.columns(2)
        with col_preview1:
            st.image(first_image_path, caption="원본 이미지", use_container_width=True)
        with col_preview2:
            try:
                from PIL import Image, ImageDraw, ImageFont
                img = Image.open(first_image_path).copy()
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", st.session_state['subtitle_settings']['font_size'])
                except:
                    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", st.session_state['subtitle_settings']['font_size'])
                sample_text = "お互いのことを考えていたと思います."
                bbox = draw.textbbox((0, 0), sample_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (1920 - text_width) // 2
                margin = st.session_state['subtitle_settings'].get('subtitle_margin', 40)
                y = 1080 - text_height - margin
                if y < 0:
                    y = 0
                stroke_width = st.session_state['subtitle_settings']['stroke_width']
                stroke_color = st.session_state['subtitle_settings']['stroke_color']
                if stroke_width > 0:
                    for adj_x in range(-stroke_width, stroke_width+1):
                        for adj_y in range(-stroke_width, stroke_width+1):
                            if adj_x != 0 or adj_y != 0:
                                draw.text((x+adj_x, y+adj_y), sample_text, font=font, fill=stroke_color)
                draw.text((x, y), sample_text, font=font, fill=st.session_state['subtitle_settings']['font_color'])
                st.image(img, caption="자막 적용 미리보기", use_container_width=True)
                st.caption(f"✅ 크기: {st.session_state['subtitle_settings']['font_size']}px | 하단 마진: {margin}px (실제 적용)")
            except Exception as e:
                st.error(f"미리보기 생성 실패: {e}")
                st.markdown("#### 💡 자막 스타일 미리보기")
                preview_html = f"""
                <div style=\"background: #333; padding: 30px; border-radius: 5px; text-align: center;\">
                    <span style=\"
                        font-size: {st.session_state['subtitle_settings']['font_size'] * 0.3}px;
                        color: {st.session_state['subtitle_settings']['font_color']};
                        text-shadow: 
                            -{st.session_state['subtitle_settings']['stroke_width']}px -{st.session_state['subtitle_settings']['stroke_width']}px 0 {st.session_state['subtitle_settings']['stroke_color']},
                            {st.session_state['subtitle_settings']['stroke_width']}px -{st.session_state['subtitle_settings']['stroke_width']}px 0 {st.session_state['subtitle_settings']['stroke_color']},
                            -{st.session_state['subtitle_settings']['stroke_width']}px {st.session_state['subtitle_settings']['stroke_width']}px 0 {st.session_state['subtitle_settings']['stroke_color']},
                            {st.session_state['subtitle_settings']['stroke_width']}px {st.session_state['subtitle_settings']['stroke_width']}px 0 {st.session_state['subtitle_settings']['stroke_color']};
                        font-weight: bold;
                        font-family: Arial, sans-serif;
                    ">お互いのことを考えていたと思います。</span>
                </div>
                """
                st.markdown(preview_html, unsafe_allow_html=True)
                st.caption("💡 이미지 생성 후 실제 미리보기를 볼 수 있습니다")
    else:
        st.markdown("#### 💡 자막 스타일 미리보기")
        preview_html = f"""
        <div style=\"background: #333; padding: 30px; border-radius: 5px; text-align: center;\">
            <span style=\"
                font-size: {st.session_state['subtitle_settings']['font_size'] * 0.3}px;
                color: {st.session_state['subtitle_settings']['font_color']};
                text-shadow: 
                    -{st.session_state['subtitle_settings']['stroke_width']}px -{st.session_state['subtitle_settings']['stroke_width']}px 0 {st.session_state['subtitle_settings']['stroke_color']},
                    {st.session_state['subtitle_settings']['stroke_width']}px -{st.session_state['subtitle_settings']['stroke_width']}px 0 {st.session_state['subtitle_settings']['stroke_color']},
                    -{st.session_state['subtitle_settings']['stroke_width']}px {st.session_state['subtitle_settings']['stroke_width']}px 0 {st.session_state['subtitle_settings']['stroke_color']},
                    {st.session_state['subtitle_settings']['stroke_width']}px {st.session_state['subtitle_settings']['stroke_width']}px 0 {st.session_state['subtitle_settings']['stroke_color']};
                font-weight: bold;
                font-family: Arial, sans-serif;
            ">お互いのことを考えていたと思います.</span>
        </div>
        """
        st.markdown(preview_html, unsafe_allow_html=True)
        st.caption("💡 이미지 생성 후 실제 미리보기를 볼 수 있습니다")
    
    # 상세 설정 (키 없이 값만 직접 변경)
    with st.expander("⚙️ 상세 자막 설정", expanded=(preset_name == "커스텀")):
        st.caption("💡 프리셋 선택 후 여기서 세부 조정 가능합니다")
        col_a, col_b = st.columns(2)
        with col_a:
            new_font_size = st.slider(
                "폰트 크기",
                min_value=50,
                max_value=140,
                value=int(st.session_state['subtitle_settings'].get('font_size', 80)),
                step=5,
                help="기본값: 80 (권장 범위: 70-100)"
            )
            st.session_state['subtitle_settings']['font_size'] = new_font_size
            new_stroke = st.slider(
                "테두리 두께",
                min_value=0,
                max_value=12,
                value=int(st.session_state['subtitle_settings'].get('stroke_width', 6)),
                step=1,
                help="기본값: 6 (권장 범위: 5-8)"
            )
            st.session_state['subtitle_settings']['stroke_width'] = new_stroke
        with col_b:
            current_color = st.session_state['subtitle_settings'].get('font_color', 'white')
            color_index = 0
            for idx, (name, color) in enumerate(COLOR_OPTIONS.items()):
                if color == current_color:
                    color_index = idx
                    break
            color_name = st.selectbox(
                "글자 색상",
                options=list(COLOR_OPTIONS.keys()),
                index=color_index
            )
            st.session_state['subtitle_settings']['font_color'] = COLOR_OPTIONS[color_name]
            new_margin = st.slider(
                "하단 마진 (px)",
                min_value=10,
                max_value=200,
                value=int(st.session_state['subtitle_settings'].get('subtitle_margin', 40)),
                step=5,
                help="자막이 하단에 너무 붙거나 잘리지 않게 여유를 두세요 (권장: 40~80)"
            )
            st.session_state['subtitle_settings']['subtitle_margin'] = new_margin
    
    st.divider()
    
    # 🎵 배경음악 선택 (선택사항)
    st.subheader("🎵 배경음악 추가 (선택사항)")
    
    # music 폴더의 파일 목록 가져오기
    music_dir = 'music'
    os.makedirs(music_dir, exist_ok=True)
    
    music_files = []
    if os.path.exists(music_dir):
        music_files = [f for f in os.listdir(music_dir) 
                      if f.endswith(('.mp3', '.wav', '.m4a')) and not f.startswith('.')]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if music_files:
            music_options = ["없음 (나레이션만)"] + music_files
            selected_music = st.selectbox(
                "배경음악 선택",
                options=music_options,
                index=0,  # 기본값: "없음 (나레이션만)"
                key="music_select",
                help="music/ 폴더의 MP3 파일 중 선택하세요"
            )
        else:
            st.info("💡 `music/` 폴더에 MP3 파일을 추가하면 배경음악을 사용할 수 있습니다.")
            selected_music = "없음 (나레이션만)"
    
    with col2:
        music_volume = st.slider(
            "음악 볼륨",
            min_value=5,
            max_value=30,
            value=15,
            step=5,
            help="배경음악 볼륨 (%) - 나레이션 방해 안 하게 낮게 설정"
        ) / 100
    
    # 배경음악 경로 설정
    background_music_path = None
    if selected_music != "없음 (나레이션만)":
        background_music_path = os.path.join(music_dir, selected_music)
        st.success(f"✅ 배경음악: **{selected_music}** (볼륨: {int(music_volume*100)}%)")
        
        # 미리듣기
        if os.path.exists(background_music_path):
            with st.expander("🔊 배경음악 미리듣기"):
                st.audio(background_music_path)
    else:
        st.info("ℹ️ 배경음악 없이 생성 (나레이션만) - 저작권 100% 안전")
    
    st.caption("⚠️ **저작권 주의**: YouTube Audio Library, Pixabay Music 등 무료 음악만 사용하세요!")
    
    # 예상 시간 계산
    num_scenes = len(st.session_state['scenes'])
    estimated_time = num_scenes * 30  # 씬당 약 30초
    st.info(f"⏱️ 예상 소요 시간: 약 {estimated_time}초 ({estimated_time//60}분 {estimated_time%60}초)")
    
    if st.button("🎬 씬 합치기 및 동영상 생성"):
        # 프로그레스 바와 상태 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎬 동영상 생성 시작...")
        
        try:
            from src.video_creator import merge_scenes_to_video
            import time
            
            # 진행률 업데이트 (각 단계별)
            status_text.text(f"📝 씬 정보 로딩 중... (0/{num_scenes})")
            progress_bar.progress(0.1)
            time.sleep(0.5)
            
            status_text.text(f"🎨 이미지 처리 중... (1/{num_scenes})")
            progress_bar.progress(0.2)
            
            # 실제 동영상 생성
            # 배경음악 정보를 씬에 추가
            print(f"\n[배경음악 설정 전달]")
            print(f"  - background_music_path: {background_music_path}")
            print(f"  - music_volume: {music_volume}")
            
            scenes_with_music = []
            for scene in st.session_state['scenes']:
                scene_copy = scene.copy()
                scene_copy['background_music'] = background_music_path
                scene_copy['music_volume'] = music_volume
                scenes_with_music.append(scene_copy)
                print(f"  - 씬 {scene['scene_num']}: background_music={background_music_path}")
            
            video_path = merge_scenes_to_video(
                scenes_with_music,
                st.session_state['narrations'],
                st.session_state['all_images'],
                output_dir=st.session_state['output_dir'],  # 세션별 출력 폴더 전달
                subtitle_settings=st.session_state['subtitle_settings']  # 자막 설정 전달
            )
            
            # 완료
            progress_bar.progress(1.0)
            status_text.text("✅ 동영상 생성 완료!")
            
            st.session_state['video'] = video_path
            
            # 성공 메시지
            st.success("🎉 동영상 생성 완료!")
            st.balloons()
            
            # 파일 정보 표시
            import os
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            st.info(f"📁 파일: `{video_path}`\n📦 크기: {file_size:.1f}MB")
            
            # 바로 재생 가능한 비디오 플레이어
            st.subheader("🎬 생성된 동영상 미리보기")
            st.video(video_path)
            
            # 다운로드 버튼
            with open(video_path, 'rb') as f:
                st.download_button(
                    label="💾 동영상 다운로드",
                    data=f,
                    file_name="final_video.mp4",
                    mime="video/mp4"
                )
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ 동영상 생성 실패: {e}")
            import traceback
            with st.expander("🔍 에러 상세 정보"):
                st.code(traceback.format_exc())

# 6단계: 업로드
if 'video' in st.session_state:
    st.header("6. 유튜브 업로드")
    title = st.text_input("동영상 제목", "시니어 추억 스토리")
    description = st.text_area("설명", "자동 생성된 스토리 동영상")
    tags = st.text_input("태그 (쉼표로 구분)", "시니어,추억,스토리")