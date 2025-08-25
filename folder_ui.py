import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                               QComboBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QPainter, QPen, QBrush, QPolygon, QLinearGradient
from PySide6.QtCore import QPoint, QRect

class FolderIconWidget(QWidget):
    """파일 폴더 아이콘 모양 위젯"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 400)
        self.setup_tab_buttons()
    
    def setup_tab_buttons(self):
        """폴더 탭 영역에 버튼들 설정"""
        # 요일 버튼들 생성
        self.day_buttons = []
        button_names = ["월", "화", "수", "목", "금", "토", "일"]
        
        for i, name in enumerate(button_names):
            btn = QPushButton(name, self)
            btn.setFixedSize(40, 40)  # 정사각형으로 변경 (40x40)
            
            # 첫 번째 버튼은 활성화 상태로
            if i == 0:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #66BB6A, stop:1 #4CAF50);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 600;
                        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #5CBB61, stop:1 #43A047);
                        transform: translateY(-1px);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #4CAF50, stop:1 #388E3C);
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #FFFFFF, stop:1 #F8F9FA);
                        color: #495057;
                        border: 1px solid #E9ECEF;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 500;
                        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #F8F9FA, stop:1 #E9ECEF);
                        border: 1px solid #DEE2E6;
                        transform: translateY(-1px);
                        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #E9ECEF, stop:1 #DEE2E6);
                        transform: translateY(0px);
                    }
                """)
            
            self.day_buttons.append(btn)
        
        self.position_buttons()
        
        # 폴더 내부 시간 설정 UI 추가
        self.setup_time_ui()
        
        # 미디어 타입 및 입력 UI 추가
        self.setup_media_ui()
    
    def position_buttons(self):
        """버튼들을 폴더 탭 영역에 배치"""
        # 폴더 탭 영역 계산
        width = self.width() if self.width() > 0 else 500
        folder_x = 50
        folder_y = 100
        tab_start_x = folder_x + 45  # 정사각형 버튼에 맞게 시작 위치 조정
        tab_start_y = folder_y + 20  # 버튼 위치를 위로 올림 (25 → 20)
        
        # 버튼들을 가로로 배치
        for i, btn in enumerate(self.day_buttons):
            btn.move(tab_start_x + (i * 60), tab_start_y)  # 정사각형 버튼에 맞게 간격 조정
    
    def resizeEvent(self, event):
        """위젯 크기 변경 시 버튼 위치 재조정"""
        super().resizeEvent(event)
        if hasattr(self, 'day_buttons'):
            self.position_buttons()
        if hasattr(self, 'time_widgets'):
            self.position_time_ui()
        if hasattr(self, 'media_widgets'):
            self.position_media_ui()
        if hasattr(self, 'schedule_widgets'):
            self.position_schedule_ui()

    def setup_time_ui(self):
        """폴더 내부에 시간 설정 UI 생성"""
        # 시작 시간 라벨
        self.start_time_label = QLabel("시작 시간", self)
        self.start_time_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E3F2FD, stop:1 #BBDEFB);
                border: 2px solid #2196F3;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 16px;
                font-weight: 600;
                color: #1565C0;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 0.5px;
            }
        """)
        
        # 시작 시간 입력 필드들
        self.start_hour = QLineEdit("시", self)
        self.start_min = QLineEdit("분", self)
        
        # 종료 시간 라벨  
        self.end_time_label = QLabel("종료 시간", self)
        self.end_time_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FCE4EC, stop:1 #F8BBD9);
                border: 2px solid #E91E63;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 16px;
                font-weight: 600;
                color: #AD1457;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 0.5px;
            }
        """)
        
        # 종료 시간 입력 필드들
        self.end_hour = QLineEdit("시", self)
        self.end_min = QLineEdit("분", self)
        
        # 입력 필드 스타일
        input_style = """
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 500;
                color: #495057;
                font-family: 'Segoe UI', Arial, sans-serif;
                selection-background-color: #007BFF;
            }
            QLineEdit:focus {
                border: 2px solid #007BFF;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F0F8FF);
                box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
            }
            QLineEdit:hover {
                border: 2px solid #6C757D;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F1F3F4);
            }
        """
        
        for widget in [self.start_hour, self.start_min, self.end_hour, self.end_min]:
            widget.setStyleSheet(input_style)
            widget.setFixedSize(45, 35)  # 약간 더 크게 조정
        
        # 위젯 리스트 저장
        self.time_widgets = [
            self.start_time_label, self.start_hour, self.start_min,
            self.end_time_label, self.end_hour, self.end_min
        ]
        
        self.position_time_ui()

    def position_time_ui(self):
        """시간 설정 UI 위치 배치"""
        width = self.width() if self.width() > 0 else 500
        height = self.height() if self.height() > 0 else 400
        
        # 폴더 내부 영역 계산
        folder_x = 50
        folder_y = 160  # 폴더 탭 아래쪽
        
        # 시작 시간 UI 배치 (모던한 간격으로 조정)
        self.start_time_label.move(folder_x + 25, folder_y + 25)
        self.start_time_label.resize(130, 45)  # 더 넉넉한 크기
        
        self.start_hour.move(folder_x + 170, folder_y + 30)  # 위치 조정
        self.start_min.move(folder_x + 225, folder_y + 30)
        
        # 종료 시간 UI 배치 (모던한 간격으로 조정)
        self.end_time_label.move(folder_x + 290, folder_y + 25)
        self.end_time_label.resize(130, 45)  # 더 넉넉한 크기
        
        self.end_hour.move(folder_x + 435, folder_y + 30)  # 위치 조정
        self.end_min.move(folder_x + 490, folder_y + 30)

    def setup_media_ui(self):
        """미디어 타입 및 입력 UI 생성"""
        # 미디어 타입 선택 콤보박스
        self.media_type_combo = QComboBox(self)
        self.media_type_combo.addItems(["미디어타입", "링크", "파일"])
        self.media_type_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                border: 2px solid #6C757D;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: 600;
                color: #495057;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 2px solid #495057;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8F9FA, stop:1 #E9ECEF);
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 15px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        # 링크/파일 입력 필드
        self.media_input = QLineEdit("링크 or 파일", self)
        self.media_input.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                border: 2px solid #E9ECEF;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: 500;
                color: #495057;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #007BFF;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F0F8FF);
            }
            QLineEdit:hover {
                border: 2px solid #6C757D;
            }
        """)
        
        # 추가 버튼
        self.add_button = QPushButton("추가", self)
        self.add_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28A745, stop:1 #20A83A);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #20A83A, stop:1 #1E7E34);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E7E34, stop:1 #155724);
            }
        """)
        
        # 미디어 위젯 리스트 저장 (스크롤 영역 제거)
        self.media_widgets = [
            self.media_type_combo, self.media_input, self.add_button
        ]
        
        # 콤보박스 변경 이벤트 연결
        self.media_type_combo.currentTextChanged.connect(self.on_media_type_changed)
        
        self.position_media_ui()
        
        # 설정된 스케줄 UI 추가
        self.setup_schedule_ui()

    def on_media_type_changed(self, text):
        """미디어 타입 변경 시 호출"""
        if text == "링크":
            self.media_input.setPlaceholderText("YouTube 링크를 입력하세요")
        elif text == "파일":
            self.media_input.setPlaceholderText("오디오 파일을 선택하세요")
        else:
            self.media_input.setPlaceholderText("링크 or 파일")

    def position_media_ui(self):
        """미디어 UI 위치 배치"""
        width = self.width() if self.width() > 0 else 500
        height = self.height() if self.height() > 0 else 400
        
        # 폴더 내부 영역 계산
        folder_x = 50
        folder_y = 240  # 시간 UI 아래쪽
        
        # 미디어 타입 콤보박스
        self.media_type_combo.move(folder_x + 25, folder_y)
        self.media_type_combo.resize(150, 45)
        
        # 링크/파일 입력 필드
        self.media_input.move(folder_x + 190, folder_y)
        self.media_input.resize(300, 45)
        
        # 추가 버튼
        self.add_button.move(folder_x + 505, folder_y)
        self.add_button.resize(90, 45)

    def setup_schedule_ui(self):
        """설정된 스케줄 UI 생성"""
        # 스케줄 제목 라벨
        self.schedule_title = QLabel("설정된 스케줄", self)
        self.schedule_title.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                padding: 5px 0px;
            }
        """)
        
        # 스케줄 스크롤 영역
        self.schedule_scroll_area = QScrollArea(self)
        self.schedule_scroll_area.setStyleSheet("""
            QScrollArea {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                border: 2px solid #E9ECEF;
                border-radius: 12px;
                padding: 8px;
            }
            QScrollBar:vertical {
                background: #F8F9FA;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #CED4DA, stop:1 #ADB5BD);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ADB5BD, stop:1 #6C757D);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # 스크롤 내용 위젯
        self.schedule_content = QWidget()
        self.schedule_layout = QVBoxLayout(self.schedule_content)
        self.schedule_layout.setSpacing(10)
        self.schedule_layout.setContentsMargins(12, 12, 12, 12)
        
        # 샘플 스케줄 추가
        self.add_sample_schedules()
        
        self.schedule_scroll_area.setWidget(self.schedule_content)
        self.schedule_scroll_area.setWidgetResizable(True)
        
        # 스케줄 위젯 리스트 저장
        self.schedule_widgets = [self.schedule_title, self.schedule_scroll_area]
        
        self.position_schedule_ui()

    def add_sample_schedules(self):
        """샘플 스케줄 항목들 추가"""
        sample_schedules = [
            {
                "days": "월, 화, 수",
                "time": "09:00 - 12:00",
                "media": "https://www.youtube.com/watch?v=example1",
                "type": "링크"
            },
            {
                "days": "목, 금",
                "time": "14:00 - 16:00", 
                "media": "audio_file.mp3",
                "type": "파일"
            },
            {
                "days": "토, 일",
                "time": "19:00 - 21:00",
                "media": "https://www.youtube.com/watch?v=example2",
                "type": "링크"
            }
        ]
        
        for schedule in sample_schedules:
            self.add_schedule_item(schedule)

    def add_schedule_item(self, schedule_data):
        """스케줄 항목 추가"""
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F9FA);
                border: 2px solid #E9ECEF;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E3F2FD, stop:1 #F8F9FA);
                border: 2px solid #2196F3;
            }
        """)
        
        main_layout = QVBoxLayout(item_frame)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 첫 번째 줄: 요일과 시간
        top_layout = QHBoxLayout()
        
        days_label = QLabel(f"📅 {schedule_data['days']}")
        days_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        time_label = QLabel(f"🕐 {schedule_data['time']}")
        time_label.setStyleSheet("""
            QLabel {
                color: #FF5722;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        top_layout.addWidget(days_label)
        top_layout.addStretch()
        top_layout.addWidget(time_label)
        
        # 두 번째 줄: 미디어 정보와 삭제 버튼
        bottom_layout = QHBoxLayout()
        
        media_icon = "🔗" if schedule_data['type'] == "링크" else "🎵"
        media_text = schedule_data['media']
        if len(media_text) > 45:
            media_text = media_text[:42] + "..."
            
        media_label = QLabel(f"{media_icon} {media_text}")
        media_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                background: transparent;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        delete_btn = QPushButton("삭제")
        delete_btn.setFixedSize(55, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF5722, stop:1 #E64A19);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 11px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E64A19, stop:1 #D84315);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #D84315, stop:1 #BF360C);
            }
        """)
        
        bottom_layout.addWidget(media_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(delete_btn)
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        
        self.schedule_layout.addWidget(item_frame)

    def position_schedule_ui(self):
        """스케줄 UI 위치 배치"""
        width = self.width() if self.width() > 0 else 500
        height = self.height() if self.height() > 0 else 400
        
        # 폴더 내부 영역 계산
        folder_x = 50
        schedule_y = 300  # 미디어 UI 아래쪽
        
        # 스케줄 제목
        self.schedule_title.move(folder_x + 25, schedule_y)
        self.schedule_title.resize(200, 30)
        
        # 스케줄 스크롤 영역
        # 폴더의 남은 공간을 계산하여 적절한 높이 설정 (2배로 증가)
        available_height = height - schedule_y - 50  # 여백을 50px로 줄임
        scroll_height = max(300, min(450, available_height))  # 최대 높이를 450px로 조정
        
        self.schedule_scroll_area.move(folder_x + 25, schedule_y + 35)
        self.schedule_scroll_area.resize(570, scroll_height)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 전체 크기
        width = self.width()
        height = self.height()
        
        # 배경을 흰색으로 설정
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # 폴더 크기 및 위치 계산
        folder_width = width - 100
        folder_height = height - 150
        folder_x = 50
        folder_y = 100
        
        # 폴더 탭 크기 (7개 버튼을 모두 감쌀 수 있도록 확장)
        tab_width = 490  # 7개 버튼 * 70px = 490px
        tab_height = 70  # 높이를 60에서 70으로 더 증가
        
        # 뒷쪽 폴더 탭 그리기 (베이지색)
        back_tab_polygon = QPolygon([
            QPoint(folder_x + 20, folder_y),
            QPoint(folder_x + 20 + tab_width, folder_y),
            QPoint(folder_x + 20 + tab_width + 15, folder_y + tab_height),
            QPoint(folder_x + 20, folder_y + tab_height)
        ])
        painter.setBrush(QBrush(QColor(240, 220, 190)))  # 베이지색
        painter.setPen(QPen(QColor(200, 180, 150), 2))
        painter.drawPolygon(back_tab_polygon)
        
        # 앞쪽 폴더 탭 그리기 (노란색) - 7개 버튼을 모두 감쌀 수 있는 크기로
        front_tab_polygon = QPolygon([
            QPoint(folder_x + 20, folder_y + 10),
            QPoint(folder_x + 20 + tab_width, folder_y + 10),
            QPoint(folder_x + 20 + tab_width + 15, folder_y + 10 + tab_height),
            QPoint(folder_x + 20, folder_y + 10 + tab_height)
        ])
        painter.setBrush(QBrush(QColor(255, 220, 100)))  # 노란색
        painter.setPen(QPen(QColor(200, 180, 80), 2))
        painter.drawPolygon(front_tab_polygon)
        
        # 메인 폴더 몸체 그리기 (노란색)
        main_folder_polygon = QPolygon([
            QPoint(folder_x, folder_y + tab_height),
            QPoint(folder_x + folder_width, folder_y + tab_height),
            QPoint(folder_x + folder_width, folder_y + folder_height),
            QPoint(folder_x, folder_y + folder_height)
        ])
        painter.setBrush(QBrush(QColor(255, 220, 100)))  # 밝은 노란색
        painter.setPen(QPen(QColor(200, 180, 80), 2))
        painter.drawPolygon(main_folder_polygon)
        
        # 폴더 그림자 효과
        shadow_offset = 5
        shadow_polygon = QPolygon([
            QPoint(folder_x + shadow_offset, folder_y + tab_height + shadow_offset),
            QPoint(folder_x + folder_width + shadow_offset, folder_y + tab_height + shadow_offset),
            QPoint(folder_x + folder_width + shadow_offset, folder_y + folder_height + shadow_offset),
            QPoint(folder_x + shadow_offset, folder_y + folder_height + shadow_offset)
        ])
        painter.setBrush(QBrush(QColor(200, 200, 200, 100)))  # 반투명 회색
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(shadow_polygon)

class YoutubeAutoPlayerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 메인 윈도우 설정
        self.setWindowTitle("Youtube Auto Player - Folder Style")
        self.setGeometry(100, 100, 800, 600)
        
        # 중앙 위젯으로 폴더 아이콘 위젯 사용
        folder_widget = FolderIconWidget()
        self.setCentralWidget(folder_widget)

def main():
    app = QApplication(sys.argv)
    
    # 애플리케이션 스타일 설정
    app.setStyle('Fusion')
    
    window = YoutubeAutoPlayerGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
