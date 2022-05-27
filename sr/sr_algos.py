from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource 
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import speech_recognition as sr
from pprint import pprint
import speech_recognition as sr
from os import path
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment

# method to pretty print dictionary
import json
def pprint(d1):
    if type(d1) == dict:
        print(json.dumps(d1, sort_keys=False, indent=4))
    else:
        print(json.dumps(dict(d1), sort_keys=False, indent=4))

def google(audio_trait_file):
    r = sr.Recognizer()
    harvard = sr.AudioFile(audio_trait_file)
    with harvard as source:
        audio = r.record(source)
    results = r.recognize_google(audio, show_all=True)
    text = results["alternative"][0]['transcript']
    confidence = results["alternative"][0]['confidence']
    return text, confidence

def ibm(audio_trait_file):
    apikey = 'jXJZ0DFtm0iLg-XinOxqIRgbHlT-376eS3TfNPlFq37i'
    url = 'https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/cabe9e09-1272-475f-a3e1-77c4c50ce8d2'
    authenticator = IAMAuthenticator(apikey)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(url)
    
    sound = AudioSegment.from_file(audio_trait_file)
    sound.export("tmp.mp3", format="mp3")
    
    with open("tmp.mp3", 'rb') as f:
        res = stt.recognize(audio=f, content_type='audio/mp3', model='en-US_NarrowbandModel').get_result()
    text = res['results'][0]['alternatives'][0]['transcript']
    confidence = res['results'][0]['alternatives'][0]['confidence']
    return text, confidence

def wit(audio_trait_file):
    AUDIO_FILE = path.join(audio_trait_file)
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
    WIT_AI_KEY = "A26KM7ZXBWPFETJQDSPN4YQFCYH62J2W"
    try:
        results = r.recognize_wit(audio, key=WIT_AI_KEY, show_all=True)
        text = results["_text"]
    except sr.UnknownValueError:
        print("Wit.ai could not understand audio")
        return 
    except sr.RequestError as e:
        print("Could not request results from Wit.ai service; {0}".format(e))
        return
    except KeyError:
        try:
            results = r.recognize_wit(audio, key=WIT_AI_KEY, show_all=True)
            text = results["text"]
        except KeyError:
            print("No prediction found.")
            return None, None
    return text, 1
    

def houndify(audio_trait_file):
    harvard = sr.AudioFile(audio_trait_file)
    r = sr.Recognizer()
    with harvard as source:
        audio = r.record(source)
    HOUNDIFY_CLIENT_ID = "iOuUT9lsQAI3nO8E7_vx8g=="
    HOUNDIFY_CLIENT_KEY = "VMxp_FhmxtLNyTVqA4_eZspCUR4BwMzwu99VW96Sn3PNQW1T_NkYeiETqW6z4OuwMq8k5X03B21-B6y0TsLJuQ=="
    try:
        results = r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY, show_all=True)
        text = results["Disambiguation"]["ChoiceData"][0]["Transcription"]
        confidence = results["Disambiguation"]["ChoiceData"][0]["ConfidenceScore"]
    except sr.UnknownValueError:
        print("Houndify could not understand audio")
        return 
    except sr.RequestError as e:
        print("Could not request results from Houndify service; {0}".format(e))
        return 
    return text, confidence