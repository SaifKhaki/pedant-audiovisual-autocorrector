from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import subprocess
import os
import wave
import srt
import datetime
import json

SetLogLevel(-1)

class sr_model():
    def __init__(self, filename) -> None:
        self.filename = filename
        self.model_address = "/home/saifbinkhaki/Documents/FYP/flask_app/venv/sr_kaldi/model"
        if not os.path.exists(self.model_address):
            print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit (1)
            
        self.wf = wave.open(self.filename, "rb")
        if self.wf.getnchannels() != 1 or self.wf.getsampwidth() != 2 or self.wf.getcomptype() != "NONE":
            print ("Audio file must be WAV format mono PCM.")
            exit (1)
            
        self.sample_rate = self.wf.getframerate()

        self.model = Model(self.model_address)
        self.rec = KaldiRecognizer(self.model, self.sample_rate)
        self.rec.SetMaxAlternatives(10)
        self.rec.SetWords(True)
        
        # test model
        self.res = json.loads(self.rec.FinalResult())

    # get var_conf
    def get_var_conf(self):
        SetLogLevel(0)
        var_lines = []
        while True:
            data = self.wf.readframes(4000)
            if self.rec.AcceptWaveform(data):
                var_lines.append(json.loads(self.rec.Result())['alternatives'])
                
            if len(data) == 0:
                var_lines.append(json.loads(self.rec.FinalResult())['alternatives'])
                break
        return var_lines

    # get conf, end, start, word
    def get_conf_end_start_word(self):
        text = ""
        conf_lines = []

        rec = KaldiRecognizer(self.model, 16000)
        wf = wave.open(self.filename, "rb")

        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(True)
        while True:
            data = wf.readframes(4000)
            if rec.AcceptWaveform(data):
                # print(rec.Result())
                result = json.loads(rec.Result())
                for i in result['result']:
                    conf_lines.append(i)
                text += result["text"] + " "
            
            if len(data) == 0:
                result = json.loads(rec.FinalResult())
                for i in result['result']:
                    conf_lines.append(i)
                text += result["text"] + " "
                break
        
        return text.strip(), conf_lines

