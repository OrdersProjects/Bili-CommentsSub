import sys
import base64
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton
from PyQt5.QtGui import QClipboard
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from utils.deviceGen import get_machine_code

# 固定加密密钥
SECRET_KEY = "zWVc0rKwENUyCVX8"  # 与加密时使用的密钥一致

# AES解密函数（使用GCM模式）
def aes_gcm_decrypt(encrypted_message):
    # 使用PBKDF2派生密钥 (32字节，即AES-256)
    key = PBKDF2(SECRET_KEY.encode(), b'salt', dkLen=32, count=1000000)
    
    # 解码Base64加密消息
    encrypted_data = base64.b64decode(encrypted_message)
    
    # 提取IV、密文和认证标签
    iv = encrypted_data[:12]  # IV 长度为 12 字节
    ciphertext = encrypted_data[12:-16]  # 密文
    tag = encrypted_data[-16:]  # 认证标签，16字节
    
    # 创建AES GCM解密器
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    
    try:
        # 解密并验证认证标签
        decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_message.decode()  # 返回解密后的消息
    except ValueError:
        return "解密失败，数据可能已被篡改"
    