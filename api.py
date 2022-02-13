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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

def convertTextToSpeech(text):

    # Create a client using the credentials and region defined in the [adminuser]
    # section of the AWS credentials file (~/.aws/credentials).
    session = Session(profile_name="adminuser")
    polly = session.client("polly")

    try:
    # Request speech synthesis
        response = polly.synthesize_speech(Text=text, OutputFormat="mp3",
                                            VoiceId="Joanna")
        print(response)
        print("Inside Try")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = os.path.join("/home/ubuntu", "speech.wav")
                

            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
                    #return 200
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                #return 400
                sys.exit(-1)


@app.get('/')
async def root():
    return {'hello': 'world'}


@app.get('/textToSpeech')
async def textToSpeech(text: str):
    #print(convertTextToSpeech(text))
    if convertTextToSpeech(text) == 200 :
        return FileResponse('/home/ubuntu/speech.wav', media_type="audio/wav")
    else : return 400
