import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--yesterday', type=str, default='./a.csv',
                    help='input csv file.')
parser.add_argument('--today', type=str, default='./b.csv',
                    help='output csv file.')

args = parser.parse_args()

# liste = [[0]*7]*1000 #np.zeros((10, 1000))
liste_temp = np.zeros((1000, 7))
f1 = open(args.today, 'r') #today
f2 = open(args.yesterday, 'r') #yesterday

from csv import reader
# open file in read mode

    # pass the file object to reader() to get the reader object
csv_reader_a = reader(f2)
csv_reader_b = reader(f1)

# Iterate over each row in the csv using reader object
i=0
for row in csv_reader_a:
    # row variable is a list that represents a row in csv
    liste_temp[i][0] =row[12]
    liste_temp[i][1] =row[7]
    liste_temp[i][2] =row[8]
    i+=1
i2=0
for row in csv_reader_b:
    # row variable is a list that represents a row in csv
    # liste[i,3:6]=row[0],row[2],row[3]

    liste_temp[i2][3] = row[12]
    liste_temp[i2][4] = row[2]
    liste_temp[i2][5] = row[3]

    i2+=1
k=0
for j in range (i):
    c=int(liste_temp[j][0])-1
    # if liste[c][4] <= liste[j][1] and liste[j][2] <= liste[c][5]:
    #     liste [j][6]=1
    #     print("%s - %s\n"% (liste[j][0],liste[c][3]))
    if liste_temp[c][4] <= liste_temp[j][1] and liste_temp[j][2] <= liste_temp[c][5]:
        liste_temp [j][6]=1
        print("%s - %s\n"% (liste_temp[j][0],liste_temp[c][3]))
        k+=1

print(k)