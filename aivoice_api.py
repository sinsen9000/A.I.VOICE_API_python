import os
import signal
import clr
import time
import json
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
clr.AddReference("./AI.Talk.Editor.Api") #pythonnet DLLの読み込み
from AI.Talk.Editor.Api import TtsControl, HostStatus #エラーは吐くが無視
tts_control = TtsControl()
app = FastAPI()
voicename = []

class sys_stop(Exception): #通常終了時（処理統一化のためエラー処理化）
    pass

class VoiceArgs(BaseModel):
    target_text: str
    name: str
    full_path: str
    volume: float
    speed: float
    pitch: float
    intonation: float
    angry: float
    pleasure: float
    sad: float

def set_preset(args):
    preset_param = json.loads(tts_control.GetVoicePreset(args.name))
    preset_param["Volume"] = args.volume
    preset_param["Speed"] = args.speed
    preset_param["Pitch"] = args.pitch
    preset_param["PitchRange"] = args.intonation
    if "Styles" in preset_param:
        preset_param["Styles"][0]["Value"] = args.pleasure
        preset_param["Styles"][1]["Value"] = args.angry
        preset_param["Styles"][2]["Value"] = args.sad
    tts_control.SetVoicePreset(str(preset_param).replace("\'","\"")) #「'」を「"」に合わせて、プリセット情報を保存
    tts_control.CurrentVoicePresetName = args.name #設定したプリセット情報をセット

@app.post("/aivoice/play")
def play(args: VoiceArgs):
    tts_control.Text = args.target_text #テキストを設定
    set_preset(args)
    play_time = tts_control.GetPlayTime()
    tts_control.Play() #再生
    time.sleep((play_time + 500) / 1000) #再生時間+α分sleepで待つ
    return "done."

@app.post("/aivoice/save")
def save(args: VoiceArgs):
    tts_control.Text = args.target_text #テキストを設定
    set_preset(args)
    tts_control.SaveAudioToFile(args.full_path)
    return "done."

@app.get("/aivoice/PresetList")
def get_preset():
    return [i for i in tts_control.VoicePresetNames]

@app.get("/aivoice/shutdown")
def disconnect():
    tts_control.Disconnect()
    tts_control.TerminateHost()
    os.kill(os.getpid(), signal.SIGTERM)
    return "done."

if __name__ == '__main__':
    if not os.path.isfile('AI.Talk.Editor.Api.dll'):
        print("A.I.VOICE Editor (v1.3.0以降) がインストールされていません。")
        raise sys_stop

    host_name = tts_control.GetAvailableHostNames()[0]
    tts_control.Initialize(host_name) #A.I.VOICE Editor APIの初期化
    if tts_control.Status == HostStatus.NotRunning:
        tts_control.StartHost() #A.I.VOICE Editorの起動
    tts_control.Connect() #A.I.VOICE Editorへ接続
    host_version = tts_control.Version
    print(f"{host_name} (v{host_version}) へ接続しました。")
    voicename = [i for i in tts_control.VoicePresetNames]

    uvicorn.run(app=app, host="0.0.0.0", port=1234) #API起動
