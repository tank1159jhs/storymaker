import os
import re
import requests
import time
import random
from PIL import Image, ImageDraw, ImageFont
from src.config import load_config

config = load_config()

# OpenAI API 설정 (프롬프트 생성용)
OPENAI_API_KEY = config.get('openai_api_key')
USE_AI_PROMPTS = OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key'

SD_API_URL = "http://127.0.0.1:7861/sdapi/v1/txt2img"

# ⚠️ 애니메이션 모델용 네거티브 프롬프트 (japaneseDollLikeness)
NEGATIVE_ANIME = "EasyNegative, bad-hands-5, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, blurry"

# ⭐ 실사/시네마틱용 강화 네거티브 프롬프트 (일본 배경/사물 특화)
# → 인물 완전 제거, 사물/배경만 허용, 중국풍 건축 차단
NEGATIVE_REALISTIC = "EasyNegative, bad-hands-5, lowres, bad anatomy, bad hands, text, error, cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, blurry, anime, cartoon, illustration, 2D, drawn, painting, CG, 3D render, unreal engine, plastic, fake, artificial, unrealistic proportions, oversaturated, person, people, human, man, woman, child, figure, silhouette, face, faces, portrait, body, crowd, pedestrian, character, Chinese architecture, Chinese style, Chinese traditional building, pagoda, Chinese temple, red pillars, Chinese ornaments, Chinese decorations, dragon motifs, Chinese roof tiles, pottery, ceramic, vase, jar, clay pot, porcelain, earthenware, terracotta, urn, jug, bowl"

DEFAULT_NEGATIVE_PROMPT = NEGATIVE_ANIME

def _generate_prompt_with_ai(text, image_style='realistic'):
    """
    OpenAI GPT를 사용하여 대본에서 이미지 프롬프트를 자동 생성
    """
    if not USE_AI_PROMPTS:
        print("[AI] OpenAI API 키 없음 - 키워드 매핑 사용")
        return None
    
    try:
        system_prompt = f"""Convert the story script to an English image prompt for Stable Diffusion.

RULES:
1. Focus on SCENERY and OBJECTS only - NO people, NO humans
2. Describe: location, time of day, weather, objects, atmosphere
3. Setting is JAPAN - use Japanese elements (traditional houses, cherry blossoms, temples, gardens, streets)
4. Keep it simple: 30-40 words maximum

EXAMPLES:
"駅で雨の日、彼女を見送った" → "Japanese train station platform, rainy evening, wet concrete, empty bench, departing train lights in distance, melancholic blue atmosphere"

"카페에서 커피를 마시며 추억을 떠올렸다" → "cozy Japanese cafe interior, warm afternoon light through window, steaming coffee cup on wooden table, vintage furniture, nostalgic mood"

"海辺を一人で歩いた" → "quiet Japanese beach shoreline, sunset, gentle waves, footprints in sand, peaceful solitary atmosphere, golden light"

DO NOT include: people, faces, figures, pottery, Chinese architecture
Output ONLY the prompt, no explanations."""
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': text}
                ],
                'max_tokens': 100,
                'temperature': 0.5
            },
            timeout=10
        )
        
        if response.status_code == 200:
            prompt = response.json()['choices'][0]['message']['content'].strip()
            # 따옴표 제거
            prompt = prompt.strip('"\'')
            print(f"[AI] 프롬프트: {prompt[:60]}...")
            return prompt
        else:
            print(f"[AI] API 오류: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[AI] 프롬프트 생성 실패: {e}")
        return None

