from datetime import datetime
import sys

def check_dependencies():
    """
    필요한 모듈들이 제대로 설치되어 있는지 확인
    """
    try:
        import schedule
    except ImportError:
        print("❌ 오류: 'schedule' 모듈이 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요: pip install schedule")
        return False
    
    try:
        import selenium
    except ImportError:
        print("❌ 오류: 'selenium' 모듈이 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요: pip install selenium")
        return False
    
    try:
        from video_scheduler import VideoScheduler, test_scheduler
    except ImportError as e:
        print(f"❌ 오류: video_scheduler 모듈을 불러올 수 없습니다: {e}")
        print("video_scheduler.py 파일이 같은 폴더에 있는지 확인하세요.")
        return False
    except AttributeError as e:
        print(f"❌ 오류: video_scheduler 모듈에서 필요한 함수를 찾을 수 없습니다: {e}")
        print("video_scheduler.py 파일이 올바르게 작성되어 있는지 확인하세요.")
        return False
    
    return True

def main():
    """
    메인 실행 함수
    """
    print("=== YouTube 동영상 스케줄러 ===")
    print("설정된 시간에 동영상을 자동으로 재생하고 종료합니다.\n")
    
    # ===== 여기서 시간 설정하세요! =====
    # 여러 개의 시간 쌍을 설정할 수 있습니다
    schedule_times = [
        {
            "start": "12:30",
            "end": "13:00", 
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "name": "점심시간"
        },  # 점심시간 방송
        {
            "start": "18:00",
            "end": "18:30", 
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "name": "저녁시간"
        },  # 저녁시간 방송
    # 추가 시간대를 원하면 아래와 같이 더 추가하세요:
    #   {
    #       "start": "09:00", 
    #       "end": "09:05", 
    #       "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    #       "name": "아침방송"
    #   },
    ]
    
    # ===== 설정 끝 =====
    
    # 의존성 확인
    if not check_dependencies():
        print("\n프로그램을 종료합니다.")
        sys.exit(1)
    
    # 의존성 확인 후 import
    try:
        from video_scheduler import VideoScheduler, test_scheduler
    except Exception as e:
        print(f"모듈 import 중 오류 발생: {e}")
        sys.exit(1)
    
    print("실행 모드를 선택하세요:")
    print("1. 자동 스케줄러 시작")
    print("2. 테스트 모드 (현재 시간 +5초 시작, +10초 종료)")
    
    try:
        mode = input("모드 선택 (1 또는 2): ").strip()
        
        if mode == "2":
            print("\n=== 테스트 모드 시작 ===")
            scheduler = test_scheduler()
            print("\n테스트가 실행 중입니다...")
            print("브라우저가 자동으로 열리고 10초 후 닫힙니다.")
            input("\n아무 키나 누르면 프로그램을 종료합니다...")
            scheduler.stop_scheduler()
            
        elif mode == "1":
            print("\n=== 자동 스케줄러 시작 ===")
            
            print("설정된 스케줄:")
            for i, schedule_time in enumerate(schedule_times, 1):
                print(f"  {i}. {schedule_time['name']}: {schedule_time['start']} ~ {schedule_time['end']}")
            print(f"- 동영상 URL: {schedule_time['url']}")
            print(f"- 현재 시간: {datetime.now().strftime('%H:%M:%S')}")
            
            confirm = input("\n스케줄을 시작하시겠습니까? (y/n): ").lower()
            if confirm in ['y', 'yes']:
                scheduler = VideoScheduler()
                
                # 여러 개의 스케줄 등록
                for schedule_time in schedule_times:
                    scheduler.add_schedule(
                        start_time=schedule_time['start'],
                        end_time=schedule_time['end'],
                        video_url=schedule_time['url'],
                        schedule_name=schedule_time['name']
                    )
                
                scheduler.start_scheduler()
                
                print("\n스케줄러가 활성화되었습니다!")
                print("설정된 시간에 자동으로 실행됩니다.")
                print("비상 정지를 원하면 Ctrl+C를 누르세요.")
                
                try:
                    input("\n엔터를 누르면 스케줄러를 중지합니다...")
                except KeyboardInterrupt:
                    print("\n\n비상 정지!")
                    scheduler.emergency_stop()
                finally:
                    scheduler.stop_scheduler()
            else:
                print("프로그램을 종료합니다.")
        else:
            print("잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
        print("\n문제 해결 방법:")
        print("1. video_scheduler.py 파일이 같은 폴더에 있는지 확인")
        print("2. 필요한 모듈들이 설치되어 있는지 확인:")
        print("   pip install schedule selenium")
        print("3. Python 버전이 3.6 이상인지 확인")

if __name__ == "__main__":
    main()