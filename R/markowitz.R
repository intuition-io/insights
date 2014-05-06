# Markowitz portfolio optimization
# --------------------------------
#
# :copyright (c) 2014 Xavier Bruhiere.
# :license: Apache 2.0, see LICENSE for more details.

#TODO Check for package to be installed
suppressPackageStartupMessages(require(polynom))
suppressPackageStartupMessages(require(fImport))
suppressPackageStartupMessages(require(PerformanceAnalytics))
suppressPackageStartupMessages(require(tseries))
suppressPackageStartupMessages(require(stats))
suppressPackageStartupMessages(require(zoo))
suppressPackageStartupMessages(require(futile.logger))
suppressPackageStartupMessages(require(TTR))


# Intermediate function used in portfolio rebalancing
reweight = function(returns, startWeight){
  flog.info('Re-computating weights')
  n          = nrow(returns)
  lastWeight = as.vector(startWeight)
  outReturn  = data.frame()

  for(i in seq(1,n)){
    rts        = as.vector(exp(returns[i,]))
    w          = lastWeight * rts
    sumW       = sum(w)
    w          = w / sumW

    r          = as.matrix(returns[i,]) %*% w

    lastWeight = w

    outReturn  = rbind(outReturn, r)
  }
  return (outReturn)
}

#TODO Instead or 'error in this try', count errors and print a bilan
getEfficientFrontier <- function(returns, periods=255, points=500, maxWeight=.334, Debug=FALSE, graph=FALSE)
{
  returnNames = colnames(returns)
  #create an empty data frame for the portfolio weights
  weights = data.frame(t(rep(NA,length(returnNames))))
  colnames(weights) = returnNames
  weights = weights[-1,]

  #Calculate Annualized Returns
  t = table.AnnualizedReturns(returns)

  #Range to optimize over
  maxRet = max(t['Annualized Return',]) - .005
  minRet = min(t['Annualized Return',]) + .005
  #set the max and min for the returns limit to 50% and the lower to .005%
  maxRet = min(.5,maxRet)
  minRet = max(0.005,minRet)

  #if all series have negative expected return, then only find the portfolio with the max return
  if (maxRet < 0){
    minRet = maxRet
    points = 1
  }
  #Debugging Print
  if (Debug){
    print("Max Return")
    print(maxRet)
    print("Min Return")
    print(minRet)
  }

  #portfolio.optim cannot have NA values in the time series, filter them out
  #m2 = removeNA(returns[,returnNames])
  m2 = removeNA(returns)
  er = NULL
  eStd = NULL

  #loop through finding the optimum portfolio for return levels between the range found above
  #portfolio.optim uses daily returns, so we have to adjust accordingly
  ok = FALSE
  for (i in seq(minRet, maxRet, length.out=points)){
    pm = 1+i
    pm = log(pm) / periods
    if (Debug){
      print("Finding Optimum for")
      print("ER")
      print(pm)
      print(exp(pm * periods) - 1)
    }
    #optimization. limit weights to <= maxWeight
    #surround in tryCatch to catch unobtainable values
    opt = tryCatch(portfolio.optim(m2,
                                   pm=pm),
                   #reshigh=rep(maxWeight,length(returnNames)),
                   #shorts = FALSE),
                   error=function(err) return(NULL))

    #check to see if feasible solution exists
    if (!is.null(opt)){
      er = c(er, exp(pm * periods) - 1)
      eStd = c(eStd, opt$ps * sqrt(periods))
      w = t(opt$pw)
      colnames(w) = returnNames
      weights = rbind(weights, w)
      #update the OK variable
      ok = (ok | TRUE)
    } else {
      #print("** Error in this try")
      #update the OK variable
      ok = (ok | FALSE)
    }
  }
  #if no feasible solutions were found for the frontier, return NULL
  if (!ok){
    print('! No feasible solutions found for the frontier')
    return (NULL)
  }
  solution      = weights
  solution$er   = er
  solution$eStd = eStd
  if (graph)
  {
    plot(eStd^2, er, col='blue')
    legend(.014, 0.015, 'Efficient frontier', col='red', lty=c(1,1))
  }
  return(solution)
}

#TODO A correctif is needed, see posts and reweight
marketPortfolio = function(solution,
                           rf,
                           graph=FALSE,
                           points=500,
                           Debug=FALSE)
{
  #find the index values for the minimum Std and the max Er
  minIdx = which(solution$eStd == min(solution$eStd))
  maxIdx = which(solution$er == max(solution$er))
  if (Debug){
    print(minIdx)
    print(maxIdx)
  }
  subset = solution[minIdx:maxIdx,c("er","eStd")]
  subset$nAbove = NA

  #for each value in the subset, count the number of points
  #that lay below a line drawn through the point and the RF asset
  for (i in seq(1,maxIdx-minIdx+1)){
    toFit              = data.frame(er=rf, eStd=0)
    toFit              = rbind(toFit,subset[i,c("er","eStd")])
    fit                = lm(toFit$er ~ toFit$eStd)
    poly               = polynomial(coef=fit$coefficients)
    toPred             = subset
    colnames(toPred)   = c("actEr","eStd")
    toPred$er          = predict(poly,toPred[,"eStd"])
    toPred$diff        = toPred$er - toPred$actEr
    subset[i,"nAbove"] = nrow(toPred[which(toPred$diff > 0),])
  }

  #get the point of tangency -- where the number of points
  #below the line is maximized
  max  = max(subset$nAbove)
  er   = subset[which(subset$nAbove == max),"er"]
  eStd = subset[which(subset$nAbove == max),"eStd"]
  #if more than one portfolio is found, return the first
  if (length(er) > 1){
    er   = er[1]
    eStd = eStd[1]
  }
  #index of the market portfolio
  idx = which(solution$er == er & solution$eStd == eStd)
  if (Debug){
    print("solution")
    print(er)
    print(eStd)
    print(solution[idx,])
  }
  #Draw the line if requested
  if (graph){
    maxStd = max(solution$eStd) + .02
    maxRetg = max(solution$er) + .02
    plot(solution$eStd,
         solution$er,
         xlim=c(0,maxStd),
         ylim=c(0,maxRetg),
         ylab="Expected Yearly Return",
         xlab="Expected Yearly Std Dev",
         main="Efficient Frontier",
         col="red",
         type="l",
         lwd=2)
    abline(v=c(0), col="black", lty="dotted")
    abline(h=c(0), col ="black", lty="dotted")
    toFit = data.frame(er=rf,eStd=0)
    toFit = rbind(toFit,solution[idx,c("er","eStd")])
    fit = lm(toFit$er ~ toFit$eStd)
    abline(coef=fit$coefficients,col="blue",lwd=2)
  }
  #Return the market portfolio wieghts and eStd and eR
  out = solution[idx,]
  return (out)
}

usage <- function(symbols)
{
    from = "2005-01-01"
    to   = "2011-12-16"
    #returnNames = c("xom.Return","ibm.Return","ief.Return")

    data = importSeries(symbols, from, to)
    for (i in seq(length(symbols)))
    {
        symbols[i] = paste(symbols[i], '.Return', sep='')
    }


    # Period is the frequency over a year of the returns
    frontier <- getEfficientFrontier(data, symbols, points=500, Debug=T, graph=T)
    mp = marketPortfolio(frontier, .02, Debug=T, graph=T)
}

#usage(c('xom', 'ibm', 'ief'))
