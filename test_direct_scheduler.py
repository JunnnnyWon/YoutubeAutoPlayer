#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
from datetime import datetime, timedelta
from playvideo import play_youtube_video

class DirectVideoScheduler:
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.active_timers = []
        
    def schedule_immediate_test(self, start_seconds=10, duration_seconds=30):
        """즉시 테스트 실행 (초 단위)"""
        print(f"🧪 즉시 테스트 스케줄링: {start_seconds}초 후 시작, {duration_seconds}초 재생")
        
        current_time = datetime.now()
        start_time = current_time + timedelta(seconds=start_seconds)
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        print(f"📅 현재 시간: {current_time.strftime('%H:%M:%S')}")
        print(f"🎵 시작 시간: {start_time.strftime('%H:%M:%S')}")
        print(f"🔇 종료 시간: {end_time.strftime('%H:%M:%S')}")
        
        # 시작 타이머
        start_timer = threading.Timer(start_seconds, self._start_video_direct)
        start_timer.start()
        self.active_timers.append(start_timer)
        
        # 종료 타이머
        end_timer = threading.Timer(start_seconds + duration_seconds, self._stop_video_direct)
        end_timer.start()
        self.active_timers.append(end_timer)
        
        self.is_running = True
        print(f"✅ 타이머 시작됨! {start_seconds}초 후 유튜브가 실행됩니다.")
        
    def _start_video_direct(self):
        """직접 비디오 시작"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n🚨🚨🚨 [{current_time}] 직접 비디오 시작! 🚨🚨🚨")
            
            if self.driver:
                print("⚠️ 기존 브라우저를 종료합니다.")
                self.driver.quit()
                self.driver = None
            
            print("🚀 브라우저 시작 중...")
            self.driver = play_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            
            if self.driver:
                print(f"✅ [{current_time}] 비디오 재생 시작 완료!")
            else:
                print(f"❌ [{current_time}] 비디오 재생 시작 실패")
                
        except Exception as e:
            print(f"❌ 비디오 시작 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def _stop_video_direct(self):
        """직접 비디오 종료"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n🚨🚨🚨 [{current_time}] 직접 비디오 종료! 🚨🚨🚨")
            
            if self.driver:
                self.driver.quit()
                self.driver = None
                print(f"✅ [{current_time}] 비디오 종료 완료!")
            else:
                print(f"⚠️ [{current_time}] 종료할 브라우저가 없습니다.")
                
        except Exception as e:
            print(f"❌ 비디오 종료 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_all(self):
        """모든 타이머 및 비디오 정지"""
        print("\n🛑 모든 작업 정지 중...")
        
        # 모든 타이머 취소
        for timer in self.active_timers:
            if timer.is_alive():
                timer.cancel()
                
        self.active_timers.clear()
        
        # 브라우저 종료
        if self.driver:
            self.driver.quit()
            self.driver = None
            
        self.is_running = False
        print("✅ 모든 작업이 정지되었습니다.")

def test_direct_scheduler():
    """직접 스케줄러 테스트"""
    print("=" * 50)
    print("🧪 직접 스케줄러 테스트")
    print("=" * 50)
    
    scheduler = DirectVideoScheduler()
    
    try:
        # 10초 후 시작, 20초 재생
        scheduler.schedule_immediate_test(start_seconds=10, duration_seconds=20)
        
        # 40초 대기
        print(f"\n⏰ 40초 대기 중...")
        time.sleep(40)
        
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단됨")
    finally:
        scheduler.stop_all()
        print("✅ 테스트 완료!")

if __name__ == "__main__":
    test_direct_scheduler()
