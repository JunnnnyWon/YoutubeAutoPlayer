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


class SongRequestTableWidget(QTableWidget):
    def __init__(self):
        super().__init__(0, 5)  # 0행, 5열(순번, 시작시간, 종료시간, 이름, URL)
        self.setup_table()
        
    def setup_table(self):
        # 컬럼 설정
        headers = ["순번", "시작 시간", "종료 시간", "제목", "URL"]
        self.setHorizontalHeaderLabels(headers)
        
        # 테이블 스타일
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
            }
        """)
        
        # 컬럼 너비 설정
        self.setColumnWidth(0, 60)  # 순번
        self.setColumnWidth(1, 100) # 시작 시간
        self.setColumnWidth(2, 100) # 종료 시간
        self.setColumnWidth(3, 300) # 제목
        
        # 테이블 동작 설정
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)

    def add_song(self, start_time, end_time, name, url):
        row = self.rowCount()
        self.insertRow(row)
        
        self.setItem(row, 0, QTableWidgetItem(str(row + 1)))  # 순번
        self.setItem(row, 1, QTableWidgetItem(start_time))
        self.setItem(row, 2, QTableWidgetItem(end_time))
        self.setItem(row, 3, QTableWidgetItem(name))
        self.setItem(row, 4, QTableWidgetItem(url))
        
    def remove_selected_song(self):
        current_row = self.currentRow()
        if current_row >= 0:
            self.removeRow(current_row)
            self.update_order_numbers()
            
    def update_order_numbers(self):
        for row in range(self.rowCount()):
            self.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
    def get_all_songs(self):
        songs = []
        for row in range(self.rowCount()):
            songs.append({
                'order': int(self.item(row, 0).text()),
                'start_time': self.item(row, 1).text(),
                'end_time': self.item(row, 2).text(),
                'name': self.item(row, 3).text(),
                'url': self.item(row, 4).text()
            })
        return songs

class ViewerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 상태 표시 영역
        status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        self.status_label = QLabel("대기 중")
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # 신청곡 목록 테이블
        self.song_table = SongRequestTableWidget()
        
        # 컨트롤 버튼들
        btn_layout = QHBoxLayout()
        self.start_btn = ModernButton("재생 시작", primary=True)
        self.stop_btn = ModernButton("정지")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(status_layout)
        layout.addWidget(self.song_table)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

class EditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.song_table = SongRequestTableWidget()  # 테이블 인스턴스 저장
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 입력 폼
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.url_input = QLineEdit()
        self.start_time = TimePickerWidget()
        self.end_time = TimePickerWidget()
        
        form_layout.addRow("제목:", self.title_input)
        form_layout.addRow("URL:", self.url_input)
        form_layout.addRow("시작 시간:", self.start_time)
        form_layout.addRow("종료 시간:", self.end_time)
        
        # 버튼들
        btn_layout = QHBoxLayout()
        self.add_btn = ModernButton("추가", primary=True)
        self.edit_btn = ModernButton("수정")
        self.delete_btn = ModernButton("삭제")
        
        # 버튼 이벤트 연결
        self.add_btn.clicked.connect(self.add_song)
        self.edit_btn.clicked.connect(self.edit_song)
        self.delete_btn.clicked.connect(self.delete_song)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.song_table)  # 저장된 테이블 인스턴스 사용
        self.setLayout(layout)
    
    def add_song(self):
        title = self.title_input.text().strip()
        url = self.url_input.text().strip()
        start = self.start_time.get_time()
        end = self.end_time.get_time()
        
        if title and url:
            self.song_table.add_song(start, end, title, url)
            self.clear_form()
            
    def edit_song(self):
        current_row = self.song_table.currentRow()
        if current_row >= 0:
            self.song_table.setItem(current_row, 1, QTableWidgetItem(self.start_time.get_time()))
            self.song_table.setItem(current_row, 2, QTableWidgetItem(self.end_time.get_time()))
            self.song_table.setItem(current_row, 3, QTableWidgetItem(self.title_input.text()))
            self.song_table.setItem(current_row, 4, QTableWidgetItem(self.url_input.text()))
            self.clear_form()
    
    def delete_song(self):
        self.song_table.remove_selected_song()
        self.clear_form()
        
    def clear_form(self):
        self.title_input.clear()
        self.url_input.clear()
        self.start_time.set_time("09:00")
        self.end_time.set_time("09:05")



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
        # 상태 변수 초기화
        self.is_running = False
        self.video_scheduler = None
        # UI 초기화
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🏫 스쿨 뮤직 타이머 v1.01")
        self.setMinimumSize(900, 800)
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        # 메인 위젯과 레이아웃 생성
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 전체 스타일 설정
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
        
        # 탭 위젯 생성
        tab_widget = QTabWidget()
        
        # VIEWER, EDITOR, SETTINGS 탭 추가
        viewer_tab = ViewerTab()
        editor_tab = EditorTab()
        settings_tab = self.create_settings_tab()
        
        tab_widget.addTab(viewer_tab, "👀 VIEWER")
        tab_widget.addTab(editor_tab, "✏️ EDITOR")
        tab_widget.addTab(settings_tab, "⚙️ SETTINGS")
        
        # 상단 상태 영역
        self.create_status_area(main_layout)
        
        # 탭 위젯 추가
        main_layout.addWidget(tab_widget)
        
        # 하단 제어 버튼
        self.create_control_buttons(main_layout)
        
        # 중앙 위젯 설정
        self.setCentralWidget(main_widget)
        
        # 상태바
        self.statusBar().showMessage("준비")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #e9ecef;
                color: #495057;
                border-top: 1px solid #dee2e6;
            }
        """)
        
        # 시간 업데이트 타이머 설정
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
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

    def create_settings_tab(self):
        settings_widget = QWidget()
        layout = QVBoxLayout()
        
        settings_title = QLabel("⚙️ 고급 설정")
        settings_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #495057; margin: 10px 0;")
        layout.addWidget(settings_title)
        
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
        
    def toggle_scheduler(self):
        if not self.is_running:
            self.start_scheduler()
        else:
            self.stop_scheduler()
    
    def start_scheduler(self):
        try:
            from video_scheduler import VideoScheduler
        except ImportError as e:
            QMessageBox.critical(self, "오류", f"video_scheduler 모듈을 불러올 수 없습니다: {e}")
            return

        # 신청곡 목록 가져오기
        songs = self.editor_tab.song_table.get_all_songs()
        if not songs:
            QMessageBox.warning(self, "경고", "등록된 신청곡이 없습니다.")
            return

        # VideoScheduler 인스턴스 생성
        self.video_scheduler = VideoScheduler()

        # 각 신청곡에 대한 스케줄 추가
        success_count = 0
        for song in songs:
            schedule_name = f"신청곡 {song['order']}"
            success = self.video_scheduler.add_schedule(
                start_time=song['start_time'],
                end_time=song['end_time'],
                video_url=song['url'],
                schedule_name=schedule_name
            )
            if success:
                success_count += 1
                self.log_message(f"✅ 신청곡 등록: {song['name']} ({song['start_time']} ~ {song['end_time']})")

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
            self.statusBar().showMessage(f"스케줄러 실행 중... ({success_count}개 신청곡)")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"스케줄러 시작 중 오류: {e}")
            self.log_message(f"❌ 스케줄러 시작 오류: {e}")

    def update_next_broadcast_info(self):
        if not self.is_running:
            self.next_broadcast_label.setText("다음 방송: 설정되지 않음")
            return
            
        # 다음 신청곡 찾기
        songs = self.editor_tab.song_table.get_all_songs()
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        next_song = None
        for song in songs:
            if song['start_time'] > current_time:
                next_song = song
                break
        
        if next_song:
            self.next_broadcast_label.setText(
                f"다음 방송: {next_song['name']} ({next_song['start_time']})"
            )
        else:
            self.next_broadcast_label.setText("다음 방송: 없음")

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
        config = configparser.ConfigParser()
        
        # 신청곡 목록 저장
        config['SONGS'] = {}
        songs = self.editor_tab.song_table.get_all_songs()
        for idx, song in enumerate(songs):
            song_data = {
                'start_time': song['start_time'],
                'end_time': song['end_time'],
                'name': song['name'],
                'url': song['url']
            }
            config['SONGS'][f'song_{idx}'] = json.dumps(song_data)
        
        # 설정 저장
        config['SETTINGS'] = {
            'fullscreen': str(self.fullscreen_check.isChecked())
        }
        
        try:
            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
        except Exception as e:
            self.log_message(f"설정 저장 중 오류: {e}")
    
    def load_config(self):
        if not os.path.exists('config.ini'):
            return
            
        config = configparser.ConfigParser()
        try:
            config.read('config.ini', encoding='utf-8')
            
            # 설정 로드
            if 'SETTINGS' in config:
                self.fullscreen_check.setChecked(config['SETTINGS'].getboolean('fullscreen', True))
            
            # 신청곡 목록 로드
            if 'SONGS' in config:
                for _, song_data in config['SONGS'].items():
                    try:
                        song = json.loads(song_data)
                        self.editor_tab.song_table.add_song(
                            song['start_time'],
                            song['end_time'],
                            song['name'],
                            song['url']
                        )
                    except json.JSONDecodeError:
                        continue
                        
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