from coinex.coinex import CoinEx
import numpy as np
# from somewhere_else import access_id, secret
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--user', type=str, default='208C0621123240C48DBA805C7C172412',
                    help='API Access ID of CoineX')
parser.add_argument('--password', type=str, default='83FC10D422EF11CB57C5EAFF9F2F2B145DB79144281B8502',
                    help='API Secret of CoineX')
parser.add_argument('--half', type=str, default='./half.csv',
                    help='50% Margin csv file.')
parser.add_argument('--third', type=str, default='./third.csv',
                    help='33% Margin csv file.')
parser.add_argument('--quarter', type=str, default='./quarter.csv',
                    help='25% Margin csv file.')
parser.add_argument('--fifth', type=str, default='./fifth.csv',
                    help='20% Margin csv file.')
parser.add_argument('--coef', type=int , metavar='N', default=10,
                    help='Custom Margin')

args = parser.parse_args()



coinex = CoinEx(args.user,args.password)

b = coinex.market_ticker_all()
coins = b['ticker']
name = list(coins.keys())
liste = np.zeros((10, len(name)))
f1 = open(args.half, 'w')
f1.write('name,last,low,high,buy,sell,profit,tempbuy,tempsell,myprofit,Ratio\n')
f2 = open(args.third, 'w')
f2.write('name,last,low,high,buy,sell,profit,tempbuy,tempsell,myprofit,Ratio\n')
f3 = open(args.quarter, 'w')
f3.write('name,last,low,high,buy,sell,profit,tempbuy,tempsell,myprofit,Ratio\n')
f4 = open(args.fifth, 'w')
f4.write('name,last,low,high,buy,sell,profit,tempbuy,tempsell,myprofit,Ratio\n')
f5 = open('Custom_Margin.csv', 'w')
f5.write('name,last,low,high,buy,sell,profit,tempbuy,tempsell,myprofit,Ratio\n')
print("Custom Margin is  1/%d\n"%(args.coef))
for i in range(len(name)):
    liste[1, i] = float(coins[name[i]]['low'])  # low
    liste[2, i] = float(coins[name[i]]['high'])  # high
    liste[0, i] = float(coins[name[i]]['last'])  # last
    liste[5, i] = (liste[2, i]-liste[1, i])/liste[1, i]  # Profit
    liste[6, i] = (1-liste[5, i]/2)*liste[0, i]  # Temp Buy
    liste[7, i] = (1+liste[5, i]/2)*liste[0, i]  # Temp Sell
    liste[3, i] = max(liste[6, i], liste[1, i])  # Buy
    liste[4, i] = min(liste[7, i], liste[2, i])  # Sell
    liste[8, i] = 100*(liste[4, i]-liste[3, i])/liste[3, i]  # My Profit
    liste[9, i] = liste[8, i]/liste[5, i]  # Ratio
    f1.write("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %(name[i],liste[0,i],liste[1,i],liste[2,i],liste[3,i],liste[4,i],liste[5,i],liste[6,i],liste[7,i],liste[8,i],liste[9,i]))

f1.close()


for i in range(len(name)):
    liste[1, i] = float(coins[name[i]]['low'])  # low
    liste[2, i] = float(coins[name[i]]['high'])  # high
    liste[0, i] = float(coins[name[i]]['last'])  # last
    liste[5, i] = (liste[2, i]-liste[1, i])/liste[1, i]  # Profit
    liste[6, i] = (1-liste[5, i]/3)*liste[0, i]  # Temp Buy
    liste[7, i] = (1+liste[5, i]/3)*liste[0, i]  # Temp Sell
    liste[3, i] = max(liste[6, i], liste[1, i])  # Buy
    liste[4, i] = min(liste[7, i], liste[2, i])  # Sell
    liste[8, i] = 100*(liste[4, i]-liste[3, i])/liste[3, i]  # My Profit
    liste[9, i] = liste[8, i]/liste[5, i]  # Ratio
    f2.write("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %(name[i],liste[0,i],liste[1,i],liste[2,i],liste[3,i],liste[4,i],liste[5,i],liste[6,i],liste[7,i],liste[8,i],liste[9,i]))

f2.close()


for i in range(len(name)):
    liste[1, i] = float(coins[name[i]]['low'])  # low
    liste[2, i] = float(coins[name[i]]['high'])  # high
    liste[0, i] = float(coins[name[i]]['last'])  # last
    liste[5, i] = (liste[2, i]-liste[1, i])/liste[1, i]  # Profit
    liste[6, i] = (1-liste[5, i]/4)*liste[0, i]  # Temp Buy
    liste[7, i] = (1+liste[5, i]/4)*liste[0, i]  # Temp Sell
    liste[3, i] = max(liste[6, i], liste[1, i])  # Buy
    liste[4, i] = min(liste[7, i], liste[2, i])  # Sell
    liste[8, i] = 100*(liste[4, i]-liste[3, i])/liste[3, i]  # My Profit
    liste[9, i] = liste[8, i]/liste[5, i]  # Ratio
    f3.write("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %(name[i],liste[0,i],liste[1,i],liste[2,i],liste[3,i],liste[4,i],liste[5,i],liste[6,i],liste[7,i],liste[8,i],liste[9,i]))

f3.close()


for i in range(len(name)):
    liste[1, i] = float(coins[name[i]]['low'])  # low
    liste[2, i] = float(coins[name[i]]['high'])  # high
    liste[0, i] = float(coins[name[i]]['last'])  # last
    liste[5, i] = (liste[2, i]-liste[1, i])/liste[1, i]  # Profit
    liste[6, i] = (1-liste[5, i]/5)*liste[0, i]  # Temp Buy
    liste[7, i] = (1+liste[5, i]/5)*liste[0, i]  # Temp Sell
    liste[3, i] = max(liste[6, i], liste[1, i])  # Buy
    liste[4, i] = min(liste[7, i], liste[2, i])  # Sell
    liste[8, i] = 100*(liste[4, i]-liste[3, i])/liste[3, i]  # My Profit
    liste[9, i] = liste[8, i]/liste[5, i]  # Ratio
    f4.write("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %(name[i],liste[0,i],liste[1,i],liste[2,i],liste[3,i],liste[4,i],liste[5,i],liste[6,i],liste[7,i],liste[8,i],liste[9,i]))

f4.close()


for i in range(len(name)):
    liste[1, i] = float(coins[name[i]]['low'])  # low
    liste[2, i] = float(coins[name[i]]['high'])  # high
    liste[0, i] = float(coins[name[i]]['last'])  # last
    liste[5, i] = (liste[2, i]-liste[1, i])/liste[1, i]  # Profit
    liste[6, i] = (1-liste[5, i]/args.coef)*liste[0, i]  # Temp Buy
    liste[7, i] = (1+liste[5, i]/args.coef)*liste[0, i]  # Temp Sell
    liste[3, i] = max(liste[6, i], liste[1, i])  # Buy
    liste[4, i] = min(liste[7, i], liste[2, i])  # Sell
    liste[8, i] = 100*(liste[4, i]-liste[3, i])/liste[3, i]  # My Profit
    liste[9, i] = liste[8, i]/liste[5, i]  # Ratio
    f5.write("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %(name[i],liste[0,i],liste[1,i],liste[2,i],liste[3,i],liste[4,i],liste[5,i],liste[6,i],liste[7,i],liste[8,i],liste[9,i]))

f5.close()

