from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
import numpy as np
from tqdm import tqdm
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from datetime import datetime
from joblib import load

es = Elasticsearch([{u'host': u'127.0.0.1', u'port': b'9200'}])
myIndex = "ehd2"


class ShowThumbnailForm(FlaskForm):
    imageId = StringField('imageId', validators=[DataRequired()])
    show = SubmitField('Show')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'


cluster_centers_df = pd.read_csv("cluster_centers.csv", index_col=0)

kms = [load("static/cluster_models/" + str(cluster_id) + ".joblib") for cluster_id in range(20)]


def getVectorById(id0: int):
    res = es.get(index=myIndex, id=float(id0))
    v = np.array(res["_source"]['vector'])
    return v


def findCluster(id0: int):
    distances = []
    v0 = getVectorById(id0)
    for i in cluster_centers_df.values:
        distances.append(np.abs(np.array(i) - v0).sum())
    cluster_id = distances.index(min(distances))
    sub_cluster = kms[cluster_id].predict([v0])[0]
    return cluster_id, sub_cluster



def searchInCluster(id0: int, cluster_id: int, sub_cluster: int):
    print("start searching")
    starting_time = datetime.now()
    v0 = getVectorById(id0)
    results = scan(es, index=myIndex, preserve_order=True,
                   query={
                          "query": {
                            "bool": {
                              "must": [
                                {
                                  "match": {
                                    "cluster": cluster_id
                                  }
                                },
                                {
                                  "match": {
                                    "sub_cluster": int(sub_cluster)
                                  }
                                }
                              ]
                            }
                          }
                        })
    resultsTime = datetime.now()-starting_time
    print(resultsTime)
    distances = []
    for item in tqdm(results):
        v = np.array(item["_source"]["vector"])
        distances.append([int(item["_source"]["id"]), np.abs(v-v0).sum()])
    starting_time = datetime.now()
    df0 = pd.DataFrame(distances, columns=['id', 'distance'])
    df0.sort_values(by='distance', inplace=True)
    resultsTime = datetime.now() - starting_time
    print(resultsTime)
    print(df0.head(20))
    return list(df0['id'].head(57))



@app.route('/', methods=['POST', 'GET'])
def search():

    showThumbnailForm = ShowThumbnailForm()
    showId = str(showThumbnailForm.imageId.data)
    visibility = "hidden"
    if showId == 'None':
        return render_template('index.html', title='Search By Image', showThumbnailForm=showThumbnailForm, visibility=visibility)
    else:
        starting_time = datetime.now()
        imagesrc = "static/thumbnails/" + str(int(showId) // 10000) + "/" + showId + ".jpg"
        cluster = findCluster(int(showId))
        thumbnailList = searchInCluster(int(showId), cluster[0], cluster[1])
        search_time = datetime.now() - starting_time
        imgSources = ["static/thumbnails/" + str(i // 10000) + "/" + str(i) + ".jpg" for i in thumbnailList]
        seconds = search_time.seconds
        micros = search_time.microseconds
        if len(imgSources)>0:
            visibility = "visible"
        return render_template('index.html', title='Search By Image',
                showThumbnailForm=showThumbnailForm, imagesrc=imagesrc, imgSources=imgSources, visibility=visibility, seconds=seconds, micros=micros)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
