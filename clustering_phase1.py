#%%
# importing libraries
import pandas as pd
from sklearn.cluster import KMeans
from tqdm import tqdm
from datetime import datetime
import numpy as np

#%%
# loading the data
print("loading data...")

df = pd.DataFrame()
path = "/home/souhaiel/Desktop/cbir2/eh_descriptors/"

starting_time = datetime.now()
for i in tqdm(range(1, 101)):
    f = open(path + "eh" + str(i) + ".txt", "r")
    lines = f.readlines()
    f.close()
    data = [c.strip().split() for c in lines]
    data = [[float(i) for i in l] for l in data]
    df = df.append(pd.DataFrame(data))
finish_time = datetime.now()
columns= [ str(i) for i in range(80,85)]
df[columns] = df[columns].apply(lambda x: x*5)
print("Data loaded successfully in ", end='')
print(finish_time-starting_time)

#%%
# Making the main clusters
KMS = []
starting_time = datetime.now()
for i in range(10):
    df2=df[i*100000:(i+1)*100000]
    kms = KMeans(n_clusters=20).fit(df2)
    KMS.append(kms)
    print("%d /9" % i)
finish_time = datetime.now()
print(finish_time-starting_time)
center_list = []
for kms in KMS:
    center_list.extend(kms.cluster_centers_)
center_kms = KMeans(n_clusters=20).fit(center_list)
new_centers = center_kms.cluster_centers_

starting_time = datetime.now()
labels= []
for i in tqdm(df.values):
    distances=[]
    for j in new_centers:
        distances.append(np.abs(np.array(i)-np.array(j)).sum())
    labels.append(distances.index(min(distances)))
finish_time = datetime.now()
print(finish_time-starting_time)
#%%
# exporting cluster centers
centers_df = pd.DataFrame(new_centers)
centers_df.to_csv("cluster_centers.csv")