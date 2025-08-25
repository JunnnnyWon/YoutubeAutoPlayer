import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
import threading

# 스케줄러 관련 import 추가
from video_scheduler import VideoScheduler
from media_controller import get_media_controller

# 폰트 매니저 import 추가
from font_manager import get_font_manager, cleanup_fonts

class RoundedFrame:
    """실제 라운드 코너를 가진 프레임 클래스"""
    def __init__(self, parent, bg_color='#ffffff', width=400, height=300, corner_radius=15):
        self.parent = parent
        self.bg_color = bg_color
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        
        # Canvas 생성
        self.canvas = tk.Canvas(parent, width=width, height=height, 
                               highlightthickness=0, bd=0, bg=parent.cget('bg'))
        self.canvas.pack(fill='both', expand=True)
        
        # 프레임 그리기
        self.draw_frame()
        
        # 내부 컨텐츠를 위한 프레임
        self.content_frame = tk.Frame(self.canvas, bg=bg_color)
        self.canvas.create_window(corner_radius, corner_radius, 
                                 window=self.content_frame, anchor='nw',
                                 width=width-2*corner_radius, height=height-2*corner_radius)
        
    def draw_frame(self):
        """라운드 프레임 그리기"""
        self.canvas.delete("background")
        
        # 라운드 사각형 그리기
        x1, y1 = 0, 0
        x2, y2 = self.width, self.height
        r = self.corner_radius
        
        # 메인 사각형
        self.canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=self.bg_color, outline="", tags="background")
        self.canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=self.bg_color, outline="", tags="background")
        
        # 코너 원들
        self.canvas.create_oval(x1, y1, x1 + 2*r, y1 + 2*r, fill=self.bg_color, outline="", tags="background")
        self.canvas.create_oval(x2 - 2*r, y1, x2, y1 + 2*r, fill=self.bg_color, outline="", tags="background")
        self.canvas.create_oval(x1, y2 - 2*r, x1 + 2*r, y2, fill=self.bg_color, outline="", tags="background")
        self.canvas.create_oval(x2 - 2*r, y2 - 2*r, x2, y2, fill=self.bg_color, outline="", tags="background")
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

