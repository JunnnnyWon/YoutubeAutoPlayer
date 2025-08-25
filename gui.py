import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# folder_ui.py에서 FolderIconWidget import
from folder_ui import FolderIconWidget

class YoutubeAutoPlayerGUI(QMainWindow):
    """Youtube Auto Player 메인 GUI"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 메인 윈도우 설정
        self.setWindowTitle("Youtube Auto Player")
        self.setGeometry(100, 100, 900, 1100)  # 높이를 1100으로 줄임
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(10)
        
        # 폴더 아이콘 위젯 추가 (상단 버튼 영역 제거)
        self.folder_widget = FolderIconWidget()
        self.folder_widget.setMinimumHeight(900)  # 최소 높이를 900으로 줄임
        self.folder_widget.setMaximumHeight(950)  # 최대 높이 제한 추가
        main_layout.addWidget(self.folder_widget)

    def create_top_button_area(self, parent_layout):
        """상단 버튼 영역 생성"""
        button_container = QWidget()
        button_container.setFixedHeight(80)
        button_container.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 8px;
            }
        """)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_container.setLayout(button_layout)
        button_layout.setContentsMargins(15, 15, 15, 15)
        button_layout.setSpacing(10)
        
        # 7개 버튼 생성
        button_names = ["월", "화", "수", "목", "금", "토", "일"]
        
        for i, name in enumerate(button_names):
            btn = QPushButton(name)
            btn.setFixedSize(80, 50)
            
            # 첫 번째 버튼은 활성화 상태로
            if i == 0:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                    QPushButton:pressed {
                        background-color: #3d8b40;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        color: #333;
                        border: 1px solid #bbb;
                        border-radius: 5px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                    }
                    QPushButton:pressed {
                        background-color: #c0c0c0;
                    }
                """)
            
            button_layout.addWidget(btn)
        
        # 나머지 공간 채우기
        button_layout.addStretch()
        
        parent_layout.addWidget(button_container)

def main():
    """메인 실행 함수"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = YoutubeAutoPlayerGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
