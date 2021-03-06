from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
import uvicorn
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
import aiofiles
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="adminuser")
polly = session.client("polly")


def convertTextToSpeech(text):   
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Joanna",
        )
    except (BotoCoreError, ClientError) as error:
        print(error)
        sys.exit(-1)

    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = "speech.wav"
            try:
                with open(output, "wb") as file:
                    file.write(stream.read())
                    return 200
            except IOError as error:
                print(error)
                sys.exit(-1)
                return 400
    else:
        print("Could not stream audio")
        sys.exit(-1)


@app.get('/')
async def root():
    return {'hello': 'world'}


@app.get('/textToSpeech')
async def textToSpeech(text: str):
    #print(convertTextToSpeech(text))
    if convertTextToSpeech(text) == 200 :
        return FileResponse('speech.wav', media_type="audio/wav")
    else : return 400

@app.post('/wav2lip')
async def wav2lip(file: UploadFile):
    async with aiofiles.open("video.mp4", 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    subprocess.run(["python", "/home/ubuntu/Wav2Lip/inference.py", "--checkpoint_path", "/home/ubuntu/Wav2Lip/checkpoints/wav2lip_gan.pth", "--face", "/home/ubuntu/wav2lip_backend/video.mp4", "--audio",  "/home/ubuntu/wav2lip_backend/speech.wav"])
    #print("The exit code was: %d" % list_files.returncode)  
    #python inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face "video.mp4" --audio "/content/sample_data/input_audio.wav"

    return FileResponse('/home/ubuntu/Wav2Lip/results/result_voice.mp4', media_type="video/mp4")
    #return {"filename": file.filename}
