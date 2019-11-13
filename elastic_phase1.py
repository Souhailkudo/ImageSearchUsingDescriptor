import pandas as pd
# import numpy as np
from elasticsearch import Elasticsearch
from tqdm import tqdm

es = Elasticsearch([{u'host': u'127.0.0.1', u'port': b'9200'}])
request_body = {
    'mappings': {
        'properties': {
            "id": {"type": "integer", "index": "true"},
            "vector": {"type": "double"},
            "cluster": {"type": "integer", "index": "true"}
        }
    }
}
esIndex = "ehd"
es.indices.create(index=esIndex, body=request_body)
for clusterLabel in tqdm(range(20)):
    df = pd.read_csv("static/clusters/cluster_" + str(clusterLabel) + ".csv")
    l = list(range(0, len(df), 1000))
    if len(df) % 1000 != 0:
        l.append(len(df))
    for j in tqdm(range(len(l) - 1)):
        df2 = df[l[j]:l[j + 1]]
        bulk_data = []
        for i in range(0, len(df2)):
            data_dict = {
                "id": df2.values[i][0],
                "vector": list(df2.values[i][1:]),
                "cluster": clusterLabel
            }
            op_dict = {
                "index": {
                    "_index": esIndex,
                    "_id": data_dict['id']
                }
            }
            bulk_data.append(op_dict)
            bulk_data.append(data_dict)
        es.bulk(index=esIndex, body=bulk_data, request_timeout=10000)
