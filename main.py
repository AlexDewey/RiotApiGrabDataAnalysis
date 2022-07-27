import os

from AverageDataCreation.recorder import GameRecorder
from Analytics.Chalbenchmark import ChalBenchmark
from Analytics.Chalregression import ChalRegression
from Analytics.ChalKNN import ChalKNN
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

Nadao = GameRecorder("na1.api.riotgames.com", API_KEY)
Nadao.seedGames(1000, "IRON", "IV")

# Example Code Below

# NAdao = ChalGameRecorder("na1.api.riotgames.com", API_KEY)
# NAdao.seedInitialGames()
# NAdao.estimateRemainingPlayers()
# NAdao.addMasteryPoints()

# benchmarkAnalysis = ChalBenchmark()
# benchmarkAnalysis.winRateAnalysis()
# benchmarkAnalysis.streakAnalysis()
# benchmarkAnalysis.gameNumAnalysis()
# benchmarkAnalysis.masteryAnalysis()
# benchmarkAnalysis.displayMastery()

# regressionTest = ChalRegression()
# regressionTest.UnivariateLogisticRegression()
# regressionTest.OVRLogisticRegression()
# regressionTest.MultinomialLogisticRegression()

# KNearestNeighbors = ChalKNN()
# KNearestNeighbors.basicPrediction()