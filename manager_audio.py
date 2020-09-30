import os
import subprocess
import speech_recognition as sr
from gtts import gTTS

r = sr.Recognizer()

async def stt ( file ):
	with sr.AudioFile ( file ) as source:
		r.adjust_for_ambient_noise ( source )
		audio = r.record ( source )

	try:
		recognized_text = r.recognize_google ( audio, language = "pt" )
		return recognized_text

	except sr.UnknownValueError:
		return sr.UnknownValueError # "Google Speech Recognition could not understand audio"

	except sr.RequestError as e:
		return sr.RequestError # ("Could not request results from Google Speech Recognition service; {0}".format(e)) 

	except:
		return False

async def tts ( text, chat_id, file_id ):
	if "vtts" not in os.listdir():
		os.mkdir ( "vtts" )
	file = "vtts/" + str ( chat_id ) + "." + str ( file_id ) + ".mp3"
	tts = gTTS ( text, lang = "pt" )
	tts.save ( file )
	return file

async def saveVoiceClient ( bot, chat_id, file_id ):
	if "vstt" not in os.listdir():
		os.mkdir ( "vstt" )
	file = "vstt/" + str ( chat_id ) + "." + str ( file_id ) + ".ogg"
	newfile = "vstt/" + str ( chat_id ) + "." + str ( file_id ) + ".wav"
	await bot.download_file ( file_id, file )

	try:
		check_ffmpeg = subprocess.run ( [ "ffmpeg", "--help" ], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL )
	except FileNotFoundError:
		print("[*] Error!!! ffmpeg não instalado.")
		return False

	try:
		process = subprocess.run ( [ "ffmpeg", "-i", file, newfile ], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL )
		if process.returncode != 0: return False
	except FileNotFoundError:
		return False
	except:
		print ( "[*] Error!!! in saveVoiceClient." )
		return False
	os.remove ( file )
	return newfile
