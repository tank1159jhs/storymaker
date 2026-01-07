# 🎨 AI 기반 프롬프트 생성 가이드

## ✅ 완료된 개선사항

### 1. **AI 프롬프트 생성 (GPT-3.5)**
- **하드코딩된 키워드 매핑 제거**
- OpenAI GPT-3.5를 사용하여 대본 → 영어 프롬프트 자동 생성
- 맥락을 이해하고 시각적 요소 추출

### 2. **2단계 폴백 시스템**
```
1차: AI 프롬프트 생성 (GPT-3.5)
  ↓ (실패 시)
2차: 키워드 매핑 (간소화된 하드코딩)
```

### 3. **AI 프롬프트 생성 규칙**
- ✅ 장소, 사물, 분위기, 조명, 시간대 추출
- ✅ 일본 배경/풍경 우선
- ✅ 사람은 **뒷모습/옆모습**만 (얼굴 제외)
- ✅ 시네마틱, 감성적 묘사
- ✅ 100단어 이내로 간결하게

---

## 📝 설정 방법

### 1. OpenAI API 키 발급
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 키 복사 (sk-... 형식)

### 2. `.env` 파일 설정
```bash
# Storymaker/.env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. 테스트 실행
```bash
cd /Users/systemi/storymaker
python3 test_ai_prompt.py
```

**예상 출력**:
```
✅ AI 프롬프트: Japanese train station waiting room, autumn morning light, 
wooden benches, nostalgic atmosphere, student silhouette from behind, 
cinematic composition, peaceful environment
```

---

## 🎯 사용 예시

### 대본 입력
```
고등학교 2학년 가을,
매일 아침 이용하던
동네 기차역 대합실입니다.
```

### AI 생성 프롬프트
```
Japanese train station waiting room, autumn season, morning light, 
wooden benches, platform visible through windows, nostalgic atmosphere, 
quiet peaceful environment, back view of student silhouette, 
cinematic composition
```

### 폴백 프롬프트 (AI 실패 시)
```
train station, waiting room, wooden bench, autumn season, morning light, 
student silhouette from behind
```

---

## 🔧 커스터마이징

### AI 프롬프트 규칙 변경
`src/image_generator.py` → `_generate_prompt_with_ai()` 함수의 `system_prompt` 수정

**예시**: 한국 배경으로 변경
```python
system_prompt = """...
Style: {image_style}
Rules:
1. Extract visual elements from Korean locations (Seoul, Busan, etc.)
2. Focus on Korean traditional architecture and modern cityscapes
...
"""
```

### 키워드 매핑 추가 (폴백용)
`src/image_generator.py` → `_extract_scene_keywords()` 함수의 딕셔너리 수정

```python
location_map = {
    '학교': 'school building',
    '교실': 'classroom',
    '복도': 'corridor',
    # 추가...
}
```

---

## 💰 비용 안내

### GPT-3.5 Turbo 요금
- **입력**: $0.50 / 1M tokens
- **출력**: $1.50 / 1M tokens

### 예상 비용 (1개 씬 = 5개 이미지)
- 1개 프롬프트 생성: ~200 tokens (입력 100 + 출력 100)
- 5개 이미지: ~1000 tokens
- **비용**: ~$0.001 (약 1.3원)

### 대안: API 키 없이 사용
`.env`에서 `OPENAI_API_KEY` 제거하거나 주석 처리:
```bash
# OPENAI_API_KEY=sk-...
```
→ 자동으로 키워드 매핑 폴백 사용

---

## 🚀 성능 비교

| 방식 | 정확도 | 속도 | 비용 | 확장성 |
|------|--------|------|------|--------|
| **AI (GPT-3.5)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 저렴 | ⭐⭐⭐⭐⭐ |
| **키워드 매핑** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 무료 | ⭐⭐ |

---

## 🐛 트러블슈팅

### 1. "OpenAI API 키 없음" 경고
**원인**: `.env`에 API 키가 없거나 잘못됨
**해결**: 
```bash
echo "OPENAI_API_KEY=sk-your-key" >> /Users/systemi/storymaker/.env
```

### 2. "OpenAI API 오류: 401"
**원인**: API 키가 만료되었거나 잘못됨
**해결**: https://platform.openai.com/api-keys 에서 새 키 발급

### 3. "OpenAI API 오류: 429"
**원인**: API 요청 한도 초과 (Rate Limit)
**해결**: 
- 잠시 대기 후 재시도
- 유료 플랜 업그레이드

### 4. 프롬프트가 맥락을 못 읽음
**원인**: GPT가 대본을 잘못 이해
**해결**: `system_prompt`에 더 구체적인 예시 추가

---

## 📊 디버깅 로그

Storymaker 실행 시 콘솔에서 확인:
```
[AI] GPT 프롬프트 생성 성공: Japanese train station...
[DEBUG] 대본 원문: 고등학교 2학년 가을, 매일 아침...
[DEBUG] 추출된 프롬프트: Japanese train station waiting room...
[DEBUG] 최종 프롬프트: Japanese train station waiting room, autumn...
```

---

## ✅ 최종 체크리스트

- [ ] OpenAI API 키 발급 및 `.env` 설정
- [ ] `test_ai_prompt.py` 실행 성공
- [ ] Storymaker에서 이미지 생성 시 AI 프롬프트 로그 확인
- [ ] 생성된 이미지가 대본 맥락을 정확히 반영하는지 확인
- [ ] 얼굴이 나오지 않고 뒷모습/옆모습만 나오는지 확인
