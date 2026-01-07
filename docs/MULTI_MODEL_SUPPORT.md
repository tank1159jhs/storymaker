# 스타일별 모델 자동 전환 (Multi-Model Support)

## 📋 개요
이미지 스타일(realistic, cinematic, anime 등)에 따라 자동으로 적절한 체크포인트 모델을 선택합니다.

## 🎯 필요한 모델

1. **Realistic Vision V5.1** → `realistic`, `semi-realistic` 스타일
2. **Deliberate V2** → `cinematic` 스타일
3. **japaneseDollLikeness** → `anime` 스타일

## ⚙️ 구현 방법

### 1. `modules/sd_models.py` 수정

현재 하드코딩된 `MODEL_FILENAME`을 동적으로 변경:

```python
# lean: 스타일별 모델 매핑
STYLE_MODEL_MAP = {
    "realistic": "realisticVisionV51_v51VAE.safetensors",
    "cinematic": "deliberate_v2.safetensors",
    "anime": "japaneseDollLikeness.safetensors",
    "semi-realistic": "chilloutmix_NiPrunedFp32Fix.safetensors"
}

# 기본 모델 (fallback)
DEFAULT_MODEL = "japaneseDollLikeness.safetensors"

def get_model_path(style="anime"):
    """스타일에 맞는 모델 경로 반환"""
    model_filename = STYLE_MODEL_MAP.get(style, DEFAULT_MODEL)
    model_path = os.path.join(paths.models_path, "Stable-diffusion", model_filename)
    
    if not os.path.exists(model_path):
        print(f"⚠️ 모델 없음: {model_filename}, 기본 모델 사용: {DEFAULT_MODEL}")
        model_path = os.path.join(paths.models_path, "Stable-diffusion", DEFAULT_MODEL)
    
    return model_path

# 현재 로드된 모델 추적
_current_model = None
_current_style = None

def load_model(style="anime"):
    """스타일에 맞는 모델 로드 (캐싱 지원)"""
    global _current_model, _current_style
    
    # 이미 로드된 모델이면 재사용
    if _current_model is not None and _current_style == style:
        return _current_model
    
    model_path = get_model_path(style)
    print(f"🎨 스타일: {style} → 모델 로드: {os.path.basename(model_path)}")
    
    # ... (기존 로드 로직)
    
    _current_model = model
    _current_style = style
    return model
```

### 2. `modules/api/api.py` 수정

API에 `style` 파라미터 추가:

```python
def text2imgapi(self, txt2imgreq: StableDiffusionTxt2ImgProcessingAPI):
    # 스타일 파라미터 추출
    style = getattr(txt2imgreq, 'style', 'anime')
    
    # 스타일에 맞는 모델 로드
    from modules import sd_models
    sd_models.load_model(style)
    
    # ... (기존 처리)
```

### 3. `src/image_generator.py` 수정

SD WebUI API 호출 시 `style` 전달:

```python
def generate_images_with_sdwebui(prompt, num_images=5, style="realistic"):
    # API 페이로드에 style 추가
    payload = {
        "prompt": full_prompt,
        "negative_prompt": negative_prompt,
        "style": style,  # ⭐ 추가
        # ... 기존 설정
    }
    
    response = requests.post(
        "http://127.0.0.1:7861/sdapi/v1/txt2img",
        json=payload
    )
```

## 🚀 사용 예시

### Before (현재)
```python
# 항상 japaneseDollLikeness 사용
generate_images_with_sdwebui(prompt, style="realistic")
# → 애니메이션 이미지 생성 (모델 안 바뀜)
```

### After (개선)
```python
# 스타일에 따라 자동 모델 전환
generate_images_with_sdwebui(prompt, style="realistic")
# → Realistic Vision V5.1 모델 로드
# → 실사 이미지 생성 ✅

generate_images_with_sdwebui(prompt, style="cinematic")
# → Deliberate V2 모델 로드
# → 시네마틱 이미지 생성 ✅
```

## ⚠️ 주의사항

1. **모델 로딩 시간**: 모델 전환 시 10-30초 소요
2. **메모리 사용**: 한 번에 하나의 모델만 로드 (메모리 절약)
3. **캐싱**: 같은 스타일 연속 사용 시 재로드 안 함

## 📂 필요한 파일

다운로드 후 아래 위치에 배치:

```
/Users/systemi/stable-diffusion-webui/models/Stable-diffusion/
├── japaneseDollLikeness.safetensors (기존)
├── realisticVisionV51_v51VAE.safetensors (다운로드 필요)
├── deliberate_v2.safetensors (다운로드 필요)
└── chilloutmix_NiPrunedFp32Fix.safetensors (선택사항)
```

## 🔧 구현 완료 후 확인

```bash
# 1. 모델 파일 확인
ls -lh /Users/systemi/stable-diffusion-webui/models/Stable-diffusion/

# 2. SD WebUI 재시작
cd /Users/systemi/stable-diffusion-webui
./webui.sh --port 7861

# 3. Storymaker에서 테스트
# - 스타일: realistic 선택
# - 이미지 생성
# - 실사 이미지 확인 ✅
```
