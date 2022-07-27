from time import sleep

import os
import mysql.connector
from dotenv import load_dotenv


class ChalBenchmark:

    def __init__(self):
        load_dotenv()
        self.USER = os.getenv("USER")
        self.PASSWORD = os.getenv("PASSWORD")
        self.HOST = os.getenv("HOST")
        self.PORT = os.getenv("PORT")
        self.DATABASE = os.getenv("DATABASE")

    def masteryAnalysis(self):
        games = self.grabApi("grabGames", 0)
        gameNum = 0
        correctAnalysis = 0
        gameCount = 0
        for game in games:
            gameCount = gameCount + 1
            print(str(gameCount) + "/" + str(len(games)))
            playerData = self.grabApi("grabPlayers", game[0])
            blueTeamMastery = 0
            redTeamMastery = 0
            for player in playerData:
                if player[2] == 1:
                    blueTeamMastery = blueTeamMastery + player[8]
                else:
                    redTeamMastery = redTeamMastery + player[8]
            if blueTeamMastery < redTeamMastery and game[1] == 0:
                correctAnalysis = correctAnalysis + 1
                gameNum = gameNum + 1
            elif redTeamMastery < blueTeamMastery and game[1] == 1:
                correctAnalysis = correctAnalysis + 1
                gameNum = gameNum + 1
            elif redTeamMastery != blueTeamMastery:
                gameNum = gameNum + 1
            print("Percent Accuracy: " + str(correctAnalysis / gameNum))

    def winRateAnalysis(self):
        games = self.grabApi("grabGames", 0)
        gameNum = 0
        correctAnalysis = 0
        gameCount = 0
        for game in games:
            gameCount = gameCount + 1
            print(str(gameCount) + "/" + str(len(games)))
            playerData = self.grabApi("grabPlayers", game[0])
            blueTeamWR = 0
            redTeamWR = 0
            for player in playerData:
                if player[2] == 1:
                    blueTeamWR = blueTeamWR + player[4]
                else:
                    redTeamWR = redTeamWR + player[4]
            if blueTeamWR < redTeamWR and game[1] == 0:
                correctAnalysis = correctAnalysis + 1
                gameNum = gameNum + 1
            elif redTeamWR < blueTeamWR and game[1] == 1:
                correctAnalysis = correctAnalysis + 1
                gameNum = gameNum + 1
            elif redTeamWR != blueTeamWR:
                gameNum = gameNum + 1
            else:
                # redTeamWR == blueTeamWR:
                print("either way")
                print("Percent Accuracy: " + str(correctAnalysis / gameNum))

        print("Percent Accuracy: " + str(correctAnalysis / gameNum))

    def streakAnalysis(self):
        games = self.grabApi("grabGames", 0)
        correctAnalysis = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        gameNum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        gameCount = 0
        for game in games:
            print(str(gameCount) + "/" + str(len(games)))
            gameCount = gameCount + 1
            playerData = self.grabApi("grabPlayers", game[0])
            blueTeamStreak = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            redTeamStreak = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for extremity in range(0, 10):
                for player in playerData:
                    if player[5] > extremity or player[5] < -extremity:
                        if player[2] == 1:
                            blueTeamStreak[extremity] = blueTeamStreak[extremity] + player[5]
                        else:
                            redTeamStreak[extremity] = redTeamStreak[extremity] + player[5]
                if blueTeamStreak[extremity] > redTeamStreak[extremity] and game[1] == 1:
                    correctAnalysis[extremity] = correctAnalysis[extremity] + 1
                    gameNum[extremity] = gameNum[extremity] + 1
                elif redTeamStreak[extremity] > blueTeamStreak[extremity] and game[1] == 0:
                    correctAnalysis[extremity] = correctAnalysis[extremity] + 1
                    gameNum[extremity] = gameNum[extremity] + 1
                elif redTeamStreak[extremity] != blueTeamStreak[extremity]:
                    gameNum[extremity] = gameNum[extremity] + 1

        for extremity in range(0, 10):
            print("For " + str(extremity) + " Extremity Percent Accuracy: " + str(correctAnalysis[extremity] / gameNum[extremity]))

    def gameNumAnalysis(self):
        games = self.grabApi("grabGames", 0)
        gameNum = 0
        correctAnalysis = 0
        gameCount = 0
        for game in games:
            gameCount = gameCount + 1
            print(str(gameCount) + "/" + str(len(games)))
            playerData = self.grabApi("grabPlayers", game[0])
            blueTeamGamesPlayed = 0
            redTeamGamesPlayed = 0
            for player in playerData:
                if player[2] == 1:
                    blueTeamGamesPlayed = blueTeamGamesPlayed + player[7]
                else:
                    redTeamGamesPlayed = redTeamGamesPlayed + player[7]
            if blueTeamGamesPlayed < redTeamGamesPlayed and game[1] == 0:
                correctAnalysis = correctAnalysis + 1
                gameNum = gameNum + 1
            elif redTeamGamesPlayed < blueTeamGamesPlayed and game[1] == 1:
                correctAnalysis = correctAnalysis + 1
                gameNum = gameNum + 1
            elif redTeamGamesPlayed != blueTeamGamesPlayed:
                gameNum = gameNum + 1
            else:
                # redTeam = blueTeam games played
                print("either way")
                print("Percent Accuracy: " + str(correctAnalysis / gameNum))

            print("Percent Accuracy: " + str(correctAnalysis / gameNum))

    def grabApi(self, requestType, data):
        successfulGrab = False
        if requestType == "grabPlayers":
            while successfulGrab is False:
                try:
                    connection = mysql.connector.connect(host=self.HOST,
                                                         database=self.DATABASE,
                                                         user=self.USER,
                                                         password=self.PASSWORD,
                                                         port=self.PORT)
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM playerStatInstances WHERE gameId=%s", (data,))
                    response = cursor.fetchall()
                    successfulGrab = True
                    return response
                except:
                    print("Couldn't grab game " + data + " ... trying again")
                finally:
                    connection.close()
        elif requestType == "grabGames":
            while successfulGrab is False:
                try:
                    connection = mysql.connector.connect(host=self.HOST,
                                                         database=self.DATABASE,
                                                         user=self.USER,
                                                         password=self.PASSWORD,
                                                         port=self.PORT)
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM games")
                    response = cursor.fetchall()
                    successfulGrab = True
                    return response
                except:
                    print("DB 'grabGames' Issues... trying again...")
                    sleep(10)
                finally:
                    connection.close()