class RoundedButton:
    """완전히 새로운 라운드 버튼 클래스 - 더 명확한 라운드 처리"""
    def __init__(self, parent, text, command=None, bg_color='#6b7280', fg_color='white', 
                 font_tuple=None, width=200, height=45, corner_radius=12, show_shadow=False):
        self.parent = parent
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font_tuple = font_tuple if font_tuple else ('Arial', 11, 'bold')
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.show_shadow = show_shadow
        self.hover_color = self._lighten_color(bg_color)
        self.is_hovered = False
        
        # Canvas 생성
        try:
            parent_bg = parent.cget('bg')
        except:
            parent_bg = '#ffffff'
            
        # 그림자가 있을 때만 추가 공간 할당
        extra_space = 6 if self.show_shadow else 2
        self.canvas = tk.Canvas(parent, width=width + extra_space, height=height + extra_space, 
                               highlightthickness=0, bd=0, bg=parent_bg)
        self.canvas.pack()
        
        # 버튼 그리기
        self.draw_button()
        
        # 이벤트 바인딩
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)
        
    def _lighten_color(self, color):
        """색상을 밝게 만들기"""
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, int(c * 1.15)) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
        
    def _darken_color(self, color):
        """색상을 어둡게 만들기"""
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.85)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        
    def draw_button(self):
        """새로운 방식의 라운드 버튼 그리기"""
        self.canvas.delete("all")
        
        # 현재 색상
        current_color = self.hover_color if self.is_hovered else self.bg_color
        
        # 그림자 (선택적)
        if self.show_shadow:
            shadow_offset = 3
            self.draw_rounded_rectangle(shadow_offset, shadow_offset, 
                                       self.width + shadow_offset, self.height + shadow_offset,
                                       self.corner_radius, '#e5e7eb')
        
        # 메인 버튼
        self.draw_rounded_rectangle(0, 0, self.width, self.height, 
                                   self.corner_radius, current_color)
        
        # 테두리
        self.draw_rounded_rectangle_outline(0, 0, self.width, self.height, 
                                           self.corner_radius, '#d1d5db', 1)
        
        # 텍스트 위치 조정
        text_offset = 3 if self.show_shadow else 1
        self.canvas.create_text(self.width // 2 + text_offset, self.height // 2 + text_offset, 
                               text=self.text, fill=self.fg_color, 
                               font=self.font_tuple, anchor="center")
    
    def draw_rounded_rectangle(self, x1, y1, x2, y2, radius, color):
        """실제 라운드 사각형 그리기"""
        # 중앙 가로 사각형
        self.canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, 
                                    fill=color, outline="")
        # 중앙 세로 사각형 
        self.canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, 
                                    fill=color, outline="")
        
        # 네 모서리 원
        self.canvas.create_oval(x1, y1, x1 + 2*radius, y1 + 2*radius, 
                               fill=color, outline="")
        self.canvas.create_oval(x2 - 2*radius, y1, x2, y1 + 2*radius, 
                               fill=color, outline="")
        self.canvas.create_oval(x1, y2 - 2*radius, x1 + 2*radius, y2, 
                               fill=color, outline="")
        self.canvas.create_oval(x2 - 2*radius, y2 - 2*radius, x2, y2, 
                               fill=color, outline="")
    
    def draw_rounded_rectangle_outline(self, x1, y1, x2, y2, radius, color, width):
        """라운드 사각형 테두리 그리기"""
        # 직선 부분들
        self.canvas.create_line(x1 + radius, y1, x2 - radius, y1, 
                               fill=color, width=width)
        self.canvas.create_line(x1 + radius, y2, x2 - radius, y2, 
                               fill=color, width=width)
        self.canvas.create_line(x1, y1 + radius, x1, y2 - radius, 
                               fill=color, width=width)
        self.canvas.create_line(x2, y1 + radius, x2, y2 - radius, 
                               fill=color, width=width)
        
        # 모서리 호들
        self.canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius, 
                              start=90, extent=90, outline=color, width=width, style="arc")
        self.canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius, 
                              start=0, extent=90, outline=color, width=width, style="arc")
        self.canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2, 
                              start=180, extent=90, outline=color, width=width, style="arc")
        self.canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2, 
                              start=270, extent=90, outline=color, width=width, style="arc")
        
    def _on_click(self, event):
        if self.command:
            self.command()
            
    def _on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
        self.canvas.config(cursor="hand2")
        
    def _on_leave(self, event):
        self.is_hovered = False
        self.draw_button()
        self.canvas.config(cursor="")
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def configure(self, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']
            self.draw_button()

class ModernVideoScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("CKBS Scheduler Program")
        self.root.geometry("1400x1000")  # 높이를 900에서 1000으로 증가
        self.root.configure(bg='#f7fafc')
        # 일반 창 모드로 시작 (전체화면 제거)
        self.root.resizable(True, True)  # 창 크기 조절 가능
        self.root.minsize(1200, 950)  # 최소 크기 설정으로 버튼 가려짐 방지
        
        # 화면 중앙에 위치시키기
        self.center_window()
        
        # 무채색 테마 - 명도 개선
        self.colors = {
            'primary': '#6b7280',      # 밝은 다크 그레이 
            'primary_dark': '#4b5563', # 다크 그레이
            'secondary': '#9ca3af',    # 밝은 미디엄 그레이
            'accent': '#d1d5db',       # 밝은 라이트 그레이
            'gradient_start': '#6b7280',
            'gradient_end': '#9ca3af',
            'bg_primary': '#f9fafb',   # 매우 연한 그레이 배경
            'bg_secondary': '#ffffff', # 화이트 카드
            'bg_hover': '#f3f4f6',     # 밝은 호버 배경
            'text_primary': '#374151', # 밝은 다크 텍스트
            'text_secondary': '#6b7280', # 밝은 그레이 텍스트
            'text_muted': '#9ca3af',   # 밝은 뮤티드 텍스트
            'border': '#e5e7eb',       # 밝은 보더
            'shadow': '#f3f4f6',       # 밝은 그림자
            'success': '#10b981',      # 성공 색상 (그린)
            'danger': '#ef4444',       # 위험 색상 (레드)
            'info': '#3b82f6',         # 정보 색상 (블루)
            'card_shadow': '#e5e7eb'   # 밝은 카드 그림자
        }
        
        # 폰트 매니저 초기화 및 잠실 폰트 설정
        self.font_manager = get_font_manager()
        self.fonts = self.font_manager.create_font_config()
        
        print("🔤 사용 중인 폰트 설정:")
        for name, config in self.fonts.items():
            print(f"  {name}: {config}")
        
        # 스케줄 데이터
        self.schedule_data = {
            'monday': [], 'tuesday': [], 'wednesday': [], 'thursday': [],
            'friday': [], 'saturday': [], 'sunday': []
        }
        
        # 스케줄러 초기화
        self.video_scheduler = VideoScheduler()
        self.scheduler_running = False
        self.media_controller = get_media_controller()
        
        # 현재 선택된 요일
        self.current_day = 'monday'
        
        # 다음 스케줄 중복 로그 방지용
        self.last_next_schedule = None
        
        self.setup_styles()
        self.create_header()
        self.create_main_content()
        self.load_schedule()
        
        # 스케줄러 상태 모니터링 시작
        self.start_status_monitoring()
        
        # 프로그램 종료 시 정리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """창을 화면 중앙에 위치시키기"""
        self.root.update_idletasks()
        
        # 화면 크기 가져오기
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 창 크기 가져오기
        window_width = 1400
        window_height = 1000  # 900에서 1000으로 증가
        
        # 중앙 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 창 위치 설정
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
    def create_rounded_button(self, parent, text, command=None, bg_color=None, fg_color='white', 
                             font_tuple=None, padx=25, pady=15, width=None):
        """라운드 처리된 버튼 생성"""
        if bg_color is None:
            bg_color = self.colors['primary']
        if font_tuple is None:
            font_tuple = self.fonts['button']
            
        # 버튼 컨테이너 (라운드 효과를 위한)
        btn_container = tk.Frame(parent, bg=parent.cget('bg'))
        
        # 실제 버튼
        btn = tk.Button(btn_container, text=text,
                       font=font_tuple,
                       bg=bg_color, fg=fg_color,
                       bd=0, relief='flat',
                       cursor='hand2',
                       padx=padx, pady=pady,
                       command=command)
        
        if width:
            btn.configure(width=width)
            
        btn.pack(fill='both', expand=True)
        
        # 라운드 효과를 위한 스타일 적용
        btn.configure(highlightthickness=0, borderwidth=0)
        
        return btn_container, btn
        
    def on_closing(self):
        """프로그램 종료 시 정리 작업"""
        self.root.destroy()
        
    def setup_styles(self):
        """모던 스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 모던 버튼 스타일
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat',
                       padding=(25, 12),
                       font=self.fonts['body'])
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('pressed', self.colors['primary_dark'])])
        
        # 세컨더리 버튼 스타일
        style.configure('Secondary.TButton',
                       background=self.colors['bg_hover'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       focuscolor='none',
                       relief='flat',
                       padding=(20, 10),
                       font=self.fonts['small'])
        
        # 모던 콤보박스 스타일
        style.configure('Modern.TCombobox',
                       fieldbackground='white',
                       background='white',
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'],
                       lightcolor=self.colors['border'],
                       darkcolor=self.colors['border'],
                       focuscolor=self.colors['primary'],
                       selectbackground=self.colors['primary'],
                       selectforeground='white',
                       font=self.fonts['body'])
        
        # 엔트리 스타일
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'],
                       focuscolor=self.colors['primary'],
                       font=self.fonts['body'])
        
    def create_header(self):
        """모던 헤더 생성"""
        header_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], height=100)
        header_frame.pack(fill='x', padx=30, pady=(30, 0))
        header_frame.pack_propagate(False)
        
        # 왼쪽: 타이틀
        left_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        left_frame.pack(side='left', fill='y')
        
        # 메인 타이틀 (카드들과 같은 높이에 맞추기 위해 패딩 추가)
        title_label = tk.Label(left_frame, 
                              text="CKBS Scheduler Program",
                              font=self.fonts['title'],
                              bg=self.colors['bg_primary'],
                              fg=self.colors['text_primary'])
        title_label.pack(anchor='w', pady=(20, 0))
        
        # 오른쪽: 현재 시간과 상태
        right_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        right_frame.pack(side='right', fill='y')
        
        # 현재 시간 카드 - 라운드 처리 (오른쪽)
        time_card_container = tk.Frame(right_frame, bg=self.colors['bg_primary'])
        time_card_container.pack(side='right', padx=(10, 5), pady=10)
        
        time_card = tk.Frame(time_card_container, bg=self.colors['bg_secondary'],
                            relief='flat', bd=0, width=160, height=110,
                            highlightthickness=1, highlightbackground=self.colors['border'])
        time_card.pack(padx=3, pady=3)
        time_card.pack_propagate(False)  # 크기 고정
        
        time_frame = tk.Frame(time_card, bg=self.colors['bg_secondary'])
        time_frame.pack(padx=20, pady=20, expand=True)
        
        # 현재 시간
        self.time_label = tk.Label(time_frame,
                                  text=datetime.now().strftime("%H:%M:%S"),
                                  font=self.fonts['time'],
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['primary'])
        self.time_label.pack()
        
        # 날짜
        self.date_label = tk.Label(time_frame,
                             text=datetime.now().strftime("%Y.%m.%d"),
                             font=self.fonts['small'],
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_secondary'])
        self.date_label.pack()
        
        # 다음 스케줄 카드 (왼쪽)
        next_schedule_card_container = tk.Frame(right_frame, bg=self.colors['bg_primary'])
        next_schedule_card_container.pack(side='right', padx=(10, 5), pady=10)
        
        next_schedule_card = tk.Frame(next_schedule_card_container, bg=self.colors['bg_secondary'],
                                    relief='flat', bd=0, width=250, height=80,
                                    highlightthickness=1, highlightbackground=self.colors['border'])
        next_schedule_card.pack(padx=3, pady=3)
        next_schedule_card.pack_propagate(False)  # 크기 고정
        
        next_schedule_frame = tk.Frame(next_schedule_card, bg=self.colors['bg_secondary'])
        next_schedule_frame.pack(padx=15, pady=10, expand=True)
        
        # 다음 스케줄 제목
        next_schedule_title = tk.Label(next_schedule_frame,
                                      text="🗓️ 다음 스케줄",
                                      font=self.fonts['small'],
                                      bg=self.colors['bg_secondary'],
                                      fg=self.colors['text_secondary'])
        next_schedule_title.pack()
        
        # 다음 스케줄 정보
        self.next_schedule_label = tk.Label(next_schedule_frame,
                                           text="스케줄 없음",
                                           font=self.fonts['schedule'],
                                           bg=self.colors['bg_secondary'],
                                           fg=self.colors['primary'])
        self.next_schedule_label.pack()
        
        # 시간 업데이트
        self.update_time()
        
    def update_time(self):
        """시간 업데이트"""
        current_time = datetime.now()
        self.time_label.config(text=current_time.strftime("%H:%M:%S"))
        self.date_label.config(text=current_time.strftime("%Y.%m.%d"))
        
        # 다음 스케줄 정보 업데이트
        self.update_next_schedule()
        
        self.root.after(1000, self.update_time)  # 1초마다 업데이트
    
    def update_next_schedule(self):
        """다음 스케줄 정보 업데이트"""
        try:
            # video_scheduler 사용 (올바른 속성명)
            if hasattr(self, 'video_scheduler') and self.video_scheduler:
                # 백엔드 스케줄러에 등록된 스케줄이 있는지 확인
                if not self.video_scheduler.schedules:
                    new_text = "등록된 스케줄 없음"
                    if self.last_next_schedule != new_text:
                        self.next_schedule_label.config(text=new_text)
                        print(f"📅 다음 스케줄 상태: {new_text}")
                        self.last_next_schedule = new_text
                    return
                
                next_schedule = self.video_scheduler.get_next_schedule()
                
                if next_schedule:
                    day_name = next_schedule.get('day_name', next_schedule.get('day', ''))
                    start_time = next_schedule.get('start_time', '')
                    
                    # 간단하게 요일과 시간만 표시
                    schedule_text = f"{day_name} {start_time}"
                    
                    # 이전과 다를 때만 업데이트 및 로그 출력
                    if self.last_next_schedule != schedule_text:
                        self.next_schedule_label.config(text=schedule_text)
                        print(f"✅ 다음 스케줄 변경: {schedule_text}")
                        self.last_next_schedule = schedule_text
                else:
                    new_text = "다음 스케줄 없음"
                    if self.last_next_schedule != new_text:
                        self.next_schedule_label.config(text=new_text)
                        print(f"📅 다음 스케줄 상태: {new_text}")
                        self.last_next_schedule = new_text
            else:
                new_text = "스케줄러 없음"
                if self.last_next_schedule != new_text:
                    self.next_schedule_label.config(text=new_text)
                    print(f"📅 다음 스케줄 상태: {new_text}")
                    self.last_next_schedule = new_text
                
        except Exception as e:
            error_text = "오류 발생"
            if self.last_next_schedule != error_text:
                print(f"❌ 다음 스케줄 업데이트 오류: {e}")
                self.next_schedule_label.config(text=error_text)
                self.last_next_schedule = error_text
        
    def create_main_content(self):
        """메인 컨텐츠 생성 - 위치 바뀜 (주간 스케줄 왼쪽, 스케줄 설정 오른쪽)"""
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # 좌측: 주간 스케줄 (기존 우측)
        self.create_modern_schedule_view(main_frame)
        
        # 우측: 스케줄 설정 (기존 좌측)
        self.create_modern_settings_panel(main_frame)
        
    def create_modern_schedule_view(self, parent):
        """모던 스케줄 뷰 생성 - 왼쪽 배치"""
        # 스케줄 뷰 컨테이너
        schedule_container = tk.Frame(parent, bg=self.colors['bg_primary'])
        schedule_container.pack(side='left', fill='both', expand=True, padx=(0, 25))
        
        # 스케줄 카드 - 라운드 처리
        schedule_card_container = tk.Frame(schedule_container, bg=self.colors['bg_primary'])
        schedule_card_container.pack(fill='both', expand=True)
        
        schedule_card = tk.Frame(schedule_card_container, bg=self.colors['bg_secondary'],
                               relief='flat', bd=0,
                               highlightthickness=1, highlightbackground=self.colors['border'])
        schedule_card.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 카드 헤더
        header = tk.Frame(schedule_card, bg=self.colors['primary'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # 헤더 내용
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(expand=True, fill='both', padx=25, pady=20)
        
        # 아이콘과 제목
        title_frame = tk.Frame(header_content, bg=self.colors['primary'])
        title_frame.pack(fill='x')
        
        icon_label = tk.Label(title_frame, text="📅",
                             font=(self.fonts['header'][0], 20),
                             bg=self.colors['primary'], fg='white')
        icon_label.pack(side='left')
        
        title_label = tk.Label(title_frame, text="주간 스케줄",
                              font=self.fonts['subtitle'],
                              bg=self.colors['primary'], fg='white')
        title_label.pack(side='left', padx=(10, 0))
        
        # 스케줄 상태
        status_label = tk.Label(header_content, text="📊 총 0개의 스케줄",
                               font=self.fonts['body'],
                               bg=self.colors['primary'], fg='white')
        status_label.pack(anchor='w', pady=(5, 0))
        
        # 스케줄 내용
        content = tk.Frame(schedule_card, bg=self.colors['bg_secondary'])
        content.pack(fill='both', expand=True, padx=25, pady=25)
        
        # 요일 탭
        self.create_modern_day_tabs(content)
        
        # 스케줄 리스트
        self.create_modern_schedule_list(content)
        
    def create_modern_day_tabs(self, parent):
        """모던 요일 탭 생성 - 라운드 버튼 사용"""
        tab_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
        tab_container.pack(fill='x', pady=(0, 25))
        
        # 탭 프레임
        tab_frame = tk.Frame(tab_container, bg=self.colors['bg_secondary'])
        tab_frame.pack()
        
        days = ['월', '화', '수', '목', '금', '토', '일']
        day_keys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        self.day_buttons = {}
        self.current_day = 'monday'
        
        # 각 요일별 라운드 버튼 프레임
        buttons_frame = tk.Frame(tab_frame, bg=self.colors['bg_secondary'])
        buttons_frame.pack()
        
        for i, (day, key) in enumerate(zip(days, day_keys)):
            # 개별 버튼 컨테이너
            btn_frame = tk.Frame(buttons_frame, bg=self.colors['bg_secondary'])
            btn_frame.pack(side='left', padx=3, pady=5)
            
            # 라운드 버튼 생성
            bg_color = self.colors['primary'] if key == self.current_day else '#ffffff'
            fg_color = 'white' if key == self.current_day else self.colors['text_primary']
            
            # 명시적 클로저로 lambda 문제 해결
            def make_command(day_key):
                return lambda: self.switch_day(day_key)
            
            rounded_btn = RoundedButton(btn_frame, day,
                                      command=make_command(key),
                                      bg_color=bg_color,
                                      fg_color=fg_color,
                                      font_tuple=self.fonts['button'],
                                      width=80, height=40, corner_radius=8, show_shadow=False)
            
            self.day_buttons[key] = rounded_btn
            
    def create_modern_schedule_list(self, parent):
        """모던 스케줄 리스트 생성 - 스크롤 없이 상단부터 스택"""
        # 리스트 컨테이너 - 스크롤 제거
        list_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
        list_container.pack(fill='both', expand=True, anchor='n')
        
        # 스케줄 아이템들을 담을 프레임
        self.scrollable_frame = tk.Frame(list_container, bg=self.colors['bg_secondary'])
        self.scrollable_frame.pack(fill='both', expand=True, anchor='n')
        
        self.update_modern_schedule_display()
        
    def create_modern_settings_panel(self, parent):
        """모던 설정 패널 생성 - 오른쪽 배치"""
        # 메인 패널 컨테이너
        panel_container = tk.Frame(parent, bg=self.colors['bg_primary'])
        panel_container.pack(side='right', fill='y')
        panel_container.configure(width=400)
        panel_container.pack_propagate(False)
        
        # 설정 카드 - 라운드 처리
        settings_card_container = tk.Frame(panel_container, bg=self.colors['bg_primary'])
        settings_card_container.pack(fill='both', expand=True)
        
        settings_card = tk.Frame(settings_card_container, bg=self.colors['bg_secondary'],
                               relief='flat', bd=0,
                               highlightthickness=1, highlightbackground=self.colors['border'])
        settings_card.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 카드 헤더
        header = tk.Frame(settings_card, bg=self.colors['primary'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # 헤더 내용
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(expand=True, fill='both', padx=25, pady=20)
        
        # 아이콘과 제목
        title_frame = tk.Frame(header_content, bg=self.colors['primary'])
        title_frame.pack(fill='x')
        
        icon_label = tk.Label(title_frame, text="⚙️",
                             font=(self.fonts['header'][0], 20),
                             bg=self.colors['primary'], fg='white')
        icon_label.pack(side='left')
        
        title_label = tk.Label(title_frame, text="스케줄 설정",
                              font=self.fonts['subtitle'],
                              bg=self.colors['primary'], fg='white')
        title_label.pack(side='left', padx=(10, 0))
        
        # 설정 컨텐츠
        content = tk.Frame(settings_card, bg=self.colors['bg_secondary'])
        content.pack(fill='both', expand=True, padx=25, pady=25)
        
        # 시간 설정 섹션
        self.create_time_section(content)
        
        # 미디어 설정 섹션
        self.create_media_section(content)
        
        # 액션 버튼들
        self.create_action_buttons(content)
        
    def create_time_section(self, parent):
        """시간 설정 섹션"""
        # 섹션 제목
        section_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        section_frame.pack(fill='x', pady=(0, 20))
        
        section_title = tk.Label(section_frame, text="🕐 시간 설정",
                                font=self.fonts['header'],
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['text_primary'])
        section_title.pack(anchor='w')
        
        # 시작 시간
        start_group = tk.Frame(parent, bg=self.colors['bg_secondary'])
        start_group.pack(fill='x', pady=(0, 15))
        
        start_label = tk.Label(start_group, text="시작 시간",
                              font=self.fonts['body'],
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_primary'])
        start_label.pack(anchor='w', pady=(0, 8))
        
        start_time_frame = tk.Frame(start_group, bg=self.colors['bg_secondary'])
        start_time_frame.pack(fill='x')
        
        self.start_hour = ttk.Combobox(start_time_frame, 
                                      values=[f"{i:02d}" for i in range(24)],
                                      width=6, state='normal', 
                                      style='Modern.TCombobox',
                                      font=self.fonts['body'])
        self.start_hour.pack(side='left')
        self.start_hour.set("09")
        
        colon1 = tk.Label(start_time_frame, text=":",
                         font=self.fonts['header'],
                         bg=self.colors['bg_secondary'],
                         fg=self.colors['text_primary'])
        colon1.pack(side='left', padx=8)
        
        self.start_minute = ttk.Combobox(start_time_frame,
                                        values=[f"{i:02d}" for i in range(0, 60)],
                                        width=6, state='normal',
                                        style='Modern.TCombobox',
                                        font=self.fonts['body'])
        self.start_minute.pack(side='left')
        self.start_minute.set("00")
        
        # 종료 시간
        end_group = tk.Frame(parent, bg=self.colors['bg_secondary'])
        end_group.pack(fill='x', pady=(0, 20))
        
        end_label = tk.Label(end_group, text="종료 시간",
                            font=self.fonts['body'],
                            bg=self.colors['bg_secondary'],
                            fg=self.colors['text_primary'])
        end_label.pack(anchor='w', pady=(0, 8))
        
        end_time_frame = tk.Frame(end_group, bg=self.colors['bg_secondary'])
        end_time_frame.pack(fill='x')
        
        self.end_hour = ttk.Combobox(end_time_frame,
                                    values=[f"{i:02d}" for i in range(24)],
                                    width=6, state='normal',
                                    style='Modern.TCombobox',
                                    font=self.fonts['body'])
        self.end_hour.pack(side='left')
        self.end_hour.set("18")
        
        colon2 = tk.Label(end_time_frame, text=":",
                         font=self.fonts['header'],
                         bg=self.colors['bg_secondary'],
                         fg=self.colors['text_primary'])
        colon2.pack(side='left', padx=8)
        
        self.end_minute = ttk.Combobox(end_time_frame,
                                      values=[f"{i:02d}" for i in range(0, 60)],
                                      width=6, state='normal',
                                      style='Modern.TCombobox',
                                      font=self.fonts['body'])
        self.end_minute.pack(side='left')
        self.end_minute.set("00")
        
    def create_media_section(self, parent):
        """미디어 설정 섹션"""
        # 구분선
        separator = tk.Frame(parent, bg=self.colors['border'], height=1)
        separator.pack(fill='x', pady=(0, 20))
        
        # 섹션 제목
        section_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        section_frame.pack(fill='x', pady=(0, 20))
        
        section_title = tk.Label(section_frame, text="🎵 미디어 설정",
                                font=self.fonts['emoji_subtitle'],
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['text_primary'])
        section_title.pack(anchor='w')
        
        # 미디어 타입
        type_group = tk.Frame(parent, bg=self.colors['bg_secondary'])
        type_group.pack(fill='x', pady=(0, 15))
        
        type_label = tk.Label(type_group, text="미디어 타입",
                             font=self.fonts['body'],
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_primary'])
        type_label.pack(anchor='w', pady=(0, 8))
        
        self.media_type = ttk.Combobox(type_group,
                                      values=["🎬 YouTube 비디오", "🎵 로컬 오디오", "📹 로컬 비디오"],
                                      state='readonly', style='Modern.TCombobox',
                                      font=self.fonts['body'])
        self.media_type.pack(fill='x')
        self.media_type.set("🎬 YouTube 비디오")
        
        # 파일/링크 경로
        path_group = tk.Frame(parent, bg=self.colors['bg_secondary'])
        path_group.pack(fill='x', pady=(0, 20))
        
        path_label = tk.Label(path_group, text="링크 또는 파일 경로",
                             font=self.fonts['body'],
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_primary'])
        path_label.pack(anchor='w', pady=(0, 8))
        
        path_frame = tk.Frame(path_group, bg=self.colors['bg_secondary'])
        path_frame.pack(fill='x')
        
        self.media_path = tk.Entry(path_frame, font=self.fonts['body'],
                                  relief='flat', bd=0,
                                  borderwidth=2,
                                  highlightthickness=2,
                                  highlightcolor=self.colors['primary'],
                                  bg='white', fg=self.colors['text_primary'])
        self.media_path.pack(side='left', fill='x', expand=True, ipady=10)
        
        # 라운드 버튼 스타일 개선
        browse_btn_container = tk.Frame(path_frame, bg=path_frame.cget('bg'))
        browse_btn_container.pack(side='right', padx=(10, 0))
        
        browse_rounded_btn = RoundedButton(browse_btn_container, "📁 찾기",
                                         command=self.browse_file,
                                         bg_color=self.colors['bg_hover'],
                                         fg_color=self.colors['text_primary'],
                                         font_tuple=self.fonts['emoji'],
                                         width=100, height=35, corner_radius=8, show_shadow=False)
        
    def create_action_buttons(self, parent):
        """액션 버튼들 생성 - 라운드 버튼 사용"""
        # 구분선
        separator = tk.Frame(parent, bg=self.colors['border'], height=1)
        separator.pack(fill='x', pady=(0, 25))
        
        button_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        button_frame.pack(fill='x', pady=(0, 20))
        
        # 추가 버튼 - 사각형 스타일
        add_btn = tk.Button(button_frame, text="➕ 스케줄 추가",
                          command=self.add_schedule,
                          bg=self.colors['primary'],
                          fg='white',
                          font=self.fonts['button'],
                          relief='flat',
                          bd=0,
                          padx=20,
                          pady=15,
                          cursor='hand2')
        add_btn.pack(fill='x', pady=(0, 15))
        
        # 스케줄러 시작/중지 버튼
        self.scheduler_btn = tk.Button(button_frame, text="▶️ 자동 스케줄러 시작",
                                     command=self.toggle_scheduler,
                                     bg=self.colors['success'],
                                     fg='white',
                                     font=self.fonts['button'],
                                     relief='flat',
                                     bd=0,
                                     padx=20,
                                     pady=15,
                                     cursor='hand2')
        self.scheduler_btn.pack(fill='x')
        
        # 스케줄러 상태 표시 레이블
        self.scheduler_status_label = tk.Label(button_frame, text="⏹️ 스케줄러 중지 상태",
                                             font=self.fonts['small'],
                                             bg=self.colors['bg_secondary'],
                                             fg=self.colors['text_muted'])
        self.scheduler_status_label.pack(pady=(10, 0))
        
        # 폰트 테스트 버튼
        font_test_btn = tk.Button(button_frame, text="🔤 폰트 테스트",
                                command=self.test_fonts,
                                bg=self.colors['info'],
                                fg='white',
                                font=self.fonts['emoji'],
                                relief='flat',
                                bd=0,
                                padx=15,
                                pady=8,
                                cursor='hand2')
        font_test_btn.pack(pady=(15, 0))
        
    def update_modern_schedule_display(self):
        """모던 스케줄 표시 업데이트 - 상단부터 스택"""
        # 기존 위젯들 삭제
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        schedules = self.schedule_data.get(self.current_day, [])
        
        if not schedules:
            # 빈 상태 표시 - 중앙 정렬
            empty_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_secondary'])
            empty_frame.pack(expand=True, fill='both')
            
            center_frame = tk.Frame(empty_frame, bg=self.colors['bg_secondary'])
            center_frame.pack(expand=True)
            
            empty_icon = tk.Label(center_frame, text="📋",
                                 font=self.fonts['emoji_large'],
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_muted'])
            empty_icon.pack()
            
            empty_text = tk.Label(center_frame, text="아직 스케줄이 없습니다",
                                 font=self.fonts['subtitle'],
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_muted'])
            empty_text.pack(pady=(10, 0))
            
            empty_subtext = tk.Label(center_frame, text="오른쪽 패널에서 새 스케줄을 추가해보세요",
                                    font=self.fonts['body'],
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_muted'])
            empty_subtext.pack(pady=(5, 0))
        else:
            # 스케줄 아이템들을 상단부터 스택으로 배치
            for i, schedule in enumerate(schedules):
                self.create_schedule_item(i, schedule)
                
    def create_schedule_item(self, index, schedule):
        """개별 스케줄 아이템 생성 - 좌우로 꽉 차게 상단부터 스택"""
        # 아이템 컨테이너 - 좌우로 꽉 채우기
        item_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_secondary'])
        item_frame.pack(fill='x', pady=(0, 10), padx=0, anchor='n')
        
        # 스케줄 카드 - 라운드 스타일
        card = tk.Frame(item_frame, bg='white', relief='flat', bd=0,
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.pack(fill='x', ipady=15, ipadx=20)
        
        # 상단: 시간 정보
        time_frame = tk.Frame(card, bg='white')
        time_frame.pack(fill='x', pady=(0, 10))
        
        # 시간 표시
        time_label = tk.Label(time_frame,
                             text=f"🕒 {schedule['start_time']} - {schedule['end_time']}",
                             font=self.fonts['emoji'],
                             bg='white', fg=self.colors['primary'])
        time_label.pack(side='left')
        
        # 삭제 버튼 - 라운드 스타일
        delete_btn_container = tk.Frame(time_frame, bg='white')
        delete_btn_container.pack(side='right')
        
        delete_btn = tk.Button(delete_btn_container, text="❌",
                              font=self.fonts['emoji'],
                              bg='white', fg=self.colors['danger'],
                              bd=0, relief='flat',
                              cursor='hand2',
                              highlightthickness=0, borderwidth=0,
                              padx=8, pady=4,
                              command=lambda idx=index: self.delete_schedule_item(idx))
        delete_btn.pack(padx=2, pady=2)
        
        # 중단: 미디어 타입
        media_frame = tk.Frame(card, bg='white')
        media_frame.pack(fill='x', pady=(0, 8))
        
        media_label = tk.Label(media_frame,
                              text=schedule['media_type'],
                              font=self.fonts['body'],
                              bg='white', fg=self.colors['text_secondary'])
        media_label.pack(anchor='w')
        
        # 하단: 경로
        path_frame = tk.Frame(card, bg='white')
        path_frame.pack(fill='x')
        
        # 경로 텍스트 (길면 생략)
        path_text = schedule['path']
        if len(path_text) > 80:
            path_text = path_text[:77] + "..."
            
        path_label = tk.Label(path_frame,
                             text=f"🔗 {path_text}",
                             font=self.fonts['emoji'],
                             bg='white', fg=self.colors['text_secondary'],
                             wraplength=700, justify='left')
        path_label.pack(anchor='w')
        
        # 카드 호버 효과
        def on_enter(e):
            card.config(highlightbackground=self.colors['primary'], bg='#fafafa')
            for child in self.get_all_children(card):
                if hasattr(child, 'config') and child.winfo_class() in ['Label', 'Frame']:
                    if child.cget('bg') == 'white':
                        child.config(bg='#fafafa')
                        
        def on_leave(e):
            card.config(highlightbackground=self.colors['border'], bg='white')
            for child in self.get_all_children(card):
                if hasattr(child, 'config') and child.winfo_class() in ['Label', 'Frame']:
                    if child.cget('bg') == '#fafafa':
                        child.config(bg='white')
            
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # 자식 위젯들에도 바인딩
        for child in self.get_all_children(card):
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
            
    def get_all_children(self, widget):
        """위젯의 모든 자식 위젯들을 재귀적으로 가져오기"""
        children = []
        for child in widget.winfo_children():
            children.append(child)
            children.extend(self.get_all_children(child))
        return children
        
    def switch_day(self, day_key):
        """요일 전환 - 라운드 버튼용"""
        if day_key == self.current_day:
            return  # 이미 선택된 요일이면 무시
            
        # 이전 버튼 비활성화 스타일로 변경
        if self.current_day in self.day_buttons:
            old_btn = self.day_buttons[self.current_day]
            old_btn.bg_color = '#ffffff'
            old_btn.fg_color = self.colors['text_primary']
            old_btn.hover_color = self._get_button_hover_color('#ffffff')
            old_btn.draw_button()
        
        # 현재 요일 설정
        self.current_day = day_key
        
        # 새 버튼 활성화 스타일로 변경
        if day_key in self.day_buttons:
            current_btn = self.day_buttons[day_key]
            current_btn.bg_color = self.colors['primary']
            current_btn.fg_color = 'white'
            current_btn.hover_color = self._get_button_hover_color(self.colors['primary'])
            current_btn.draw_button()
        
        # 스케줄 표시 업데이트
        self.update_modern_schedule_display()
        
    def _get_button_hover_color(self, base_color):
        """버튼 호버 색상 계산"""
        if base_color == '#ffffff':
            return '#f3f4f6'  # 흰색 버튼의 호버
        else:
            # 다른 색상은 밝게
            if base_color.startswith('#'):
                color = base_color[1:]
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            lightened = tuple(min(255, int(c * 1.15)) for c in rgb)
            return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
        
    def update_schedule_display(self):
        """레거시 메서드 - 호환성을 위해 유지"""
        self.update_modern_schedule_display()
        
    def delete_schedule_item(self, index):
        """특정 인덱스의 스케줄 삭제"""
        try:
            # 스케줄러 실행 중에는 삭제 금지
            if self.scheduler_running:
                self.show_warning_message(
                    "⚠️ 스케줄러 실행 중입니다!\n\n"
                    "스케줄 실행 중에는 스케줄을 삭제할 수 없습니다.\n"
                    "실행 중인 스케줄을 갑자기 삭제하면 예기치 않은\n"
                    "오류가 발생할 수 있습니다.\n\n"
                    "📌 먼저 '자동 스케줄러 중지' 버튼을 클릭한 후\n"
                    "   스케줄을 삭제해주세요."
                )
                return
            
            del self.schedule_data[self.current_day][index]
            self.update_modern_schedule_display()
            self.save_schedule()  # 이미 여기서 백엔드 동기화 및 다음 스케줄 업데이트가 이루어짐
            self.show_success_message("스케줄이 삭제되었습니다")
            
        except IndexError:
            self.show_error_message("삭제할 스케줄을 찾을 수 없습니다")
    
    def check_time_overlap(self, day, start_time, end_time):
        """시간 겹침 체크"""
        try:
            # 새로운 스케줄의 시간을 분으로 변환
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))
            new_start = start_hour * 60 + start_min
            new_end = end_hour * 60 + end_min
            
            # 해당 요일의 기존 스케줄들과 비교
            for schedule in self.schedule_data.get(day, []):
                existing_start_hour, existing_start_min = map(int, schedule['start_time'].split(':'))
                existing_end_hour, existing_end_min = map(int, schedule['end_time'].split(':'))
                existing_start = existing_start_hour * 60 + existing_start_min
                existing_end = existing_end_hour * 60 + existing_end_min
                
                # 겹침 체크 (시작시간이 기존 종료시간 전이고, 종료시간이 기존 시작시간 후인 경우)
                if not (new_end <= existing_start or new_start >= existing_end):
                    return True, f"{schedule['start_time']} ~ {schedule['end_time']}"
            
            return False, None
            
        except Exception as e:
            print(f"❌ 시간 겹침 체크 오류: {e}")
            return False, None
            
    def add_schedule(self):
        """스케줄 추가"""
        # 스케줄러 실행 중에는 추가 금지
        if self.scheduler_running:
            self.show_warning_message(
                "⚠️ 스케줄러 실행 중입니다!\n\n"
                "스케줄 실행 중에는 새로운 스케줄을 추가할 수 없습니다.\n"
                "변경사항이 실행 중인 스케줄에 올바르게 반영되지 않을 수 있습니다.\n\n"
                "📌 먼저 '자동 스케줄러 중지' 버튼을 클릭한 후\n"
                "   스케줄을 추가해주세요."
            )
            return
            
        start_time = f"{self.start_hour.get()}:{self.start_minute.get()}"
        end_time = f"{self.end_hour.get()}:{self.end_minute.get()}"
        media_type = self.media_type.get()
        path = self.media_path.get().strip()
        
        # 유효성 검사
        if not path:
            self.show_error_message("링크 또는 파일 경로를 입력해주세요")
            return
            
        # 시간 유효성 검사
        try:
            # 시간 형식 검증 (수동 입력 지원)
            start_hour_val = int(self.start_hour.get())
            start_min_val = int(self.start_minute.get())
            end_hour_val = int(self.end_hour.get())
            end_min_val = int(self.end_minute.get())
            
            # 범위 검증
            if not (0 <= start_hour_val <= 23) or not (0 <= start_min_val <= 59):
                self.show_error_message("시작 시간이 올바르지 않습니다 (시간: 0-23, 분: 0-59)")
                return
                
            if not (0 <= end_hour_val <= 23) or not (0 <= end_min_val <= 59):
                self.show_error_message("종료 시간이 올바르지 않습니다 (시간: 0-23, 분: 0-59)")
                return
            
            start_minutes = start_hour_val * 60 + start_min_val
            end_minutes = end_hour_val * 60 + end_min_val
            
            if start_minutes >= end_minutes:
                self.show_error_message("종료 시간은 시작 시간보다 늦어야 합니다")
                return
                
            # 시간 형식 정규화
            start_time = f"{start_hour_val:02d}:{start_min_val:02d}"
            end_time = f"{end_hour_val:02d}:{end_min_val:02d}"
            
        except ValueError:
            self.show_error_message("시간은 숫자로만 입력해주세요")
            return
        
        # 시간 겹침 체크
        is_overlap, overlap_time = self.check_time_overlap(self.current_day, start_time, end_time)
        if is_overlap:
            self.show_warning_message(
                f"⚠️ 스케줄 시간이 겹칩니다!\n\n"
                f"📅 기존 스케줄: {overlap_time}\n"
                f"🆕 새 스케줄: {start_time} ~ {end_time}\n\n"
                f"❌ 같은 시간대에 두 개의 스케줄을 실행할 수 없습니다.\n\n"
                f"💡 해결 방법:\n"
                f"   • 기존 스케줄을 먼저 삭제하거나\n"
                f"   • 겹치지 않는 다른 시간으로 설정해주세요"
            )
            return
            
        schedule = {
            'start_time': start_time,
            'end_time': end_time,
            'media_type': media_type,
            'path': path
        }
        
        # GUI 데이터에 추가
        self.schedule_data[self.current_day].append(schedule)
        
        # UI 및 저장 (백엔드 동기화 포함)
        self.update_modern_schedule_display()
        self.save_schedule()  # 이미 여기서 백엔드 동기화 및 다음 스케줄 업데이트가 이루어짐
        
        # 입력 필드 초기화
        self.media_path.delete(0, tk.END)
        
        self.show_success_message("스케줄이 성공적으로 추가되었습니다")
        
    def show_success_message(self, message):
        """성공 메시지 표시"""
        messagebox.showinfo("✅ 성공", message)
        
    def show_error_message(self, message):
        """에러 메시지 표시"""
        messagebox.showerror("❌ 오류", message)
        
    def show_warning_message(self, message):
        """경고 메시지 표시"""
        messagebox.showwarning("⚠️ 경고", message)
        
    def add_to_backend_scheduler(self, schedule):
        """백엔드 스케줄러에 스케줄 추가"""
        try:
            # 요일 매핑
            day_mapping = {
                'monday': '월요일', 'tuesday': '화요일', 'wednesday': '수요일', 
                'thursday': '목요일', 'friday': '금요일', 'saturday': '토요일', 'sunday': '일요일'
            }
            
            day_kr = day_mapping.get(self.current_day, '월요일')
            
            # 미디어 타입 매핑
            media_type_mapping = {
                '🎥 YouTube 비디오': 'youtube',
                '🎧 로컬 오디오': 'local_audio',
                '📺 로컬 비디오': 'local_video',
                'YouTube 비디오': 'youtube',  # 레거시 호환성
                'Local Audio': 'local_audio'  # 레거시 호환성
            }
            
            backend_media_type = media_type_mapping.get(schedule['media_type'], 'youtube')
            
            # 백엔드 스케줄러에 추가
            success = self.video_scheduler.add_daily_schedule(
                day=day_kr,
                start_time=schedule['start_time'],
                end_time=schedule['end_time'],
                source=schedule['path'],
                schedule_name=f"{day_kr} 스케줄",
                media_type=backend_media_type
            )
            
            if success:
                print(f"✅ 백엔드 스케줄러에 스케줄 추가 성공: {day_kr} {schedule['start_time']} ~ {schedule['end_time']}")
                # 스케줄러가 실행 중이면 재시작
                if self.scheduler_running:
                    self.restart_scheduler()
                # 다음 스케줄 정보 즉시 업데이트
                self.update_next_schedule()
            else:
                print(f"❌ 백엔드 스케줄러에 스케줄 추가 실패")
                
        except Exception as e:
            print(f"❌ 백엔드 스케줄러 연동 오류: {e}")
    
    def restart_scheduler(self):
        """스케줄러 재시작"""
        try:
            print("🔄 스케줄러 재시작 중...")
            self.video_scheduler.stop_scheduler()
            self.sync_all_schedules_to_backend()
            self.video_scheduler.start_scheduler()
            print("✅ 스케줄러 재시작 완료")
            # 다음 스케줄 정보 업데이트
            self.update_next_schedule()
        except Exception as e:
            print(f"❌ 스케줄러 재시작 실패: {e}")
    
    def sync_all_schedules_to_backend(self):
        """모든 GUI 스케줄을 백엔드 스케줄러와 동기화"""
        try:
            # 백엔드 스케줄러 초기화 (기존 스케줄 모두 삭제)
            print("🔄 백엔드 스케줄러 초기화 중...")
            self.video_scheduler.schedules.clear()
            
            # 요일 매핑
            day_mapping = {
                'monday': '월요일', 'tuesday': '화요일', 'wednesday': '수요일', 
                'thursday': '목요일', 'friday': '금요일', 'saturday': '토요일', 'sunday': '일요일'
            }
            
            # 미디어 타입 매핑
            media_type_mapping = {
                '🎥 YouTube 비디오': 'youtube',
                '🎧 로컬 오디오': 'local_audio',
                '📺 로컬 비디오': 'local_video',
                'YouTube 비디오': 'youtube',  # 레거시 호환성
                'Local Audio': 'local_audio'  # 레거시 호환성
            }
            
            total_schedules = 0
            
            for day_key, schedules in self.schedule_data.items():
                day_kr = day_mapping.get(day_key, '월요일')
                
                for schedule in schedules:
                    backend_media_type = media_type_mapping.get(schedule['media_type'], 'youtube')
                    
                    success = self.video_scheduler.add_daily_schedule(
                        day=day_kr,
                        start_time=schedule['start_time'],
                        end_time=schedule['end_time'],
                        source=schedule['path'],
                        schedule_name=f"{day_kr} {schedule['start_time']} 스케줄",  # 더 명확한 이름
                        media_type=backend_media_type
                    )
                    
                    if success:
                        total_schedules += 1
            
            print(f"✅ 총 {total_schedules}개 스케줄이 백엔드와 동기화되었습니다")
            return total_schedules > 0
            
        except Exception as e:
            print(f"❌ 스케줄 동기화 실패: {e}")
            return False
    
    def toggle_scheduler(self):
        """스케줄러 시작/중지 토글"""
        try:
            if not self.scheduler_running:
                # 스케줄러 시작
                if self.sync_all_schedules_to_backend():
                    self.video_scheduler.start_scheduler()
                    self.scheduler_running = True
                    
                    # UI 업데이트
                    self.scheduler_btn.config(text="⏹️ 자동 스케줄러 중지", bg=self.colors['danger'])
                    self.scheduler_status_label.config(text="🔴 스케줄러 실행 중", fg=self.colors['success'])
                    
                    print("✅ 자동 스케줄러가 시작되었습니다")
                    self.show_success_message("자동 스케줄러가 시작되었습니다!")
                    
                    # 다음 스케줄 정보 업데이트
                    self.update_next_schedule()
                else:
                    self.show_error_message("실행할 스케줄이 없습니다")
            else:
                # 스케줄러 중지
                self.video_scheduler.stop_scheduler()
                self.scheduler_running = False
                
                # UI 업데이트
                self.scheduler_btn.config(text="▶️ 자동 스케줄러 시작", bg=self.colors['success'])
                self.scheduler_status_label.config(text="⏹️ 스케줄러 중지 상태", fg=self.colors['text_muted'])
                
                print("⏹️ 자동 스케줄러가 중지되었습니다")
                self.show_success_message("자동 스케줄러가 중지되었습니다")
                
                # 다음 스케줄 정보 숨김
                self.next_schedule_label.config(text="스케줄러 중지")
                
        except Exception as e:
            print(f"❌ 스케줄러 토글 실패: {e}")
            self.show_error_message(f"스케줄러 조작 실패: {str(e)}")
    
    def start_status_monitoring(self):
        """스케줄러 상태 모니터링 시작"""
        def monitor():
            while True:
                try:
                    # 미디어 컨트롤러 상태 확인
                    status = self.media_controller.get_current_status()
                    
                    # 상태 업데이트 (필요시 GUI 업데이트)
                    
                    # 1분마다 체크
                    threading.Event().wait(60)
                    
                except Exception as e:
                    print(f"상태 모니터링 오류: {e}")
                    threading.Event().wait(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def on_closing(self):
        """프로그램 종료 시 정리"""
        try:
            print("🧹 프로그램 종료 중...")
            
            # 스케줄러 정지
            if hasattr(self, 'video_scheduler'):
                self.video_scheduler.stop_scheduler()
            
            # 미디어 컨트롤러 정리
            if hasattr(self, 'media_controller'):
                self.media_controller.force_stop_all()
            
            # 폰트 정리
            cleanup_fonts()
            
            print("✅ 정리 완료")
            
        except Exception as e:
            print(f"정리 중 오류: {e}")
        
        finally:
            self.root.destroy()
        
    def test_fonts(self):
        """폰트 테스트 창 열기"""
        try:
            self.font_manager.test_fonts(self.root)
        except Exception as e:
            print(f"❌ 폰트 테스트 오류: {e}")
            self.show_error_message(f"폰트 테스트 중 오류가 발생했습니다: {str(e)}")
        
    def browse_file(self):
        """파일 찾기"""
        media_type = self.media_type.get()
        
        # 미디어 타입에 따른 파일 필터 설정
        if "YouTube" in media_type:
            # YouTube인 경우 파일 대화상자 대신 URL 입력 안내
            self.show_warning_message("YouTube 비디오의 경우 URL을 직접 입력해주세요")
            self.media_path.focus()
            return
        elif "오디오" in media_type:
            filetypes = [
                ("오디오 파일", "*.mp3 *.wav *.flac *.m4a *.aac *.ogg"),
                ("모든 파일", "*.*")
            ]
            title = "오디오 파일 선택"
        else:  # 비디오
            filetypes = [
                ("비디오 파일", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"),
                ("모든 파일", "*.*")
            ]
            title = "비디오 파일 선택"
            
        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )
        
        if filename:
            self.media_path.delete(0, tk.END)
            self.media_path.insert(0, filename)
            
    def save_schedule(self):
        """스케줄 저장"""
        try:
            with open('schedule.json', 'w', encoding='utf-8') as f:
                json.dump(self.schedule_data, f, ensure_ascii=False, indent=2)
            print(f"💾 스케줄 저장 완료: {sum(len(day_schedules) for day_schedules in self.schedule_data.values())}개 스케줄")
            
            # 저장 후 백엔드와 즉시 동기화
            if hasattr(self, 'video_scheduler'):
                self.sync_all_schedules_to_backend()
                # 다음 스케줄 업데이트
                if hasattr(self, 'update_next_schedule'):
                    self.update_next_schedule()
                    
        except Exception as e:
            print(f"❌ 스케줄 저장 오류: {e}")
            self.show_error_message(f"스케줄 저장 중 오류가 발생했습니다:\n{str(e)}")
            
    def load_schedule(self):
        """스케줄 로드"""
        try:
            if os.path.exists('schedule.json'):
                with open('schedule.json', 'r', encoding='utf-8') as f:
                    self.schedule_data = json.load(f)
                print(f"📂 스케줄 로드 완료: {sum(len(day_schedules) for day_schedules in self.schedule_data.values())}개 스케줄")
                
                # UI 업데이트
                if hasattr(self, 'update_modern_schedule_display'):
                    self.update_modern_schedule_display()
                
                # 백엔드 스케줄러와 동기화
                if hasattr(self, 'video_scheduler'):
                    self.sync_all_schedules_to_backend()
                    # 다음 스케줄 업데이트
                    if hasattr(self, 'update_next_schedule'):
                        self.update_next_schedule()
            else:
                print("📂 schedule.json 파일이 없어서 빈 스케줄로 시작합니다")
        except Exception as e:
            print(f"❌ 스케줄 로드 오류: {e}")
            self.show_error_message(f"스케줄 로드 중 오류가 발생했습니다:\n{str(e)}")

def main():
    try:
        root = tk.Tk()
        
        # 고해상도 디스플레이 지원
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
            
        app = ModernVideoScheduler(root)
        
        # 창 아이콘 설정 (선택사항)
        try:
            root.iconbitmap(default='icon.ico')
        except:
            pass
            
        root.mainloop()
        
    except Exception as e:
        print(f"애플리케이션 시작 중 오류: {e}")
        messagebox.showerror("오류", f"애플리케이션을 시작할 수 없습니다:\n{str(e)}")

if __name__ == "__main__":
    main()
