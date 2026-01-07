# 🎯 장면 맥락 인식 이미지 생성 시스템

## 문제점
기존 시스템은 **한국어 대본을 그대로** SD WebUI에 전달하여 맥락 없는 이미지가 생성됨:
- "안녕하세요. 오늘은 특별한..." → 의미 없는 동양 궁전
- "고등학교 2학년 가을..." → 30대 남성 얼굴
- "벤치 창가 쪽에는..." → 얼굴이 보이는 두 여자

## ✅ 해결책: 장면 키워드 추출 시스템

### 1. **한국어 → 영어 키워드 자동 변환**

```python
def _extract_scene_keywords(text):
    """대본에서 장면 요소를 추출하여 SD-friendly 프롬프트로 변환"""
```

### 2. **키워드 매핑 사전**

#### 🏞️ 장소/배경 키워드 (40개)
| 한국어 | 영어 프롬프트 |
|--------|---------------|
| 기차역, 역 | train station, station |
| 대합실 | waiting room |
| 벤치 | wooden bench |
| 창가 | window side, near window |
| 우산 | umbrella |
| 비 | rain, rainy weather, wet ground |
| 교복 | school uniform |
| 여학생 | female student from behind |
| 책 | book |
| 아침 | morning light, early morning |
| 가을 | autumn season |
| 기차 | train |
| 철도 | railway, railroad tracks |

#### 🎭 분위기/감정 키워드 (12개)
| 한국어 | 영어 프롬프트 |
|--------|---------------|
| 조용 | quiet, peaceful |
| 허전 | empty atmosphere, lonely |
| 그리움 | nostalgic |
| 기억, 추억 | memory, reminiscence |
| 감성 | emotional, sentimental |
| 특별 | special moment |

### 3. **프롬프트 생성 흐름**

```
대본 입력:
"고등학교 2학년 가을,
매일 아침 이용하던
동네 기차역 대합실입니다."

↓ 키워드 추출

추출된 키워드:
"autumn season, morning light, early morning, train station, waiting room"

↓ 스타일 프롬프트 추가

최종 프롬프트 (Cinematic):
"autumn season, morning light, early morning, train station, waiting room, 
cinematic, movie scene, film still, Japanese atmosphere, dramatic lighting, 
back view, silhouette, from behind, nostalgic atmosphere, emotional, 
background focus, no face visible, faceless"
```

### 4. **예상 결과**

#### 씬 1-1 (인트로)
**대본**: "특별한 사건이 있는 이야기는 아닙니다. 조용히 남아 있던..."
**키워드**: `quiet, peaceful, remaining, special moment`
**이미지**: 조용한 일본 풍경, 감성적 분위기

#### 씬 1-2 (기차역)
**대본**: "고등학교 2학년 가을, 매일 아침 이용하던 동네 기차역 대합실"
**키워드**: `autumn season, morning light, train station, waiting room`
**이미지**: 가을 아침 기차역 대합실 내부

#### 씬 1-3 (벤치와 여학생)
**대본**: "항상 같은 벤치. 그 벤치 창가 쪽에는 늘 한 여학생이..."
**키워드**: `wooden bench, window side, female student from behind, school uniform`
**이미지**: 창가 벤치에 앉은 여학생 뒷모습 (교복)

#### 씬 1-4 (책)
**대본**: "단정한 교복, 무릎 위에 올려둔 책, 기차가 들어올 때마다..."
**키워드**: `school uniform, book, train`
**이미지**: 책을 든 학생의 뒷모습, 배경에 기차

#### 씬 1-5 (비오는 날)
**대본**: "비가 억수같이 쏟아지던 날이 있었습니다. 우산을 펴며..."
**키워드**: `rain, rainy weather, wet ground, umbrella`
**이미지**: 비 오는 역, 우산, 젖은 바닥

## 🎨 스타일별 프롬프트 강화

### Realistic
```
키워드 + photorealistic, realistic photography, Japanese scenery, 
natural lighting, 8k, back view, side view, atmospheric, 
background focus, no face visible, faceless
```

### Cinematic
```
키워드 + cinematic, movie scene, film still, Japanese atmosphere, 
dramatic lighting, film grain, depth of field, back view, silhouette, 
nostalgic atmosphere, emotional, storytelling, no face visible
```

### Semi-realistic
```
키워드 + semi-realistic, Japanese style, detailed background, 
beautiful lighting, soft realistic textures, back view, faceless
```

## 🚫 네거티브 프롬프트 강화

**얼굴 완전 차단**:
```
face, faces, portrait, portraits, frontal view, front view, 
looking at camera, facing camera, facing viewer, eye contact, 
close-up face, detailed face, facial features, head shot, headshot, 
person facing forward, direct gaze, looking forward, human face, 
character face, visible face
```

## 📊 디버깅 출력

```
[DEBUG] 스타일: cinematic
[DEBUG] 대본 원문: 고등학교 2학년 가을, 매일 아침 이용하던...
[DEBUG] 추출된 키워드: autumn season, morning light, train station, waiting room
[DEBUG] 고급 설정: Steps=20, Sampler=DPM++ 2M, CFG=7.0
[DEBUG] 최종 프롬프트: autumn season, morning light, train station, waiting room, cinematic, movie scene...
[DEBUG] 네거티브: EasyNegative, bad-hands-5, lowres... face, faces, portrait...
```

## ✅ 개선 효과

### Before
- ❌ 한국어 대본 그대로 전달 → 맥락 없는 이미지
- ❌ "안녕하세요" → 동양 궁전
- ❌ "고등학교" → 30대 남성
- ❌ "벤치에 앉은" → 정면 얼굴

### After
- ✅ 키워드 추출 → 맥락 있는 영어 프롬프트
- ✅ "기억, 조용" → 감성적 일본 풍경
- ✅ "가을, 아침, 기차역" → 가을 아침 기차역
- ✅ "벤치, 창가, 여학생" → 창가 벤치 뒷모습 (얼굴 없음)

## 🎯 결론

1. **맥락 이해**: 대본에서 장면 요소를 정확히 추출
2. **SD 최적화**: 영어 키워드로 변환 + 스타일 프롬프트
3. **얼굴 제거**: 뒷모습/옆모습만 허용 → 배경/분위기 강조
4. **일관성**: 같은 대본 → 같은 장면 요소 → 일관된 이미지

이제 **대본의 맥락을 정확히 반영한 감성적인 이미지**가 생성됩니다! 🎬✨
