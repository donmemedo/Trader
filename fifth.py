import numpy as np
from csv import reader
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--input', type=str, default='./half.csv',
                    help='input csv file.')
parser.add_argument('--output', type=str, default='./fifi.csv',
                    help='output csv file.')
parser.add_argument('--coef', type=int , metavar='N', default=5,
                    help='Margin')

args = parser.parse_args()
f = open(args.input, 'r') #today
f1 = open(args.input, 'r') #today
f2 = open(args.output, 'w') #yesterday
f2.write('name,last,low,high,buy,sell,profit,tempbuy,tempsell,myprofit,Ratio\n')
csv_reader_a = reader(f1)

lene=len(f.readlines())
liste_temp = np.zeros((lene, 7))
# open file in read mode

    # pass the file object to reader() to get the reader object
csv_reader_a = reader(f1)

# Iterate over each row in the csv using reader object
i=0
for row in csv_reader_a:
    # row variable is a list that represents a row in csv
    # print(row)
    # if not row[0]:
    #     break
    liste_temp[i][0] =row[1]
    liste_temp[i][1] =row[2]
    liste_temp[i][2] =row[3]
    # liste[1, i] = float(coins[name[i]]['low'])  # low
    # liste[2, i] = float(coins[name[i]]['high'])  # high
    # liste[0, i] = float(coins[name[i]]['last'])  # last
    profit = (liste_temp[i][2] - liste_temp[i][1]) / liste_temp[i][1]  # Profit
    tb = (1 - profit / args.coef) * liste_temp[i][0]  # Temp Buy
    ts = (1 + profit / args.coef) * liste_temp[i][0]  # Temp Sell
    buy = max(tb, liste_temp[i][1])  # Buy
    sell = min(ts, liste_temp[i][2])  # Sell
    mp = 100 * (sell - buy) / buy  # My Profit
    rat = mp / profit  # Ratio
    f2.write("%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" % (
    row[0], liste_temp[i][0], liste_temp[i][1], liste_temp[i][2], buy, sell, profit, tb, ts,
    mp, rat))
    i+=1
f2.close()
