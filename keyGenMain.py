import sys
import time
import base64
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

# 固定加密密钥
SECRET_KEY = "zWVc0rKwENUyCVX8"  # 你可以修改为你自己的密钥

# AES加密函数（使用GCM模式）
def aes_gcm_encrypt(password, message):
    # 使用PBKDF2派生密钥 (32字节，即AES-256)
    key = PBKDF2(password.encode(), b'salt', dkLen=32, count=1000000)
    
    # 生成随机IV (12字节)
    iv = get_random_bytes(12)
    
    # 创建AES GCM加密器
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    
    # 对消息进行加密
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    
    # 返回IV, 密文和认证标签（Base64编码）
    encrypted_message = base64.b64encode(iv + ciphertext + tag).decode()
    
    return encrypted_message

class EncryptWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AES GCM 加密")
        self.setGeometry(100, 100, 400, 300)

        # 布局
        layout = QVBoxLayout()

        # 机器码输入框
        self.machine_code_input = QLineEdit(self)
        self.machine_code_input.setPlaceholderText("请输入机器码")
        self.machine_code_input.setFixedHeight(30)
        layout.addWidget(self.machine_code_input)

        # 按钮 - 用于生成加密卡密
        self.generate_button = QPushButton("生成加密卡密", self)
        self.generate_button.clicked.connect(self.generate_encrypted_code)
        layout.addWidget(self.generate_button)

        # 可全选复制的文本框 - 显示加密后的卡密
        self.encrypted_code_output = QTextEdit(self)
        self.encrypted_code_output.setReadOnly(True)
        self.encrypted_code_output.setTextInteractionFlags(self.encrypted_code_output.textInteractionFlags() | 0x08000000)  # 允许全选复制
        layout.addWidget(self.encrypted_code_output)

        # 复制按钮
        self.copy_button = QPushButton("复制加密卡密", self)
        self.copy_button.clicked.connect(self.copy_encrypted_code)
        layout.addWidget(self.copy_button)

        self.setLayout(layout)

    def generate_encrypted_code(self):
        # 获取机器码
        machine_code = self.machine_code_input.text()

        if machine_code:
            # 获取当前时间戳
            timestamp = str(int(time.time()))
            message = f"{machine_code}|{timestamp}"
            encrypted_code = aes_gcm_encrypt(SECRET_KEY, message)
            self.encrypted_code_output.setText(encrypted_code)
        else:
            self.encrypted_code_output.setText("请输入有效的机器码")

    def copy_encrypted_code(self):
        # 获取加密后的卡密并复制到剪贴板
        encrypted_code = self.encrypted_code_output.toPlainText()
        if encrypted_code:
            clipboard = QApplication.clipboard()
            clipboard.setText(encrypted_code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EncryptWindow()
    window.show()
    sys.exit(app.exec_())
