import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta

class ModernVideoScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 CKBS Scheduler")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f7fafc')
        self.root.state('zoomed')  # 최대화로 시작
        
        # 무채색 테마
        self.colors = {
            'primary': '#4a5568',      # 다크 그레이
            'primary_dark': '#2d3748', # 더 다크 그레이
            'secondary': '#718096',    # 미디엄 그레이
            'accent': '#a0aec0',       # 라이트 그레이
            'gradient_start': '#4a5568',
            'gradient_end': '#718096',
            'bg_primary': '#f7fafc',   # 매우 연한 그레이 배경
            'bg_secondary': '#ffffff', # 화이트 카드
            'bg_hover': '#edf2f7',     # 호버 배경
            'text_primary': '#1a202c', # 다크 텍스트
            'text_secondary': '#4a5568', # 그레이 텍스트
            'text_muted': '#a0aec0',   # 뮤티드 텍스트
            'border': '#e2e8f0',       # 라이트 보더
            'shadow': '#f0f0f0',       # 그림자
            'success': '#38a169',      # 성공 색상 (그린)
            'danger': '#e53e3e',       # 위험 색상 (레드)
            'card_shadow': '#e2e8f0'   # 카드 그림자
        }
        
        # 스케줄 데이터
        self.schedule_data = {
            'monday': [], 'tuesday': [], 'wednesday': [], 'thursday': [],
            'friday': [], 'saturday': [], 'sunday': []
        }
        
        self.setup_styles()
        self.create_header()
        self.create_main_content()
        self.load_schedule()
        
        # 프로그램 종료 시 정리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
                       font=('굴림', 10))
        
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
                       font=('굴림', 9))
        
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
                       font=('굴림', 10))
        
        # 엔트리 스타일
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'],
                       focuscolor=self.colors['primary'],
                       font=('굴림', 10))
        
    def create_header(self):
        """모던 헤더 생성"""
        header_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], height=100)
        header_frame.pack(fill='x', padx=30, pady=(30, 0))
        header_frame.pack_propagate(False)
        
        # 왼쪽: 타이틀
        left_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        left_frame.pack(side='left', fill='y')
        
        # 메인 타이틀
        title_label = tk.Label(left_frame, 
                              text="CKBS Scheduler",
                              font=('굴림', 32, 'bold'),
                              bg=self.colors['bg_primary'],
                              fg=self.colors['text_primary'])
        title_label.pack(anchor='w')
        
        # 오른쪽: 현재 시간과 상태
        right_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        right_frame.pack(side='right', fill='y', padx=(0, 20))
        
        # 현재 시간 카드
        time_card = tk.Frame(right_frame, bg=self.colors['bg_secondary'],
                            relief='flat', bd=0, width=160, height=80)
        time_card.pack(side='right', padx=10, pady=10)
        time_card.pack_propagate(False)  # 크기 고정
        
        time_frame = tk.Frame(time_card, bg=self.colors['bg_secondary'])
        time_frame.pack(padx=20, pady=15, expand=True)
        
        # 현재 시간
        self.time_label = tk.Label(time_frame,
                                  text=datetime.now().strftime("%H:%M:%S"),
                                  font=('굴림', 18, 'bold'),
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['primary'])
        self.time_label.pack()
        
        # 날짜
        date_label = tk.Label(time_frame,
                             text=datetime.now().strftime("%Y년 %m월 %d일"),
                             font=('굴림', 9),
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_secondary'])
        date_label.pack()
        
        # 시간 업데이트
        self.update_time()
        
    def update_time(self):
        """시간 업데이트"""
        current_time = datetime.now()
        self.time_label.config(text=current_time.strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)  # 1초마다 업데이트
        
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
        
        # 스케줄 카드
        schedule_card = tk.Frame(schedule_container, bg=self.colors['bg_secondary'],
                               relief='flat', bd=0)
        schedule_card.pack(fill='both', expand=True)
        
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
                             font=('굴림', 20),
                             bg=self.colors['primary'], fg='white')
        icon_label.pack(side='left')
        
        title_label = tk.Label(title_frame, text="주간 스케줄",
                              font=('굴림', 16, 'bold'),
                              bg=self.colors['primary'], fg='white')
        title_label.pack(side='left', padx=(10, 0))
        
        # 스케줄 상태
        status_label = tk.Label(header_content, text="📊 총 0개의 스케줄",
                               font=('굴림', 11),
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
        """모던 요일 탭 생성"""
        tab_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
        tab_container.pack(fill='x', pady=(0, 25))
        
        # 탭 프레임
        tab_frame = tk.Frame(tab_container, bg=self.colors['bg_hover'])
        tab_frame.pack(fill='x', ipady=5, ipadx=5)
        
        days = ['월', '화', '수', '목', '금', '토', '일']
        day_keys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        self.day_buttons = {}
        self.current_day = 'monday'
        
        for i, (day, key) in enumerate(zip(days, day_keys)):
            btn = tk.Button(tab_frame, text=day,
                           font=('굴림', 12, 'bold'),
                           bg=self.colors['primary'] if key == self.current_day else 'white',
                           fg='white' if key == self.current_day else self.colors['text_primary'],
                           bd=0, relief='flat',
                           cursor='hand2',
                           pady=15, padx=25,
                           command=lambda k=key: self.switch_day(k))
            btn.pack(side='left', padx=3)
            self.day_buttons[key] = btn
            
            # 탭 호버 효과
            def on_enter(e, button=btn, day_key=key):
                if day_key != self.current_day:
                    button.config(bg=self.colors['bg_hover'])
            
            def on_leave(e, button=btn, day_key=key):
                if day_key != self.current_day:
                    button.config(bg='white')
                    
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
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
        
        # 설정 카드
        settings_card = tk.Frame(panel_container, bg=self.colors['bg_secondary'],
                               relief='flat', bd=0)
        settings_card.pack(fill='both', expand=True)
        
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
                             font=('굴림', 20),
                             bg=self.colors['primary'], fg='white')
        icon_label.pack(side='left')
        
        title_label = tk.Label(title_frame, text="스케줄 설정",
                              font=('굴림', 16, 'bold'),
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
        
        section_title = tk.Label(section_frame, text="⏰ 시간 설정",
                                font=('굴림', 14, 'bold'),
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['text_primary'])
        section_title.pack(anchor='w')
        
        # 시작 시간
        start_group = tk.Frame(parent, bg=self.colors['bg_secondary'])
        start_group.pack(fill='x', pady=(0, 15))
        
        start_label = tk.Label(start_group, text="시작 시간",
                              font=('굴림', 11),
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_primary'])
        start_label.pack(anchor='w', pady=(0, 8))
        
        start_time_frame = tk.Frame(start_group, bg=self.colors['bg_secondary'])
        start_time_frame.pack(fill='x')
        
        self.start_hour = ttk.Combobox(start_time_frame, 
                                      values=[f"{i:02d}" for i in range(24)],
                                      width=6, state='normal', 
                                      style='Modern.TCombobox',
                                      font=('굴림', 11))
        self.start_hour.pack(side='left')
        self.start_hour.set("09")
        
        colon1 = tk.Label(start_time_frame, text=":",
                         font=('굴림', 14),
                         bg=self.colors['bg_secondary'],
                         fg=self.colors['text_primary'])
        colon1.pack(side='left', padx=8)
        
        self.start_minute = ttk.Combobox(start_time_frame,
                                        values=[f"{i:02d}" for i in range(0, 60)],
                                        width=6, state='normal',
                                        style='Modern.TCombobox',
                                        font=('굴림', 11))
        self.start_minute.pack(side='left')
        self.start_minute.set("00")
        
        # 종료 시간
        end_group = tk.Frame(parent, bg=self.colors['bg_secondary'])
        end_group.pack(fill='x', pady=(0, 20))
        
        end_label = tk.Label(end_group, text="종료 시간",
                            font=('굴림', 11),
                            bg=self.colors['bg_secondary'],
                            fg=self.colors['text_primary'])
        end_label.pack(anchor='w', pady=(0, 8))
        
        end_time_frame = tk.Frame(end_group, bg=self.colors['bg_secondary'])
        end_time_frame.pack(fill='x')
        
        self.end_hour = ttk.Combobox(end_time_frame,
                                    values=[f"{i:02d}" for i in range(24)],
                                    width=6, state='normal',
                                    style='Modern.TCombobox',
                                    font=('굴림', 11))
        self.end_hour.pack(side='left')
        self.end_hour.set("18")
        
        colon2 = tk.Label(end_time_frame, text=":",
                         font=('굴림', 14),
                         bg=self.colors['bg_secondary'],
                         fg=self.colors['text_primary'])
        colon2.pack(side='left', padx=8)
        
        self.end_minute = ttk.Combobox(end_time_frame,
                                      values=[f"{i:02d}" for i in range(0, 60)],
                                      width=6, state='normal',
                                      style='Modern.TCombobox',
                                      font=('굴림', 11))
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
                                font=('굴림', 14, 'bold'),
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['text_primary'])
        section_title.pack(anchor='w')
        
        # 미디어 타입
        type_group = tk.Frame(parent, bg=self.colors['bg_secondary'])
        type_group.pack(fill='x', pady=(0, 15))
        
        type_label = tk.Label(type_group, text="미디어 타입",
                             font=('굴림', 11),
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_primary'])
        type_label.pack(anchor='w', pady=(0, 8))
        
        self.media_type = ttk.Combobox(type_group,
                                      values=["🎬 YouTube 비디오", "🎵 로컬 오디오", "📹 로컬 비디오"],
                                      state='readonly', style='Modern.TCombobox',
                                      font=('굴림', 11))
        self.media_type.pack(fill='x')
        self.media_type.set("🎬 YouTube 비디오")
        
        # 파일/링크 경로
        path_group = tk.Frame(parent, bg=self.colors['bg_secondary'])
        path_group.pack(fill='x', pady=(0, 20))
        
        path_label = tk.Label(path_group, text="링크 또는 파일 경로",
                             font=('굴림', 11),
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_primary'])
        path_label.pack(anchor='w', pady=(0, 8))
        
        path_frame = tk.Frame(path_group, bg=self.colors['bg_secondary'])
        path_frame.pack(fill='x')
        
        self.media_path = tk.Entry(path_frame, font=('굴림', 11),
                                  relief='flat', bd=0,
                                  borderwidth=2,
                                  highlightthickness=2,
                                  highlightcolor=self.colors['primary'],
                                  bg='white', fg=self.colors['text_primary'])
        self.media_path.pack(side='left', fill='x', expand=True, ipady=10)
        
        # 라운드 버튼 스타일 개선
        browse_btn = tk.Button(path_frame, text="📁 찾기",
                              bg=self.colors['bg_hover'],
                              fg=self.colors['text_primary'],
                              bd=0, relief='flat',
                              font=('굴림', 10),
                              cursor='hand2',
                              command=self.browse_file,
                              padx=20, pady=10)
        browse_btn.pack(side='right', padx=(10, 0))
        
        # 호버 효과
        def on_enter(e):
            browse_btn.config(bg=self.colors['border'])
        def on_leave(e):
            browse_btn.config(bg=self.colors['bg_hover'])
            
        browse_btn.bind("<Enter>", on_enter)
        browse_btn.bind("<Leave>", on_leave)
        
    def create_action_buttons(self, parent):
        """액션 버튼들 생성"""
        # 구분선
        separator = tk.Frame(parent, bg=self.colors['border'], height=1)
        separator.pack(fill='x', pady=(0, 25))
        
        button_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        button_frame.pack(fill='x', pady=(0, 20))
        
        # 추가 버튼 - 라운드 스타일
        add_btn = tk.Button(button_frame, text="➕ 스케줄 추가",
                           bg=self.colors['primary'],
                           fg='white', bd=0, relief='flat',
                           font=('굴림', 12, 'bold'),
                           cursor='hand2',
                           command=self.add_schedule,
                           pady=18)
        add_btn.pack(fill='x', pady=(0, 10))
        
        # 삭제 버튼 - 라운드 스타일
        delete_btn = tk.Button(button_frame, text="🗑️ 선택 삭제",
                              bg=self.colors['danger'],
                              fg='white', bd=0, relief='flat',
                              font=('굴림', 12, 'bold'),
                              cursor='hand2',
                              command=self.delete_schedule,
                              pady=18)
        delete_btn.pack(fill='x')
        
        # 버튼 호버 효과
        def on_add_enter(e):
            add_btn.config(bg=self.colors['primary_dark'])
        def on_add_leave(e):
            add_btn.config(bg=self.colors['primary'])
            
        def on_delete_enter(e):
            delete_btn.config(bg='#dc2626')
        def on_delete_leave(e):
            delete_btn.config(bg=self.colors['danger'])
            
        add_btn.bind("<Enter>", on_add_enter)
        add_btn.bind("<Leave>", on_add_leave)
        delete_btn.bind("<Enter>", on_delete_enter)
        delete_btn.bind("<Leave>", on_delete_leave)
        
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
                                 font=('굴림', 48),
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_muted'])
            empty_icon.pack()
            
            empty_text = tk.Label(center_frame, text="아직 스케줄이 없습니다",
                                 font=('굴림', 16),
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_muted'])
            empty_text.pack(pady=(10, 0))
            
            empty_subtext = tk.Label(center_frame, text="오른쪽 패널에서 새 스케줄을 추가해보세요",
                                    font=('굴림', 12),
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
                             font=('굴림', 12, 'bold'),
                             bg='white', fg=self.colors['primary'])
        time_label.pack(side='left')
        
        # 삭제 버튼 - 라운드 스타일
        delete_btn = tk.Button(time_frame, text="❌",
                              font=('굴림', 9),
                              bg='white', fg=self.colors['danger'],
                              bd=0, relief='flat',
                              cursor='hand2',
                              padx=8, pady=4,
                              command=lambda idx=index: self.delete_schedule_item(idx))
        delete_btn.pack(side='right')
        
        # 중단: 미디어 타입
        media_frame = tk.Frame(card, bg='white')
        media_frame.pack(fill='x', pady=(0, 8))
        
        media_label = tk.Label(media_frame,
                              text=schedule['media_type'],
                              font=('굴림', 11),
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
                             font=('굴림', 10),
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
        """요일 전환"""
        # 이전 버튼 색상 변경
        self.day_buttons[self.current_day].configure(
            bg='white',
            fg=self.colors['text_primary']
        )
        
        # 현재 요일 설정
        self.current_day = day_key
        self.day_buttons[day_key].configure(
            bg=self.colors['primary'],
            fg='white'
        )
        
        # 스케줄 표시 업데이트
        self.update_modern_schedule_display()
        
    def update_schedule_display(self):
        """레거시 메서드 - 호환성을 위해 유지"""
        self.update_modern_schedule_display()
        
    def delete_schedule_item(self, index):
        """특정 인덱스의 스케줄 삭제"""
        try:
            del self.schedule_data[self.current_day][index]
            self.update_modern_schedule_display()
            self.save_schedule()
            self.show_success_message("스케줄이 삭제되었습니다")
        except IndexError:
            self.show_error_message("삭제할 스케줄을 찾을 수 없습니다")
            
    def add_schedule(self):
        """스케줄 추가"""
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
            
        schedule = {
            'start_time': start_time,
            'end_time': end_time,
            'media_type': media_type,
            'path': path
        }
        
        self.schedule_data[self.current_day].append(schedule)
        self.update_modern_schedule_display()
        self.save_schedule()
        
        # 입력 필드 초기화
        self.media_path.delete(0, tk.END)
        
        self.show_success_message("스케줄이 성공적으로 추가되었습니다")
        
    def delete_schedule(self):
        """선택된 스케줄 삭제 (레거시 방식)"""
        schedules = self.schedule_data.get(self.current_day, [])
        if not schedules:
            self.show_error_message("삭제할 스케줄이 없습니다")
            return
            
        # 마지막 스케줄 삭제
        del self.schedule_data[self.current_day][-1]
        self.update_modern_schedule_display()
        self.save_schedule()
        self.show_success_message("마지막 스케줄이 삭제되었습니다")
        
    def show_success_message(self, message):
        """성공 메시지 표시"""
        messagebox.showinfo("✅ 성공", message)
        
    def show_error_message(self, message):
        """에러 메시지 표시"""
        messagebox.showerror("❌ 오류", message)
        
    def show_warning_message(self, message):
        """경고 메시지 표시"""
        messagebox.showwarning("⚠️ 경고", message)
        
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
        except Exception as e:
            self.show_error_message(f"스케줄 저장 중 오류가 발생했습니다:\n{str(e)}")
            
    def load_schedule(self):
        """스케줄 로드"""
        try:
            if os.path.exists('schedule.json'):
                with open('schedule.json', 'r', encoding='utf-8') as f:
                    self.schedule_data = json.load(f)
                if hasattr(self, 'update_modern_schedule_display'):
                    self.update_modern_schedule_display()
        except Exception as e:
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
