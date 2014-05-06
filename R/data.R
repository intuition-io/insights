# Insights R library
# ------------------
#
# :copyright (c) 2014 Xavier Bruhiere.
# :license: Apache 2.0, see LICENSE for more details.

# From http://statsadventure.blogspot.fr
#TODO - transaction costs, turnover constraints

#TODO Check for package to be installed
suppressPackageStartupMessages(require(tseries))
suppressPackageStartupMessages(require(stats))
suppressPackageStartupMessages(require(zoo))
suppressPackageStartupMessages(require(futile.logger))
suppressPackageStartupMessages(require(TTR))

# Initial setup
options(scipen=100)
options(digits=4)
flog.threshold(INFO)

# Fetch from the net and return a shaped cumulative returns from it
downloadOneSerie = function (symbol, from, to) {
    # Read data from Yahoo! Finance
    flog.info('Downloading quotes %s fron yahoo! finance, from %s to %s.', symbol, from, to)
    input       = yahooSeries(symbol, from=from, to=to)

    # Character Strings for Column Names
    adjClose    = paste(symbol, ".Adj.Close", sep="")
    inputReturn = paste(symbol, ".Return", sep="")
    CReturn     = paste(symbol, ".CReturn", sep="")

    # Calculate the Returns and put it on the time series
    #input.Return = returns(input[, adjClose])
    input.Return = ROC(input[, adjClose])
    colnames(input.Return)[1] = inputReturn
    input = merge(input,input.Return)

    #Calculate the cumulative return and put it on the time series
    flog.info('Computing cumulative returns')
    input.first   = input[, adjClose][1]
    input.CReturn = fapply(input[,adjClose],FUN = function(x) log(x) - log(input.first))
    colnames(input.CReturn)[1] = CReturn
    input = merge(input,input.CReturn)

    #Deleting things (not sure I need to do this, but I can't not delete things if
    # given a way to...
    flog.debug('Cleaning temporary columns')
    rm(input.first,input.Return,input.CReturn,adjClose,inputReturn,CReturn)

    #Return the timeseries
    return(input)
}

# Main entry for data access
importSeries <- function(symbols,
                         from,
                         to)
{
    merged <- NULL
    for(sym in symbols)
    {
        flog.info('Fetching %s from %s', sym, source)
        # Remote access to quotes, provided by yahoo! finance
        returns = downloadOneSerie(sym, from, to)

        # Merging with previous downloads
        if (!is.null(merged))
            merged = merge(merged, returns)
        else
            merged = returns
    }
    flog.info('Got data')
    return(merged)
}
