# import pandas as pd
import numpy as np
from tqdm import tqdm
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from datetime import datetime
# from sklearn.cluster import KMeans
from joblib import load


es = Elasticsearch([{u'host': u'127.0.0.1', u'port': b'9200'}])
request_body = {
    'mappings': {
        'properties': {
            "id": {"type": "integer", "index": "true"},
            "vector": {"type": "double"},
            "cluster": {"type": "integer", "index": "true"},
            "sub_cluster": {"type": "integer", "index": "true"}
        }
    }
}
esIndex = "ehd2"
es.indices.delete(index=esIndex)
es.indices.create(index=esIndex, body=request_body)
esIndex_old = "ehd"
starting_time = datetime.now()
for cluster_id in range(20):
    cluster_time = datetime.now()
    kms = load("static/cluster_models/" + str(cluster_id) + ".joblib")
    results = scan(es, index=esIndex_old, preserve_order=True,
                   query={'query': {'match': {'cluster': cluster_id}}})
    bulk_data = []
    for item in tqdm(results):
        v = np.array(item["_source"]["vector"])
        v[80:85] *= 5
        sub_cluster = kms.predict([v])
        data_dict = {
            "id": item["_source"]["id"],
            "vector": list(v),
            "cluster": cluster_id,
            "sub_cluster": int(sub_cluster)
        }
        op_dict = {
            "index": {
                "_index": esIndex,
                "_id": data_dict['id']
            }
        }
        bulk_data.append(op_dict)
        bulk_data.append(data_dict)
        if len(bulk_data) > 999:
            es.bulk(index=esIndex, body=bulk_data, request_timeout=10000)
            bulk_data = []
    if len(bulk_data) > 0:
        es.bulk(index=esIndex, body=bulk_data, request_timeout=10000)
        bulk_data = []

    print("cluster %d finished in:" % cluster_id)
    print(datetime.now() - cluster_time)


finish_time = datetime.now()
print(finish_time - starting_time)