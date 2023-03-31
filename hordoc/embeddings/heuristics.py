import sqlite_utils
from sqlite_utils import Database
# Connect to the database file
db : Database = sqlite_utils.Database('../../data/horde_help.db')
print(db.table_names())


def get_messages_with_thanks_and_reply (db: Database):
	excluded_users = ('db0','Airic')
	query = f"""
	select chan_id, msg_id, uid, t, user, msg, r, te, re
	from horde_help
	where "msg" like "%thanks%"
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
	return db.execute_returning_dicts(query)[0]

def get_messages_by_time_delta (db: Database, start_time, delta):
	query = f"""
	select chan_id, msg_id, uid, t, user, msg, r, te, re
	from horde_help
	where t <= {start_time}
	and t > {start_time - delta}
	order by msg_id"""
	return db.execute_returning_dicts(query)

def get_messages_by_time_delta_and_uid (db: Database, start_time, delta, uid):
	query = f"""
	select chan_id, msg_id, uid, t, user, msg, r, te, re
	from horde_help
	where t <= {start_time}
	and t > {start_time - delta}
	and uid = {uid}
	order by msg_id"""
	return db.execute_returning_dicts(query)

