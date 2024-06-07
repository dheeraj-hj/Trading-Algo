from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.optimizer import worker
from pyalgotrade.barfeed import yahoofeed


# statergy-1


class CustomEMA(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, emaPeriod):
        super(CustomEMA, self).__init__(feed)
        initial_cash = 100000  # Set the initial cash to a large value, e.g., $1,000,000
        self.getBroker().setCash(initial_cash)
        self.__instrument = instrument
        self.__ema = ma.EMA(feed[instrument].getPriceDataSeries(), emaPeriod)
        self.__longPos = None

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info(f"BUY at ${execInfo.getPrice():.2f}")
    
    def onEnterCanceled(self, position):
        self.__longPos = None


    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info(f"SELL at ${execInfo.getPrice():.2f}")
       
        self.__longPos = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__longPos.exitMarket()

    def onBars(self, bars):
        bar = bars[self.__instrument]
        if self.__ema[-1] is None or self.__ema[-2] is None:
            return

        if self.__longPos is not None:
            if self.exitLongSignal(bar):
                self.__longPos.exitMarket()
        else:
            if self.enterLongSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bar.getPrice())
                # shares  = 1
                self.__longPos = self.enterLong(self.__instrument, shares, True)

    def enterLongSignal(self, bar):
        prevClose = self.getFeed()[self.__instrument].getCloseDataSeries()[-2]
        return prevClose is not None and prevClose > self.__ema[-2] and bar.getOpen() > self.__ema[-1]

    def exitLongSignal(self, bar):
        prevClose = self.getFeed()[self.__instrument].getCloseDataSeries()[-2]
        return prevClose is not None and prevClose < self.__ema[-2] and bar.getOpen() < self.__ema[-1] and bar.getClose() < self.__ema[-1]

    def getResult(self):
        return self.getBroker().getEquity()

if __name__ == '__main__':
    worker.run(CustomEMA, "localhost", 5000)



# statergy -2 

# class CustomEMA(strategy.BacktestingStrategy):
#     def __init__(self, feed, instrument, emaPeriod):
#         super(CustomEMA, self).__init__(feed)
#         initial_cash = 100000  # Set the initial cash
#         self.getBroker().setCash(initial_cash)
#         self.__instrument = instrument
#         self.__ema = ma.EMA(feed[instrument].getPriceDataSeries(), emaPeriod)
#         self.__longPos = None
#         self.__shortPos = None

#     def onEnterOk(self, position):
#         execInfo = position.getEntryOrder().getExecutionInfo()
#         action = position.getEntryOrder().Action
#         self.info(f"{'BUY-Long' if action == 'BUY' else 'SELL-short'} at ${execInfo.getPrice():.2f}")

#     def onEnterCanceled(self, position):
#         if position == self.__longPos:
#             self.__longPos = None
#         elif position == self.__shortPos:
#             self.__shortPos = None

#     def onExitOk(self, position):
#         execInfo = position.getExitOrder().getExecutionInfo()
#         self.info(f"{'SELL' if position.getEntryOrder().getAction() == 'BUY' else 'BUY'} at ${execInfo.getPrice():.2f}")

#         if position == self.__longPos:
#             self.__longPos = None
#         elif position == self.__shortPos:
#             self.__shortPos = None

#     def onExitCanceled(self, position):
#         # If the exit was canceled, re-submit it.
#         position.exitMarket()

#     def onBars(self, bars):
#         bar = bars[self.__instrument]
#         if self.__ema[-1] is None or self.__ema[-2] is None:
#             return

#         if self.__longPos is not None and self.__longPos.getEntryOrder().getExecutionInfo() is not None:
#             if self.exitLongSignal(bar):
#                 self.__longPos.exitMarket()
#         elif self.__shortPos is not None and self.__shortPos.getEntryOrder().getExecutionInfo() is not None:
#             if self.exitShortSignal(bar):
#                 self.__shortPos.exitMarket()
#         else:
#             if self.enterLongSignal(bar):
#                 shares = 1
#                 if(self.getBroker().getCash() > bar.getPrice()):
#                     stopLossPrice = bar.getPrice() * 0.990  # 0.2% stop loss
#                     # takeProfitPrice = bar.getPrice() * 1.02  # 2% take profit
#                     self.__longPos = self.enterLongStop(self.__instrument, stopLossPrice, shares)
#             if self.enterShortSignal(bar):
#                 shares = 1
#                 if(self.getBroker().getCash() > bar.getPrice()):
#                     stopLossPrice = bar.getPrice() * 1.01  # 0.2% stop loss
#                     # takeProfitPrice = bar.getPrice() * 0.98  # 2% take profit
#                     self.__shortPos = self.enterShortStop(self.__instrument,  stopLossPrice, shares)

#     def enterLongSignal(self, bar):
#         prevClose = self.getFeed()[self.__instrument].getCloseDataSeries()[-2]
#         return prevClose is not None and prevClose > self.__ema[-2] and bar.getOpen() > self.__ema[-1]

#     def exitLongSignal(self, bar):
#         if self.__longPos is not None:
#             entryPrice = self.__longPos.getEntryOrder().getExecutionInfo().getPrice()
#             return bar.getClose() < self.__ema[-1] or bar.getPrice() >= entryPrice * 1.04
#         return False

#     def enterShortSignal(self, bar):
#         prevClose = self.getFeed()[self.__instrument].getCloseDataSeries()[-2]
#         return prevClose is not None and prevClose < self.__ema[-2] and bar.getOpen() < self.__ema[-1]

#     def exitShortSignal(self, bar):
#         if self.__shortPos is not None:
#             entryPrice = self.__shortPos.getEntryOrder().getExecutionInfo().getPrice()
#             return bar.getClose() > self.__ema[-1] or bar.getPrice() <= entryPrice * 0.96
#         return False

#     def getResult(self):
#         return self.getBroker().getEquity()

# if __name__ == '__main__':
#     worker.run(CustomEMA, "localhost", 5000)

