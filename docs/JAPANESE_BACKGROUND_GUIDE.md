# 일본 배경/사물 실사 모델 가이드 🗾

## 🎯 목적
**일본 스토리 동영상** 제작 시 필요한 요소:
- ✅ **일본 거리, 건물, 풍경** (교토, 도쿄, 시골)
- ✅ **전통 건축물** (신사, 사찰, 전통 가옥)
- ✅ **자연 풍경** (벚꽃, 단풍, 설경, 바다, 산)
- ✅ **실내 사물** (다다미, 쇼지문, 차 세트, 제등)
- ❌ **얼굴/인물 불필요** (배경만 필요)

## ⚠️ 현재 문제
**japaneseDollLikeness** 모델은 애니메이션 전용:
- `realistic` 스타일 선택 → 애니메이션 배경 생성 ❌
- `cinematic` 스타일 선택 → 애니메이션 배경 생성 ❌
- 프롬프트만으로는 실사 변환 불가능

## ✅ 해결책

### 1단계: 실사 모델 다운로드 (필수)

**추천: Realistic Vision V5.1** (일본 배경 최적)

```bash
# 1. CivitAI에서 다운로드 (무료 회원가입 필요)
https://civitai.com/models/4201/realistic-vision-v51

# 2. 다운로드한 파일 이동
mv ~/Downloads/realisticVisionV51_v51VAE.safetensors \
   /Users/systemi/stable-diffusion-webui/models/Stable-diffusion/

# 3. SD WebUI 재시작
cd /Users/systemi/stable-diffusion-webui
./webui.sh --port 7861
```

### 2단계: 모델 변경

SD WebUI 브라우저에서:
1. http://127.0.0.1:7861 열기
2. 상단 **Checkpoint** 드롭다운 클릭
3. `realisticVisionV51_v51VAE` 선택
4. Storymaker에서 이미지 생성 (`realistic` 스타일)

## 🎨 일본 배경 프롬프트 예시

### 🏘️ 전통 거리 (교토, 시골)
```
Japanese traditional street, Kyoto style, old wooden buildings, 
stone pavement, paper lanterns, morning light, photorealistic, 
8k, highly detailed, no people
```

### 🏯 신사/사찰
```
Japanese shrine, torii gate, stone lanterns, autumn leaves, 
moss-covered stones, peaceful atmosphere, natural lighting, 
photorealistic, no people
```

### 🌸 자연 풍경 (계절별)
```
# 봄 - 벚꽃
Japanese cherry blossom trees, sakura petals falling, 
traditional path, spring season, photorealistic

# 가을 - 단풍
Japanese autumn forest, red maple leaves, traditional bridge, 
peaceful stream, fall colors, cinematic lighting

# 겨울 - 설경
Japanese village in snow, traditional houses with snow-covered roofs, 
winter landscape, realistic
```

### 🏠 실내 사물
```
Traditional Japanese room, tatami floor, shoji screen, sliding door, 
natural light through window, minimalist interior, photorealistic
```

```
Japanese tea ceremony room, matcha bowl, bamboo whisk, wooden table, 
traditional atmosphere, soft lighting, highly detailed objects
```

### 🌃 도시 풍경
```
Tokyo street at night, neon signs, rain reflections on pavement, 
urban landscape, city lights, cinematic lighting, photorealistic
```

### 🎋 전통 사물 (클로즈업)
```
Japanese stone lantern, moss-covered, garden setting, 
detailed texture, natural lighting, macro photography, 8k
```

```
Japanese paper lantern (chochin), red and white, traditional design, 
hanging, soft glow, night scene, photorealistic
```

## 💡 프롬프트 작성 팁

### ✅ 추가하면 좋은 키워드 (배경 특화)
- **품질**: `photorealistic`, `8k`, `highly detailed`, `realistic photography`
- **사람 제거**: `no people`, `empty`, `uninhabited`, `deserted`
- **조명**: `natural lighting`, `golden hour`, `soft light`, `dramatic lighting`
- **분위기**: `peaceful`, `nostalgic`, `cinematic`, `atmospheric`
- **시점**: `landscape photography`, `architectural photography`, `product shot`

