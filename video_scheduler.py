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
        self.scheduler_thread = None
        
    def add_schedule(self, start_time, end_time, video_url, schedule_name="방송"):
        """
        스케줄을 추가하는 함수 (기존 호환성 유지)
        """
        return self.add_daily_schedule("매일", start_time, end_time, video_url, schedule_name)
    
    def add_daily_schedule(self, day, start_time, end_time, video_url, schedule_name="방송"):
        """
        요일별 스케줄을 추가하는 함수
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
            'day': day,
            'start_time': start_time,
            'end_time': end_time,
            'video_url': video_url,
            'name': schedule_name
        }
        
        self.schedules.append(schedule_info)
        print(f"✅ 스케줄 추가됨: {schedule_name} ({day} {start_time} ~ {end_time})")
        return True

    def start_scheduler(self):
        """모든 등록된 스케줄을 활성화하는 함수"""
        if not self.schedules:
            print("❌ 등록된 스케줄이 없습니다.")
            return
            
        print(f"\n📅 총 {len(self.schedules)}개의 스케줄을 등록합니다:")
        
        # 요일 매핑 - 주말 포함 (명시적)
        day_mapping = {
            "월요일": schedule.every().monday,
            "화요일": schedule.every().tuesday,
            "수요일": schedule.every().wednesday,
            "목요일": schedule.every().thursday,
            "금요일": schedule.every().friday,
            "토요일": schedule.every().saturday,  # 토요일 명시적 추가
            "일요일": schedule.every().sunday,    # 일요일 명시적 추가
            "매일": schedule.every().day
        }
        
        # 기존 스케줄 클리어
        schedule.clear()
        self.current_jobs.clear()
        
        # 주말 스케줄 카운터
        weekend_schedule_count = 0
        weekday_schedule_count = 0
        
        for schedule_info in self.schedules:
            day = schedule_info.get('day', '매일')
            start_time = schedule_info['start_time']
            end_time = schedule_info['end_time']
            video_url = schedule_info['video_url']
            name = schedule_info['name']
            
            print(f"🔄 스케줄 등록 중: {name} ({day} {start_time} ~ {end_time})")
            
            # 주말 카운트
            if day in ["토요일", "일요일"]:
                weekend_schedule_count += 1
                print(f"  🏖️ 주말 스케줄 감지: {day}")
            else:
                weekday_schedule_count += 1
            
            # 요일별 스케줄링
            if day in day_mapping:
                scheduler_obj = day_mapping[day]
                
                try:
                    # 시작 시간 스케줄링
                    job1 = scheduler_obj.at(start_time).do(
                        self._start_video, video_url, name
                    )
                    
                    # 종료 시간 스케줄링  
                    job2 = scheduler_obj.at(end_time).do(
                        self._stop_video, name
                    )
                    
                    self.current_jobs.extend([job1, job2])
                    print(f"  ✅ {name}: {day} {start_time}에 시작, {end_time}에 종료")
                    
                    # 주말인 경우 추가 로그 및 검증
                    if day in ["토요일", "일요일"]:
                        print(f"  � 주말 스케줄 등록 완료: {day}")
                        print(f"    - 시작 작업: {job1}")
                        print(f"    - 종료 작업: {job2}")
                        print(f"    - 다음 실행: {job1.next_run}")
                        
                except Exception as e:
                    print(f"❌ {day} 스케줄 등록 실패: {e}")
                    import traceback
                    traceback.print_exc()
                    
            else:
                print(f"❌ 지원하지 않는 요일: {day}")
        
        self.is_running = True
        
        # 스케줄러 실행 (별도 스레드에서)
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print(f"\n✅ 스케줄러가 활성화되었습니다. {len(self.current_jobs)}개 작업이 등록됨")
        print(f"📊 스케줄 통계:")
        print(f"  - 평일 스케줄: {weekday_schedule_count}개")
        print(f"  - 주말 스케줄: {weekend_schedule_count}개")
        print(f"  - 총 작업: {len(self.current_jobs)}개")
        
        print("📋 등록된 작업 목록:")
        for i, job in enumerate(schedule.get_jobs()):
            job_day = "Unknown"
            if hasattr(job, 'start_day'):
                job_day = job.start_day
            elif 'monday' in str(job):
                job_day = "월요일"
            elif 'tuesday' in str(job):
                job_day = "화요일"
            elif 'wednesday' in str(job):
                job_day = "수요일"
            elif 'thursday' in str(job):
                job_day = "목요일"
            elif 'friday' in str(job):
                job_day = "금요일"
            elif 'saturday' in str(job):
                job_day = "토요일"
            elif 'sunday' in str(job):
                job_day = "일요일"
            
            print(f"  {i+1}. {job} (요일: {job_day})")
            
        # 주말 스케줄이 있는 경우 특별 알림
        if weekend_schedule_count > 0:
            print(f"\n🏖️ 주말 스케줄 {weekend_schedule_count}개가 정상 등록되었습니다!")
            print("  토요일과 일요일에도 자동 실행됩니다.")

    def _start_video(self, video_url, schedule_name="방송"):
        """비디오 재생 시작"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_day = datetime.now().strftime('%A')  # 요일 (영어)
            current_day_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][datetime.now().weekday()]
            weekday_num = datetime.now().weekday()  # 0=월요일, 6=일요일
            
            print(f"\n🎵 [{current_time}] {schedule_name} 시작! (오늘: {current_day_kr}, weekday: {weekday_num})")
            print(f"📺 동영상 URL: {video_url}")
            
            # 주말인지 확인하고 로그 출력
            if weekday_num >= 5:  # 5=토요일, 6=일요일
                print(f"🏖️ 주말 스케줄 실행 중: {current_day_kr}")
            
            # 이미 실행 중인 브라우저가 있으면 종료
            if self.driver:
                print("⚠️ 기존 브라우저를 종료합니다.")
                self.driver.quit()
                self.driver = None
            
            # 새 브라우저 시작
            self.driver = play_youtube_video(video_url)
            
            if self.driver:
                print(f"✅ {schedule_name} 재생 시작 완료! (요일: {current_day_kr})")
                if weekday_num >= 5:
                    print(f"🎉 주말 스케줄 성공적으로 실행됨!")
            else:
                print(f"❌ {schedule_name} 재생 시작 실패")
                
        except Exception as e:
            print(f"❌ {schedule_name} 시작 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    def _stop_video(self, schedule_name="방송"):
        """비디오 재생 종료"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_day_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][datetime.now().weekday()]
            
            if self.driver:
                print(f"\n🔇 [{current_time}] {schedule_name} 종료 (오늘: {current_day_kr})")
                self.driver.quit()
                self.driver = None
                print(f"✅ {schedule_name} 종료 완료")
            else:
                print(f"⚠️ [{current_time}] {schedule_name} 종료 요청이지만 실행 중인 브라우저가 없습니다.")
                
        except Exception as e:
            print(f"❌ {schedule_name} 종료 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_scheduler(self):
        """스케줄러 실행"""
        print("⏰ 스케줄러 루프 시작...")
        print("📋 스케줄러 디버깅 정보:")
        
        # 등록된 모든 작업 출력
        jobs = schedule.get_jobs()
        for i, job in enumerate(jobs):
            print(f"  작업 {i+1}: {job}")
            print(f"    다음 실행: {job.next_run}")
            print(f"    함수: {job.job_func.__name__}")
        
        minute_counter = 0
        
        while self.is_running:
            try:
                now = datetime.now()
                current_weekday = now.weekday()  # 0=월요일, 6=일요일
                current_day_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][current_weekday]
                
                # 매 분마다 상태 출력 (디버깅용)
                if now.second == 0:
                    minute_counter += 1
                    jobs = schedule.get_jobs()
                    
                    if minute_counter % 5 == 0:  # 5분마다 상세 정보 출력
                        print(f"\n⏰ [{now.strftime('%Y-%m-%d %H:%M:%S')}] 스케줄러 상태 체크")
                        print(f"📅 오늘: {current_day_kr} (weekday: {current_weekday})")
                        print(f"📊 등록된 작업 수: {len(jobs)}")
                        
                        if current_weekday >= 5:  # 주말인 경우
                            print(f"🏖️ 현재 주말입니다: {current_day_kr}")
                            weekend_jobs = [job for job in jobs if '토요일' in str(job) or '일요일' in str(job)]
                            print(f"🎯 주말 관련 작업 수: {len(weekend_jobs)}")
                        
                        if jobs:
                            next_job = min(jobs, key=lambda job: job.next_run)
                            print(f"⏳ 다음 실행 예정: {next_job.next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"📋 다음 작업: {next_job}")
                        else:
                            print("⚠️ 등록된 작업이 없습니다!")
                
                # 스케줄 실행
                schedule.run_pending()
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ 스케줄러 실행 중 오류: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)  # 오류 발생 시 5초 대기
        
        print("🛑 스케줄러 루프 종료")

    def stop_scheduler(self):
        """스케줄러 중지"""
        print("\n🛑 스케줄러를 중지합니다...")
        self.is_running = False
        schedule.clear()
        
        if self.driver:
            self.driver.quit()
            self.driver = None
            
        self.current_jobs.clear()
        print("✅ 스케줄러가 중지되었습니다.")
    
    def emergency_stop(self):
        """비상 정지"""
        print("\n🚨 비상 정지!")
        self.is_running = False
        if self.driver:
            self.driver.quit()
            self.driver = None
        schedule.clear()
        self.current_jobs.clear()
        print("✅ 모든 작업이 긴급 중단되었습니다.")

def test_scheduler():
    """테스트용 스케줄러 - 주말 포함"""
    from datetime import datetime, timedelta
    
    # 현재 시간 + 5초, +10초로 테스트 시간 설정
    now = datetime.now()
    start_time = (now + timedelta(seconds=5)).strftime("%H:%M")
    end_time = (now + timedelta(seconds=10)).strftime("%H:%M")
    
    current_day = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][now.weekday()]
    
    print(f"테스트 스케줄: {start_time} ~ {end_time}")
    print(f"오늘: {current_day}")
    
    scheduler = VideoScheduler()
    
    # 오늘 요일로 테스트 스케줄 추가
    scheduler.add_daily_schedule(
        day=current_day,
        start_time=start_time,
        end_time=end_time,
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        schedule_name=f"테스트 방송 ({current_day})"
    )
    
    # 주말인 경우 특별 메시지
    if current_day in ["토요일", "일요일"]:
        print(f"🏖️ 주말 테스트입니다: {current_day}")
    
    scheduler.start_scheduler()
    return scheduler