import json
import os
from time import sleep

import mysql
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


class GameRecorder:

    def __init__(self, REGION, API_KEY):
        self.REGION = REGION
        self.API_KEY = API_KEY
        self.puuidList = []

        load_dotenv()

        self.USER = os.getenv("USER")
        self.PASSWORD = os.getenv("PASSWORD")
        self.HOST = os.getenv("HOST")
        self.PORT = os.getenv("PORT")
        self.DATABASE = os.getenv("DATABASE")

        response = requests.get("http://ddragon.leagueoflegends.com/cdn/12.8.1/data/en_US/champion.json")
        self.champDictionary = json.loads(response.text)

    def seedGames(self, numGames, tier, division):

        gamesRecorded = 0

        # Continue until number of games met
        while numGames >= gamesRecorded:
            # Grab accounts in division desired
            accounts = self.grabApi("grabAccounts", [tier, division])

            for account in accounts:
                # Grab puuid
                puuid = self.grabApi("grabPuuid", account)

                # Grab most recent game
                gameAnalyzed = self.grabApi("grabRecentGame", puuid)

                alreadyExists = self.grabApi("gameIdExists", gameAnalyzed['metadata']['matchId'])

                if alreadyExists:
                    continue

                # Grab players from most recent game
                players = gameAnalyzed['metadata']['participants']

                # Grab every player stats
                playerStats = list()
                for player in players:
                    # We already have team
                    # Grab champMastery, playerChampWR, gamesOnChampSeason, recentGamesOnChamp, team
                    print("SummonerId")
                    summonerId, name = self.grabApi("grabSummonerId", player)
                    print("Riot Data")
                    champMastery, recentGamesOnChamp, team, champId = self.grabApi("grabRIOTData", [player, gameAnalyzed, summonerId])
                    print("OPGG Data")
                    playerChampWR, gamesOnChampSeason = self.grabApi("grabOPGGData", [player, gameAnalyzed, summonerId, champId, name])
                    playerStats.append([champMastery, playerChampWR, gamesOnChampSeason, recentGamesOnChamp, team])

                # Add complete entry
                self.putApi("recordEntry", [playerStats, ])

                # If successful, increase games recorded account, and stop once limit has been hit
                gamesRecorded = gamesRecorded + 1
                if numGames >= gamesRecorded:
                    break


    def grabApi(self, requestType, data):
        successfulGrab = False
        if requestType == "grabAccounts":
            while successfulGrab is False:
                try:
                    sleep(0.5)
                    response = requests.get("https://" + self.REGION + "/lol/league/v4/entries/RANKED_SOLO_5x5/" +
                                            data[0] + "/" + data[1] + "?api_key=" + self.API_KEY)
                    if response.status_code != 200:
                        raise Exception('Wrong Status Code')
                    returnData = json.loads(response.text)
                    successfulGrab = True
                    return returnData
                except Exception as e:
                    print(e)
                    sleep(10)
        elif requestType == "grabPuuid":
            while successfulGrab is False:
                try:
                    sleep(0.5)
                    response = requests.get(
                        "https://" + self.REGION + "/lol/summoner/v4/summoners/" + data['summonerId'] + "?api_key=" + self.API_KEY)
                    if response.status_code != 200:
                        raise Exception('Wrong Status Code')
                    returnData = json.loads(response.text)
                    if not isinstance(returnData, dict):
                        raise ValueError('rejected call')
                    successfulGrab = True
                    return returnData['puuid']
                except:
                    print("Failure to grab puuid with summonerId " + data + " ... trying again...")
                    sleep(10)
        elif requestType == "grabRecentGame":
            while successfulGrab is False:
                try:
                    sleep(0.5)
                    response = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + data + "/ids?type=ranked&start=0&count=20&api_key=" + self.API_KEY)
                    if response.status_code != 200:
                        raise Exception('Wrong Status Code')
                    gamesData = json.loads(response.text)

                    successfulGrab = True
                    return self.grabApi("grabRecentGameValue", gamesData)
                except Exception as e:
                    print(e)
                    sleep(10)
        elif requestType == "grabRecentGameValue":
            while successfulGrab is False:
                try:
                    sleep(0.5)
                    response = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/" + data[
                        0] + "?api_key=" + self.API_KEY)
                    if response.status_code != 200:
                        raise Exception('Wrong Status Code')
                    chosenGameData = json.loads(response.text)
                    return chosenGameData
                except Exception as e:
                    print(e)
                    sleep(10)
        elif requestType == "grabSummonerId":
            while successfulGrab is False:
                try:
                    sleep(0.5)
                    response = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + str(data) + "?api_key=" + self.API_KEY)
                    if response.status_code != 200:
                        raise Exception('Wrong Status Code')
                    returnData = json.loads(response.text)
                    return returnData['id'], returnData['name']
                except Exception as e:
                    print(e)
                    sleep(10)
        elif requestType == "grabRIOTData":
            while successfulGrab is False:
                try:
                    # data: [player, gameAnalyzed, summonerId]
                    # needs: [champMastery, recentGamesOnChamp, team]
                    sleep(0.5)
                    # champMastery
                    for participant in data[1]['info']['participants']:
                        if participant['summonerId'] == data[2]:
                            champId = participant['championId']
                            break
                    response = requests.get("https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" +
                                            str(data[2]) + "/by-champion/" + str(champId) + "?api_key=" + self.API_KEY)
                    if response.status_code != 200:
                        raise Exception('Wrong Status Code')
                    returnData = json.loads(response.text)
                    champMastery = returnData['championPoints']

                    successfulGrab2 = False
                    while successfulGrab2 is False:
                        try:
                            # recentGamesOnChamp
                            # Grab all games
                            sleep(0.5)
                            response = requests.get(
                                "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + str(
                                    data[0]) + "/ids?type=ranked&start=0&count=100&api_key=" + self.API_KEY)
                            if response.status_code != 200:
                                raise Exception('Wrong Status Code')
                            gamesData = json.loads(response.text)
                            successfulGrab2 = True
                        except Exception as e:
                            print(e)
                            sleep(10)

                    # Start after game analyzed
                    afterAnalyzedGame = False
                    recentGamesOnChamp = 0
                    numGamesAnalyzed = 20
                    for game in gamesData:

                        print(numGamesAnalyzed)

                        successfulGrab3 = False
                        while successfulGrab3 is False:
                            try:
                                sleep(0.5)
                                response2 = requests.get(
                                    "https://americas.api.riotgames.com/lol/match/v5/matches/" + str(game)
                                    + "?api_key=" + self.API_KEY)
                                if response2.status_code != 200:
                                    raise Exception('Wrong Status Code')
                                chosenGameData = json.loads(response2.text)
                                successfulGrab3 = True
                            except Exception as e:
                                print(e)
                                sleep(10)

                        if chosenGameData['metadata']['matchId'] == game:
                            afterAnalyzedGame = True
                        if numGamesAnalyzed == 0:
                            break
                        if afterAnalyzedGame and numGamesAnalyzed != 0:
                            numGamesAnalyzed = numGamesAnalyzed - 1
                            for participant in chosenGameData['info']['participants']:
                                if participant['summonerId'] == data[2] and participant['championId'] == champId:
                                    recentGamesOnChamp = recentGamesOnChamp + 1
                                    break

                    # team
                    for participant in data[1]['info']['participants']:
                        if participant['summonerId'] == data[2]:
                            team = participant['teamId']

                    return [champMastery, recentGamesOnChamp, team, champId]

                except Exception as e:
                    print(e)
                    sleep(10)
        elif requestType == "grabOPGGData":
            while successfulGrab is False:
                try:
                    # data: [player, gameAnalyzed, summonerId, champId, name]
                    # needs: [playerChampWR, gamesOnChampSeason]
                    sleep(1)

                    headers = {
                        'User-Agent': 'Deweys Program'
                    }

                    response = requests.get("https://na.op.gg/summoners/na/" + data[4] + "/champions", headers=headers)
                    soup = BeautifulSoup(response.text, "html.parser")

                    x = soup.find_all('script', type='application/json')
                    x2 = json.loads(x[0].text)
                    x3 = x2['props']['pageProps']['data']['most_champions']['champion_stats']

                    champWins = 0
                    champLosses = 0

                    for championId in x3:
                        if championId['id'] == data[3]:
                            champWins = championId['win']
                            champLosses = championId['lose']

                    gamesOnChamp = int(champWins) + int(champLosses)

                    if (champWins == 0 and champLosses == 0) or gamesOnChamp == 0:
                        wrOnChamp = 0.5
                    elif champWins != 0 and champLosses == 0:
                        wrOnChamp = 1
                    else:
                        wrOnChamp = int(champWins) / int(gamesOnChamp)

                    # Testing to see if op.gg data is misleading
                    wrOnChampRiot, gamesOnChampRiot = self.grabApi("grabAlternativeStats", data)

                    if gamesOnChampRiot > gamesOnChamp:
                        return [wrOnChampRiot, gamesOnChampRiot]
                    else:
                        return [wrOnChamp, gamesOnChamp]
                except Exception as e:
                    print("Failure to grab op.gg data for summonerStats we might be blocked from website :(")
                    print(e)
                    sleep(10)
        elif requestType == "grabAlternativeStats":
            while successfulGrab is False:
                try:
                    # data: [player, gameAnalyzed, summonerId, champId, name]
                    # needs: [playerChampWR, gamesOnChampSeason]
                    response = requests.get(
                        "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + str(
                            data[0]) + "/ids?type=ranked&start=0&count=100&api_key=" + self.API_KEY)
                    if response.status_code != 200:
                        raise Exception('Wrong Status Code')
                    gamesData = json.loads(response.text)

                    champWins = 0
                    champLosses = 0

                    gameListing = 1
                    for game in gamesData:

                        print(gameListing)
                        gameListing = gameListing + 1

                        successfulGrab2 = False
                        while successfulGrab2 is False:
                            try:
                                sleep(0.1)
                                response2 = requests.get(
                                    "https://americas.api.riotgames.com/lol/match/v5/matches/" + str(
                                        game) + "?api_key=" + self.API_KEY)
                                if response2.status_code != 200:
                                    raise Exception('Wrong Status Code')
                                chosenGameData = json.loads(response2.text)
                                successfulGrab2 = True
                            except Exception as e:
                                print(e)
                                sleep(10)

                        for participant in chosenGameData['info']['participants']:
                            if participant['summonerId'] == data[2]:
                                if data[3] == participant['championId']:
                                    print("cool!")
                                    if participant['win']:
                                        champWins = champWins + 1
                                    else:
                                        champLosses = champLosses + 1
                                else:
                                    break

                    gamesOnChamp = int(champWins) + int(champLosses)

                    if (champWins == 0 and champLosses == 0) or gamesOnChamp == 0:
                        wrOnChamp = 0.5
                    elif champWins != 0 and champLosses == 0:
                        wrOnChamp = 1
                    else:
                        wrOnChamp = int(champWins) / int(gamesOnChamp)

                    return wrOnChamp, gamesOnChamp
                except Exception as e:
                    print(e)
                    sleep(10)
        elif requestType == "gameIdExists":
            while successfulGrab is False:
                try:
                    connection = mysql.connector.connect(host=self.HOST,
                                                         database=self.DATABASE,
                                                         user=self.USER,
                                                         password=self.PASSWORD,
                                                         port=self.PORT)

                    cursor = connection.cursor()
                    data = str(data[4:])
                    cursor.execute("SELECT * FROM games WHERE gameId=%s", (data,))
                    response = cursor.fetchall()
                    successfulGrab = True
                    if len(response) == 0:
                        return False
                    else:
                        return True
                except:
                    print("DB 'gameIdExists' Issues... trying again...")
                    sleep(10)
                finally:
                    connection.close()

    def putApi(self, requestType, data):
        successfulPut = False
        if requestType == "recordData":
            while successfulPut is False:
                try:
                    connection = mysql.connector.connect(host=self.HOST,
                                                         database=self.DATABASE,
                                                         user=self.USER,
                                                         password=self.PASSWORD,
                                                         port=self.PORT)
                    cursor = connection.cursor()
                    cursor.execute("")
                    connection.commit()
                except Exception as e:
                    print(e)
                    return False
                finally:
                    connection.close()

                return True