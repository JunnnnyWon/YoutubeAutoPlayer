"""
폰트 관리 모듈
잠실 폰트 로딩 및 관리를 담당
"""

import os
import tkinter as tk
from tkinter import font
import platform

class FontManager:
    def __init__(self):
        """폰트 매니저 초기화"""
        self.font_folder = "Pretendard-1.3.9/public/static"
        self.font_files = {
            'thin': 'Pretendard-Thin.otf',
            'extralight': 'Pretendard-ExtraLight.otf',
            'light': 'Pretendard-Light.otf',
            'regular': 'Pretendard-Regular.otf',
            'medium': 'Pretendard-Medium.otf',
            'semibold': 'Pretendard-SemiBold.otf',
            'bold': 'Pretendard-Bold.otf',
            'extrabold': 'Pretendard-ExtraBold.otf',
            'black': 'Pretendard-Black.otf'
        }
        
        self.font_family_name = "Pretendard"
        self.loaded_fonts = {}
        self.system_fonts = {}
        
        # 폰트 로딩 시도
        self.load_fonts()
        
        # 시스템 기본 폰트 설정
        self.setup_fallback_fonts()
    
    def get_font_path(self, font_filename):
        """폰트 파일의 전체 경로 반환"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, self.font_folder, font_filename)
        return font_path if os.path.exists(font_path) else None
    
    def load_fonts(self):
        """프리텐다드 폰트 파일들을 시스템에 로딩"""
        print("🔤 프리텐다드 폰트 로딩 중...")
        
        try:
            # Windows에서 폰트 등록
            if platform.system() == "Windows":
                import winreg
                from ctypes import windll
                
                for weight, filename in self.font_files.items():
                    font_path = self.get_font_path(filename)
                    if font_path:
                        try:
                            # 폰트 파일을 시스템에 임시 등록
                            result = windll.gdi32.AddFontResourceW(font_path)
                            if result:
                                self.loaded_fonts[weight] = font_path
                                print(f"✅ {weight} 폰트 로딩 성공: {filename}")
                            else:
                                print(f"❌ {weight} 폰트 로딩 실패: {filename}")
                        except Exception as e:
                            print(f"❌ {weight} 폰트 로딩 오류: {e}")
                    else:
                        print(f"❌ {weight} 폰트 파일을 찾을 수 없음: {filename}")
            
            # 폰트 새로고침 알림
            if self.loaded_fonts:
                try:
                    from ctypes import windll
                    windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)  # WM_FONTCHANGE
                    print(f"✅ 총 {len(self.loaded_fonts)}개 프리텐다드 폰트 로딩 완료")
                except:
                    pass
            else:
                print("⚠️ 프리텐다드 폰트를 로딩할 수 없습니다. 기본 폰트를 사용합니다.")
                
        except Exception as e:
            print(f"❌ 폰트 로딩 중 오류 발생: {e}")
    
    def setup_fallback_fonts(self):
        """기본 폰트 설정 (잠실 폰트 로딩 실패 시 사용)"""
        system = platform.system()
        
        if system == "Windows":
            self.system_fonts = {
                'primary': '맑은 고딕',
                'secondary': 'Segoe UI',
                'fallback': 'Arial'
            }
        elif system == "Darwin":  # macOS
            self.system_fonts = {
                'primary': 'SF Pro Display',
                'secondary': 'Helvetica Neue',
                'fallback': 'Arial'
            }
        else:  # Linux
            self.system_fonts = {
                'primary': 'DejaVu Sans',
                'secondary': 'Liberation Sans',
                'fallback': 'Arial'
            }
    
    def get_font_family(self, weight='regular'):
        """폰트 패밀리명 반환 (프리텐다드 폰트 우선, 없으면 시스템 폰트)"""
        if self.loaded_fonts:
            return self.font_family_name
        else:
            return self.system_fonts.get('primary', 'Arial')
    
    def create_font_config(self):
        """UI에서 사용할 폰트 설정 딕셔너리 생성"""
        base_family = self.get_font_family()
        # 이모지 지원이 좋은 폰트 (Windows의 경우 Segoe UI Emoji)
        emoji_family = 'Segoe UI Emoji' if platform.system() == "Windows" else 'Apple Color Emoji'
        
        return {
            'title': (base_family, 28, 'bold'),          # 메인 타이틀
            'subtitle': (base_family, 16, 'bold'),       # 서브 타이틀  
            'header': (base_family, 14, 'bold'),         # 헤더
            'body': (base_family, 11),                   # 본문
            'small': (base_family, 10),                  # 작은 텍스트
            'button': (base_family, 11, 'bold'),         # 버튼
            'time': (base_family, 18, 'bold'),           # 시간 표시
            'schedule': (base_family, 13, 'bold'),       # 스케줄 정보
            'emoji': (emoji_family, 11),                 # 이모지용 폰트
            'emoji_large': (emoji_family, 48),           # 큰 이모지용 폰트
            'emoji_subtitle': (emoji_family, 16, 'bold') # 제목용 이모지 폰트
        }
    
    def get_available_weights(self):
        """사용 가능한 폰트 굵기 목록 반환"""
        if self.loaded_fonts:
            return list(self.loaded_fonts.keys())
        else:
            return ['normal', 'bold']
    
    def test_fonts(self, root):
        """폰트 테스트 함수 (개발용)"""
        print("\n🔤 폰트 테스트 시작...")
        
        # 테스트 창 생성
        test_window = tk.Toplevel(root)
        test_window.title("프리텐다드 폰트 테스트")
        test_window.geometry("600x400")
        
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(test_window)
        scrollbar = tk.Scrollbar(test_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 폰트 설정 가져오기
        font_config = self.create_font_config()
        
        # 각 폰트 스타일 테스트
        row = 0
        for font_name, font_tuple in font_config.items():
            # 라벨
            label = tk.Label(scrollable_frame, 
                           text=f"{font_name.upper()}: 안녕하세요! Hello World! 123",
                           font=font_tuple,
                           pady=5)
            label.grid(row=row, column=0, sticky="w", padx=10, pady=2)
            
            # 폰트 정보
            info_label = tk.Label(scrollable_frame,
                                text=f"({font_tuple})",
                                font=('Courier', 9),
                                fg='gray')
            info_label.grid(row=row, column=1, sticky="w", padx=10, pady=2)
            
            row += 1
        
        # 로딩된 폰트 정보 표시
        info_text = f"로딩된 프리텐다드 폰트: {len(self.loaded_fonts)}개\n"
        info_text += f"사용 중인 기본 폰트: {self.get_font_family()}"
        
        info_label = tk.Label(scrollable_frame,
                            text=info_text,
                            font=('Courier', 10),
                            fg='blue',
                            justify='left')
        info_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        
        # 위젯 배치
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        print("✅ 폰트 테스트 창이 열렸습니다.")
    
    def cleanup(self):
        """폰트 정리 (프로그램 종료 시 호출)"""
        try:
            if platform.system() == "Windows" and self.loaded_fonts:
                from ctypes import windll
                for font_path in self.loaded_fonts.values():
                    windll.gdi32.RemoveFontResourceW(font_path)
                print("🔤 임시 폰트 해제 완료")
        except Exception as e:
            print(f"❌ 폰트 정리 중 오류: {e}")

# 전역 폰트 매니저 인스턴스
font_manager = None

def get_font_manager():
    """전역 폰트 매니저 인스턴스 반환"""
    global font_manager
    if font_manager is None:
        font_manager = FontManager()
    return font_manager

def cleanup_fonts():
    """폰트 정리 함수 (프로그램 종료 시 호출)"""
    global font_manager
    if font_manager:
        font_manager.cleanup()
        font_manager = None

if __name__ == "__main__":
    # 테스트 실행
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨기기
    
    fm = FontManager()
    fm.test_fonts(root)
    
    root.mainloop()
