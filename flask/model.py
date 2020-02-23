import pandas as pd
from sklearn import svm, preprocessing
import json
import csv
import numpy as np
import warnings

class Model:

    def __init__(self):
        #warnings.filterwarnings("ignore")
        self.train()
        self.split_data()
        



    def split_data(self):
        with open('data.csv', encoding='utf-8') as file:
            readCSV = csv.reader(file, delimiter=',')
            self.follow_data = {'x': [], 'y': [], 'z': []}
            self.nonfollow_data = {'x': [], 'y': [], 'z': []}
            for row in readCSV:
                if row[0] != '':
                    # remove outliers for graphing purposes
                    if int(row[2]) < 10000:
                        if row[4] == '1':
                            self.follow_data['x'].append(int(row[2]))
                            self.follow_data['y'].append(int(row[3]))
                            self.follow_data['z'].append(int(row[7]))
                        else:
                            self.nonfollow_data['x'].append(int(row[2]))
                            self.nonfollow_data['y'].append(int(row[3]))
                            self.nonfollow_data['z'].append(int(row[7]))
            print(len(self.follow_data['x']))
            print(len(self.nonfollow_data['y']))

        
        
    def predict(self, X):
        X = self.scaler.transform(X)
        return self.clf.predict_proba(X)[0][1]

        
    def train(self):
        df = pd.read_csv('data.csv', index_col=0)
        df['ratio'] = df['followers'] / df['following']


        df.private = df.private.astype(int)
        df.recently_joined = df.recently_joined.astype(int)
        df.verified = df.verified.astype(int)

        cols = ['followers','following','private', 'verified',
                'post_count', 'mutual', 'highlight_count',
                'recently_joined', 'ratio']


        
        
        y = df.pop('following_back')
        x = df[cols]
        mask = x.followers > 999999
        column_name = 'followers'
        x.loc[mask, column_name] = 999999

        mask = x.ratio > 999999
        column_name = 'ratio'
        x.loc[mask, column_name] = 999999
        
        self.scaler  = preprocessing.MinMaxScaler()
        x_scaled = self.scaler.fit_transform(x)
        df = pd.DataFrame(x_scaled)
        df.columns = cols

        X = df
        self.clf = svm.SVC(probability=True)
        self.clf.fit(X, y)

if __name__ == '__main__':
    m = Model()