### ❌ 피해야 할 키워드
- **사람 관련**: `person`, `people`, `face`, `portrait`, `character`, `human`
- **애니메이션**: `anime`, `cartoon`, `illustration`, `2D`
- **저품질**: `low quality`, `blurry`, `pixelated`

## 🎬 실전 예시

### 스토리: 老人の思い出 (노인의 추억)

**씬 1: 고향 마을**
```
대본: "昔々、京都の小さな村に住んでいました"
프롬프트: Japanese traditional village, Kyoto, old wooden houses, 
          stone walls, peaceful atmosphere, morning light, 
          photorealistic, no people
결과: ✅ 실사 교토 시골 마을
```

**씬 2: 벚꽃 계절**
```
대본: "春になると、桜が満開になりました"
프롬프트: Japanese cherry blossom trees, sakura in full bloom, 
          traditional street, spring season, pink petals falling, 
          peaceful, photorealistic, no people
결과: ✅ 실사 벚꽃 거리
```

**씬 3: 신사 방문**
```
대본: "神社に行って、昔のことを思い出しました"
프롬프트: Japanese shrine interior, wooden pillars, stone floor, 
          torii gate in background, peaceful atmosphere, 
          natural lighting, photorealistic, no people
결과: ✅ 실사 신사 내부
```

**씬 4: 해변 석양**
```
대본: "夕方、海辺を歩いていました"
프롬프트: Japanese beach at sunset, torii gate in water, 
          orange sky, peaceful ocean, dramatic lighting, 
          landscape photography, no people
결과: ✅ 실사 일본 해변 석양
```

## 📊 비교 결과

| 요소 | japaneseDollLikeness | Realistic Vision V5.1 |
|------|----------------------|----------------------|
| 일본 거리 | 애니메이션 스타일 ❌ | 실사 사진 ✅ |
| 전통 건축물 | 일러스트 느낌 ❌ | 사진 품질 ✅ |
| 자연 풍경 | 그림 같은 느낌 ❌ | 실제 사진 ✅ |
| 실내 사물 | 만화 느낌 ❌ | 제품 사진 ✅ |
| 생성 속도 | 빠름 ⚡ | 빠름 ⚡ |
| macOS 지원 | 우수 ✅ | 우수 ✅ |

## 🚀 시작하기

### 최소 필요 사항
1. ✅ **Realistic Vision V5.1** 모델 다운로드 (~2.1GB)
2. ✅ SD WebUI에서 체크포인트 변경
3. ✅ Storymaker에서 `realistic` 스타일 선택

### 추가 옵션 (선택사항)
- **Deliberate V2**: 더 드라마틱한 시네마틱 배경
- **DreamShaper 8**: 빠른 생성 속도, 다목적

## 📂 다운로드 가이드
자세한 내용: `/Users/systemi/stable-diffusion-webui/DOWNLOAD_REALISTIC_MODELS.md`

## 🆘 문제 해결

**Q: CivitAI 링크가 안 열려요**
→ 무료 회원가입 필요 (5분 소요)

**Q: 파일이 너무 커요 (2GB)**
→ pruned 버전 선택 (2.1GB, 품질 동일)

**Q: macOS에서 생성이 느려요**
→ 정상입니다 (CUDA보다 느림, 하지만 품질 동일)

**Q: 사람이 자꾸 나와요**
→ 네거티브 프롬프트에 `people, person, face, portrait` 추가

**Q: 애니메이션 느낌이 남아있어요**
→ 모델을 제대로 변경했는지 확인 (SD WebUI 상단 체크포인트)

## ⏭️ 다음 단계 (향후 개선)

**자동 모델 전환** (코드 수정으로 가능):
```python
# 스타일별 자동 모델 선택
- realistic → Realistic Vision V5.1
- cinematic → Deliberate V2
- anime → japaneseDollLikeness
```

**현재는 수동 변경 필요** (SD WebUI에서 체크포인트 선택)

---

**제작**: 2026년 1월 2일
**목적**: 일본 스토리 동영상 제작용 실사 배경 이미지 생성
**핵심**: 배경/풍경/사물 중심, 얼굴/인물 제외
