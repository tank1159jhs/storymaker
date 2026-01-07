#!/bin/bash
# Storymaker AI 프롬프트 생성 퀵스타트

echo "🎨 Storymaker AI 프롬프트 생성 설정"
echo "====================================="
echo ""

# 1. OpenAI API 키 확인
if grep -q "OPENAI_API_KEY=sk-" /Users/systemi/storymaker/.env 2>/dev/null; then
    echo "✅ OpenAI API 키가 설정되어 있습니다."
    echo "   → AI 프롬프트 생성이 활성화됩니다."
else
    echo "⚠️  OpenAI API 키가 없습니다."
    echo "   → 키워드 매핑 폴백 사용"
    echo ""
    echo "📝 설정 방법:"
    echo "   1. https://platform.openai.com/api-keys 접속"
    echo "   2. 'Create new secret key' 클릭"
    echo "   3. 아래 명령어 실행:"
    echo ""
    echo "      echo 'OPENAI_API_KEY=sk-your-key' >> /Users/systemi/storymaker/.env"
    echo ""
fi

# 2. 테스트 실행
echo ""
echo "🧪 AI 프롬프트 테스트"
echo "-------------------------------------"
cd /Users/systemi/storymaker
python3 test_ai_prompt.py

echo ""
echo "====================================="
echo "✅ 설정 완료!"
echo ""
echo "📝 다음 단계:"
echo "   1. Storymaker 실행: streamlit run app.py"
echo "   2. 이미지 생성 시 콘솔에서 '[AI] GPT 프롬프트...' 로그 확인"
echo "   3. 맥락에 맞는 이미지가 생성되는지 확인"
