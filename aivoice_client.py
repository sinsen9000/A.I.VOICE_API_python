import requests
import json
from datetime import datetime
import os

def AIVOICE_voice(v_name:str, sentence:str, filepath:str, interval="100", speed="100", intonation="100", volume="100", param={"activation": False}):
    wav_file = f"{filepath}.wav"
    if int(interval) > 200: interval = "200"
    elif int(interval) < 50: interval = "50"
    if int(speed) > 400 : speed = "400"
    elif int(speed) < 50: speed = "50"
    AIVOICE_name = v_name

    # 発声処理
    send_param = {
        "target_text":sentence,
        "name":AIVOICE_name,
        "full_path":wav_file,
        "volume":int(volume)/100,
        "speed":int(speed)/100,
        "pitch":int(interval)/100,
        "intonation":int(intonation)/100,
        "angry":0,
        "pleasure":0,
        "sad":0
    }
    if param["activation"]:
        if param["emo"] == "yorokobi":
            send_param.pleasure = param["value"]
        elif param["emo"] == "ikari":
            send_param.pleasure = param["value"]
        elif param["emo"] == "aware":
            send_param.pleasure = param["value"]
    url = "http://127.0.0.1:1234/aivoice/save"
    result=requests.post(url, json.dumps(send_param))
    _ = result.text

file_name = "%s" %(datetime.now().strftime("%d%H%M%S"))
file_path = f"{os.getcwd()}\wav\{file_name}" #ファイル形式を除いたファイルパス
preset_param = {"activation": True,"emo": "yorokobi","value":0.5} #プリセット内の感情値を調整する用。emoが調整する感情で、valueが値（0~1の範囲内）
AIVOICE_voice("紲星 あかり","これはテストです。",file_path,param=preset_param)
