import pandas as pd 
import numpy as np 
import yfinance as yf 
import datetime as dt 
from pandas_datareader import data as pdr 

yf.pdr_override() 

stock = input("Enter a stock ticker symbol: ")
print(stock)

#Pulling yahoo finance data for given 'stock' from 2018 to today
startyear = 2018
startmonth = 1
startday = 1
start = dt.datetime(startyear,startmonth,startday)
now = dt.datetime.now() 
df = pdr.get_data_yahoo(stock,start,now)    


#6 shorter-term and 6 longer-term moving averages used
emaUsed = [3,5,8,10,12,15,30,35,40,45,50,60]
for x in emaUsed: 
	ema = x 
	df['Ema_' + str(ema)] = round(df.iloc[:,4].ewm(span=ema, adjust = False).mean(),2)

pos = 0     
num = 0 
percentageChanges = []

for i in df.index: 
	cmin = min(df["Ema_3"][i], df["Ema_5"][i],df["Ema_8"][i],df["Ema_10"][i],df["Ema_12"][i],df["Ema_15"][i])     #lowest value of the 6 shorter-term MA
	cmax = max(df["Ema_30"][i], df["Ema_35"][i],df["Ema_40"][i],df["Ema_45"][i],df["Ema_50"][i],df["Ema_60"][i])  #greatest value of the 6 longer-term MA
	close = df["Adj Close"][i]   
	
	#If short term MA is above long term MA and we don't know a pos, then buy. "Red White Blue"
	if cmin > cmax:    
		if pos == 0: 
			bp = close    #buy price
			pos = 1
			print('Buying at ' + str(bp))

	#If long term MA us above short term MA and we hold a pos, then sell. "Blue White Red"
	elif cmin < cmax: 
		if pos == 1: 
			pos = 0 
			sp = close   #sell price
			print("Selling at " + str(sp))
			pc = ((sp/bp) -1)*100
			percentageChanges.append(pc)


	#Upon completion of trading period, if we still hold a stock, sell it at current price
	if num == df["Adj Close"].count() -1 and pos == 1: 
		pos = 0 
		sp = close 
		print("Selling at "+str(sp))
		pc = ((sp/bp)-1)* 100
		percentageChanges.append(pc)

	num += 1


#Calculation of summary metrics 
gains = 0 
ng = 0 
losses = 0 
nl = 0 
totalR = 1

for i in percentageChanges: 
	if i > 0: 
		gains += i
		ng += 1
	else: 
		losses += i 
		nl += 1
	totalR *= (i/100)+1

totalR = int(totalR)

if ng > 0: 
	avgGain = gains/ng
	maxR = max(percentageChanges)
else: 
	avgGain = 0 
	maxR = 'undefined'

if nl > 0: 
	avgloss = losses/nl
	maxL = min(percentageChanges)
	ratio = -avgGain/avgloss
else: 
	avgloss = 0 
	maxL = 'undefined'

#Batting Average
if ng > 0 or nl > 0: 
	battingAvg = round(ng/(ng+nl),2)
else: 
	battingAvg = 0 

percentageChanges = list(map(int,percentageChanges))
percentageChanges = list(map(lambda pc : str(pc) + "%", percentageChanges))

#Summary of financial metrics 
print()
print("Result for "+ str(stock) + " going back to " + str(df.index[0]) + ", Sample size: " + str(ng + nl) + ' trades')
print("EMAs used: "+ str([3,5,8,10,12,15,30,35,40,45,50,60]))
print("List of gains/losses for each of the "+ str(ng + nl) + ' trades: ' + str(percentageChanges))
print("Batting Average: " + str(int(battingAvg*100)) + "%")
print("Gain/Loss ratio: " + str(round(ratio,2)))
print("Average gain: " + str(int(avgGain)) + "%")
print("Average loss: " + str(int(avgloss)) + "%")
print("Max Return: " + str(int(maxR)) + "%")
print("Max Loss: " + str(int(maxL)) + "%")
print("Total return over " + str(ng+nl) + " trades: " + str(int(totalR*100)) + "%")


#Below is an email alert functionality, such that when price of 'stock' exceeds a desired 'TargetPrice', the user receives an email alert

import os 
import smtplib 
import imghdr 
from email.message import EmailMessage

EMAIL_ADDRESS = input("Please enter your email address here: ")
EMAIL_PASSWORD = input("Please enter your app's password here: ")

msg = EmailMessage() 

yf.pdr_override() 
start = dt.datetime(2018,12,1)
now = dt.datetime.now() 

stock = "AAPL"
TargetPrice = int(input("Please enter your stock's target price here: "))

alerted = False

while True: 
	df = pdr.get_data_yahoo(stock,start,now)
	currentClose = df["Adj Close"][-1]
	condition = currentClose > TargetPrice

	if condition and not alerted:
		alerted = True
		with smtplib.SMTP('smtp.gmail.com',587) as smtp: 
			smtp.ehlo() 
			smtp.starttls() 
			smtp.ehlo() 
			smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
			subject = "Alert on " + stock 
			body = stock + " Has activated the alert price of " + str(TargetPrice) +\
			"\nCurrent Price: " + str(currentClose)

			msg = f'Subject: {subject}\n\n{body}'
			
			smtp.sendmail(EMAIL_ADDRESS,'kahwaichong78@gmail.com',msg)


	else: 
		print("no new alerts")




















