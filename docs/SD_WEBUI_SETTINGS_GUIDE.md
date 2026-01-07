# SD WebUI 설정과 Storymaker 연동 가이드

## 🎯 질문 요약

### Q1: 체크포인트 변경
> SD WebUI 웹사이트(http://127.0.0.1:7861)에서 체크포인트를 수동으로 바꾸면 Storymaker에 자동 반영되나요?

### Q2: Sampling Steps 변경
> SD WebUI에서 Sampling Steps를 20에서 30으로 바꾸면 자동 반영되나요?

---

## ✅ A1: 체크포인트 변경 (자동 반영됨)

### **맞습니다! 자동 반영됩니다.** ⭐

**동작 방식:**
```
1. SD WebUI 브라우저 열기 (http://127.0.0.1:7861)
2. 상단 "Checkpoint" 드롭다운 클릭
3. 모델 선택:
   - realisticVisionV51_v51VAE (실사)
   - japaneseDollLikeness (애니메이션)
4. Storymaker에서 이미지 생성
5. ✅ 선택한 체크포인트로 이미지 생성됨
```

**이유:**
- Storymaker는 **SD WebUI REST API**를 호출합니다
- SD WebUI가 **현재 로드된 체크포인트**로 이미지를 생성합니다
- Storymaker 코드 수정 불필요 ✅

**주의사항:**
- ⚠️ SD WebUI **재시작 시** `modules/sd_models.py`에 하드코딩된 모델 로드
- 현재 설정: `realisticVisionV51_v51VAE.safetensors` (없으면 `japaneseDollLikeness.safetensors`)
- 💡 재시작 후에는 **수동으로 다시 변경** 필요

---

## ❌ A2: Sampling Steps 변경 (자동 반영 안 됨)

### **자동 반영되지 않습니다!** ⚠️

**이유:**
- Storymaker 소스 코드에 **하드코딩**되어 있습니다
- SD WebUI 웹사이트 설정은 **브라우저에서 수동 생성할 때만** 사용됩니다
- Storymaker는 REST API를 통해 **자체 파라미터**를 전달합니다

**하드코딩 위치:**
```python
# src/image_generator.py
def _generate_single_image(..., steps=20, sampler_name="DPM++ 2M", cfg_scale=7.0):
    payload = {
        "steps": steps,  # 항상 20 (이전 설정)
        "sampler_name": sampler_name,
        "cfg_scale": cfg_scale
    }
```

---

## ✅ 해결책: Storymaker UI에 설정 추가

### **완료! 이제 Storymaker에서 직접 조절 가능합니다.** 🎉

**추가된 UI (고급 설정):**

```
⚙️ 고급 설정 (SD WebUI API)
┌─────────────────────────────────────────────────────┐
│ 🎚️ Sampling Steps: 20 [슬라이더: 10~50]            │
│ 🔧 Sampler: DPM++ 2M [드롭다운]                     │
│ 🎛️ CFG Scale: 7.0 [슬라이더: 1.0~15.0]             │
│                                                     │
│ 💡 팁: 기본값(Steps=20, Sampler=DPM++ 2M, CFG=7.0)│
│      이 대부분의 경우 최적입니다.                   │
│      - Steps ↑ → 품질 향상, 시간 증가               │
│      - CFG Scale ↑ → 프롬프트 정확도 향상          │
└─────────────────────────────────────────────────────┘
```

### **사용 방법:**

1. **Storymaker 실행**
   ```bash
   cd /Users/systemi/storymaker
   streamlit run app.py
   ```

2. **3. 이미지 준비 → AI로 자동 생성** 선택

3. **⚙️ 고급 설정** 클릭 (접힌 상태)

4. **원하는 값 조절:**
   - Sampling Steps: 10~50 (기본: 20)
   - Sampler: DPM++ 2M / Euler a / DDIM 등
   - CFG Scale: 1.0~15.0 (기본: 7.0)

5. **🎨 모든 씬 이미지 생성 시작** 클릭

6. ✅ **설정한 값으로 이미지 생성됨!**

---

## 📊 비교: SD WebUI 설정 vs Storymaker 설정

| 설정 항목 | SD WebUI 웹사이트 | Storymaker UI |
|-----------|-------------------|---------------|
| **Checkpoint** | ✅ 자동 반영 | ⚠️ 간접 반영 (SD WebUI 설정) |
| **Sampling Steps** | ❌ 무시됨 | ✅ **직접 설정** (신규 추가) |
| **Sampler** | ❌ 무시됨 | ✅ **직접 설정** (신규 추가) |
| **CFG Scale** | ❌ 무시됨 | ✅ **직접 설정** (신규 추가) |
| **Width/Height** | ❌ 무시됨 | ⚠️ 하드코딩 (768x512) |

---

## 🎨 추천 설정

### **일반 실사 배경 (빠른 생성)**
```
Checkpoint: realisticVisionV51_v51VAE
Steps: 20
Sampler: DPM++ 2M
CFG Scale: 7.0
```

### **고품질 시네마틱 배경**
```
Checkpoint: deliberate_v2
Steps: 30
Sampler: DPM++ 2M Karras
CFG Scale: 8.0
```

### **애니메이션 스타일**
```
Checkpoint: japaneseDollLikeness (수동 변경)
Steps: 20
Sampler: DPM++ 2M
CFG Scale: 7.0
```

---

## 🔧 체크포인트 변경 방법 (상세)

### **방법 1: SD WebUI 웹사이트에서 변경 (임시)** ⭐

```
1. SD WebUI 브라우저 열기:
   http://127.0.0.1:7861

2. 상단 "Checkpoint" 드롭다운 클릭

3. 모델 선택:
   - realisticVisionV51_v51VAE.safetensors (실사)
   - japaneseDollLikeness.safetensors (애니메이션)

4. Storymaker에서 이미지 생성
   → 선택한 모델로 생성 ✅

⚠️ 주의: SD WebUI 재시작 시 초기화됨
```

### **방법 2: sd_models.py 수정 (영구)**

영구적으로 기본 모델을 변경하려면:

```python
# /Users/systemi/stable-diffusion-webui/modules/sd_models.py

# 메인 모델 설정 (실사)
MODEL_FILENAME = os.path.abspath(os.path.join(
    paths.models_path, 
    "Stable-diffusion", 
    "realisticVisionV51_v51VAE.safetensors"  # 원하는 모델
))

# Fallback 모델 (애니메이션)
FALLBACK_MODEL = os.path.abspath(os.path.join(
    paths.models_path, 
    "Stable-diffusion", 
    "japaneseDollLikeness.safetensors"
))
```

---

## 🎯 japaneseDollLikeness 파일 관리

### **권장: 그냥 두세요! (Fallback용)** ✅

```bash
# 권장 폴더 구조
/Users/systemi/stable-diffusion-webui/models/Stable-diffusion/
├── realisticVisionV51_v51VAE.safetensors  # ⭐ 메인 (실사)
└── japaneseDollLikeness.safetensors       # 🔄 백업 (애니메이션)
```

**이유:**
1. ✅ **Fallback 보험**: 메인 모델 문제 시 자동으로 Fallback 사용
2. ✅ **애니메이션 스타일 필요 시**: SD WebUI에서 수동 변경 가능
3. ✅ **용량 2GB**: 큰 부담 아님

**삭제해도 되는 경우:**
- ❌ 애니메이션 스타일 100% 불필요
- ❌ 저장 공간 부족 (2GB 필요)

---

## 🚀 최종 워크플로우

### **Step 1: SD WebUI 실행**
```bash
cd /Users/systemi/stable-diffusion-webui
./webui.sh --api --listen --port 7861
```

### **Step 2: 체크포인트 확인 (선택사항)**
```
브라우저: http://127.0.0.1:7861
Checkpoint: realisticVisionV51_v51VAE (기본값)
```

### **Step 3: Storymaker 실행**
```bash
cd /Users/systemi/storymaker
streamlit run app.py
```

### **Step 4: 이미지 생성 설정**
```
1. 대본 입력
2. 3. 이미지 준비 → AI로 자동 생성
3. 🎨 이미지 스타일: realistic (또는 cinematic)
4. ⚙️ 고급 설정 (선택):
   - Steps: 20 (기본) 또는 30 (고품질)
   - Sampler: DPM++ 2M (기본)
   - CFG Scale: 7.0 (기본)
5. 🎨 모든 씬 이미지 생성 시작
```

### **Step 5: 결과 확인**
```
✅ 실사 일본 배경 이미지 생성 완료!
```

---

## 📝 요약

### ✅ **체크포인트 변경**
- SD WebUI 웹사이트에서 수동 변경 → **자동 반영** ✅
- Storymaker 코드 수정 불필요

### ✅ **Sampling Steps/Sampler/CFG Scale**
- SD WebUI 설정 → **무시됨** ❌
- **Storymaker UI에서 직접 설정** → **반영됨** ✅ (신규 추가)

### ✅ **japaneseDollLikeness**
- **권장: 그냥 두기** (Fallback용)
- 필요 시 SD WebUI에서 수동 변경 가능

---

**제작일**: 2026년 1월 2일  
**목적**: SD WebUI와 Storymaker 연동 이해  
**핵심**: SD WebUI 설정 vs Storymaker 설정 구분
