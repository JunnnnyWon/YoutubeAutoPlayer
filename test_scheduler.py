#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from video_scheduler import VideoScheduler
import time

def test_scheduler_now():
    """현재 시간 기준으로 즉시 실행 테스트"""
    print("=" * 50)
    print("🧪 스케줄러 즉시 실행 테스트")
    print("=" * 50)
    
    now = datetime.now()
    current_day = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][now.weekday()]
    
    # 1분 후 시작, 2분 후 종료
    start_time = (now + timedelta(minutes=1)).strftime("%H:%M")
    end_time = (now + timedelta(minutes=2)).strftime("%H:%M")
    
    print(f"📅 테스트 일정:")
    print(f"   - 오늘: {current_day}")
    print(f"   - 현재 시간: {now.strftime('%H:%M:%S')}")
    print(f"   - 시작 예정: {start_time}")
    print(f"   - 종료 예정: {end_time}")
    print(f"   - 대기 시간: 1분")
    
    # 스케줄러 생성
    scheduler = VideoScheduler()
    
    # 오늘 즉시 실행으로 스케줄 추가 ("오늘" 사용)
    success = scheduler.add_daily_schedule(
        day="오늘",  # "일요일" 대신 "오늘" 사용
        start_time=start_time,
        end_time=end_time,
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        schedule_name=f"즉시 테스트 (오늘)"
    )
    
    if not success:
        print("❌ 스케줄 추가 실패!")
        return None
    
    print(f"\n✅ 스케줄 추가 성공!")
    
    # 스케줄러 시작
    scheduler.start_scheduler()
    
    print(f"\n⏰ 스케줄러 시작됨. {start_time}에 유튜브가 실행됩니다...")
    print("📊 180초 후 자동 종료됩니다.")
    
    return scheduler

if __name__ == "__main__":
    scheduler = test_scheduler_now()
    
    if scheduler:
        try:
            # 180초 대기 (3분)
            time.sleep(180)
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중단됨")
        finally:
            print("\n🔧 스케줄러 정리 중...")
            scheduler.stop_scheduler()
            print("✅ 테스트 완료!")
