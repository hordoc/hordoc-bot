import datetime
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/gtr-t5-large")

import httpx

def get_blogmarks():
    url = "https://datasette.simonwillison.net/simonwillisonblog/blog_blogmark.json?_size=max&_shape=objects"
    while url:
        data = httpx.get(url, timeout=10).json()
        yield from data["rows"]
        url = data.get("next_url")
        print(url)

blogmarks = list(get_blogmarks())
ids = [bm["id"] for bm in blogmarks]
from torch.hub import _get_torch_home
_get_torch_home()

texts = [
    bm["link_title"] + " " + bm["commentary"]
    for bm in blogmarks
]
print([text for text in texts[:10]])
print(datetime.datetime.now().isoformat())
embeddings = model.encode(texts[0])
print(datetime.datetime.now().isoformat())


