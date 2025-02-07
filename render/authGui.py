import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit,QMessageBox
from PyQt5.QtCore import Qt

from render.gui import create_gui
from utils.deviceGen import get_machine_code
from utils.keyDecode import aes_gcm_decrypt


class VerificationWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("激活窗口")
        self.setGeometry(300, 300, 400, 200)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 显示机器码
        self.machine_code = get_machine_code()
        
        # 使用 QTextEdit 显示机器码，支持全选复制
        self.machine_code_label = QLabel("机器码:")
        self.machine_code_output = QTextEdit(self)
        self.machine_code_output.setReadOnly(True)
        self.machine_code_output.setText(self.machine_code)
        self.machine_code_output.setTextInteractionFlags(self.machine_code_output.textInteractionFlags() | 0x08000000)  # 允许全选复制
        self.machine_code_output.setFixedHeight(50)  # 适当设置高度

        # 复制按钮
        self.copy_button = QPushButton("复制机器码")
        self.copy_button.clicked.connect(self.copy_machine_code)

        # 卡密输入框（调整为非密码框，扩大尺寸）
        self.activation_code_input = QTextEdit()
        self.activation_code_input.setPlaceholderText("请输入卡密")

        # 验证按钮
        self.verify_button = QPushButton("验证卡密")
        self.verify_button.clicked.connect(self.verify_activation_code)

        # 布局
        layout.addWidget(self.machine_code_label)
        layout.addWidget(self.machine_code_output)
        layout.addWidget(self.copy_button)
        layout.addWidget(self.activation_code_input)
        layout.addWidget(self.verify_button)

        self.setLayout(layout)

    def copy_machine_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.machine_code)

    def verify_activation_code(self):
        input_code = self.activation_code_input.toPlainText().strip()

        # 解密卡密并验证
        try:
            decrypted_code = aes_gcm_decrypt(input_code)
            machine_code_from_code = decrypted_code.split("|")[0]
            if machine_code_from_code == get_machine_code():
                print("卡密验证成功，进入主窗口！")
                self.save_activation_code(input_code)
                self.accept_activation()
            else:
                print("卡密无效！")
                QMessageBox.warning(self, "警告", "卡密无效！")
        except Exception as e:
            print("未找到激活文件或解密失败！")
            QMessageBox.warning(self, "警告", "卡密无效！")

    def save_activation_code(self, code): 
        with open("key", "w") as file:
            file.write(code)
        print("卡密已保存到 key 文件！")

    def accept_activation(self):
        self.close()
        create_gui()

def authMain():
    app = QApplication(sys.argv)

    # 检查是否存在有效的激活文件
    try:
        with open("key", "r") as file:
            encrypted_code = file.read().strip()
            decrypted_code = aes_gcm_decrypt(encrypted_code)

            # 提取机器码并进行比对
            machine_code_from_code = decrypted_code.split("|")[0]
            if machine_code_from_code == get_machine_code():
                print("激活验证成功")
                create_gui()
                sys.exit(app.exec_())
            else:
                verification_window = VerificationWindow()
                verification_window.show()
    except (FileNotFoundError, ValueError):
        # 激活失败时显示验证窗口
        print("未找到有效的激活文件或卡密无效")
        verification_window = VerificationWindow()
        verification_window.show()

    sys.exit(app.exec_())