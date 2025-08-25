import time
import schedule
import threading
from datetime import datetime, timedelta
from functools import partial
from play_video import play_youtube_video
from media_controller import get_media_controller, MediaType

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
        return self.add_daily_schedule("매일", start_time, end_time, video_url, schedule_name, "youtube")
    
    def add_daily_schedule(self, day, start_time, end_time, source, schedule_name="방송", media_type="youtube"):
        """
        요일별 스케줄을 추가하는 함수 (YouTube와 로컬 음원 지원)
        
        Args:
            day: 요일 ("월요일", "화요일", ... 또는 "매일")
            start_time: 시작 시간 ("HH:MM")
            end_time: 종료 시간 ("HH:MM")
            source: YouTube URL 또는 로컬 파일 경로
            schedule_name: 스케줄 이름
            media_type: "youtube" 또는 "local_audio"
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

        # 미디어 타입 검증
        if media_type not in ["youtube", "local_audio"]:
            print(f"❌ 지원하지 않는 미디어 타입: {media_type}")
            return False

        schedule_info = {
            'day': day,
            'start_time': start_time,
            'end_time': end_time,
            'source': source,
            'name': schedule_name,
            'media_type': media_type
        }
        
        self.schedules.append(schedule_info)
        print(f"✅ 스케줄 추가됨: {schedule_name} ({day} {start_time} ~ {end_time}) - {media_type}")
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
            source = schedule_info['source']
            name = schedule_info['name']
            media_type = schedule_info.get('media_type', 'youtube')
            
            print(f"🔄 스케줄 처리 중: {name} ({day} {start_time} ~ {end_time}) - {media_type}")
            
            # 다음 실행 시간 계산
            target_times = self._calculate_next_execution_times(day, start_time, end_time, weekday_map, now)
            
            for target_time, action in target_times:
                if target_time > now:
                    delay = (target_time - now).total_seconds()
                    
                    if action == "start":
                        timer = threading.Timer(delay, self._start_media, args=(source, name, media_type))
                        print(f"  ⏰ 시작 타이머: {target_time.strftime('%Y-%m-%d %H:%M:%S')} ({delay:.1f}초 후) - {media_type}")
                    else:  # action == "end"
                        timer = threading.Timer(delay, self._stop_media, args=(name,))
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
        """모든 활성 타이머 정리 - 비동기 처리로 개선"""
        if not self.active_timers:
            return
            
        print(f"🔄 {len(self.active_timers)}개 타이머 정리 중...")
        
        # 백그라운드에서 비동기적으로 타이머 정리
        def clear_timers_async():
            try:
                cleared_count = 0
                for timer in self.active_timers:
                    if timer.is_alive():
                        timer.cancel()
                        cleared_count += 1
                print(f"✅ {cleared_count}개 타이머 정리 완료")
            except Exception as e:
                print(f"⚠️ 타이머 정리 중 오류: {e}")
        
        # 백그라운드 스레드에서 실행
        clear_thread = threading.Thread(target=clear_timers_async, daemon=True)
        clear_thread.start()
        
        # 즉시 리스트 정리 (UI 블로킹 방지)
        self.active_timers.clear()
    
    def _start_media(self, source, schedule_name="방송", media_type="youtube"):
        """미디어 재생 시작 (YouTube 또는 로컬 음원)"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_day_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][datetime.now().weekday()]
            weekday_num = datetime.now().weekday()
            
            print(f"\n🚨🚨🚨 _START_MEDIA 함수 호출됨! 🚨🚨🚨")
            print(f"🎵 [{current_time}] {schedule_name} 시작! (오늘: {current_day_kr}, 타입: {media_type})")
            print(f"📁 소스: {source}")
            
            # 주말인지 확인하고 로그 출력
            if weekday_num >= 5:
                print(f"🏖️ 주말 스케줄 실행 중: {current_day_kr}")
            
            # 🛡️ 미디어 컨트롤러를 통한 안전한 재생
            media_controller = get_media_controller()
            status = media_controller.get_current_status()
            print(f"🔍 현재 미디어 상태: {status}")
            
            success = False
            
            if media_type == "youtube":
                # YouTube 재생
                success = media_controller.play_youtube(source)
                if success:
                    self.driver = media_controller.active_driver  # 레거시 호환성
                    
            elif media_type == "local_audio":
                # 로컬 음원 재생
                success = media_controller.play_local_audio(source)
                
            else:
                print(f"❌ 지원하지 않는 미디어 타입: {media_type}")
                return
            
            if success:
                print(f"✅ {schedule_name} 재생 시작 완료! (요일: {current_day_kr}, 타입: {media_type})")
                if weekday_num >= 5:
                    print(f"🎉 주말 스케줄 성공적으로 실행됨!")
            else:
                print(f"❌ {schedule_name} 재생 시작 실패")
                
        except Exception as e:
            print(f"❌ {schedule_name} 시작 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    def _stop_media(self, schedule_name="방송"):
        """미디어 재생 종료 (YouTube 또는 로컬 음원) - 향상된 안전 종료"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_day_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][datetime.now().weekday()]
            
            print(f"\n🚨🚨🚨 _STOP_MEDIA 함수 호출됨! 🚨🚨🚨")
            print(f"🔇 [{current_time}] {schedule_name} 종료 (오늘: {current_day_kr})")
            
            # 🛡️ 미디어 컨트롤러를 통한 안전한 정지
            media_controller = get_media_controller()
            status = media_controller.get_current_status()
            print(f"🔍 정지 전 미디어 상태: {status}")
            
            # 현재 미디어가 실제로 활성화되어 있는지 확인
            is_media_active = (
                status.get('state') == 'playing' or 
                status.get('has_youtube') or 
                status.get('has_audio')
            )
            
            if not is_media_active:
                print(f"ℹ️ {schedule_name}: 종료할 활성 미디어가 없습니다.")
                self.driver = None  # 레거시 정리
                return
            
            # 미디어 컨트롤러를 통한 안전 정지
            success = False
            try:
                print(f"🛑 {schedule_name}: 미디어 컨트롤러를 통한 안전 정지 시도...")
                success = media_controller.safe_stop_current()
                
                if success:
                    print(f"✅ {schedule_name}: 미디어 컨트롤러를 통한 정지 성공")
                else:
                    print(f"⚠️ {schedule_name}: 미디어 컨트롤러 정지 중 일부 문제 발생")
                    
            except Exception as controller_error:
                print(f"❌ {schedule_name}: 미디어 컨트롤러 정지 실패: {controller_error}")
                success = False
            
            # 정지 실패 시 강제 정지 시도
            if not success:
                print(f"🔧 {schedule_name}: 강제 정지 시도...")
                try:
                    media_controller.force_stop_all()
                    success = True
                    print(f"✅ {schedule_name}: 강제 정지 완료")
                except Exception as force_error:
                    print(f"❌ {schedule_name}: 강제 정지도 실패: {force_error}")
            
            # 레거시 정리 (이중 안전장치)
            if self.driver:
                try:
                    print(f"🔧 {schedule_name}: 레거시 WebDriver 정리 시도...")
                    # WebDriver 상태 체크
                    try:
                        self.driver.current_url  # 상태 체크
                        self.driver.quit()
                        print(f"✅ {schedule_name}: 레거시 WebDriver 정상 종료")
                    except Exception:
                        print(f"ℹ️ {schedule_name}: 레거시 WebDriver가 이미 종료되어 정리만 수행")
                    
                except Exception as legacy_error:
                    print(f"⚠️ {schedule_name}: 레거시 정리 중 오류: {legacy_error}")
                finally:
                    self.driver = None
            
            # 최종 상태 확인
            try:
                final_status = media_controller.get_current_status()
                if final_status.get('state') == 'idle':
                    print(f"🎯 {schedule_name}: 완전 종료 확인됨")
                else:
                    print(f"⚠️ {schedule_name}: 종료 후에도 일부 프로세스가 남아있을 수 있음")
            except Exception as status_check_error:
                print(f"⚠️ {schedule_name}: 최종 상태 확인 실패: {status_check_error}")
            
            print(f"🏁 {schedule_name}: 종료 과정 완료")
                
        except Exception as e:
            print(f"❌ {schedule_name} 종료 중 오류 발생: {e}")
            # 오류 발생 시에도 정리는 수행
            self.driver = None
            try:
                # 오류 상황에서도 강제 정리 시도
                media_controller = get_media_controller()
                media_controller.force_stop_all()
                print(f"🔧 {schedule_name}: 오류 상황에서 강제 정리 완료")
            except Exception as emergency_error:
                print(f"❌ {schedule_name}: 비상 정리도 실패: {emergency_error}")
            
            import traceback
            traceback.print_exc()

    # 레거시 호환성을 위한 기존 함수들
    def _start_video(self, video_url, schedule_name="방송"):
        """비디오 재생 시작 (레거시 호환성 함수)"""
        return self._start_media(video_url, schedule_name, "youtube")

    def _stop_video(self, schedule_name="방송"):
        """비디오 재생 종료 (레거시 호환성 함수)"""
        return self._stop_media(schedule_name)

    def stop_scheduler(self):
        """스케줄러 중지 - 응답성 개선된 버전"""
        print("\n🛑 스케줄러를 중지합니다...")
        
        # 즉시 실행 플래그 비활성화 (새로운 타이머 생성 방지)
        self.is_running = False
        
        # 백그라운드에서 정리 작업 수행 (UI 블로킹 방지)
        def cleanup_async():
            try:
                print("🧹 백그라운드 정리 작업 시작...")
                
                # 1. 타이머 정리 (이미 비동기 처리됨)
                self._clear_timers()
                
                # 2. schedule 라이브러리 정리
                schedule.clear()
                
                # 3. 미디어 컨트롤러를 통한 안전한 정지 (단축된 타임아웃)
                try:
                    media_controller = get_media_controller()
                    # 빠른 정지를 위해 force_stop_all 사용
                    media_controller.force_stop_all()
                    print("✅ 미디어 컨트롤러 정지 완료")
                except Exception as e:
                    print(f"⚠️ 미디어 컨트롤러 정지 중 오류: {e}")
                
                # 4. 레거시 WebDriver 정리 (타임아웃 적용)
                if self.driver:
                    try:
                        import threading
                        quit_event = threading.Event()
                        
                        def quit_driver():
                            try:
                                self.driver.quit()
                                quit_event.set()
                            except Exception:
                                quit_event.set()  # 오류가 있어도 완료 처리
                        
                        quit_thread = threading.Thread(target=quit_driver, daemon=True)
                        quit_thread.start()
                        
                        # 2초 타임아웃으로 대기
                        if quit_event.wait(2.0):
                            print("✅ 레거시 WebDriver 정리 완료")
                        else:
                            print("⚠️ 레거시 WebDriver 정리 타임아웃 (백그라운드에서 계속 진행)")
                            
                    except Exception as legacy_error:
                        print(f"⚠️ 레거시 WebDriver 정리 중 오류: {legacy_error}")
                    finally:
                        self.driver = None
                
                # 5. 작업 목록 정리
                self.current_jobs.clear()
                
                print("🏁 백그라운드 정리 작업 완료")
                
            except Exception as e:
                print(f"❌ 백그라운드 정리 중 오류: {e}")
        
        # 백그라운드에서 정리 작업 실행
        cleanup_thread = threading.Thread(target=cleanup_async, daemon=True)
        cleanup_thread.start()
        
        # UI에 즉시 완료 알림 (실제 정리는 백그라운드에서 진행)
        print("✅ 스케줄러 중지 요청 완료 (백그라운드 정리 진행 중...)")
        
        return True  # UI 응답성을 위해 즉시 반환
    
    def emergency_stop(self):
        """비상 정지 - 모든 미디어 강제 정지 - 응답성 개선된 버전"""
        print("\n🚨 비상 정지!")
        
        # 즉시 실행 플래그 비활성화
        self.is_running = False
        
        # 백그라운드에서 강제 정리 (UI 블로킹 방지)
        def emergency_cleanup():
            try:
                print("� 비상 정리 작업 시작...")
                
                # 미디어 컨트롤러를 통한 강제 정지
                try:
                    from media_controller import emergency_stop_all_media
                    emergency_stop_all_media()
                    print("🛡️ 미디어 컨트롤러를 통한 강제 정지 완료")
                except Exception as e:
                    print(f"⚠️ 미디어 컨트롤러 강제 정지 실패: {e}")
                
                # 타이머 및 스케줄 정리
                self._clear_timers()
                schedule.clear()
                
                # 레거시 WebDriver 강제 정리 (타임아웃 1초)
                if self.driver:
                    try:
                        import threading
                        quit_event = threading.Event()
                        
                        def force_quit():
                            try:
                                self.driver.quit()
                            except Exception:
                                pass
                            finally:
                                quit_event.set()
                        
                        quit_thread = threading.Thread(target=force_quit, daemon=True)
                        quit_thread.start()
                        
                        if quit_event.wait(1.0):
                            print("🔧 레거시 WebDriver 강제 종료 완료")
                        else:
                            print("⚠️ 레거시 WebDriver 강제 종료 타임아웃")
                            
                    except Exception as e:
                        print(f"❌ 레거시 WebDriver 강제 종료 실패: {e}")
                    finally:
                        self.driver = None
                
                self.current_jobs.clear()
                print("🏁 비상 정리 완료")
                
            except Exception as e:
                print(f"❌ 비상 정리 중 오류: {e}")
        
        # 백그라운드에서 비상 정리 실행
        emergency_thread = threading.Thread(target=emergency_cleanup, daemon=True)
        emergency_thread.start()
        
        print("✅ 비상 정지 요청 완료 (백그라운드 정리 진행 중...)")
        
        return True  # UI 응답성을 위해 즉시 반환

    def get_next_execution_time(self):
        """다음 실행 시간 반환 (GUI용)"""
        if not self.schedules or not self.is_running:
            return None
            
        now = datetime.now()
        next_times = []
        
        weekday_map = {
            "월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, 
            "금요일": 4, "토요일": 5, "일요일": 6
        }
        
        for schedule_info in self.schedules:
            day = schedule_info.get('day', '매일')
            start_time = schedule_info['start_time']
            end_time = schedule_info['end_time']
            
            target_times = self._calculate_next_execution_times(day, start_time, end_time, weekday_map, now)
            
            for target_time, action in target_times:
                if target_time > now and action == "start":
                    next_times.append((target_time, schedule_info))
        
        if next_times:
            # 가장 가까운 시간 반환
            next_time, next_schedule = min(next_times, key=lambda x: x[0])
            return {
                'time': next_time,
                'schedule': next_schedule
            }
        
        return None
    
    def get_next_schedule(self):
        """다음 스케줄 정보 반환 (GUI 헤더용)"""
        try:
            if not self.schedules:
                return None
                
            now = datetime.now()
            next_times = []
            
            weekday_map = {
                "월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, 
                "금요일": 4, "토요일": 5, "일요일": 6
            }
            
            # 요일 이름 매핑 (축약형)
            day_name_map = {
                "월요일": "월", "화요일": "화", "수요일": "수", "목요일": "목",
                "금요일": "금", "토요일": "토", "일요일": "일", "매일": "매일"
            }
            
            for schedule_info in self.schedules:
                day = schedule_info.get('day', '매일')
                start_time = schedule_info['start_time']
                end_time = schedule_info['end_time']
                
                target_times = self._calculate_next_execution_times(day, start_time, end_time, weekday_map, now)
                
                for target_time, action in target_times:
                    if target_time > now and action == "start":
                        # 스케줄 정보에 추가 정보 포함
                        schedule_with_info = {
                            'day': day,
                            'day_name': day_name_map.get(day, day),
                            'start_time': start_time,
                            'end_time': end_time,
                            'content': schedule_info.get('name', '방송'),
                            'media_type': schedule_info.get('media_type', 'youtube'),
                            'source': schedule_info.get('source', ''),
                            'target_time': target_time
                        }
                        next_times.append((target_time, schedule_with_info))
            
            if next_times:
                # 가장 가까운 시간의 스케줄 반환
                next_time, next_schedule = min(next_times, key=lambda x: x[0])
                return next_schedule
            
            return None
            
        except Exception as e:
            print(f"❌ 다음 스케줄 조회 중 오류: {e}")
            return None

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
        source="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        schedule_name=f"테스트 방송 ({current_day})",
        media_type="youtube"
    )
    
    # 주말인 경우 특별 메시지
    if current_day in ["토요일", "일요일"]:
        print(f"🏖️ 주말 테스트입니다: {current_day}")
    
    scheduler.start_scheduler()
    return scheduler

def test_local_audio_scheduler():
    """로컬 음원 테스트 스케줄러"""
    from datetime import datetime, timedelta
    
    # 현재 시간 + 5초, +10초로 테스트 시간 설정
    now = datetime.now()
    start_time = (now + timedelta(seconds=5)).strftime("%H:%M")
    end_time = (now + timedelta(seconds=10)).strftime("%H:%M")
    
    current_day = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][now.weekday()]
    
    print(f"로컬 음원 테스트 스케줄: {start_time} ~ {end_time}")
    print(f"오늘: {current_day}")
    
    scheduler = VideoScheduler()
    
    # 로컬 음원 테스트 스케줄 추가
    scheduler.add_daily_schedule(
        day=current_day,
        start_time=start_time,
        end_time=end_time,
        source="music/test_audio.mp3",  # 테스트용 로컬 파일
        schedule_name=f"테스트 음원 ({current_day})",
        media_type="local_audio"
    )
    
    scheduler.start_scheduler()
    return scheduler
