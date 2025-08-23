import time
import schedule
import threading
from datetime import datetime, timedelta
from playvideo import play_youtube_video

class VideoScheduler:
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.current_jobs = []
        self.schedules = []
        
    def add_schedule(self, start_time, end_time, video_url, schedule_name="방송"):
        """
        스케줄을 추가하는 함수
        
        Args:
            start_time (str): 시작 시간 (HH:MM 형식)
            end_time (str): 종료 시간 (HH:MM 형식) 
            video_url (str): 재생할 YouTube 동영상 URL
            schedule_name (str): 스케줄 이름
        """
        # 시간 형식 검증
        try:
            datetime.strptime(start_time, '%H:%M')
            datetime.strptime(end_time, '%H:%M')
        except ValueError:
            print(f"❌ 잘못된 시간 형식: {start_time} ~ {end_time}")
            return False
            
        # 종료 시간이 시작 시간보다 늦은지 확인
        start_dt = datetime.strptime(start_time, '%H:%M').time()
        end_dt = datetime.strptime(end_time, '%H:%M').time()
        
        if end_dt <= start_dt:
            print(f"❌ 종료 시간이 시작 시간보다 늦어야 합니다: {start_time} ~ {end_time}")
            return False
        
        schedule_info = {
            'start_time': start_time,
            'end_time': end_time,
            'video_url': video_url,
            'name': schedule_name
        }
        
        self.schedules.append(schedule_info)
        print(f"✅ 스케줄 추가됨: {schedule_name} ({start_time} ~ {end_time})")
        return True
        
    def start_scheduler(self):
        """
        모든 등록된 스케줄을 활성화하는 함수
        """
        if not self.schedules:
            print("❌ 등록된 스케줄이 없습니다.")
            return
            
        print(f"\n📅 총 {len(self.schedules)}개의 스케줄을 등록합니다:")
        
        for schedule_info in self.schedules:
            start_time = schedule_info['start_time']
            end_time = schedule_info['end_time']
            video_url = schedule_info['video_url']
            name = schedule_info['name']
            
            # 시작 시간 스케줄링
            job1 = schedule.every().day.at(start_time).do(
                self._start_video, video_url, name
            )
            
            # 종료 시간 스케줄링  
            job2 = schedule.every().day.at(end_time).do(
                self._stop_video, name
            )
            
            self.current_jobs.extend([job1, job2])
            print(f"  - {name}: {start_time}에 시작, {end_time}에 종료")
        
        self.is_running = True
        
        # 스케줄러 실행 (별도 스레드에서)
        scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print("\n✅ 스케줄러가 활성화되었습니다. 매일 설정된 시간에 자동으로 실행됩니다.")
        
    def _start_video(self, video_url, schedule_name="방송"):
        """비디오 재생 시작"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n🎵 [{current_time}] {schedule_name} 시작 - 동영상을 재생합니다.")
            
            # 이미 실행 중인 브라우저가 있으면 종료
            if self.driver:
                print("기존 브라우저를 종료하고 새로 시작합니다.")
                self.driver.quit()
                
            self.driver = play_youtube_video(video_url)
            print(f"✅ {schedule_name} 재생 중...")
            
        except Exception as e:
            print(f"❌ {schedule_name} 재생 중 오류 발생: {e}")
    
    def _stop_video(self, schedule_name="방송"):
        """비디오 재생 종료"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            
            if self.driver:
                print(f"\n🔇 [{current_time}] {schedule_name} 종료 - 브라우저를 닫습니다.")
                self.driver.quit()
                self.driver = None
                print(f"✅ {schedule_name} 종료 완료")
            else:
                print(f"⚠️ [{current_time}] {schedule_name} 종료 요청이지만 실행 중인 브라우저가 없습니다.")
                
        except Exception as e:
            print(f"❌ {schedule_name} 종료 중 오류 발생: {e}")
    
    def _run_scheduler(self):
        """스케줄러 실행"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        print("\n🛑 스케줄러를 중지합니다...")
        self.is_running = False
        schedule.clear()
        
        if self.driver:
            self.driver.quit()
            self.driver = None
            
        self.current_jobs.clear()
        self.schedules.clear()
        print("✅ 스케줄러가 중지되었습니다.")
    
    def emergency_stop(self):
        """비상 정지"""
        print("\n🚨 비상 정지!")
        if self.driver:
            self.driver.quit()
            self.driver = None
        print("✅ 모든 작업이 긴급 중단되었습니다.")

def test_scheduler():
    """
    테스트 함수: 현재 시간 +5초에 시작, +10초에 종료
    """
    print("=== 테스트 모드 ===")
    now = datetime.now()
    
    # 5초 후 시작, 10초 후 종료
    start_time = (now + timedelta(seconds=5)).strftime('%H:%M:%S')
    end_time = (now + timedelta(seconds=10)).strftime('%H:%M:%S')
    
    print(f"현재 시간: {now.strftime('%H:%M:%S')}")
    print(f"시작 예정: {start_time}")
    print(f"종료 예정: {end_time}")
    
    scheduler = VideoScheduler()
    
    # 초 단위까지 포함한 스케줄링을 위해 직접 구현
    def wait_and_start():
        wait_seconds = 5
        print(f"{wait_seconds}초 후 동영상이 재생됩니다...")
        time.sleep(wait_seconds)
        
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        scheduler._start_video(video_url, "테스트")
        
        # 5초 더 기다린 후 종료 (총 10초)
        print("5초 후 브라우저가 종료됩니다...")
        time.sleep(5)
        scheduler._stop_video("테스트")
    
    # 테스트 실행
    test_thread = threading.Thread(target=wait_and_start, daemon=True)
    test_thread.start()
    
    return scheduler

if __name__ == "__main__":
    # 테스트 모드 선택
    mode = input("실행 모드를 선택하세요 (1: 일반, 2: 테스트): ").strip()
    
    if mode == "2":
        scheduler = test_scheduler()
        input("엔터를 누르면 프로그램을 종료합니다...")
        scheduler.stop_scheduler()
    else:
        # 직접 스케줄 설정 예시
        scheduler = VideoScheduler()
        
        # 여러 스케줄 추가
        scheduler.add_schedule("12:30", "13:00", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "점심시간")
        scheduler.add_schedule("18:00", "18:30", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "저녁시간")
        
        scheduler.start_scheduler()
        
        try:
            input("엔터를 누르면 스케줄러를 중지합니다...")
        except KeyboardInterrupt:
            scheduler.emergency_stop()
        finally:
            scheduler.stop_scheduler()