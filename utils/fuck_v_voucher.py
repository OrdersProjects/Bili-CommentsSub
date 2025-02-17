import requests
import json
import configparser
from managers.header_manager import get_header
from PyQt5.QtWidgets import (
    QTableWidgetItem, QMessageBox, QFileDialog
)
from managers.log_manager import LogManager
log_manager = LogManager()
def get_gaia_vtoken(v_voucher,bili_jct,referer):
    #读取config.ini文件的ttorcapikey
    config = configparser.ConfigParser()
    config.read("config.ini")
    ttorc_apikey = config.get("ttorc", "ttorcapikey")
    captcha = get_captha(v_voucher,bili_jct,referer)
    geetest = captcha["geetest"]
    token = captcha["token"]
    if geetest != 0:
        if geetest == "null":
            QMessageBox.warning(None, "警告", "无解风控")
            return
        else:
            QMessageBox.warning(None, "警告", "获取验证码错误")
            return
    else:
        gt = geetest["gt"]
        challenge = geetest["challenge"]
    #需要验证码
    QMessageBox.warning(None, "警告", "验证码错误")
    api = "http://api.ttocr.com/api/recognize"
    #请求API，Post
    data = f"gt={gt}&challenge={challenge}&appkey={ttorc_apikey}&itemid=33&referer={referer}"
    response = requests.post(api, data=data)
    response_json = json.loads(response.text)
    if response_json["code"] == 1:
        resultid = response_json["resultid"]
    else:
        log_manager.log("get_gaia_vtoken", response.text)
        QMessageBox.warning(None, "警告", "TTOCR验证码识别失败")
        return
    result = get_ttorc_result(resultid,ttorc_apikey)
    challenge = result["challenge"]
    validate = result["validate"]
    seccode = result["seccode"]
    #获取grisk_id
    api_grisk = "https://api.bilibili.com/x/gaia-vgate/v1/validate"
    data = {
       challenge: challenge,
       validate: validate,
       seccode: seccode,
       token: token 
    }
    response = requests.post(api_grisk, data=data,headers=get_header())
    response_json = json.loads(response.text)
    if response_json["code"] == 0:
        data = response_json["data"]
        grisk_id = data["grisk_id"]
        return grisk_id
    else:
        return response_json["code"]
    
#根据v_voucher获取captha
def get_captha(v_voucher,bili_jct):
    api = "https://api.bilibili.com/x/gaia-vgate/v1/register"
    data = {
        "csrf": bili_jct,
        "v_voucher": v_voucher
    }
    response = requests.post(api, data=data,headers=get_header())
    response_json = json.loads(response.text)
    if response_json["code"] == 0:
        data = response_json["data"]
        if data["geetest"] == "null":
            log_manager.log("get_captha", response.text)
            return "null"
        else:
            log_manager.log("get_captha", response.text)
            return data
    else:
        return response_json["code"]

#获取TTOCR验证结果
def get_ttorc_result(resultid,ttorc_apikey):
    api = f"http://api.ttocr.com/api/results"
    data = f"appkey={ttorc_apikey}&resultid={resultid}"
    response = requests.post(api, data=data)
    response_json = json.loads(response.text)
    if response_json["code"] != 1:
        log_manager.log("get_ttorc_result", response.text)
        QMessageBox.warning(None, "警告", "TTOCR验证码识别失败")
        return
    return response_json["data"]
