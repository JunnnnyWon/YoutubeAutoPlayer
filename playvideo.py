from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

def play_youtube_video(video_url):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(base_dir, "profile")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    if "&autoplay=1" not in video_url and "?autoplay=1" not in video_url:
        if "?" in video_url:
            video_url += "&autoplay=1"
        else:
            video_url += "?autoplay=1"

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(video_url)
    time.sleep(5)
    try:
        play_button = driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button")
        if play_button.get_attribute("aria-label") == "재생(k)":
            play_button.click()
    except Exception:
        pass

    # driver.quit()과 time.sleep(1000) 절대 넣지 마세요!
    return driver

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    play_youtube_video(video_url)