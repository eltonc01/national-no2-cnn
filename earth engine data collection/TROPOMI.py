import pandas as pd
from tqdm import tqdm
import numpy as np
import ee
import datetime
import logging
import multiprocessing
from retry import retry
import psutil
import os

ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')

# dictionary of all the dates that are needed per monitor
time_dict = np.load('date dict.npy', allow_pickle=True).item()

omi = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
omi = omi.select(['tropospheric_NO2_column_number_density', 'cloud_fraction'])
df_no2 = pd.read_csv('no2 sites.csv')

imglist = []


def dailySort(dayOffset):
    start = startDate.advance(dayOffset, 'days')
    end = start.advance(1, 'days')

    img = omi.filterDate(start, end)

    flag1 = ee.Algorithms.IsEqual(ee.Number(img.size()), ee.Number(0))

    size = ee.Algorithms.If(flag1, 10, img.size())

    limg = img.toList(size)

    def getArraysNO2(index):
        return ee.Image(limg.get(index)).sampleRectangle(roi, defaultValue=1000).getArray(
            'tropospheric_NO2_column_number_density').toList()

    def getArraysCloud(index):
        return ee.Image(limg.get(index)).sampleRectangle(roi, defaultValue=1000).getArray('cloud_fraction').toList()

    no2 = ee.List.sequence(0, limg.size().subtract(1)).map(getArraysNO2).map(processArrays, True)
    clouds = ee.List.sequence(0, limg.size().subtract(1)).map(getArraysCloud).map(processArrays, True)

    flag = ee.Algorithms.IsEqual(ee.Number(clouds.size()), ee.Number(0))

    return ee.Algorithms.If(flag, None, ee.List([ee.Array(no2).transpose().toList().map(transpose).map(matrix),
                                                 ee.Array(clouds).transpose().toList().map(transpose).map(matrix).map(
                                                     avg).reduce(ee.Reducer.mean())]))


def processArrays(lis):
    return ee.Algorithms.If(ee.Algorithms.IsEqual(ee.Number(ee.List(lis).map(avg).reduce(ee.Reducer.mean())).lt(1),
                                                  ee.Number(1)), ee.List(lis), None)


def avg(lis):
    return ee.List(lis).reduce(ee.Reducer.mean())


def matrix(lis):
    return ee.List(lis).map(avg)


def transpose(lis):
    return ee.Array(lis).transpose().toList()


years = [2018, 2019, 2020, 2021, 2022]

for r in tqdm(range(len(df_no2))):
    loc = (df_no2.loc[r, 'Longitude'], df_no2.loc[r, 'Latitude'])
    num = df_no2.loc[r, 'Site Num']
    loc = ee.Geometry.Point(loc[0], loc[1])
    roi = loc.buffer(13000)

    zone = df_no2.loc[r, 'Time Zone']

    for year in years:
        try:
            month_list = time_dict[year][num]
            startMonth = month_list[0][4:6]
            endMonth = month_list[-1][4:6]
        except KeyboardInterrupt:
            raise
        except:
            continue

        if year == 2018:
            if int(endMonth) < 7:
                continue
            startMonth = '07'

        startDate = ee.Date(f'{year}-{startMonth}-01T00', zone)
        endDate = ee.Date(f'{year}-{endMonth}-01T00', zone)

        numberOfDays = endDate.difference(startDate, 'days')

        samp = ee.List.sequence(0, numberOfDays.subtract(1)).map(dailySort)  # .getInfo()

        imglist.append([samp, num, startMonth, year])

items = imglist


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


@retry(tries=10, delay=1, backoff=2)
def getArr(index, items):
    year = items[3]
    sdate = datetime.datetime(year, int(items[2]), 1)
    num = items[1]
    samp = items[0].getInfo()

    arrs = {}
    for i in samp:
        if i is not None and i[1] <= 0.30:
            day = (sdate + datetime.timedelta(days=samp.index(i))).strftime('%m%d')
            arrs[day] = np.array(i[0])
            if arrs[day].shape[1] < 25:
                print('error')

    np.save(f'savepath/{num} {year}.npy', arrs)
    print(f'Done: {index}, Year: {year}')


if __name__ == '__main__':
    logging.basicConfig()

    pool = multiprocessing.Pool(processes=25)
    pool.starmap(getArr, enumerate(items))

    pool.close()
