import os
import json
import shutil
from datetime import datetime
from pathlib import Path

class SessionManager:
    """세션 관리 클래스"""
    
    def __init__(self, base_dir='output'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def list_sessions(self):
        """모든 세션 목록 반환"""
        sessions = []
        
        if not os.path.exists(self.base_dir):
            return sessions
        
        for item in os.listdir(self.base_dir):
            session_path = os.path.join(self.base_dir, item)
            
            if os.path.isdir(session_path):
                # 세션 정보 수집
                info = self._get_session_info(item, session_path)
                sessions.append(info)
        
        # 날짜 역순 정렬 (최신순)
        sessions.sort(key=lambda x: x['id'], reverse=True)
        return sessions
    
    def _get_session_info(self, session_id, session_path):
        """세션 정보 추출"""
        info = {
            'id': session_id,
            'path': session_path,
            'name': self._get_session_name(session_id, session_path),
            'created': self._parse_session_date(session_id),
            'file_count': 0,
            'size_mb': 0,
            'has_video': False,
            'has_images': False,
            'has_narrations': False
        }
        
        # 파일 정보 수집
        try:
            files = os.listdir(session_path)
            info['file_count'] = len(files)
            
            # 파일 타입별 체크
            for file in files:
                if file.endswith('.mp4'):
                    info['has_video'] = True
                elif file.endswith('.jpg') or file.endswith('.png'):
                    info['has_images'] = True
                elif file.endswith('.mp3'):
                    info['has_narrations'] = True
            
            # 총 크기 계산
            total_size = sum(
                os.path.getsize(os.path.join(session_path, f))
                for f in files
                if os.path.isfile(os.path.join(session_path, f))
            )
            info['size_mb'] = round(total_size / (1024 * 1024), 2)
            
        except Exception as e:
            print(f"세션 정보 수집 오류: {e}")
        
        return info
    
    def _parse_session_date(self, session_id):
        """세션 ID에서 날짜 파싱 (YYYYMMDDHHMM)"""
        try:
            if len(session_id) == 12 and session_id.isdigit():
                year = int(session_id[0:4])
                month = int(session_id[4:6])
                day = int(session_id[6:8])
                hour = int(session_id[8:10])
                minute = int(session_id[10:12])
                return datetime(year, month, day, hour, minute)
            else:
                # 커스텀 이름인 경우 폴더 생성 시간 사용
                return datetime.fromtimestamp(
                    os.path.getctime(os.path.join(self.base_dir, session_id))
                )
        except:
            return datetime.now()
    
    def _get_session_name(self, session_id, session_path):
        """세션 이름 가져오기 (metadata.json에서 또는 기본값)"""
        metadata_path = os.path.join(session_path, 'metadata.json')
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    return metadata.get('name', session_id)
            except:
                pass
        
        return session_id
    
    def rename_session(self, session_id, new_name):
        """세션 이름 변경"""
        session_path = os.path.join(self.base_dir, session_id)
        metadata_path = os.path.join(session_path, 'metadata.json')
        
        # metadata.json 생성 또는 업데이트
        metadata = {'name': new_name, 'updated_at': datetime.now().isoformat()}
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    metadata.update(existing)
            except:
                pass
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return True
    
    def delete_session(self, session_id):
        """세션 삭제"""
        session_path = os.path.join(self.base_dir, session_id)
        
        if os.path.exists(session_path):
            shutil.rmtree(session_path)
            return True
        
        return False
    
    def export_session(self, session_id, export_path=None):
        """세션을 ZIP으로 압축"""
        import zipfile
        
        session_path = os.path.join(self.base_dir, session_id)
        
        if not os.path.exists(session_path):
            return None
        
        if export_path is None:
            export_path = f"{session_path}.zip"
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(session_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, session_path)
                    zipf.write(file_path, arcname)
        
        return export_path
    
    def get_session_files(self, session_id, file_type=None):
        """세션의 특정 타입 파일 목록 반환"""
        session_path = os.path.join(self.base_dir, session_id)
        
        if not os.path.exists(session_path):
            return []
        
        files = []
        for file in os.listdir(session_path):
            file_path = os.path.join(session_path, file)
            
            if not os.path.isfile(file_path):
                continue
            
            if file_type:
                if file_type == 'video' and file.endswith('.mp4'):
                    files.append(file_path)
                elif file_type == 'image' and (file.endswith('.jpg') or file.endswith('.png')):
                    files.append(file_path)
                elif file_type == 'audio' and file.endswith('.mp3'):
                    files.append(file_path)
            else:
                files.append(file_path)
        
        return files
