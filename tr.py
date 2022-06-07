import numpy as np
liste = [[0]*7]*1000 #np.zeros((10, 1000))
liste_temp = np.zeros((1000, 7))
f1 = open("b.csv", 'r')
f2 = open("a.csv", 'r')

from csv import reader
# open file in read mode

    # pass the file object to reader() to get the reader object
csv_reader_a = reader(f1)
csv_reader_b = reader(f2)

# Iterate over each row in the csv using reader object
i=0
for row in csv_reader_a:
    # row variable is a list that represents a row in csv
    liste[i][0] =row[0]
    liste[i][1] =row[7]
    liste[i][2] =row[8]
    liste_temp[i][0] =row[12]
    liste_temp[i][1] =row[7]
    liste_temp[i][2] =row[8]
    i+=1
i=0
for row in csv_reader_b:
    # row variable is a list that represents a row in csv
    # liste[i,3:6]=row[0],row[2],row[3]
    liste[i][3] = row[0]
    liste[i][4] = row[2]
    liste[i][5] = row[3]
    liste_temp[i][3] = row[12]
    liste_temp[i][4] = row[2]
    liste_temp[i][5] = row[3]

    i+=1
for j in range (i):
    if liste[j][4] <= liste[j][1] and liste[j][2] <= liste[j][5]:
        liste [j][6]=1
        print("%s - %s\n"% (liste[j][0],liste[j][3]))
    if liste_temp[j][4] <= liste_temp[j][1] and liste_temp[j][2] <= liste_temp[j][5]:
        liste_temp [j][6]=1
        print("%s - %s\n"% (liste_temp[j][0],liste_temp[j][3]))