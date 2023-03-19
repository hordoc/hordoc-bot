import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
guilds_ids = []
forums_ids = []

@client.event
async def on_ready():
	print(f'We have logged in as {client.user}')
	guilds = [guild for guild in client.guilds if guild.id in guilds_ids]
	for guild in guilds:
		forums = [channel for channel in guild.forums if channel.id in forums_ids]
		for forum in forums:
			threads = forum.threads
			for thread in threads:
				thread_name = thread.name
				first_message = await thread.fetch_message(0)
				other_messages = [await thread.fetch_message(i) for i in range(1, thread.message_count)]
				other_users_messages = [message for message in other_messages if message.author.id != client.user.id and message.author.id != first_message.author.id]
				author_messages = [message for message in other_messages if message.author.id == first_message.author.id]
				print(f'Thread name: {thread_name}')
				print(f'First message: {first_message.content}')
				print(f'Other users messages: {[message.content for message in other_users_messages]}')
				print(f'Author messages: {[message.content for message in author_messages]}')

@client.event
async def on_message(message):
	pass