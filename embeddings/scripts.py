
import json

import torch
from embeddings_search import get_embeddings, rephrase_question
from sentence_transformers import util
import requests
import json

def find_closest_question(question, rows, threshold=0.8) :
	with open('./embeddings.json') as f :
		question = 'I have kudos but cant generate the image'
		question_embedding = get_embeddings(question)
		contents= json.loads(f.read())
		embeddings = [torch.tensor(c['embeddings']) for c in contents]

		closest_n = util.semantic_search(question_embedding, embeddings, top_k=5)
		print(closest_n[0])

		best_score = closest_n[0][0]['score']
		ids = [c['corpus_id'] for c in closest_n[0]]
		db_ids = [contents[i]['id'] for i in ids]
		questions = [row for row in rows if row[0] in db_ids]
		if best_score < threshold :
			print('threshold not met : ', best_score)
		print(questions)


def rephrase_from_db(rows, save_to_file=False) :
	rephrased = [{'id' : row[0] ,'rephrased' : rephrase_question(row[2],row[3])} for row in rows]
	if save_to_file :
		with open('rephrased.json', 'w+') as f :
			json.dump(rephrased, f)
	return rephrased

if __name__ == "__main__" :
	url = 'https://horde-qna-db.spevktator.io/horde_support.json?sql=select+threads.id%2C+datetime%28round%28messages.created_at+%2F+1000%29%2C+%27unixepoch%27%29+as+timestamp%2C+threads.name%2C+content+from+threads+join+messages+on+threads.id+%3D+messages.id+order+by+timestamp+desc'
	data = requests.get(url).json()
	rows = data['rows']

channel_id = '1021208495414071307'
url = 'https://horde-qna-db.spevktator.io/horde_support.json?sql=select+id%2C+content+from+messages+where+%22channel_id%22+%3D+%3Ap0+order+by+id+desc+limit+101&p0=1021208495414071307'
data = requests.get(url).json()
messages = [d[1] for d in data['rows']]
#print(messages[0])
question = 'What is the recommended method for joining the horde and contributing to the parallelization of GPU processing for the benefit of others?'
question_embedding = get_embeddings(question)
embeddings = get_embeddings(messages)
closest_n = util.semantic_search(question_embedding, embeddings, top_k=10)
#print(closest_n)
ids = [c['corpus_id'] for c in closest_n[0]]
closest_n_text = [messages[i] for i in ids]
for i in closest_n_text :
	print(i)
	print('---------------------')