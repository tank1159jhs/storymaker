"""자막 스타일 설정 관리"""

# 기본 자막 설정 (잘림 방지 완벽 보장)
DEFAULT_SUBTITLE_SETTINGS = {
    'font_size': 80,
    'font_color': 'white',
    'stroke_color': 'black',
    'stroke_width': 6,
    'position_y': 920,  # 하단 (1080 - 100 여유 - 60 높이 = 920)
    'font_family': 'Arial Unicode'
}

# 프리셋 스타일 (폰트 크기별 자동 계산된 안전 위치)
SUBTITLE_PRESETS = {
    'YouTube 기본': {
        'font_size': 80,
        'font_color': 'white',
        'stroke_color': 'black',
        'stroke_width': 6,
        'position_y': 920  # 하단 안전 (80px 폰트 + 100px 여유)
    },
    '대형 (가독성 강조)': {
        'font_size': 100,
        'font_color': 'white',
        'stroke_color': 'black',
        'stroke_width': 7,
        'position_y': 890  # 대형 폰트 (100px + 90px 여유)
    },
    '소형 (깔끔)': {
        'font_size': 70,
        'font_color': 'white',
        'stroke_color': 'black',
        'stroke_width': 5,
        'position_y': 940  # 소형 폰트 (70px + 70px 여유)
    },
    '노란색 (밝음)': {
        'font_size': 80,
        'font_color': 'yellow',
        'stroke_color': 'black',
        'stroke_width': 6,
        'position_y': 920
    },
    '파란색 (시원함)': {
        'font_size': 80,
        'font_color': '#00D4FF',
        'stroke_color': 'black',
        'stroke_width': 6,
        'position_y': 920
    },
    '중앙 배치': {
        'font_size': 80,
        'font_color': 'white',
        'stroke_color': 'black',
        'stroke_width': 6,
        'position_y': 500  # 중앙 (540 - 40)
    },
    '상단 배치': {
        'font_size': 80,
        'font_color': 'white',
        'stroke_color': 'black',
        'stroke_width': 6,
        'position_y': 100  # 상단 (100px 여유)
    }
}

def calculate_safe_position(font_size, placement='bottom'):
    """폰트 크기에 따른 안전한 위치 자동 계산
    
    Args:
        font_size: 폰트 크기 (px)
        placement: 배치 위치 ('bottom', 'center', 'top')
    
    Returns:
        안전한 position_y 값
    """
    VIDEO_HEIGHT = 1080
    
    if placement == 'bottom':
        # 하단: 화면 높이 - 여유(100px) - 폰트높이 추정치(font_size * 0.8)
        margin = 100
        estimated_height = int(font_size * 0.8)
        return VIDEO_HEIGHT - margin - estimated_height
    
    elif placement == 'center':
        # 중앙: 화면 중앙 - 폰트높이 절반
        estimated_height = int(font_size * 0.8)
        return (VIDEO_HEIGHT // 2) - (estimated_height // 2)
    
    elif placement == 'top':
        # 상단: 여유만 확보
        return 100
    
    return 920  # 기본값

# 사용 가능한 폰트 (macOS)
AVAILABLE_FONTS = [
    'Arial Unicode',
    'Hiragino Sans',
    'Apple Gothic',
    'Noto Sans',
    'Arial'
]

# 색상 옵션
COLOR_OPTIONS = {
    '흰색': 'white',
    '노란색': 'yellow',
    '파란색': '#00D4FF',
    '빨간색': '#FF4444',
    '초록색': '#44FF44',
    '주황색': '#FF8800',
    '분홍색': '#FF88FF',
    '보라색': '#8888FF'
}

def get_font_path(font_name):
    """폰트 이름에서 실제 경로 반환"""
    font_map = {
        'Arial Unicode': '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        'Hiragino Sans': '/System/Library/Fonts/Hiragino Sans GB.ttc',
        'Apple Gothic': '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
        'Noto Sans': '/System/Library/Fonts/Supplemental/NotoSansGothic-Regular.ttf',
        'Arial': 'Arial'
    }
    
    return font_map.get(font_name, 'Arial')
