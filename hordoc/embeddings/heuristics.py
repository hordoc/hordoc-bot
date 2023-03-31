from math import floor
import sqlite_utils
from sqlite_utils import Database
from sentence_transformers import SentenceTransformer, util

from hordoc.embeddings.embeddings_search import find_most_similar, get_embeddings
# Connect to the database file
db : Database = sqlite_utils.Database('../../data/horde_help.db')

def print_and_buffer(txt, buffer):
	print(txt)
	return buffer + txt + '\n'

guild_id = 781145214752129095
time_delta_milliseconds = 1000 * 60 * 60 # 1 hour
score_threshold = 0.5
def get_messages_with_thanks_and_reply (db: Database):
	excluded_users = ('db0','Airic')
	query = f"""
	select chan_id, msg_id, uid, t, user, msg, r
	from horde_help
	where "msg" like "%thank%"
	and ("r" is not null and "r" != "")
	and "user" not in  {str(excluded_users)}
	order by msg_id"""
	return db.execute_returning_dicts(query)

def get_message_by_id (db: Database, msg_id):
	query = f"""
	select chan_id, msg_id, uid, t, user, msg, r, te, re
	from horde_help
	where msg_id = {msg_id}
	order by msg_id"""
	result= db.execute_returning_dicts(query)
	if(len(result) == 0):
		return None
	return result[0]

def get_messages_by_time_delta (db: Database, start_time, delta, channel_id):
	query = f"""
	select chan_id, msg_id, uid, t, user, msg, r, te, re
	from horde_help
	where t <= {start_time}
	and t > {start_time - delta}
	order by msg_id"""
	return db.execute_returning_dicts(query)

def get_messages_by_time_delta_and_uid (db: Database, start_time, delta, uid, channel_id):
	query = f"""
	select chan_id, msg_id, uid, t, user, msg
	from horde_help
	where t < {start_time}
	and t >= {start_time - delta}
	and uid = {uid}
	and chan_id = {channel_id}
	and msg like '%?%'
	order by msg_id"""
	return db.execute_returning_dicts(query)


if __name__ == '__main__' :
	messages = get_messages_with_thanks_and_reply(db)
	txt = ''
	for message in messages:
		reply = get_message_by_id(db, message['r'])
		if reply is None:
			continue
		if(reply['uid'] == message['uid']):
			continue
		asker_messages = get_messages_by_time_delta_and_uid(db, int(message['t']), time_delta_milliseconds, message['uid'], message['chan_id'])
		if(len(asker_messages) == 0):
			continue
		reply_embeddings = get_embeddings([reply['msg']])[0]
		askers_messages_text = [m['msg'] for m in asker_messages]
		askers_messages_embeddings = get_embeddings(askers_messages_text)
		most_similars =  util.semantic_search(reply_embeddings, askers_messages_embeddings, 5)[0]
		most_similars = list(filter(lambda m: m['score'] > score_threshold, most_similars))
		if(len(most_similars) == 0):
			continue
		most_similar_messages = [{'msg' : asker_messages[m['corpus_id']] , 'score' : floor( m['score'] * 100)}  for m in most_similars]
		txt = print_and_buffer(f"LINK  : https://discord.com/channels/{guild_id}/{message['chan_id']}/{message['msg_id']}",txt)
		for m in most_similar_messages:
			txt = print_and_buffer(f"Q?{m['score']:3d}%  {m['msg']['msg']}",txt)
		txt = print_and_buffer( 'REPLY : ' + reply['msg'],txt)
		txt = print_and_buffer( 'THANKS: ' + message['msg'],txt)
		txt = print_and_buffer('-----------------',txt)
		#print(asker_messages)
	with open('output.txt', 'w+',  encoding="utf-8") as f:
		f.write(txt)
