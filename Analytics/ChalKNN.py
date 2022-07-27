import os
import random
from math import floor, ceil
from time import sleep

import matplotlib.pyplot as plt
import mysql
import numpy as np
import seaborn as sns
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, confusion_matrix, classification_report, accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from itertools import chain, combinations

from dotenv import load_dotenv


def splitAndCleanData(rawData, trainAmount):
    # todo: Consider validation data
    # 1 is win, 0 is loss
    rawData_list = list()
    for entry in rawData:
        entry_list = list(entry)
        if (entry[0] == 1 and entry[1] == 1) or (entry[0] == 0 and entry[1] == 2):
            entry_list[0] = 1
        else:
            entry_list[0] = 0
        rawData_list.append(entry_list)

    # shuffling data
    random.seed(1)
    random.shuffle(rawData_list)
    train = rawData_list[0:floor(len(rawData_list)*trainAmount)]
    test = rawData_list[ceil(len(rawData_list)*trainAmount):]
    return train, test

def powerset(list_name):
    s = list(list_name)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

class ChalKNN:

    def __init__(self):
        load_dotenv()
        self.USER = os.getenv("USER")
        self.PASSWORD = os.getenv("PASSWORD")
        self.HOST = os.getenv("HOST")
        self.PORT = os.getenv("PORT")
        self.DATABASE = os.getenv("DATABASE")

    def basicPrediction(self):
        rawData = self.grabApi("grabAllGames")
        train, test = splitAndCleanData(rawData, 0.8)

        possible_values = [3, 4, 5, 6]

        records = list()
        for n in range(2, 20):
            for value_list in powerset(possible_values):
                if len(value_list) > 0:
                    x_train = np.asarray(train, dtype=np.float)
                    x_train = x_train[:, value_list]
                    x_train = x_train.reshape(-1, len(value_list))

                    y_train = np.array(train[:], dtype=np.int32)
                    y_train = y_train[:, 0]

                    x_test = np.array(test, dtype=np.float)
                    x_test = x_test[:, value_list]
                    x_test = x_test.reshape(-1, len(value_list))

                    y_test = np.array(test[:], dtype=np.int32)
                    y_test = y_test[:, 0]

                    # scaler = StandardScaler()
                    scaler = MinMaxScaler()
                    scaler.fit(x_train)

                    x_train = scaler.transform(x_train)
                    x_test = scaler.transform(x_test)

                    classifier = KNeighborsClassifier(n_neighbors=n)
                    classifier.fit(x_train, y_train)

                    y_pred = classifier.predict(x_test)

                    # result = confusion_matrix(y_test, y_pred)
                    # print("Confusion Matrix:")
                    # print(result)
                    # result1 = classification_report(y_test, y_pred)
                    # print("Classification ReportL")
                    # print(result1)
                    result2 = accuracy_score(y_test, y_pred)
                    print("Accuracy:", result2)
                    records.append([n, value_list, result2])

        print(records)

    def grabApi(self, requestType):
        successfulGrab = False
        if requestType == "grabAllGames":
            while successfulGrab is False:
                try:
                    connection = mysql.connector.connect(host=self.HOST,
                                                         database=self.DATABASE,
                                                         user=self.USER,
                                                         password=self.PASSWORD,
                                                         port=self.PORT)
                    cursor = connection.cursor()
                    cursor.execute("SELECT games.win, psi.team, psi.champ, psi.wrOnChamp, psi.streak, psi.gamesOnChamp, psi.masteryPoints FROM games INNER JOIN playerStatInstances psi ON games.gameId=psi.gameId;")
                    response = cursor.fetchall()
                    successfulGrab = True
                    return response
                except:
                    print("DB 'grabAllGames' Issues... trying again...")
                    sleep(10)
                finally:
                    connection.close()