import json

class _ManagerClients ( object ):
	def __init__ ( self ):
		self.file = "clientsV1.json"

	def load ( self ):
		try:
			with open ( self.file, "r", encoding = "utf-8" ) as clientsV1_file:
				content = json.loads ( clientsV1_file.read ().strip () )
			return content
		except FileNotFoundError:
			with open ( self.file, "w", encoding = "utf-8" ) as clientsV1_file:
				clientsV1_file.write("{}")
			return self.load()

	def save ( self, content ):
		with open ( self.file, "w", encoding = "utf-8" ) as clientsV1_file:
			clientsV1_file.write ( json.dumps ( content ) )

	def createClient ( self, chat_id, whats_name_message_id ):
		clients = self.load ()
		clients.update ( { str ( chat_id ): { "whats_name_message_id" : whats_name_message_id } } )
		self.save ( clients )

	def existClient ( self, chat_id ):
		clients = self.load ()
		return str ( chat_id ) in clients

	def existNameClient ( self, chat_id ):
		clients = self.load ()
		return "name" in clients [ str ( chat_id ) ]

	def setNameClient ( self, chat_id, name ):
		clients = self.load ()
		clients [ str ( chat_id ) ][ "name" ] = name
		self.save ( clients )

	def getClient ( self, chat_id ):
		clients = self.load ()
		return clients [ str ( chat_id ) ]

ManagerClients = _ManagerClients ()
