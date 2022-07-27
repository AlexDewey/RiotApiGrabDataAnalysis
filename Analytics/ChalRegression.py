import os
import random
from math import floor, ceil
from time import sleep

import matplotlib.pyplot as plt
import mysql
import numpy as np
from dotenv import load_dotenv
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score


class ChalRegression:

    def __init__(self):
        load_dotenv()
        self.USER = os.getenv("USER")
        self.PASSWORD = os.getenv("PASSWORD")
        self.HOST = os.getenv("HOST")
        self.PORT = os.getenv("PORT")
        self.DATABASE = os.getenv("DATABASE")

    def UnivariateLogisticRegression(self):
        rawData = self.grabApi("grabAllGames")
        train, test = self.splitAndCleanData(rawData, 0.8)

        y_train = np.array(train[:], dtype=np.int32)
        y_train = y_train[:, 0]

        y_test = np.array(test[:], dtype=np.int32)
        y_test = y_test[:, 0]

        testing_values = [[3, "WR"], [4, "Streak"], [5, "games"], [6, "mastery"]]

        for value in testing_values:
            x_train = np.asarray(train, dtype=np.float)
            x_train = x_train[:, value[0]]
            x_train = x_train.reshape(-1, 1)

            x_test = np.array(test, dtype=np.float)
            x_test = x_test[:, value[0]]
            x_test = x_test.reshape(-1, 1)

            model = LogisticRegression()

            model.fit(x_train, y_train)

            y_pred = model.predict(x_test)

            cm = confusion_matrix(y_test, y_pred)
            disp = ConfusionMatrixDisplay(confusion_matrix=cm)

            disp.plot()
            # plt.show()

            print(str(value[1]) + " LR accuracy:" + str(accuracy_score(y_test, y_pred)))

    def OVRLogisticRegression(self):
        rawData = self.grabApi("grabAllGames")
        train, test = self.splitAndCleanData(rawData, 0.8)

        y_train = np.array(train[:], dtype=np.int32)
        y_train = y_train[:, 0]

        y_test = np.array(test[:], dtype=np.int32)
        y_test = y_test[:, 0]

        x_train = np.asarray(train, dtype=np.float)
        x_train = x_train[:, [3, 4, 5, 6]]
        x_train = x_train.reshape(-1, 4)

        x_test = np.array(test, dtype=np.float)
        x_test = x_test[:, [3, 4, 5, 6]]
        x_test = x_test.reshape(-1, 4)

        model = LogisticRegression(multi_class='ovr')

        model.fit(x_train, y_train)

        y_pred = model.predict(x_test)

        print("OVR LR accuracy:" + str(accuracy_score(y_test, y_pred)))


    def MultinomialLogisticRegression(self):
        rawData = self.grabApi("grabAllGames")
        train, test = self.splitAndCleanData(rawData, 0.8)

        y_train = np.array(train[:], dtype=np.int32)
        y_train = y_train[:, 0]

        y_test = np.array(test[:], dtype=np.int32)
        y_test = y_test[:, 0]

        x_train = np.asarray(train, dtype=np.float)
        x_train = x_train[:, [3, 4, 5, 6]]
        x_train = x_train.reshape(-1, 4)

        x_test = np.array(test, dtype=np.float)
        x_test = x_test[:, [3, 4, 5, 6]]
        x_test = x_test.reshape(-1, 4)

        model = LogisticRegression(multi_class='multinomial', solver='lbfgs')

        model.fit(x_train, y_train)

        y_pred = model.predict(x_test)

        print("Multinomial LR accuracy:" + str(accuracy_score(y_test, y_pred)))


    def splitAndCleanData(self, rawData, trainAmount):
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