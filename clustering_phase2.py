import pandas as pd
import numpy as np
from tqdm import tqdm
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from datetime import datetime
from sklearn.cluster import KMeans
from joblib import dump

es = Elasticsearch([{u'host': u'127.0.0.1', u'port': b'9200'}])
myIndex = "ehd"

starting_time = datetime.now()
for cluster_id in tqdm(range(20)):
    results = scan(es, index=myIndex, preserve_order=True,
                   query={'query': {'match': {'cluster': cluster_id}}})
    vectors = []
    for item in tqdm(results):
        v = np.array(item["_source"]["vector"])
        v[80:85] *= 5
        element = [int(item["_source"]["id"])]
        element.extend(v)
        vectors.append(element)
    df = pd.DataFrame(vectors)
    df.set_index(0, inplace=True)
    kms = KMeans(n_clusters=10).fit(df)
    dump(kms, 'static/cluster_models/' + str(cluster_id) + '.joblib')

finish_time = datetime.now()
print(finish_time - starting_time)