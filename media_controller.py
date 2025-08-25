# 통합 미디어 컨트롤러 - YouTube와 로컬 음원의 충돌 방지
import threading
import time
import logging
from typing import Optional, Dict, Any
from enum import Enum

class MediaType(Enum):
    YOUTUBE = "youtube"
    LOCAL_AUDIO = "local_audio"
    NONE = "none"

class MediaState(Enum):
    IDLE = "idle"
    LOADING = "loading"
    PLAYING = "playing"
    STOPPING = "stopping"
    ERROR = "error"

class MediaController:
    """
    YouTube와 로컬 음원 재생을 통합 관리하는 컨트롤러
    충돌 방지와 안전한 전환을 보장
    """
    
    def __init__(self):
        self.current_media_type = MediaType.NONE
        self.current_state = MediaState.IDLE
        self.active_driver = None  # YouTube용 WebDriver
        self.active_audio_player = None  # 로컬 음원용 플레이어
        self.lock = threading.RLock()  # 재진입 가능한 락
        self.logger = logging.getLogger(__name__)
        
        # 상태 변화 콜백
        self.state_change_callbacks = []
        
    def add_state_callback(self, callback):
        """상태 변화 콜백 등록"""
        self.state_change_callbacks.append(callback)
        
    def _notify_state_change(self, old_state: MediaState, new_state: MediaState):
        """상태 변화 알림"""
        for callback in self.state_change_callbacks:
            try:
                callback(old_state, new_state, self.current_media_type)
            except Exception as e:
                self.logger.error(f"상태 변화 콜백 오류: {e}")
    
    def _set_state(self, new_state: MediaState):
        """안전한 상태 변경"""
        with self.lock:
            old_state = self.current_state
            self.current_state = new_state
            self.logger.info(f"미디어 상태 변경: {old_state.value} -> {new_state.value}")
            self._notify_state_change(old_state, new_state)
    
    def get_current_status(self) -> Dict[str, Any]:
        """현재 미디어 상태 반환"""
        with self.lock:
            return {
                "media_type": self.current_media_type.value,
                "state": self.current_state.value,
                "has_youtube": self.active_driver is not None,
                "has_audio": self.active_audio_player is not None
            }
    
    def is_busy(self) -> bool:
        """미디어가 사용 중인지 확인"""
        with self.lock:
            return self.current_state in [MediaState.LOADING, MediaState.PLAYING, MediaState.STOPPING]
    
    def _is_driver_alive(self, driver) -> bool:
        """WebDriver가 살아있는지 안전하게 확인"""
        if driver is None:
            return False
        
        try:
            # 짧은 타임아웃으로 driver 상태 체크
            driver.current_url
            return True
        except Exception as e:
            self.logger.warning(f"WebDriver 상태 체크 실패: {e}")
            return False
    
    def _safe_quit_driver(self, driver, timeout=3.0):
        """WebDriver를 타임아웃과 함께 안전하게 종료 - 응답성 개선된 버전"""
        if driver is None:
            return True
            
        try:
            # 먼저 driver가 살아있는지 확인
            if not self._is_driver_alive(driver):
                self.logger.info("WebDriver가 이미 종료되었습니다")
                return True
            
            # 즉시 종료 시도 (대부분의 경우 빠르게 종료됨)
            try:
                driver.quit()
                self.logger.info("WebDriver 즉시 종료 성공")
                return True
            except Exception as immediate_error:
                self.logger.warning(f"WebDriver 즉시 종료 실패: {immediate_error}")
            
            # 즉시 종료 실패 시 타임아웃을 사용한 안전한 종료 (단축된 타임아웃)
            import threading
            
            quit_success = threading.Event()
            quit_error = threading.Event()
            
            def quit_driver():
                try:
                    driver.quit()
                    quit_success.set()
                except Exception as e:
                    self.logger.error(f"driver.quit() 스레드 오류: {e}")
                    quit_error.set()
            
            quit_thread = threading.Thread(target=quit_driver, daemon=True)
            quit_thread.start()
            
            # 단축된 타임아웃 대기 (응답성 개선)
            if quit_success.wait(timeout):
                self.logger.info("WebDriver 스레드 종료 완료")
                return True
            elif quit_error.wait(0.1):
                self.logger.warning("WebDriver 스레드 종료 중 오류 발생")
                return False
            else:
                self.logger.warning(f"WebDriver 종료 타임아웃 ({timeout}초) - 백그라운드에서 계속 진행")
                return False
                
        except Exception as e:
            self.logger.error(f"WebDriver 안전 종료 실패: {e}")
            return False
    
    def force_stop_all(self):
        """모든 미디어 강제 정지 - 응답성 개선된 버전"""
        self.logger.warning("모든 미디어 강제 정지 실행")
        with self.lock:
            self._set_state(MediaState.STOPPING)
            
            # YouTube 정지 - 단축된 타임아웃으로 빠른 응답
            if self.active_driver:
                self.logger.info("YouTube WebDriver 강제 종료 시도")
                # 응답성을 위해 타임아웃 단축 (3초 -> 1.5초)
                success = self._safe_quit_driver(self.active_driver, timeout=1.5)
                if not success:
                    self.logger.warning("WebDriver 강제 종료 - 프로세스 레벨에서 정리됨")
                        
                self.active_driver = None
            
            # 로컬 음원 정지
            if self.active_audio_player:
                try:
                    self.active_audio_player.stop()
                    self.logger.info("로컬 음원 강제 정지 완료")
                except Exception as e:
                    self.logger.error(f"로컬 음원 강제 정지 오류: {e}")
                finally:
                    self.active_audio_player = None
            
            self.current_media_type = MediaType.NONE
            self._set_state(MediaState.IDLE)
            self.logger.info("강제 정지 과정 완료")
    
    def safe_stop_current(self):
        """현재 재생 중인 미디어 안전하게 정지 - 응답성 개선된 버전"""
        with self.lock:
            if self.current_state == MediaState.IDLE:
                self.logger.info("이미 유휴 상태입니다")
                return True
                
            self._set_state(MediaState.STOPPING)
            success = True
            
            try:
                if self.current_media_type == MediaType.YOUTUBE and self.active_driver:
                    self.logger.info("YouTube 재생 안전 정지")
                    
                    # 향상된 안전 종료 로직 (단축된 타임아웃)
                    if self._is_driver_alive(self.active_driver):
                        # 응답성을 위해 타임아웃 단축 (8초 -> 3초)
                        success = self._safe_quit_driver(self.active_driver, timeout=3.0)
                        if not success:
                            self.logger.warning("WebDriver 정상 종료 실패, 강제 정리")
                    else:
                        self.logger.info("WebDriver가 이미 종료되어 있어 정리만 수행")
                        success = True
                    
                    self.active_driver = None
                    
                elif self.current_media_type == MediaType.LOCAL_AUDIO and self.active_audio_player:
                    self.logger.info("로컬 음원 재생 안전 정지")
                    try:
                        self.active_audio_player.stop()
                        self.logger.info("로컬 음원 정지 완료")
                    except Exception as audio_error:
                        self.logger.error(f"로컬 음원 정지 오류: {audio_error}")
                        success = False
                    finally:
                        self.active_audio_player = None
                    
            except Exception as e:
                self.logger.error(f"미디어 정지 오류: {e}")
                # 오류가 발생해도 정리는 수행
                if self.current_media_type == MediaType.YOUTUBE:
                    self.active_driver = None
                elif self.current_media_type == MediaType.LOCAL_AUDIO:
                    self.active_audio_player = None
                success = False
            
            finally:
                self.current_media_type = MediaType.NONE
                self._set_state(MediaState.IDLE)
                self.logger.info(f"미디어 정지 과정 완료 (성공: {success})")
                
            return success
    
    def play_youtube(self, video_url: str, end_time: Optional[float] = None) -> bool:
        """
        YouTube 비디오 재생
        기존 미디어가 있다면 안전하게 정지 후 실행
        """
        self.logger.info(f"YouTube 재생 요청: {video_url}")
        
        with self.lock:
            # 기존 미디어 정지
            if not self.safe_stop_current():
                self.logger.error("기존 미디어 정지 실패")
                return False
            
            # 상태 변경
            self._set_state(MediaState.LOADING)
            self.current_media_type = MediaType.YOUTUBE
        
        try:
            # YouTube 재생 로직
            from play_video import play_youtube_video
            
            self.logger.info("YouTube 비디오 로딩 중...")
            driver = play_youtube_video(video_url)
            
            # 드라이버 상태 검증
            if driver is None:
                raise Exception("WebDriver 생성 실패")
            
            if not self._is_driver_alive(driver):
                raise Exception("WebDriver가 생성되었지만 응답하지 않음")
            
            with self.lock:
                self.active_driver = driver
                self._set_state(MediaState.PLAYING)
            
            # 종료 시간이 설정되어 있다면 타이머 설정
            if end_time:
                def auto_stop():
                    time.sleep(end_time)
                    # 종료 시에도 WebDriver 상태 체크
                    if self.active_driver and self._is_driver_alive(self.active_driver):
                        self.safe_stop_current()
                    else:
                        self.logger.info("자동 종료 시점에 WebDriver가 이미 종료됨")
                        with self.lock:
                            self.active_driver = None
                            self.current_media_type = MediaType.NONE
                            self._set_state(MediaState.IDLE)
                
                stop_thread = threading.Thread(target=auto_stop, daemon=True)
                stop_thread.start()
            
            self.logger.info("YouTube 재생 시작 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"YouTube 재생 실패: {e}")
            with self.lock:
                self.active_driver = None
                self.current_media_type = MediaType.NONE
                self._set_state(MediaState.ERROR)
            return False
    
    def play_local_audio(self, audio_path: str, end_time: Optional[float] = None) -> bool:
        """
        로컬 음원 재생
        기존 미디어가 있다면 안전하게 정지 후 실행
        """
        self.logger.info(f"로컬 음원 재생 요청: {audio_path}")
        
        with self.lock:
            # 기존 미디어 정지
            if not self.safe_stop_current():
                self.logger.error("기존 미디어 정지 실패")
                return False
            
            # 상태 변경
            self._set_state(MediaState.LOADING)
            self.current_media_type = MediaType.LOCAL_AUDIO
        
        try:
            # LocalAudioPlayer 사용으로 변경
            from audio_player import get_audio_player
            
            self.logger.info("로컬 음원 로딩 중...")
            audio_player = get_audio_player()
            
            if not audio_player.is_available():
                raise Exception("오디오 플레이어를 사용할 수 없습니다")
            
            success = audio_player.play(audio_path, end_time)
            
            if not success:
                raise Exception("오디오 재생 시작 실패")
            
            with self.lock:
                self.active_audio_player = audio_player
                self._set_state(MediaState.PLAYING)
            
            self.logger.info("로컬 음원 재생 시작 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"로컬 음원 재생 실패: {e}")
            with self.lock:
                self.active_audio_player = None
                self.current_media_type = MediaType.NONE
                self._set_state(MediaState.ERROR)
            return False
    
    def wait_for_idle(self, timeout: float = 10.0) -> bool:
        """유휴 상태가 될 때까지 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.lock:
                if self.current_state == MediaState.IDLE:
                    return True
            time.sleep(0.1)
        return False
    
    def start_health_monitor(self):
        """WebDriver 상태 모니터링 시작"""
        def monitor():
            while True:
                try:
                    with self.lock:
                        if (self.current_media_type == MediaType.YOUTUBE and 
                            self.active_driver and 
                            self.current_state == MediaState.PLAYING):
                            
                            if not self._is_driver_alive(self.active_driver):
                                self.logger.warning("WebDriver 응답 없음 감지 - 자동 정리")
                                self.active_driver = None
                                self.current_media_type = MediaType.NONE
                                self._set_state(MediaState.IDLE)
                    
                    time.sleep(5)  # 5초마다 체크
                    
                except Exception as e:
                    self.logger.error(f"상태 모니터링 오류: {e}")
                    time.sleep(10)  # 오류 시 더 긴 대기
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.logger.info("WebDriver 상태 모니터링 시작")

# 전역 미디어 컨트롤러 인스턴스
_global_media_controller = None

def get_media_controller() -> MediaController:
    """전역 미디어 컨트롤러 인스턴스 반환"""
    global _global_media_controller
    if _global_media_controller is None:
        _global_media_controller = MediaController()
        # 자동으로 상태 모니터링 시작
        _global_media_controller.start_health_monitor()
    return _global_media_controller

def emergency_stop_all_media():
    """긴급 상황 시 모든 미디어 정지"""
    controller = get_media_controller()
    controller.force_stop_all()
