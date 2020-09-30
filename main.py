import os
import asyncio
import telepot
import speech_recognition as sr
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from manager_clients import ManagerClients
from manager_audio import saveVoiceClient, tts, stt

FILE_TERMO_SERVICO = "termo_servico.txt"
FILE_TOKEN_BOT = "token_bot.txt"

with open ( FILE_TOKEN_BOT, "r", encoding = "utf-8" ) as token_file:
	bot = telepot.aio.Bot ( token_file.read ().strip () )
answerer = telepot.helper.Answerer ( bot )

async def on_chat_message ( data ):
	content_type, chat_type, chat_id = telepot.glance ( data )

	if content_type == "text":
		if not ManagerClients.existClient ( chat_id ):
			await bot.sendMessage ( chat_id, "Seja bem-vindo(a)." )
			inline_keyboard = InlineKeyboardMarkup  ( inline_keyboard = [ [
				InlineKeyboardButton ( text = "Aceito", callback_data = "TermoServicoAceito" ),
				InlineKeyboardButton ( text = "Não", callback_data = "TermoServicoNaoAceito" )
			] ] )
			with open ( FILE_TERMO_SERVICO, "r", encoding = "utf-8" ) as termo_servico_file:
				await bot.sendMessage ( chat_id, termo_servico_file.read(), reply_markup = inline_keyboard )

		elif not ManagerClients.existNameClient ( chat_id ):
			ManagerClients.setNameClient ( chat_id, data[ "text" ] )
			await bot.deleteMessage ( ( chat_id, ManagerClients.getClient ( chat_id ) [ "whats_name_message_id" ] ) )
			await bot.sendMessage (
				chat_id,
				f"Certo, {data[ 'text' ]}, agora você pode:\n - Enviar uma audio utilizando o microfone que transcreverei para texto.\n - Enviar um texto que transformarei em áudio.",
				reply_markup = ReplyKeyboardRemove ()
			)
		else:
			editable = await bot.sendMessage ( chat_id, "Aguarde um momento...", reply_to_message_id = data [ "message_id" ] )
			editable = telepot.message_identifier ( editable )
			await bot.editMessageText ( editable, "Processando..." )
			try:
				file = await tts ( data [ "text" ], chat_id, data [ "message_id" ] )
				await bot.editMessageText ( editable, "Finalizado." )
				await bot.deleteMessage ( editable )
				await bot.sendAudio ( chat_id, ( data[ "text" ], open ( file, "rb" ) ), reply_to_message_id = data [ "message_id" ] )
				os.remove ( file )
			except AssertionError:
				await bot.editMessageText ( editable, "Nenhum texto identificado." )
			except:
				await bot.editMessageText ( editable, "Ocorreu um erro ao tentar transformar em áudio." )
	elif content_type in [ "voice", "audio" ] and ManagerClients.existClient ( chat_id ):
		editable = await bot.sendMessage ( chat_id, "Aguarde um momento...", reply_to_message_id = data [ "message_id" ] )
		file = await saveVoiceClient ( bot, chat_id, data[ content_type ][ "file_id" ] )
		editable = telepot.message_identifier ( editable )
		await bot.editMessageText ( editable, "Processando..." )
		if file == False:
			await bot.sendMessage ( chat_id, "Ocorreu um erro ao tentar entender o áudio." )
		else:
			text_result = await stt ( file )
			await bot.editMessageText ( editable, "Finalizado." )
			if text_result == sr.UnknownValueError:
				await bot.editMessageText ( editable, "Não foi possível entender o áudio." )
			elif text_result == sr.RequestError:
				await bot.editMessageText ( editable, "Não foi possível solicitar resultados do serviço de reconhecimento de fala no momento." )
			elif text_result == False:
				await bot.editMessageText ( editable, "Ocorreu um erro ao tentar entender o áudio." )
			else:
				await bot.editMessageText ( editable, text_result )
			os.remove ( file )
	else:
		await bot.sendMessage ( chat_id, "Não tenho suporte a este formato de informação!", reply_to_message_id = data [ "message_id" ] )


async def on_callback_query ( data ):
	query_id, from_id, query_data = telepot.glance ( data, flavor = "callback_query" )

	if not ManagerClients.existClient ( from_id ):
		if query_data in [ "TermoServicoAceito", "TermoServicoNaoAceito" ]:
			if query_data == "TermoServicoAceito":
				await bot.answerCallbackQuery ( query_id, text = "Aguarde um momento..." )
				edited = telepot.message_identifier ( data [ "message" ] )
				await bot.editMessageText ( edited, "Você aceitou o termo de serviço." )

				firstname_inline = KeyboardButton ( text = data[ "from" ][ "first_name" ] ) if "first_name" in data[ "from" ] else None
				username_inline = KeyboardButton ( text = data[ "from" ][ "username" ] ) if "username" in data[ "from" ] else None
				keyboard = []
				if firstname_inline: keyboard.append ( [ firstname_inline ] )
				if username_inline: keyboard.append ( [ username_inline ] )

				keyboard = ReplyKeyboardMarkup ( keyboard = keyboard, resize_keyboard = True )
				whats_name = await bot.sendMessage ( from_id, "Como gostaria de si chamar?\nEscolha uma das opções abaixo ou digite outra.", reply_markup = keyboard )
				ManagerClients.createClient ( from_id, whats_name [ "message_id" ] )
			else:
				edited = telepot.message_identifier ( data [ "message" ] )
				await bot.editMessageText ( edited, "Você não aceitou o termo de serviço." )

if __name__ == '__main__':
	loop = asyncio.get_event_loop ()
	loop.create_task ( MessageLoop (
		bot, {
			"chat": on_chat_message,
			"callback_query": on_callback_query
		}
	).run_forever () )

	print ( "Serviço Iniciado." )
	try:
		loop.run_forever ()
	except KeyboardInterrupt:
		print ( "Serviço Desligado." )
		exit ( 0 )