def _extract_scene_keywords(text):
    """
    대본 텍스트에서 핵심 키워드를 추출 (폴백용)
    AI 프롬프트 생성 실패 시에만 사용 - 일본 배경/사물 중심
    """
    keywords = []
    
    # 1. 일본 장소
    locations = {
        '역': 'Japanese train station', '駅': 'Japanese train station', 'ホーム': 'station platform',
        '카페': 'Japanese cafe interior', 'カフェ': 'Japanese cafe interior', '喫茶店': 'Japanese coffee shop',
        '학교': 'Japanese school', '学校': 'Japanese school', '교실': 'Japanese classroom', '教室': 'Japanese classroom',
        '공원': 'Japanese park', '公園': 'Japanese park', '바다': 'Japanese beach', '海': 'Japanese coastline',
        '병원': 'hospital corridor', '病院': 'hospital corridor', '집': 'Japanese home interior', '家': 'Japanese home interior',
        '거리': 'Japanese street', '通り': 'Japanese street', '산': 'Japanese mountain', '山': 'Japanese mountain'
    }
    
    # 2. 날씨/시간/계절
    weather = {
        '비': 'rainy weather, wet surfaces', '雨': 'rainy weather, wet surfaces',
        '눈': 'snowy, snow covered', '雪': 'snowy, snow covered',
        '아침': 'early morning light', '朝': 'early morning light',
        '저녁': 'evening golden hour', '夕方': 'evening golden hour',
        '밤': 'night scene, city lights', '夜': 'night scene, lantern lights',
        '가을': 'autumn leaves, fall colors', '秋': 'autumn leaves, fall colors',
        '봄': 'cherry blossoms, spring', '春': 'cherry blossoms, spring',
        '여름': 'summer sunshine', '夏': 'summer sunshine'
    }
    
    # 3. 사물/오브젝트 (인물 대신)
    objects = {
        '커피': 'coffee cup on table', 'コーヒー': 'coffee cup on table',
        '벤치': 'empty wooden bench', 'ベンチ': 'empty wooden bench',
        '창문': 'window with soft light', '窓': 'window with soft light',
        '편지': 'handwritten letter', '手紙': 'handwritten letter',
        '꽃': 'flowers', '花': 'flowers', '桜': 'cherry blossoms',
        '바람': 'wind blowing leaves', '風': 'wind blowing leaves'
    }
    
    # 4. 감정/분위기
    moods = {
        '이별': 'farewell atmosphere', '別れ': 'farewell atmosphere',
        '재회': 'hopeful mood', '再会': 'hopeful mood',
        '추억': 'nostalgic atmosphere', '思い出': 'nostalgic atmosphere', '懐かしい': 'nostalgic atmosphere',
        '슬픔': 'melancholic mood', '悲しみ': 'melancholic mood',
        '행복': 'warm joyful atmosphere', '幸せ': 'warm joyful atmosphere'
    }
    
    # 키워드 추출 (각 카테고리 하나씩)
    for word, eng in locations.items():
        if word in text:
            keywords.append(eng)
            break
    
    for word, eng in weather.items():
        if word in text:
            keywords.append(eng)
            break
    
    for word, eng in objects.items():
        if word in text:
            keywords.append(eng)
            break
    
    for word, eng in moods.items():
        if word in text:
            keywords.append(eng)
            break
    
    # 기본값 (일본 분위기)
    if not keywords:
        keywords = ['Japanese scenery', 'soft natural lighting', 'peaceful atmosphere']
    
    return ', '.join(keywords)

def _generate_single_image(prompt, img_path, seed_value, combined_text, scene_num, part_num, negative_prompt=None, width=1280, height=720, steps=20, sampler_name="DPM++ 2M", cfg_scale=7.0):
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt or DEFAULT_NEGATIVE_PROMPT,
        "seed": seed_value,
        "width": width,
        "height": height,
        "steps": steps,
        "sampler_name": sampler_name,
        "batch_size": 1,
        "n_iter": 1,
        "cfg_scale": cfg_scale  # ⭐ CFG Scale 추가
    }
    try:
        response = requests.post(SD_API_URL, json=payload, timeout=180)  # 타임아웃 증가
        response.raise_for_status()
        r = response.json()
        if 'images' in r and r['images']:
            import base64
            image_data = base64.b64decode(r['images'][0])
            with open(img_path, 'wb') as f:
                f.write(image_data)
            return img_path
        else:
            print(f"[SDAPI] 이미지 생성 실패: 응답에 이미지 없음")
    except Exception as e:
        print(f"[SDAPI] 이미지 생성 오류: {e}")
    print(f"    ⚠️ SD WebUI API 실패 - 더미 이미지 생성")
    img = Image.new('RGB', (width, height), color=(70, 130, 180))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    text = f"씬 {scene_num}-{part_num}\n\n{combined_text[:150]}..."
    draw.text((100, 100), text, fill='white', font=font)
    img.save(img_path)
    return img_path

