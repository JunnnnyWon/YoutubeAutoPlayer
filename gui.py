import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import configparser
import threading
import logging

class ModernButton(QPushButton):
    def __init__(self, text="", icon_name="", primary=False):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #45a049, stop:1 #4CAF50);
                }
                QPushButton:pressed {
                    background: #3e8e41;
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f9fa, stop:1 #e9ecef);
                    color: #495057;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    font-size: 13px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e9ecef, stop:1 #dee2e6);
                    border-color: #adb5bd;
                }
                QPushButton:pressed {
                    background: #dee2e6;
                }
            """)

class StatusIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.status = "idle"  # idle, running, error
        self.setFixedSize(20, 20)
        
    def set_status(self, status: str):
        self.status = status
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = {
            "idle": "#6c757d",
            "running": "#28a745", 
            "error": "#dc3545",
            "warning": "#ffc107"
        }
        
        painter.setBrush(QBrush(QColor(colors.get(self.status, "#6c757d"))))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 16, 16)

class TimePickerWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.hour_combo = QComboBox()
        self.hour_combo.addItems([f"{i:02d}" for i in range(24)])
        self.hour_combo.setCurrentText("09")
        
        # 분 단위를 1분으로 변경 (0~59분)
        self.minute_combo = QComboBox()
        self.minute_combo.addItems([f"{i:02d}" for i in range(60)])
        self.minute_combo.setCurrentText("00")
        
        for combo in [self.hour_combo, self.minute_combo]:
            combo.setStyleSheet("""
                QComboBox {
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    padding: 4px 8px;
                    background: white;
                    min-width: 50px;
                }
                QComboBox:focus {
                    border-color: #80bdff;
                    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid #6c757d;
                    margin-right: 4px;
                }
            """)
        
        layout.addWidget(self.hour_combo)
        layout.addWidget(QLabel(":"))
        layout.addWidget(self.minute_combo)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_time(self):
        return f"{self.hour_combo.currentText()}:{self.minute_combo.currentText()}"
    
    def set_time(self, time_str):
        try:
            hour, minute = time_str.split(":")
            self.hour_combo.setCurrentText(hour)
            self.minute_combo.setCurrentText(minute)
        except:
            pass

class ScheduleTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 테이블 헤더
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("요일"))
        header_layout.addWidget(QLabel("시작 시간"))
        header_layout.addWidget(QLabel("종료 시간"))
        header_layout.addWidget(QLabel("활성화"))
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("""
            QWidget {
                background: #f8f9fa;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                padding: 8px;
            }
        """)
        
        layout.addWidget(header_widget)
        
        # 스케줄 테이블 (토요일, 일요일 추가)
        self.schedule_data = {}
        days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        
        for i, day in enumerate(days):
            day_layout = QHBoxLayout()
            day_layout.setContentsMargins(8, 4, 8, 4)
            
            # 요일 라벨
            day_label = QLabel(day)
            day_label.setMinimumWidth(80)
            
            # 주말은 다른 색상으로 표시
            if day in ["토요일", "일요일"]:
                day_label.setStyleSheet("font-weight: bold; color: #dc3545;")  # 빨간색
            else:
                day_label.setStyleSheet("font-weight: bold; color: #495057;")  # 기본 색상
            
            # 시간 선택기들
            start_time = TimePickerWidget()
            end_time = TimePickerWidget()
            
            # 기본값 설정 (주말은 비활성화)
            if day in ["토요일", "일요일"]:
                end_time.set_time("09:05")
                enabled_default = False
            else:
                end_time.set_time("09:05")
                enabled_default = True
            
            # 활성화 체크박스
            enabled_check = QCheckBox()
            enabled_check.setChecked(enabled_default)
            enabled_check.setStyleSheet("""
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #ced4da;
                    border-radius: 3px;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #28a745;
                    border-radius: 3px;
                    background: #28a745;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik04LjUgMUwzLjUgNkwxLjUgNCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                }
            """)
            
            day_layout.addWidget(day_label)
            day_layout.addWidget(start_time, 1)
            day_layout.addWidget(end_time, 1)
            day_layout.addWidget(enabled_check)
            
            day_widget = QWidget()
            day_widget.setLayout(day_layout)
            
            # 주말 배경색 다르게 설정
            if day in ["토요일", "일요일"]:
                day_widget.setStyleSheet("""
                    QWidget {
                        border-bottom: 1px solid #e9ecef;
                        background: #fff3cd;
                    }
                    QWidget:hover {
                        background: #ffeaa7;
                    }
                """)
            else:
                day_widget.setStyleSheet("""
                    QWidget {
                        border-bottom: 1px solid #e9ecef;
                        background: white;
                    }
                    QWidget:hover {
                        background: #f8f9fa;
                    }
                """)
            
            layout.addWidget(day_widget)
            
            self.schedule_data[day] = {
                'start_time': start_time,
                'end_time': end_time,
                'enabled': enabled_check
            }
        
        self.setLayout(layout)
    
    def get_schedule_data(self):
        data = {}
        for day, widgets in self.schedule_data.items():
            data[day] = {
                'start_time': widgets['start_time'].get_time(),
                'end_time': widgets['end_time'].get_time(),
                'enabled': widgets['enabled'].isChecked()
            }
        return data

class PlaylistManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 상단 컨트롤
        top_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube 플레이리스트 URL을 입력하세요...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #80bdff;
                box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
            }
        """)
        
        add_btn = ModernButton("추가", primary=True)
        add_btn.clicked.connect(self.add_playlist)
        add_btn.setMaximumWidth(80)
        
        top_layout.addWidget(self.url_input)
        top_layout.addWidget(add_btn)
        
        # 플레이리스트 목록
        self.playlist_widget = QListWidget()
        self.playlist_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background: white;
                alternate-background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e9ecef;
                background: white;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
            }
            QListWidget::item:hover {
                background: #e3f2fd;
            }
        """)
        
        # 하단 컨트롤
        bottom_layout = QHBoxLayout()
        
        self.selected_label = QLabel("선택된 플레이리스트: 없음")
        self.selected_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        
        remove_btn = ModernButton("선택 삭제")
        remove_btn.clicked.connect(self.remove_selected)
        remove_btn.setMaximumWidth(100)
        
        bottom_layout.addWidget(self.selected_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(remove_btn)
        
        layout.addLayout(top_layout)
        layout.addWidget(QLabel("저장된 플레이리스트:"))
        layout.addWidget(self.playlist_widget)
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        # 신호 연결
        self.playlist_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
    def add_playlist(self):
        url = self.url_input.text().strip()
        if url and "youtube.com" in url:
            # URL에서 플레이리스트 이름 추출 (간단한 버전)
            playlist_name = f"플레이리스트 {self.playlist_widget.count() + 1}"
            
            item = QListWidgetItem(f"{playlist_name}\n{url}")
            item.setData(Qt.ItemDataRole.UserRole, url)
            self.playlist_widget.addItem(item)
            
            self.url_input.clear()
            
    def remove_selected(self):
        current = self.playlist_widget.currentRow()
        if current >= 0:
            self.playlist_widget.takeItem(current)
            self.on_selection_changed()
    
    def on_selection_changed(self):
        current = self.playlist_widget.currentItem()
        if current:
            self.selected_label.setText(f"선택된 플레이리스트: {current.text().split()[0]}")
        else:
            self.selected_label.setText("선택된 플레이리스트: 없음")
    
    def get_selected_url(self):
        current = self.playlist_widget.currentItem()
        if current:
            return current.data(Qt.ItemDataRole.UserRole)
        return None

class SchoolMusicTimerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scheduler_thread = None
        self.video_scheduler = None  
        self.is_running = False
        self.init_ui()
        self.load_config()
        self.setup_system_tray()
        
    def init_ui(self):
        self.setWindowTitle("🏫 스쿨 뮤직 타이머 v1.0")
        self.setMinimumSize(900, 800)  # 토요일, 일요일 추가로 높이 증가
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        # 메인 위젯
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 전체 스타일
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: #e9ecef;
                color: #495057;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                color: #007bff;
                border-bottom: 2px solid #007bff;
            }
            QTabBar::tab:hover {
                background: #f8f9fa;
            }
        """)
        
        # 상단 상태 영역
        self.create_status_area(main_layout)
        
        # 탭 위젯
        self.create_tab_widget(main_layout)
        
        # 하단 제어 버튼들
        self.create_control_buttons(main_layout)
        
        # 상태바
        self.statusBar().showMessage("준비")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #e9ecef;
                color: #495057;
                border-top: 1px solid #dee2e6;
            }
        """)
        
    def create_status_area(self, main_layout):
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.Box)
        status_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                margin: 8px;
                color: white;
            }
        """)
        
        status_layout = QHBoxLayout()
        status_frame.setLayout(status_layout)
        
        # 현재 시간
        self.current_time_label = QLabel()
        self.current_time_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        # 상태 표시기
        status_info_layout = QVBoxLayout()
        
        status_row = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        self.status_label = QLabel("대기 중")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        
        status_row.addWidget(self.status_indicator)
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        
        # 다음 방송 정보
        self.next_broadcast_label = QLabel("다음 방송: 설정되지 않음")
        self.next_broadcast_label.setStyleSheet("font-size: 14px; color: #f8f9fa;")
        
        status_info_layout.addLayout(status_row)
        status_info_layout.addWidget(self.next_broadcast_label)
        
        status_layout.addWidget(self.current_time_label)
        status_layout.addStretch()
        status_layout.addLayout(status_info_layout)
        
        main_layout.addWidget(status_frame)
        
        # 시간 업데이트 타이머
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
        
    def create_tab_widget(self, main_layout):
        tab_widget = QTabWidget()
        
        # 스케줄 탭
        schedule_tab = QWidget()
        schedule_layout = QVBoxLayout()
        
        schedule_title = QLabel("📅 요일별 스케줄 설정 (주말 포함)")
        schedule_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #495057; margin: 10px 0;")
        schedule_layout.addWidget(schedule_title)
        
        # 주말 안내 텍스트 추가
        weekend_info = QLabel("💡 토요일, 일요일은 노란색 배경으로 표시되며 기본적으로 비활성화됩니다.")
        weekend_info.setStyleSheet("font-size: 12px; color: #6c757d; margin: 5px 0; padding: 8px; background: #fff3cd; border-radius: 4px;")
        schedule_layout.addWidget(weekend_info)
        
        self.schedule_table = ScheduleTableWidget()
        schedule_layout.addWidget(self.schedule_table)
        
        schedule_tab.setLayout(schedule_layout)
        tab_widget.addTab(schedule_tab, "📅 스케줄")
        
        # 플레이리스트 탭
        playlist_tab = QWidget()
        playlist_layout = QVBoxLayout()
        
        playlist_title = QLabel("🎵 플레이리스트 관리")
        playlist_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #495057; margin: 10px 0;")
        playlist_layout.addWidget(playlist_title)
        
        self.playlist_manager = PlaylistManagerWidget()
        playlist_layout.addWidget(self.playlist_manager)
        
        playlist_tab.setLayout(playlist_layout)
        tab_widget.addTab(playlist_tab, "🎵 플레이리스트")
        
        # 설정 탭
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "⚙️ 설정")
        
        main_layout.addWidget(tab_widget)
        
    def create_settings_tab(self):
        settings_widget = QWidget()
        layout = QVBoxLayout()
        
        settings_title = QLabel("⚙️ 고급 설정")
        settings_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #495057; margin: 10px 0;")
        layout.addWidget(settings_title)
        
        # 오늘 실행 안함 옵션
        self.disable_today_check = QCheckBox("오늘은 실행 안 함")
        self.disable_today_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #495057;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        layout.addWidget(self.disable_today_check)
        
        # 자동 전체화면 옵션
        self.fullscreen_check = QCheckBox("자동 전체화면 모드")
        self.fullscreen_check.setChecked(True)
        self.fullscreen_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #495057;
                spacing: 8px;
            }
        """)
        layout.addWidget(self.fullscreen_check)
        
        # 로그 영역
        log_label = QLabel("📋 실행 로그")
        log_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #495057; margin-top: 20px;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background: #f8f9fa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                color: #495057;
            }
        """)
        layout.addWidget(self.log_text)
        
        layout.addStretch()
        settings_widget.setLayout(layout)
        
        return settings_widget
        
    def create_control_buttons(self, main_layout):
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 8px;
                padding: 16px;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_frame.setLayout(button_layout)
        
        # 메인 컨트롤 버튼들
        self.start_btn = ModernButton("🚀 자동 방송 시작", primary=True)
        self.start_btn.clicked.connect(self.toggle_scheduler)
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet(self.start_btn.styleSheet() + "font-size: 16px;")
        
        self.emergency_stop_btn = ModernButton("🛑 비상 정지")
        self.emergency_stop_btn.clicked.connect(self.emergency_stop)
        self.emergency_stop_btn.setEnabled(False)
        
        test_btn = ModernButton("🧪 테스트 실행")
        test_btn.clicked.connect(self.test_mode)
        
        save_btn = ModernButton("💾 설정 저장")
        save_btn.clicked.connect(self.save_config)
        
        button_layout.addWidget(self.start_btn, 2)
        button_layout.addWidget(self.emergency_stop_btn, 1)
        button_layout.addWidget(test_btn, 1)
        button_layout.addWidget(save_btn, 1)
        
        main_layout.addWidget(button_frame)
        
    def setup_system_tray(self):
        # 시스템 트레이 아이콘 설정
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        # 트레이 메뉴
        tray_menu = QMenu()
        
        show_action = QAction("열기", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("종료", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()
            
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.current_time_label.setText(current_time)
        
        # 다음 방송 시간 업데이트
        self.update_next_broadcast_info()
        
    def update_next_broadcast_info(self):
        if not self.is_running:
            self.next_broadcast_label.setText("다음 방송: 설정되지 않음")
            return
            
        # 현재 요일과 시간을 기반으로 다음 방송 시간 계산
        now = datetime.now()
        schedule_data = self.schedule_table.get_schedule_data()
        
        # 요일 매핑 (월요일=0, 일요일=6)
        days_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        today_kr = days_kr[now.weekday()]
        
        # 오늘 스케줄 확인 (활성화 체크만 확인)
        today_schedule = schedule_data.get(today_kr, {})
        is_today_enabled = today_schedule.get('enabled', False)
        
        if is_today_enabled:
            start_time = today_schedule['start_time']
            current_time_str = now.strftime('%H:%M')
            
            # 오늘 방송이 아직 시작되지 않았는지 확인
            if current_time_str < start_time:
                next_time = f"다음 방송: 오늘({today_kr}) {start_time}"
            else:
                # 오늘 방송이 지났으면 다음 방송일 찾기
                next_time = self.find_next_broadcast_day(now, schedule_data)
        else:
            # 오늘 방송이 없으면 다음 방송일 찾기
            next_time = self.find_next_broadcast_day(now, schedule_data)
        
        if self.playlist_manager.get_selected_url():
            current_item = self.playlist_manager.playlist_widget.currentItem()
            if current_item and "다음 방송:" in next_time and "설정되지 않음" not in next_time:
                playlist_name = current_item.text().split('\n')[0]
                next_time += f" ({playlist_name})"
        
        self.next_broadcast_label.setText(next_time)
    
    def find_next_broadcast_day(self, current_time, schedule_data):
        """다음 방송 예정일을 찾는 함수 (활성화 체크만 확인)"""
        days_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        
        for i in range(1, 8):  # 내일부터 일주일 후까지
            check_date = current_time + timedelta(days=i)
            check_day = days_kr[check_date.weekday()]
            check_schedule = schedule_data.get(check_day, {})
            
            # 활성화 체크만 확인
            is_enabled = check_schedule.get('enabled', False)
            
            if is_enabled:
                start_time = check_schedule['start_time']
                if i == 1:
                    return f"다음 방송: 내일({check_day}) {start_time}"
                else:
                    return f"다음 방송: {check_day} {start_time}"
        
        return "다음 방송: 설정되지 않음"
    
    def toggle_scheduler(self):
        if not self.is_running:
            self.start_scheduler()
        else:
            self.stop_scheduler()
    
    def start_scheduler(self):
        try:
            # video_scheduler 모듈 import
            from video_scheduler import VideoScheduler
        except ImportError as e:
            QMessageBox.critical(self, "오류", f"video_scheduler 모듈을 불러올 수 없습니다: {e}")
            return
        
        # 설정 검증
        if not self.playlist_manager.get_selected_url():
            QMessageBox.warning(self, "경고", "플레이리스트를 선택해주세요.")
            return
            
        if self.disable_today_check.isChecked():
            QMessageBox.information(self, "알림", "오늘 실행 안함이 활성화되어 있습니다.")
            return
        
        # 스케줄 데이터 가져오기
        schedule_data = self.schedule_table.get_schedule_data()
        selected_url = self.playlist_manager.get_selected_url()
        
        # 활성화된 스케줄만 필터링 (활성화 체크만 확인)
        active_schedules = []
        
        for day, data in schedule_data.items():
            self.log_message(f"📋 {day} 스케줄 확인: 활성화={data['enabled']}, 시간={data['start_time']}~{data['end_time']}")
            
            if data['enabled']:
                active_schedules.append((day, data))
                self.log_message(f"✅ {day} 스케줄 활성 목록에 추가: {data['start_time']} ~ {data['end_time']}")
            else:
                self.log_message(f"⏭️ {day} 스케줄 스킵됨 (비활성화)")
        
        self.log_message(f"📊 총 활성화된 스케줄 수: {len(active_schedules)}")
        
        if not active_schedules:
            QMessageBox.warning(self, "경고", "활성화된 스케줄이 없습니다.")
            return
        
        # VideoScheduler 인스턴스 생성
        self.video_scheduler = VideoScheduler()
        
        # 요일별 스케줄 추가
        success_count = 0
        for day, data in active_schedules:
            schedule_name = f"{day} 방송"
            success = self.video_scheduler.add_daily_schedule(
                day=day,
                start_time=data['start_time'],
                end_time=data['end_time'],
                video_url=selected_url,
                schedule_name=schedule_name
            )
            if success:
                success_count += 1
                self.log_message(f"✅ {day} 스케줄 등록: {data['start_time']} ~ {data['end_time']}")
            else:
                self.log_message(f"❌ {day} 스케줄 등록 실패")
        
        if success_count == 0:
            QMessageBox.critical(self, "오류", "스케줄 등록에 실패했습니다.")
            return
        
        # 스케줄러 시작
        try:
            self.video_scheduler.start_scheduler()
            
            self.is_running = True
            self.start_btn.setText("⏹️ 스케줄러 중지")
            self.emergency_stop_btn.setEnabled(True)
            self.status_indicator.set_status("running")
            self.status_label.setText("스케줄러 실행 중")
            
            self.log_message(f"🚀 스케줄러 시작완료! ({success_count}개 스케줄 등록)")
                
            self.statusBar().showMessage(f"스케줄러 실행 중... ({success_count}개 활성)")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"스케줄러 시작 중 오류: {e}")
            self.log_message(f"❌ 스케줄러 시작 오류: {e}")
        
    def stop_scheduler(self):
        if self.video_scheduler:
            self.video_scheduler.stop_scheduler()
            self.video_scheduler = None
            
        self.is_running = False
        self.start_btn.setText("🚀 자동 방송 시작")
        self.emergency_stop_btn.setEnabled(False)
        self.status_indicator.set_status("idle")
        self.status_label.setText("대기 중")
        
        self.log_message("스케줄러가 중지되었습니다.")
        self.statusBar().showMessage("준비")
        
    def emergency_stop(self):
        reply = QMessageBox.question(
            self, 
            "비상 정지", 
            "정말로 비상 정지하시겠습니까?\n모든 실행 중인 작업이 즉시 중단됩니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.video_scheduler:
                self.video_scheduler.emergency_stop()
            self.stop_scheduler()
            self.log_message("비상 정지 실행됨!")
            self.status_indicator.set_status("error")
            self.status_label.setText("비상 정지됨")
            
    def test_mode(self):
        """테스트 모드 - 실제 playvideo 호출"""
        try:
            from playvideo import play_youtube_video
            
            self.log_message("🧪 테스트 모드 실행 중...")
            self.status_indicator.set_status("warning")
            self.status_label.setText("테스트 실행 중")
            
            # 현재 요일 확인
            current_day = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][datetime.now().weekday()]
            
            if current_day in ["토요일", "일요일"]:
                self.log_message(f"🏖️ 주말 테스트 중: {current_day}")
            
            # 선택된 URL 가져오기
            test_url = self.playlist_manager.get_selected_url()
            if not test_url:
                test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 기본 테스트 URL
                self.log_message("⚠️ 선택된 플레이리스트가 없어 기본 URL로 테스트합니다.")
            
            self.log_message(f"📺 테스트 URL: {test_url}")
            
            # YouTube 창 열기
            driver = play_youtube_video(test_url)
            
            if driver:
                self.log_message("✅ 테스트 영상 재생 시작!")
                
                # 5초 후 창 닫기
                QTimer.singleShot(5000, lambda: self.close_test_video(driver))
            else:
                self.log_message("❌ 테스트 영상 재생 실패")
                self.test_complete()
                
        except Exception as e:
            self.log_message(f"❌ 테스트 중 오류: {e}")
            self.test_complete()
    
    def close_test_video(self, driver):
        """테스트 영상 창 닫기"""
        try:
            if driver:
                driver.quit()
                self.log_message("🔇 테스트 영상 종료")
        except Exception as e:
            self.log_message(f"⚠️ 테스트 영상 종료 중 오류: {e}")
        finally:
            self.test_complete()
        
    def test_complete(self):
        self.log_message("🧪 테스트 완료!")
        if not self.is_running:
            self.status_indicator.set_status("idle")
            self.status_label.setText("대기 중")
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        
        # 로그가 너무 길어지면 맨 위 줄 삭제
        if self.log_text.document().lineCount() > 100:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # 개행 문자 삭제
        
    def save_config(self):
        # config.ini에 설정 저장
        config = configparser.ConfigParser()
        
        # 스케줄 데이터 저장
        schedule_data = self.schedule_table.get_schedule_data()
        config['SCHEDULE'] = {}
        for day, data in schedule_data.items():
            config['SCHEDULE'][day] = json.dumps(data)
        
        # 플레이리스트 데이터 저장
        config['PLAYLISTS'] = {}
        for i in range(self.playlist_manager.playlist_widget.count()):
            item = self.playlist_manager.playlist_widget.item(i)
            config['PLAYLISTS'][f'playlist_{i}'] = item.data(Qt.ItemDataRole.UserRole)
        
        # 설정 저장
        config['SETTINGS'] = {
            'disable_today': str(self.disable_today_check.isChecked()),
            'fullscreen': str(self.fullscreen_check.isChecked()),
            'selected_playlist': str(self.playlist_manager.playlist_widget.currentRow())
        }
        
        try:
            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
            self.log_message("설정이 저장되었습니다.")
            QMessageBox.information(self, "알림", "설정이 저장되었습니다.")
        except Exception as e:
            self.log_message(f"설정 저장 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"설정 저장 중 오류가 발생했습니다:\n{e}")
    
    def load_config(self):
        if not os.path.exists('config.ini'):
            return
            
        config = configparser.ConfigParser()
        try:
            config.read('config.ini', encoding='utf-8')
            
            # 설정 로드
            if 'SETTINGS' in config:
                settings = config['SETTINGS']
                self.disable_today_check.setChecked(settings.getboolean('disable_today', False))
                self.fullscreen_check.setChecked(settings.getboolean('fullscreen', True))
            
            # 스케줄 데이터 로드
            if 'SCHEDULE' in config:
                for day, json_data in config['SCHEDULE'].items():
                    try:
                        data = json.loads(json_data)
                        if day in self.schedule_table.schedule_data:
                            widgets = self.schedule_table.schedule_data[day]
                            widgets['start_time'].set_time(data.get('start_time', '09:00'))
                            widgets['end_time'].set_time(data.get('end_time', '09:05'))
                            widgets['enabled'].setChecked(data.get('enabled', False))
                    except json.JSONDecodeError:
                        continue
            
            # 플레이리스트 로드
            if 'PLAYLISTS' in config:
                for key, url in config['PLAYLISTS'].items():
                    if url:
                        item = QListWidgetItem(f"플레이리스트 {self.playlist_manager.playlist_widget.count() + 1}\n{url}")
                        item.setData(Qt.ItemDataRole.UserRole, url)
                        self.playlist_manager.playlist_widget.addItem(item)
                        
                # 선택된 플레이리스트 복원
                if 'SETTINGS' in config and 'selected_playlist' in config['SETTINGS']:
                    selected_idx = int(config['SETTINGS'].get('selected_playlist', -1))
                    if 0 <= selected_idx < self.playlist_manager.playlist_widget.count():
                        self.playlist_manager.playlist_widget.setCurrentRow(selected_idx)
            
            self.log_message("설정이 로드되었습니다.")
            
        except Exception as e:
            self.log_message(f"설정 로드 중 오류: {e}")
    
    def closeEvent(self, event):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
            self.tray_icon.showMessage(
                "스쿨 뮤직 타이머",
                "프로그램이 시스템 트레이에서 계속 실행됩니다.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()
    
    def quit_application(self):
        if self.is_running:
            reply = QMessageBox.question(
                self,
                "종료 확인",
                "스케줄러가 실행 중입니다.\n정말로 종료하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.tray_icon.hide()
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 트레이 아이콘 지원
    
    # 어플리케이션 정보 설정
    app.setApplicationName("스쿨 뮤직 타이머")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("School Music Timer")
    
    # 시스템 트레이 지원 확인
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "시스템 트레이", 
                           "시스템 트레이를 사용할 수 없습니다.")
    
    window = SchoolMusicTimerGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()