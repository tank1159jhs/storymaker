# StoryMaker - YouTube Story Video Generator

유튜브 감성 스토리 영상을 자동으로 생성하는 AI 기반 도구입니다.

## 🎯 주요 기능

### 1. 다국어 지원
- **한국어**, **일본어**, **영어** 대본 지원
- Azure TTS를 사용한 자연스러운 음성 합성
- 다양한 화자 선택 가능

### 2. 일본 배경/사물 특화 이미지 생성
- Stable Diffusion WebUI 연동 (실사 모델)
- **사물/오브젝트 중심** 구도 (건축물 회피)
- GPT-3.5 자동 프롬프트 생성 (대본 맥락 반영)
- 감성적 스토리텔링: 뒷모습/옆모습 중심, 얼굴 차단
- 중국풍 건축 자동 필터링

### 3. 전문적인 영상 제작
- 자막 시스템 (MoviePy 2.x 호환)
- 배경음악 자동 루프
- 말하기 속도 조절 (느림/보통/빠름)
- 씬 타이밍 자동 동기화

### 4. 간편한 워크플로우
- 웹 기반 UI (Streamlit)
- 트렌드 분석 기능 (YouTube API)
- 세션별 출력 폴더 자동 관리

## 🚀 빠른 시작

### 1. 필수 요구사항
```bash
# Python 3.8 이상
python --version

# Stable Diffusion WebUI 실행 중 (포트 7861)
# → 실사 모델 권장: realisticVisionV60B1_v51VAE.safetensors
```

### 2. 설치
```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정
`.env` 파일 생성:
```env
OPENAI_API_KEY=your_openai_api_key_here
AZURE_TTS_KEY=your_azure_tts_key_here
AZURE_TTS_REGION=your_region
YOUTUBE_API_KEY=your_youtube_api_key_here  # 선택
```

### 4. 실행
```bash
# SD WebUI 먼저 실행
cd ../stable-diffusion-webui
./webui.sh --port 7861

# 새 터미널에서 StoryMaker 실행
cd /Users/systemi/storymaker
streamlit run app.py
```

## 📚 상세 문서

- **[QUICKSTART.md](QUICKSTART.md)** - 5분 시작 가이드
- **[USER_GUIDE.md](USER_GUIDE.md)** - 전체 기능 설명
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 코드 구조
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 빠른 참조

### 개발 가이드 (docs/)
- **[AI_PROMPT_GENERATION.md](docs/AI_PROMPT_GENERATION.md)** - GPT 프롬프트 생성
- **[JAPANESE_BACKGROUND_GUIDE.md](docs/JAPANESE_BACKGROUND_GUIDE.md)** - 일본풍 이미지 설정
- **[SCENE_CONTEXT_EXTRACTION.md](docs/SCENE_CONTEXT_EXTRACTION.md)** - 씬 분석 로직
- **[MULTI_MODEL_SUPPORT.md](docs/MULTI_MODEL_SUPPORT.md)** - 멀티 모델 지원
- **[SD_WEBUI_SETTINGS_GUIDE.md](docs/SD_WEBUI_SETTINGS_GUIDE.md)** - SD WebUI 설정

## 🎬 사용 예시

### 일본어 감성 스토리
```
大本: 駅のホームで雨の音を聞いていました。
映像: 駅の待合室のベンチ、窓に雨粒、傘が壁に立てかけられている様子
```

### 한국어 감성 스토리
```
대본: 오래된 카페 창가에 앉아 따뜻한 커피를 마셨다.
영상: 나무 테이블 위의 커피 잔, 창밖으로 비 오는 거리, 뒷모습의 인물
```

## 🛠️ 기술 스택

- **UI**: Streamlit
- **TTS**: Azure Cognitive Services
- **Image**: Stable Diffusion WebUI API
- **Video**: MoviePy 2.x
- **AI**: OpenAI GPT-3.5
- **Analysis**: YouTube Data API v3

## ⚙️ 설정 팁

### 1. 실사 모델 설정 (권장)
```bash
cd stable-diffusion-webui/models/Stable-diffusion
# realisticVisionV60B1_v51VAE.safetensors 다운로드
# WebUI에서 모델 선택
```

### 2. 프롬프트 최적화
- `docs/AI_PROMPT_GENERATION.md` 참조
- 사물/오브젝트 중심 키워드 사용
- 건축물 키워드 회피

### 3. 자막 위치 조정
- 기본값: `position_y=850` (하단)
- 마진: `bottom=30, top=10`

### 4. 말하기 속도
- 느림: 0.8x (감성적)
- 보통: 1.0x (기본)
- 빠름: 1.2x (역동적)

## 📁 프로젝트 구조

```
storymaker/
├── app.py                    # Streamlit 메인 앱
├── requirements.txt          # Python 의존성
├── .env                      # 환경 변수 (생성 필요)
├── src/                      # 핵심 모듈
│   ├── config.py            # 설정 로더
│   ├── story_generator.py   # 스토리 생성
│   ├── tts_generator.py     # 음성 합성
│   ├── image_generator.py   # 이미지 생성 (SD WebUI)
│   ├── video_creator.py     # 영상 조립
│   ├── subtitle_generator.py # 자막 생성
│   └── trend_analyzer.py    # 트렌드 분석
├── docs/                     # 개발 문서
├── music/                    # 배경음악 파일
└── output/                   # 생성된 영상
```

## 🐛 문제 해결

### SD WebUI 연결 실패
```bash
# SD WebUI 실행 확인
curl http://127.0.0.1:7861/sdapi/v1/sd-models
```

### 자막 하단 잘림
- `subtitle_settings.py`에서 `position_y` 값 조정 (850 → 800)
- 또는 UI에서 "자막 설정" → "Y 위치" 조정

### 중국풍 이미지 생성됨
- 네거티브 프롬프트 자동 적용 확인
- `image_generator.py`의 `NEGATIVE_REALISTIC` 확인

### MoviePy 오류
```bash
# MoviePy 2.x 재설치
pip uninstall moviepy
pip install "moviepy>=2.0.0"
```

## 📄 라이센스

MIT License

## 🤝 기여

이슈와 PR은 언제나 환영합니다!

---

**최종 업데이트**: 2026년 1월 5일
**버전**: 1.0.0