def generate_images_from_script_only(script, scene_num=1, all_scripts=None, output_dir='output', image_style='anime', num_images=5, steps=20, sampler_name="DPM++ 2M", cfg_scale=7.0):
    """
    대본(script)에서 씬별로 이미지를 생성하는 함수. Pollinations 흔적 없이 SD WebUI REST API만 사용.
    
    Args:
        script: 씬 대본
        scene_num: 씬 번호
        all_scripts: 전체 대본 (사용 안 함)
        output_dir: 출력 디렉토리
        image_style: 이미지 스타일 (realistic, cinematic, anime, semi-realistic)
        num_images: 생성할 이미지 개수
        steps: Sampling Steps (기본: 20)
        sampler_name: Sampler 이름 (기본: "DPM++ 2M")
        cfg_scale: CFG Scale (기본: 7.0)
    """
    # 1. 타임스탬프 블록 추출
    timestamp_blocks = []  # (timestamp, text)
    current_ts = None
    current_lines = []
    for line in script.strip().split('\n'):
        line = line.strip()
        ts_match = re.match(r'\[(\d+:\d+)\]', line)
        if ts_match:
            if current_ts is not None and current_lines:
                timestamp_blocks.append((current_ts, '\n'.join(current_lines)))
            current_ts = ts_match.group(1)
            text = line.split(']', 1)[1].strip() if ']' in line else ''
            current_lines = [text] if text else []
        else:
            if current_ts is not None:
                current_lines.append(line)
    if current_ts is not None and current_lines:
        timestamp_blocks.append((current_ts, '\n'.join(current_lines)))
    if not timestamp_blocks:
        timestamp_blocks = [("0:00", script.strip())]

    # 2. 블록 2개씩 묶어서 num_images개 그룹 만들기
    group_size = 2
    num_groups = num_images
    block_groups = []
    for i in range(num_groups):
        start = i * group_size
        end = start + group_size
        group = timestamp_blocks[start:end]
        if not group:
            continue
        group_text = '\n'.join([text for ts, text in group])
        group_ts = ','.join([ts for ts, text in group])
        block_groups.append((group_ts, group_text))
    while len(block_groups) < num_groups:
        last_group = block_groups[-1]
        last_text = last_group[1] if last_group[1].strip() else 'scenery, landscape, background'
        block_groups.append((last_group[0], last_text))

    os.makedirs(output_dir, exist_ok=True)
    base_seed = random.randint(1, 100000)
    generated_images = []
    for idx, (group_ts, group_text) in enumerate(block_groups, start=1):
        # ⭐ 1차: AI로 프롬프트 생성 시도
        scene_keywords = _generate_prompt_with_ai(group_text, image_style)
        
        # ⭐ 2차: AI 실패 시 키워드 매핑 폴백
        if not scene_keywords:
            scene_keywords = _extract_scene_keywords(group_text)
        
        # 스타일 프롬프트 추가 (realistic, cinematic, anime 등)
        # 🎬 일본 배경/사물 특화 - 인물 없음
        style_prompt = ''
        if image_style == 'realistic':
            style_prompt = ', photorealistic, realistic photography, natural lighting, high resolution, 8k, masterpiece, best quality, highly detailed, cinematic composition, no people, empty scene, Japanese aesthetic, emotional atmosphere'
        elif image_style == 'cinematic':
            style_prompt = ', cinematic, movie scene, film still, dramatic lighting, professional color grading, film grain, shallow depth of field, anamorphic, 8k, masterpiece, highly detailed, no people, empty scene, Japanese setting, emotional storytelling, atmospheric'
        elif image_style == 'anime':
            style_prompt = ', anime style, best quality, vibrant colors, highly detailed, illustration, beautiful lighting, masterpiece, emotional scene, Studio Ghibli inspired, no people, scenery focus'
        elif image_style == 'semi-realistic':
            style_prompt = ', semi-realistic, digital painting, beautiful lighting, artstation trending, masterpiece, highly detailed, no people, empty scene, Japanese aesthetic, emotional atmosphere'
        
        # ⭐ 최종 프롬프트: 장면 키워드 + 스타일
        prompt = scene_keywords + style_prompt
        
        # 스타일별 네거티브 프롬프트 선택
        if image_style in ['realistic', 'cinematic']:
            negative_prompt = NEGATIVE_REALISTIC
        else:
            negative_prompt = NEGATIVE_ANIME
        
        seed_value = base_seed + (scene_num * 1000) + (idx * 100) + random.randint(0, 50)
        img_path = f'{output_dir}/scene_{scene_num}_group{idx}.jpg'
        print(f"🎨 씬 {scene_num}-그룹{idx}: {group_text[:60]}...")
        result_path = _generate_single_image(
            prompt, img_path, seed_value, group_text, scene_num, idx, 
            negative_prompt=negative_prompt,
            steps=steps,
            sampler_name=sampler_name,
            cfg_scale=cfg_scale
        )
        generated_images.append(result_path)
    return generated_images
