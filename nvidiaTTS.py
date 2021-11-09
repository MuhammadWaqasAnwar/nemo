import io
import json
import librosa
import ffmpeg
import requests
import numpy as np
import uvicorn
import asyncio
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import soundfile as sf
import nemo
import nemo.collections.asr as nemo_asr

# simply use ASRModel to instantiate any ASR pretrained model
quartznet = nemo_asr.models.ASRModel.from_pretrained(model_name="QuartzNet15x5Base-En")

# initializing the FastAPI object
app = FastAPI()

# Allowing the cors
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def speech_to_text(filePath):
    text = quartznet.transcribe(paths2audio_files=[filePath])
    return text


async def convertFormat():
    out, _ = (ffmpeg
    .input("audioFile.mp3")
    .output("audio_file.wav", acodec='pcm_s16le', ac=1, ar='16k')
    .overwrite_output()
    .run(capture_stdout=True)
    )
    data = np.frombuffer(out,dtype=np.int16)
    return data

@app.get("/")
def index():
    print("*"*1000, "DefaultRoute")
    return Response("Hello, nemo",status_code = 200)

@app.post("/file_to_transcribe")
async def result(request:Request):
    try:
        form = await request.form()
        if request.method=='POST':
            print("Request Recieved...")
            fileType = form['audioFile'].filename
            if fileType[-3:] == 'mp3' or fileType[-3:] =='m4a' or fileType[-3:] =='wma':
                with open("audioFile.mp3","wb") as f:
                    file = await form['audioFile'].read()
                    f.write(file)
                data = await convertFormat()
                data,_ = sf.read("audio_file.wav")
            elif fileType[-3:] == 'wav' :
                file = await form['audioFile'].read()
                data, samplerate = librosa.load(io.BytesIO(file), sr=16000, mono=True)
                sf.write("audio_file.wav",data,samplerate)
            else:
                raise Exception("File Type Not Supported!")
            text = speech_to_text("audio_file.wav")
        return jsonable_encoder({'result':text})
    except Exception as e:
        print(str(e))
        return {
            'output': '',
            'error': str(e)
        }
