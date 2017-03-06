# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from gplearn.genetic import SymbolicRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor

import numpy
import csv


x_train_data = []
y_train_data = []

x_test_data = []
y_test_data = []

with open('train_data.csv', 'rb') as train:
    reader = csv.reader(train)
    for row in reader:

        # code: 0
        # name: 1
        # outstanding: 2
        # totals: 3
        # pe: 4
        # holders: 5
        # date: 6
        # open: 7
        # high: 8
        # close: 9
        # low: 10
        # volume: 11
        # p_change: 12
        # total_dd: 13
        # total_buy_dd: 14
        # total_sell_dd: 15
        # last_30_mins_dd: 16
        # last_30_mins_buy_dd: 17
        # last_30_mins_sell_dd: 18
        # last_15_mins_dd: 19
        # last_15_mins_buy_dd: 20
        # last_15_mins_sell_dd: 21
        # total_dd_in_rmb: 22
        # total_dd_out_rmb: 23
        # last_15_mins_dd_in_rmb: 24
        # last_15_mins_dd_out_rmb: 25
        # last_30_mins_dd_in_rmb: 26
        # last_30_mins_dd_out_rmb: 27
        # next_day_high_p: 28
        # next_day_close_p: 29
        # item = [row[2], row[3], row[4], row[5], row[7], row[8], row[9], row[10], row[11], row[12],
        #         row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],
        #         row[23],row[24],row[25],row[26], row[27]]
        item = [float(row[13]), float(row[14])]
        target = float(row[28])
        x_train_data.append(item)
        y_train_data.append(target)

with open('test_data.csv', 'rb') as test:
    reader = csv.reader(test)
    for row in reader:
        # item = [row[2], row[3], row[4], row[5], row[7], row[8], row[9], row[10], row[11], row[12],
        #         row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],
        #         row[23],row[24],row[25],row[26], row[27]]
        item = [float(row[13]), float(row[14])]
        target = float(row[28])
        x_test_data.append(item)
        y_test_data.append(target)

est_gp = SymbolicRegressor(population_size=500,
                           generations=20, stopping_criteria=0.01,
                           p_crossover=0.7, p_subtree_mutation=0.1,
                           p_hoist_mutation=0.05, p_point_mutation=0.1,
                           max_samples=0.9, verbose=1,
                           parsimony_coefficient=0.01, random_state=0)
x_train_data = numpy.array(x_train_data)
y_train_data = numpy.array(y_train_data)
print type(x_train_data[1][1])
print y_train_data
est_gp.fit(x_train_data, y_train_data)

print est_gp._program



