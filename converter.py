from os import path
from pydub import AudioSegment

# files                                                                         
src = "speech/huda.mp3"
dst = "speech/huda.wav"

# convert wav to mp3                                                            
sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")