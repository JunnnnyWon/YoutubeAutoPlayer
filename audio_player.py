# 로컬 오디오 재생 전용 모듈
import os
import threading
import time
import logging
from typing import Optional

class LocalAudioPlayer:
    """
    로컬 오디오 파일 재생을 담당하는 클래스
    pygame을 사용하여 다양한 오디오 형식 지원
    """
    
    def __init__(self):
        self.is_playing = False
        self.current_file = None
        self.logger = logging.getLogger(__name__)
        self._init_pygame()
    
    def _init_pygame(self):
        """pygame 초기화"""
        try:
            import pygame
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.pygame = pygame
            self.logger.info("pygame 오디오 엔진 초기화 완료")
        except ImportError:
            self.logger.error("pygame이 설치되지 않았습니다. pip install pygame을 실행해주세요.")
            self.pygame = None
        except Exception as e:
            self.logger.error(f"pygame 초기화 실패: {e}")
            self.pygame = None
    
    def is_available(self) -> bool:
        """오디오 플레이어 사용 가능 여부"""
        return self.pygame is not None
    
    def play(self, file_path: str, duration: Optional[float] = None) -> bool:
        """
        오디오 파일 재생
        
        Args:
            file_path: 재생할 오디오 파일 경로
            duration: 재생 시간 (초), None이면 전체 재생
        
        Returns:
            재생 성공 여부
        """
        if not self.is_available():
            self.logger.error("pygame이 사용 불가능합니다.")
            return False
        
        if not os.path.exists(file_path):
            self.logger.error(f"오디오 파일을 찾을 수 없습니다: {file_path}")
            return False
        
        try:
            # 기존 재생 중인 음원 정지
            self.stop()
            
            self.logger.info(f"오디오 파일 로딩: {file_path}")
            self.pygame.mixer.music.load(file_path)
            
            # 재생 시작
            self.pygame.mixer.music.play()
            self.is_playing = True
            self.current_file = file_path
            
            self.logger.info(f"오디오 재생 시작: {os.path.basename(file_path)}")
            
            # 지정된 시간 후 자동 정지
            if duration:
                def auto_stop():
                    time.sleep(duration)
                    self.stop()
                
                stop_thread = threading.Thread(target=auto_stop, daemon=True)
                stop_thread.start()
                self.logger.info(f"자동 정지 타이머 설정: {duration}초")
            
            return True
            
        except Exception as e:
            self.logger.error(f"오디오 재생 실패: {e}")
            self.is_playing = False
            self.current_file = None
            return False
    
    def stop(self):
        """오디오 재생 정지"""
        if not self.is_available():
            return
        
        try:
            if self.is_playing:
                self.pygame.mixer.music.stop()
                self.logger.info(f"오디오 재생 정지: {os.path.basename(self.current_file) if self.current_file else 'Unknown'}")
            
            self.is_playing = False
            self.current_file = None
            
        except Exception as e:
            self.logger.error(f"오디오 정지 실패: {e}")
    
    def pause(self):
        """오디오 일시정지"""
        if not self.is_available() or not self.is_playing:
            return
        
        try:
            self.pygame.mixer.music.pause()
            self.logger.info("오디오 일시정지")
        except Exception as e:
            self.logger.error(f"오디오 일시정지 실패: {e}")
    
    def resume(self):
        """오디오 재생 재개"""
        if not self.is_available():
            return
        
        try:
            self.pygame.mixer.music.unpause()
            self.logger.info("오디오 재생 재개")
        except Exception as e:
            self.logger.error(f"오디오 재생 재개 실패: {e}")
    
    def set_volume(self, volume: float):
        """
        볼륨 설정
        
        Args:
            volume: 볼륨 (0.0 ~ 1.0)
        """
        if not self.is_available():
            return
        
        try:
            volume = max(0.0, min(1.0, volume))  # 0.0 ~ 1.0 범위로 제한
            self.pygame.mixer.music.set_volume(volume)
            self.logger.info(f"볼륨 설정: {volume:.2f}")
        except Exception as e:
            self.logger.error(f"볼륨 설정 실패: {e}")
    
    def get_supported_formats(self) -> list:
        """지원하는 오디오 형식 목록"""
        return ['.mp3', '.wav', '.ogg', '.flac', '.m4a']
    
    def cleanup(self):
        """리소스 정리"""
        try:
            self.stop()
            if self.pygame:
                self.pygame.mixer.quit()
                self.logger.info("pygame 리소스 정리 완료")
        except Exception as e:
            self.logger.error(f"리소스 정리 실패: {e}")

# 전역 오디오 플레이어 인스턴스
_global_audio_player = None

def get_audio_player() -> LocalAudioPlayer:
    """전역 오디오 플레이어 인스턴스 반환"""
    global _global_audio_player
    if _global_audio_player is None:
        _global_audio_player = LocalAudioPlayer()
    return _global_audio_player
