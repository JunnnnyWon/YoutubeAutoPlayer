"""
Anti-detection utilities for YouTube automation
"""
from selenium.webdriver.chrome.options import Options
import random
import time


class AntiDetection:
    """봇 탐지 방지를 위한 유틸리티 클래스"""
    
    @staticmethod
    def random_delay(min_delay=1.0, max_delay=3.0):
        """랜덤한 지연 시간 추가"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    @staticmethod
    def human_like_delay():
        """인간 같은 랜덤 지연"""
        return random.uniform(0.8, 2.5)
    
    @staticmethod
    def simulate_human_behavior(driver):
        """인간의 행동을 시뮬레이션"""
        # 스크롤 동작
        driver.execute_script("window.scrollTo(0, 100);")
        AntiDetection.random_delay(0.5, 1.5)
        
        # 마우스 움직임 시뮬레이션
        driver.execute_script("""
            var event = new MouseEvent('mousemove', {
                'view': window,
                'bubbles': true,
                'cancelable': true,
                'clientX': Math.random() * window.innerWidth,
                'clientY': Math.random() * window.innerHeight
            });
            document.dispatchEvent(event);
        """)
        
        AntiDetection.random_delay(0.3, 1.0)
    
    @staticmethod
    def random_mouse_movement(driver):
        """랜덤 마우스 움직임"""
        driver.execute_script("""
            var event = new MouseEvent('mousemove', {
                'view': window,
                'bubbles': true,
                'cancelable': true,
                'clientX': Math.random() * window.innerWidth,
                'clientY': Math.random() * window.innerHeight
            });
            document.dispatchEvent(event);
        """)
        time.sleep(random.uniform(0.5, 1.5))
    
    @staticmethod
    def random_scroll(driver):
        """랜덤 스크롤 동작"""
        scroll_commands = [
            "window.scrollTo(0, 100);",
            "window.scrollTo(0, 200);",
            "window.scrollTo(0, 50);",
            "window.scrollTo(0, 0);"
        ]
        
        for command in random.sample(scroll_commands, 2):
            driver.execute_script(command)
            time.sleep(random.uniform(0.5, 1.5))
    
    @staticmethod
    def bypass_video_restrictions(driver):
        """비디오 제한사항 우회"""
        try:
            # 쿠키 동의 버튼 클릭
            driver.execute_script("""
                var acceptButton = document.querySelector('[aria-label*="Accept"], [aria-label*="동의"], button[contains(text(), "Accept")], button[contains(text(), "동의")]');
                if (acceptButton) {
                    acceptButton.click();
                }
            """)
            
            # 로그인 관련 팝업 닫기
            driver.execute_script("""
                var closeButtons = document.querySelectorAll('[aria-label*="Close"], [aria-label*="닫기"], button[contains(text(), "Close")], button[contains(text(), "닫기")]');
                closeButtons.forEach(function(btn) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                    }
                });
            """)
            
        except Exception as e:
            print(f"제한사항 우회 중 오류: {e}")
    
    @staticmethod
    def wait_for_video_load(driver, timeout=15):
        """비디오 로딩 대기"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                video_loaded = driver.execute_script("""
                    var video = document.querySelector('video');
                    return video && video.readyState >= 3;
                """)
                if video_loaded:
                    return True
                time.sleep(1)
            return False
        except Exception as e:
            print(f"비디오 로딩 대기 중 오류: {e}")
            return False
    
    @staticmethod
    def ensure_images_loaded(driver, timeout=10):
        """이미지 로딩 확인 및 강제 로딩"""
        try:
            print("🖼️ 이미지 로딩 상태 확인 중...")
            
            # 이미지 로딩 강제 활성화
            driver.execute_script("""
                // 이미지 로딩 설정 변경
                if (navigator.userAgent.includes('Chrome')) {
                    // Chrome에서 이미지 로딩 활성화
                    var style = document.createElement('style');
                    style.innerHTML = 'img { display: block !important; visibility: visible !important; }';
                    document.head.appendChild(style);
                }
                
                // 모든 이미지 요소 찾기 및 로딩 강제
                var images = document.querySelectorAll('img');
                images.forEach(function(img) {
                    if (!img.complete || img.naturalHeight === 0) {
                        var src = img.src;
                        img.src = '';
                        img.src = src;  // 강제 새로고침
                    }
                });
            """)
            
            # 이미지 로딩 대기
            start_time = time.time()
            while time.time() - start_time < timeout:
                loaded_images = driver.execute_script("""
                    var images = document.querySelectorAll('img');
                    var loaded = 0;
                    var total = images.length;
                    
                    for(var i = 0; i < total; i++) {
                        if(images[i].complete && images[i].naturalHeight > 0) {
                            loaded++;
                        }
                    }
                    
                    return {loaded: loaded, total: total};
                """)
                
                if loaded_images['total'] > 0 and loaded_images['loaded'] > 0:
                    print(f"✅ 이미지 로딩 완료: {loaded_images['loaded']}/{loaded_images['total']}")
                    return True
                
                time.sleep(1)
            
            print("⚠️ 이미지 로딩 타임아웃")
            return False
            
        except Exception as e:
            print(f"❌ 이미지 로딩 확인 중 오류: {e}")
            return False


def setup_anti_detection_chrome_options():
    """봇 탐지 방지를 위한 Chrome 옵션 설정"""
    chrome_options = Options()
    
    # 기본 봇 탐지 방지 옵션
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 브라우저 창 크기 설정 (적당한 사이즈)
    chrome_options.add_argument("--window-size=1280,720")  # 720p 크기
    chrome_options.add_argument("--window-position=100,100")  # 화면 위치
    
    # User Agent 설정 (실제 브라우저와 동일하게)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    # 추가 보안 옵션
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins-discovery")
    
    # 이미지 로딩 관련 설정
    chrome_options.add_argument("--enable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--enable-gpu-rasterization")
    
    # 자동재생 정책 설정 (음소거 없이 자동재생 허용)
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    
    # 미디어 관련 설정
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--disable-background-media-suspend")
    chrome_options.add_argument("--allow-autoplay-policy")
    
    # 전체화면 방지 및 창 모드 유지
    chrome_options.add_argument("--disable-fullscreen")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-default-apps")
    
    # 추가 자동재생 허용 설정
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_setting_values.notifications": 1,
        "profile.default_content_setting_values.auto_select_certificate": 1,
        "profile.default_content_setting_values.images": 1,  # 이미지 로딩 허용
        "profile.managed_default_content_settings.images": 1,  # 이미지 로딩 허용
        "profile.content_settings.exceptions.media_stream_mic": {},
        "profile.content_settings.exceptions.media_stream_camera": {}
    })
    chrome_options.add_argument("--disable-bundled-ppapi-flash")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-default-apps")
    
    # 언어 및 지역 설정
    chrome_options.add_argument("--lang=ko-KR")
    chrome_options.add_experimental_option('prefs', {
        'intl.accept_languages': 'ko-KR,ko,en-US,en',
        'profile.default_content_setting_values.notifications': 2,
        'profile.managed_default_content_settings.images': 1  # 이미지 로딩 활성화
    })
    
    return chrome_options
