from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.optimizer import worker
from pyalgotrade.barfeed import yahoofeed

class CustomEMA(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, emaPeriod):
        super(CustomEMA, self).__init__(feed)
        initial_cash = 4000  # Set the initial cash to a large value, e.g., $1,000,000
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
                # shares = int(self.getBroker().getCash() * 0.9 / bar.getPrice())
                shares  = 1
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
