# 최종 테스트 가이드

2026년 1월 5일 - 코드 정리 후 최종 검증

## ✅ 완료된 작업 요약

### 1. 자막 시스템 개선
- ✅ 하단 잘림 현상 해결 (`method='label'` + 마진 추가)
- ✅ 보수적 높이 계산 (폰트 크기 × 1.5 × 줄 수)
- ✅ 안전 마진 확대 (bottom=30, top=10)

### 2. 배경음악(BGM) 시스템
- ✅ MoviePy 2.x 호환 (`with_subclip` → `subclipped`)
- ✅ 자동 루프 기능
- ✅ 로그 간소화 (15줄 → 3줄)

### 3. 말하기 속도 파라미터
- ✅ `voice_speed` 정확히 전달
- ✅ 반환값 개수 일치 (3개: audio_path, timings, processed_script)

### 4. 일본어 대본 지원
- ✅ GPT 프롬프트 생성 (한국어/일본어/영어)
- ✅ 사물/오브젝트 중심 이미지 생성
- ✅ 중국풍 건축 차단 (네거티브 프롬프트)
- ✅ 일본어 폴백 키워드 맵

### 5. 코드 정리
- ✅ 개발 문서 12개 삭제
- ✅ 테스트 파일 6개 삭제
- ✅ 백업 파일 3개 삭제
- ✅ 로그 간소화 (image_generator, video_creator, app)
- ✅ 레거시 함수 제거
- ✅ README.md 업데이트

## 🧪 필수 테스트 항목

### Test 1: 일본어 대본 + 사물 중심 이미지
**목적**: 일본어 지원 및 중국풍 차단 확인

**대본 예시**:
```
駅のホームで雨の音を聞いていました。
古い喫茶店で、温かいコーヒーを飲んでいました。
```

**예상 결과**:
- ✅ 일본어 음성 합성 성공 (Azure TTS)
- ✅ 이미지: 우산, 벤치, 커피 잔 등 사물 중심
- ✅ 중국풍 건축물 없음 (기와, 붉은 기둥, 용 문양 등)
- ✅ 뒷모습/옆모습만 (얼굴 없음)

**테스트 방법**:
```bash
streamlit run app.py
# 2단계에서 위 대본 입력
# 화자: ja-JP-NanamiNeural (일본어 여성)
# 이미지 스타일: realistic
```

---

### Test 2: 자막 하단 잘림 확인
**목적**: 자막 위치 및 마진 검증

**테스트 대본**:
```
긴 자막 테스트입니다. 이것은 매우 긴 문장으로 자막이 여러 줄에 걸쳐 표시될 가능성이 있습니다.
```

**예상 결과**:
- ✅ 자막이 화면 하단에서 잘리지 않음
- ✅ 마진이 적용되어 있음 (bottom=30, top=10)
- ✅ 여러 줄 자막도 정상 표시

**확인 방법**:
1. 영상 생성 후 `output/[timestamp]/final_video.mp4` 재생
2. 자막 하단이 화면 밖으로 잘리는지 확인
3. 필요시 UI에서 "자막 설정" → "Y 위치" 조정 (850 → 800)

---

### Test 3: 배경음악(BGM) 루프
**목적**: 짧은 BGM이 자동 루프되는지 확인

**테스트 조건**:
- 대본: 3개 씬 (약 30초 이상)
- BGM: 짧은 곡 선택 (15초 이하)

**예상 결과**:
- ✅ BGM이 영상 끝까지 반복됨
- ✅ 볼륨 조절 정상 (0.3)
- ✅ 로그 간소화 (3줄만 출력)

**확인 방법**:
```bash
# 로그 확인
cat output/[timestamp]/debug_log.txt  # 있다면

# BGM 길이 vs 영상 길이 비교
ffprobe output/[timestamp]/final_video.mp4
```

---

### Test 4: 말하기 속도 조절
**목적**: 느림/보통/빠름 속도가 정확히 적용되는지 확인

**테스트 조건**:
- 동일 대본 3번 실행
- 속도: 느림 → 보통 → 빠름

**예상 결과**:
- ✅ 느림: 음성 길이 약 25% 증가
- ✅ 보통: 기본 길이
- ✅ 빠름: 음성 길이 약 20% 감소
- ✅ 자막 타이밍이 음성과 동기화

**확인 방법**:
```python
# 터미널에서 음성 파일 길이 확인
ffprobe -i output/[timestamp]/narration_scene_1_*.mp3 -show_entries format=duration -v quiet -of csv="p=0"
```

