from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import random
from anti_detection import AntiDetection, setup_anti_detection_chrome_options

def play_youtube_video(video_url):
    print(f"🎵 YouTube 비디오 재생 시작: {video_url}")
    
    # 봇 탐지 우회를 위한 Chrome 옵션 설정
    chrome_options = setup_anti_detection_chrome_options()
    
    # 프로필 디렉토리 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(base_dir, "profile")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(options=chrome_options)
    
    # webdriver 속성 완전히 숨기기
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko', 'en-US', 'en']})")
    
    try:
        print("🌐 YouTube 메인 페이지 방문 중...")
        # 1. YouTube 메인 페이지 방문 (인간적인 패턴)
        driver.get("https://www.youtube.com")
        time.sleep(AntiDetection.human_like_delay())
        
        # 2. 인간적인 행동 시뮬레이션
        print("🖱️ 인간적인 브라우징 패턴 시뮬레이션...")
        AntiDetection.random_mouse_movement(driver)
        AntiDetection.random_scroll(driver)
        
        # 3. 쿠키 및 제한사항 처리
        AntiDetection.bypass_video_restrictions(driver)
        
        print(f"📹 비디오 URL로 이동: {video_url}")
        # 4. 실제 비디오 URL로 이동
        if "&autoplay=1" not in video_url and "?autoplay=1" not in video_url:
            separator = "&" if "?" in video_url else "?"
            video_url += f"{separator}autoplay=1&mute=0"
        
        driver.get(video_url)
        
        # 5. 비디오 로딩 대기 및 오류 처리
        print("⏳ 비디오 로딩 대기 중...")
        if not AntiDetection.wait_for_video_load(driver):
            print("❌ 비디오 로딩 실패")
            return driver
        
        # 6. 추가 제한사항 우회
        AntiDetection.bypass_video_restrictions(driver)
        
        # 7. 페이지가 완전히 로드될 때까지 대기
        wait = WebDriverWait(driver, 20)
        
        try:
            print("🎬 비디오 플레이어 로딩 대기...")
            # 비디오 플레이어 로딩 대기
            player = wait.until(EC.presence_of_element_located((By.ID, "movie_player")))
            time.sleep(AntiDetection.human_like_delay())
            
            # 8. 재생 버튼 클릭 시도
            print("▶️ 재생 버튼 클릭 시도...")
            try:
                play_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-play-button")))
                
                # 재생 버튼이 일시정지 상태인지 확인 (즉, 비디오가 이미 재생 중인지)
                aria_label = play_button.get_attribute("aria-label")
                if aria_label and any(keyword in aria_label for keyword in ["재생", "Play"]):
                    # 마우스를 재생 버튼으로 천천히 이동 후 클릭
                    actions = ActionChains(driver)
                    actions.move_to_element(play_button).perform()
                    time.sleep(random.uniform(0.5, 1.0))
                    play_button.click()
                    print("✅ 재생 버튼 클릭 성공!")
                else:
                    print("ℹ️ 비디오가 이미 재생 중입니다.")
                    
            except Exception as e:
                print(f"⚠️ 재생 버튼 클릭 실패: {e}")
                # 대체 방법들
                fallback_methods = [
                    lambda: driver.find_element(By.TAG_NAME, "body").click(),
                    lambda: ActionChains(driver).send_keys(" ").perform(),
                    lambda: driver.execute_script("document.querySelector('video').play()"),
                    lambda: driver.execute_script("document.querySelector('.ytp-play-button').click()")
                ]
                
                for i, method in enumerate(fallback_methods):
                    try:
                        print(f"🔄 대체 재생 방법 {i+1} 시도...")
                        method()
                        time.sleep(1)
                        break
                    except Exception as fallback_error:
                        print(f"❌ 대체 방법 {i+1} 실패: {fallback_error}")
            
            # 9. 볼륨 조정 (인간적인 행동)
            try:
                print("🔊 볼륨 조정 중...")
                time.sleep(2)
                volume_area = driver.find_element(By.CSS_SELECTOR, ".ytp-volume-area")
                actions = ActionChains(driver)
                actions.move_to_element(volume_area).click().perform()
                time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ 볼륨 조정 실패: {e}")
            
            # 10. 최종 상태 확인
            time.sleep(3)
            try:
                video_element = driver.find_element(By.TAG_NAME, "video")
                if video_element.get_property("paused"):
                    print("🔄 비디오가 일시정지 상태입니다. 재시도...")
                    video_element.click()
                else:
                    print("🎉 비디오 재생 성공!")
            except Exception as e:
                print(f"⚠️ 최종 상태 확인 실패: {e}")
                
        except Exception as e:
            print(f"❌ 비디오 플레이어 로딩 실패: {e}")
            
    except Exception as e:
        print(f"💥 전체 재생 과정에서 오류 발생: {e}")
    
    print("🏁 YouTube 비디오 재생 과정 완료")
    return driver

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    play_youtube_video(video_url)