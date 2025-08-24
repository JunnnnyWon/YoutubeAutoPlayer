# YouTube 봇 탐지 우회를 위한 추가 유틸리티

import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

class AntiDetection:
    @staticmethod
    def human_like_delay():
        """인간적인 지연 시간"""
        return random.uniform(1.5, 3.5)
    
    @staticmethod
    def random_mouse_movement(driver):
        """랜덤한 마우스 움직임"""
        try:
            actions = ActionChains(driver)
            body = driver.find_element(By.TAG_NAME, "body")
            for _ in range(random.randint(2, 4)):
                x = random.randint(50, 500)
                y = random.randint(50, 400)
                actions.move_to_element_with_offset(body, x, y).perform()
                time.sleep(random.uniform(0.5, 1.0))
        except Exception:
            pass
    
    @staticmethod
    def random_scroll(driver):
        """랜덤한 스크롤 동작"""
        try:
            for _ in range(random.randint(1, 3)):
                scroll_amount = random.randint(100, 500)
                driver.execute_script(f"window.scrollTo(0, {scroll_amount});")
                time.sleep(random.uniform(0.8, 1.5))
        except Exception:
            pass
    
    @staticmethod
    def simulate_typing_behavior(element, text):
        """인간적인 타이핑 시뮬레이션"""
        try:
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
        except Exception:
            pass
    
    @staticmethod
    def wait_for_video_load(driver, max_retries=5):
        """비디오 로딩 대기 및 재시도"""
        for attempt in range(max_retries):
            try:
                # 비디오 플레이어가 로드되었는지 확인
                player = driver.find_element(By.ID, "movie_player")
                if player:
                    time.sleep(AntiDetection.human_like_delay())
                    
                    # 오류 메시지 확인
                    error_elements = driver.find_elements(By.CSS_SELECTOR, ".ytp-error")
                    if error_elements and any(elem.is_displayed() for elem in error_elements):
                        print(f"비디오 로딩 오류 감지 (시도 {attempt + 1}/{max_retries})")
                        
                        # 새로고침 시도
                        if attempt < max_retries - 1:
                            print("페이지 새로고침 중...")
                            driver.refresh()
                            time.sleep(AntiDetection.human_like_delay() * 2)
                            continue
                    else:
                        print("비디오 로딩 성공!")
                        return True
                        
            except Exception as e:
                print(f"비디오 로딩 확인 중 오류: {e}")
                
            time.sleep(AntiDetection.human_like_delay())
            
        print("비디오 로딩 최대 재시도 횟수 초과")
        return False
    
    @staticmethod
    def bypass_video_restrictions(driver):
        """비디오 제한 우회 시도"""
        try:
            # 1. 쿠키 승인 버튼 클릭
            try:
                cookie_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Accept'], button[aria-label*='수락'], button[aria-label*='동의']")
                if cookie_button.is_displayed():
                    cookie_button.click()
                    time.sleep(1)
            except Exception:
                pass
            
            # 2. 연령 제한 확인 버튼
            try:
                age_gate_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='이해'], .age-gate button")
                if age_gate_button.is_displayed():
                    age_gate_button.click()
                    time.sleep(2)
            except Exception:
                pass
            
            # 3. 광고 건너뛰기
            try:
                skip_ad_button = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-skip-button, .ytp-skip-ad-button")
                if skip_ad_button.is_displayed():
                    time.sleep(5)  # 광고 건너뛰기 버튼이 활성화될 때까지 대기
                    skip_ad_button.click()
            except Exception:
                pass
                
        except Exception as e:
            print(f"제한 우회 시도 중 오류: {e}")

def setup_anti_detection_chrome_options():
    """봇 탐지 우회를 위한 Chrome 옵션 설정"""
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    
    # 기본 옵션
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-infobars")
    
    # 봇 탐지 우회 핵심 옵션들
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 추가 우회 옵션들
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-service-autorun")
    chrome_options.add_argument("--password-store=basic")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # User-Agent (실제 사용자처럼 보이게)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return chrome_options
