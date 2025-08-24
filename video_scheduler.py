import time
import schedule
import threading
from datetime import datetime, timedelta
from functools import partial
from playvideo import play_youtube_video

class VideoScheduler:
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.current_jobs = []
        self.schedules = []
        self.scheduler_thread = None
        self.active_timers = []  # 직접 타이머 관리용
        self.use_direct_timer = True  # 직접 타이머 사용 플래그
        
    def add_schedule(self, start_time, end_time, video_url, schedule_name="방송"):
        """
        스케줄을 추가하는 함수 (기존 호환성 유지)
        """
        return self.add_daily_schedule("매일", start_time, end_time, video_url, schedule_name)
    
    def _create_start_function(self, video_url, schedule_name):
        """시작 함수를 동적으로 생성"""
        def start_func():
            return self._start_video(video_url, schedule_name)
        start_func.__name__ = f"START_{schedule_name}"
        return start_func
    
    def _create_end_function(self, schedule_name):
        """종료 함수를 동적으로 생성"""
        def end_func():
            return self._stop_video(schedule_name)
        end_func.__name__ = f"END_{schedule_name}"
        return end_func
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
        """모든 등록된 스케줄을 활성화하는 함수 (직접 타이머 방식)"""
        if not self.schedules:
            print("❌ 등록된 스케줄이 없습니다.")
            return
            
        print(f"\n📅 총 {len(self.schedules)}개의 스케줄을 등록합니다:")
        
        if self.use_direct_timer:
            return self._start_direct_timer_scheduler()
        else:
            return self._start_schedule_library_scheduler()
    
    def _start_direct_timer_scheduler(self):
        """직접 타이머를 사용한 스케줄러"""
        print("🔧 직접 타이머 방식 사용")
        
        # 기존 타이머 정리
        self._clear_timers()
        
        now = datetime.now()
        current_weekday = now.weekday()  # 0=월요일, 6=일요일
        
        # 요일 매핑
        weekday_map = {
            "월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, 
            "금요일": 4, "토요일": 5, "일요일": 6
        }
        
        timer_count = 0
        
        for schedule_info in self.schedules:
            day = schedule_info.get('day', '매일')
            start_time = schedule_info['start_time']
            end_time = schedule_info['end_time']
            video_url = schedule_info['video_url']
            name = schedule_info['name']
            
            print(f"🔄 스케줄 처리 중: {name} ({day} {start_time} ~ {end_time})")
            
            # 다음 실행 시간 계산
            target_times = self._calculate_next_execution_times(day, start_time, end_time, weekday_map, now)
            
            for target_time, action in target_times:
                if target_time > now:
                    delay = (target_time - now).total_seconds()
                    
                    if action == "start":
                        timer = threading.Timer(delay, self._start_video, args=(video_url, name))
                        print(f"  ⏰ 시작 타이머: {target_time.strftime('%Y-%m-%d %H:%M:%S')} ({delay:.1f}초 후)")
                    else:  # action == "end"
                        timer = threading.Timer(delay, self._stop_video, args=(name,))
                        print(f"  ⏰ 종료 타이머: {target_time.strftime('%Y-%m-%d %H:%M:%S')} ({delay:.1f}초 후)")
                    
                    timer.start()
                    self.active_timers.append(timer)
                    timer_count += 1
        
        if timer_count == 0:
            print("❌ 설정된 시간에 실행할 스케줄이 없습니다.")
            return
        
        self.is_running = True
        print(f"\n✅ 직접 타이머 스케줄러가 활성화되었습니다. {timer_count}개 타이머 등록됨")
        
        # 모니터링 스레드 시작
        self.scheduler_thread = threading.Thread(target=self._monitor_timers, daemon=True)
        self.scheduler_thread.start()
    
    def _calculate_next_execution_times(self, day, start_time, end_time, weekday_map, now):
        """다음 실행 시간들을 계산"""
        target_times = []
        
        try:
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
        except ValueError:
            print(f"❌ 잘못된 시간 형식: {start_time} ~ {end_time}")
            return target_times
        
        if day == "매일":
            # 매일 실행
            start_today = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            end_today = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            
            if start_today > now:
                target_times.append((start_today, "start"))
                target_times.append((end_today, "end"))
            else:
                # 내일 실행
                start_tomorrow = start_today + timedelta(days=1)
                end_tomorrow = end_today + timedelta(days=1)
                target_times.append((start_tomorrow, "start"))
                target_times.append((end_tomorrow, "end"))
                
        elif day in weekday_map:
            # 특정 요일 실행
            target_weekday = weekday_map[day]
            
            # 이번 주 해당 요일
            days_until_target = (target_weekday - now.weekday()) % 7
            if days_until_target == 0:  # 오늘이 해당 요일
                target_date = now.date()
                start_target = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
                
                if start_target > now:
                    # 오늘 아직 시간이 남음
                    end_target = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=end_hour, minutes=end_minute)
                    target_times.append((start_target, "start"))
                    target_times.append((end_target, "end"))
                else:
                    # 다음 주 해당 요일
                    days_until_target = 7
            
            if not target_times:  # 오늘이 아니거나 시간이 지남
                target_date = now.date() + timedelta(days=days_until_target)
                start_target = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
                end_target = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=end_hour, minutes=end_minute)
                target_times.append((start_target, "start"))
                target_times.append((end_target, "end"))
        
        return target_times
    
    def _monitor_timers(self):
        """타이머 모니터링"""
        print("⏰ 타이머 모니터링 시작...")
        
        while self.is_running:
            try:
                # 활성 타이머 수 확인
                active_count = sum(1 for timer in self.active_timers if timer.is_alive())
                
                if active_count == 0 and self.active_timers:
                    print("📋 모든 타이머가 완료되었습니다.")
                
                time.sleep(60)  # 1분마다 체크
                
            except Exception as e:
                print(f"❌ 타이머 모니터링 중 오류: {e}")
                time.sleep(5)
        
        print("🛑 타이머 모니터링 종료")
    
    def _clear_timers(self):
        """모든 활성 타이머 정리"""
        for timer in self.active_timers:
            if timer.is_alive():
                timer.cancel()
        self.active_timers.clear()
    
    def _start_schedule_library_scheduler(self):
        """기존 schedule 라이브러리 방식 (백업용)"""
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
            "매일": schedule.every().day,
            "오늘": schedule.every().day  # 오늘 즉시 실행용 추가
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
                    print(f"  🔧 스케줄 등록 시작...")
                    
                    # 각 작업을 별도로 등록 (변수 참조 문제 해결)
                    # 시작 시간 스케줄링
                    start_job = scheduler_obj.at(start_time).do(
                        self._start_video, video_url, name
                    )
                    start_job.tag = f"{name}_START"
                    
                    print(f"      시작 작업 등록됨: {start_job}")
                    
                    # 종료 시간 스케줄링을 완전히 분리된 방식으로  
                    end_job = scheduler_obj.at(end_time).do(
                        self._stop_video, name
                    )
                    end_job.tag = f"{name}_END"
                    
                    print(f"      종료 작업 등록됨: {end_job}")
                    
                    self.current_jobs.extend([start_job, end_job])
                    print(f"  ✅ {name}: {day} {start_time}에 시작, {end_time}에 종료")
                    
                    # 주말인 경우 추가 로그 및 검증
                    if day in ["토요일", "일요일"]:
                        print(f"  🏖️ 주말 스케줄 등록 완료: {day}")
                        print(f"    - 시작 다음 실행: {start_job.next_run}")
                        print(f"    - 종료 다음 실행: {end_job.next_run}")
                        
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
            job_tag = getattr(job, 'tag', 'No tag')
            
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
            
            print(f"  {i+1}. {job} (요일: {job_day}, 태그: {job_tag})")
            print(f"      다음 실행: {job.next_run}")
            
            # 시작 작업과 종료 작업 구분
            if "START" in job_tag:
                print(f"      🎵 START 작업")
            elif "END" in job_tag:
                print(f"      🔇 END 작업")
            
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
            
            print(f"\n🚨🚨🚨 _START_VIDEO 함수 호출됨! 🚨🚨🚨")
            print(f"🎵 [{current_time}] {schedule_name} 시작! (오늘: {current_day_kr}, weekday: {weekday_num})")
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
            print("🚀 브라우저 시작 중...")
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
            
            print(f"\n🚨🚨🚨 _STOP_VIDEO 함수 호출됨! 🚨🚨🚨")
            
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
                
                # 스케줄 실행 (실행 전 로그 추가)
                pending_jobs = [job for job in schedule.get_jobs() if job.should_run]
                if pending_jobs:
                    print(f"\n🎯 [{now.strftime('%H:%M:%S')}] 실행 예정 작업 {len(pending_jobs)}개:")
                    for job in pending_jobs:
                        func_name = job.job_func.__name__ if hasattr(job, 'job_func') else "Unknown"
                        tag = getattr(job, 'tag', 'No tag')
                        print(f"   - {func_name} ({tag}) - 예정시간: {job.next_run}")
                        
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
        
        # 직접 타이머 정리
        self._clear_timers()
        
        # 기존 schedule 라이브러리 정리
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
        
        # 모든 타이머 즉시 취소
        self._clear_timers()
        
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