---

### Test 5: GPT 프롬프트 생성
**목적**: OpenAI API를 통한 프롬프트 자동 생성 확인

**전제 조건**:
- `.env` 파일에 `OPENAI_API_KEY` 설정됨

**테스트 대본**:
```
雨の日、駅の待合室で一人で座っていた。
```

**예상 결과**:
- ✅ GPT가 사물 중심 프롬프트 생성
- ✅ "rain droplets on window", "wooden bench", "umbrella" 등
- ✅ 건축물 키워드 없음 ("shrine", "temple", "traditional house" 회피)

**로그 확인**:
```
[AI] GPT 프롬프트 생성 성공: rain droplets on window glass, wooden...
```

---

## 🚨 알려진 이슈 및 해결 방법

### Issue 1: SD WebUI 연결 실패
**증상**: `requests.exceptions.ConnectionError`

**해결**:
```bash
# SD WebUI 실행 확인
curl http://127.0.0.1:7861/sdapi/v1/sd-models

# 포트가 다르면 src/config.py 수정
SD_API_URL = "http://127.0.0.1:7861/sdapi/v1/txt2img"
```

---

### Issue 2: 일본어 음성 안 나옴
**증상**: Azure TTS 오류

**해결**:
```bash
# .env 파일 확인
AZURE_TTS_KEY=your_key_here
AZURE_TTS_REGION=koreacentral

# 지원 화자 확인
python -c "from src.tts_generator import get_available_voices; print(get_available_voices('ja-JP'))"
```

---

### Issue 3: 중국풍 이미지가 생성됨
**증상**: 기와, 붉은 기둥, 용 문양 등

**해결**:
1. `src/image_generator.py` → `NEGATIVE_REALISTIC` 확인
2. 네거티브 프롬프트에 다음 포함 여부 확인:
   ```
   Chinese architecture, pagoda, Chinese temple, red pillars, dragon motifs
   ```
3. SD WebUI에서 "Realistic Vision V6.0" 모델 사용 중인지 확인

---

### Issue 4: 자막이 여전히 잘림
**증상**: 하단 자막 일부가 보이지 않음

**해결**:
```python
# subtitle_settings.py에서 조정
DEFAULT_SUBTITLE_SETTINGS = {
    'position_y': 800,  # 850 → 800으로 변경 (더 위로)
    # ...
}
```

또는 UI에서:
1. "자막 설정" 열기
2. "Y 위치" 슬라이더를 800으로 조정
3. 영상 재생성

---

## 📊 성능 벤치마크

### 예상 처리 시간 (3개 씬 기준)
- **트렌드 분석**: ~10초 (선택)
- **스토리 생성**: ~5초 (GPT-4)
- **음성 합성**: ~3초/씬 (Azure TTS)
- **이미지 생성**: ~10초/씬 (SD WebUI, RTX 4090 기준)
- **영상 조립**: ~5초

**총 예상 시간**: 약 1분 30초

### 리소스 사용량
- **CPU**: 중간 (MoviePy 처리)
- **GPU**: 높음 (SD WebUI)
- **RAM**: ~4GB
- **디스크**: ~50MB/영상

---

## ✅ 최종 체크리스트

테스트 완료 후 아래 항목을 확인하세요:

- [ ] 일본어 대본으로 영상 생성 성공
- [ ] 이미지에 사물/오브젝트 중심 구도 확인
- [ ] 중국풍 건축물 없음 확인
- [ ] 자막 하단 잘림 없음 확인
- [ ] BGM 자동 루프 동작 확인
- [ ] 말하기 속도 조절 동작 확인
- [ ] GPT 프롬프트 생성 동작 확인 (OpenAI API 설정 시)
- [ ] 로그가 간소화되어 출력됨 확인
- [ ] README.md 문서 업데이트 확인

---

## 🎉 테스트 완료 후

모든 테스트가 통과하면:

1. **Git 커밋**:
   ```bash
   git add .
   git commit -m "코드 정리 및 최종 검증 완료 (2026-01-05)"
   ```

2. **프로덕션 배포**:
   ```bash
   # 실제 사용자에게 배포
   ```

3. **문서 공유**:
   - README.md 공유
   - USER_GUIDE.md 사용자에게 전달
   - QUICKSTART.md로 빠른 시작 가이드 제공

---

**테스트 담당자**: _____________________
**테스트 날짜**: _____________________
**통과 여부**: ⬜ PASS  ⬜ FAIL
**비고**: _____________________
