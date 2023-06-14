import pandas as pd
import ee
import multiprocessing
import psutil
import os
from retry import retry
import urllib.request
import numpy as np


ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')

df_sites = pd.read_csv('no2 sites.csv')

pop = ee.ImageCollection("CIESIN/GPWv411/GPW_Population_Density").select('population_density').filterDate('2017-01-01', '2021-01-01').first()

scale = 1000

rows = 20
cols = 24


@retry(tries=10, delay=1, backoff=2)
def getArr(index, items):
    num = items[0]
    loc = ee.Geometry.Point(items[2], items[1])
    roi = loc.buffer(12000)
    url = items[-1].getDownloadUrl({'region': roi,
                                   'bands': [items[6]],
                                   'format': 'NPY',
                                   'scale': scale})

    path = f'savepath/{items[5]}/{num}.npy'
    urllib.request.urlretrieve(url, path)
    arr = np.load(path).astype('float64')
    arr = findWindow(arr, rows, cols)
    np.save(path, arr)
    print(f'{items[5]} done: {index}')


def findWindow(arr, rows, cols):
    if arr.shape == (rows, cols):
        return arr

    vert = arr.shape[0] - rows
    horiz = arr.shape[1] - cols

    if vert % 2 == 0:
        top = vert / 2
        bottom = arr.shape[0] - top
    else:
        top = int(vert / 2)
        bottom = arr.shape[0] - top - 1
    if horiz % 2 == 0:
        left = horiz / 2
        right = arr.shape[1] - left
    else:
        left = int(horiz / 2)
        right = arr.shape[1] - left - 1

    return arr[int(top):int(bottom), int(left):int(right)]
    

def limit_cpu():
    p = psutil.Process(os.getpid())
    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)


if __name__ == '__main__':
    for img in norm:
        name = 'pop density'
        band = 'population density'
        img = imp
    
        site_items = df_sites.to_numpy().tolist()
        site_items = [x + [name, band, img] for x in site_items]
    
        pool = multiprocessing.Pool(None, limit_cpu)
        pool.starmap(getArr, enumerate(site_items))
    
        pool.close()


