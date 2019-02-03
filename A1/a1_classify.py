from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import chi2
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold
from scipy import stats

import numpy as np
import argparse
import sys
import os
import csv

def accuracy( C ):
    ''' Compute accuracy given Numpy array confusion matrix C. Returns a floating point value '''
    return np.trace(C) / np.sum(C)

def recall( C ):
    ''' Compute recall given Numpy array confusion matrix C. Returns a list of floating point values '''
    recalls = []
    for i in range(C.shape[0]):
        recalls.append(C[i,i]/np.sum(C[i,:]))

    return recalls

def precision( C ):
    ''' Compute precision given Numpy array confusion matrix C. Returns a list of floating point values '''
    recalls = []
    for i in range(C.shape[0]):
        recalls.append(C[i,i]/np.sum(C[:,i]))

    return recalls

def class31(filename):
    ''' This function performs experiment 3.1

    Parameters
       filename : string, the name of the npz file from Task 2

    Returns:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier
    '''
    all_results = []
    iBest = 0
    feats = np.load(filename)
    feats = feats[feats.files[0]]
    y = feats[:,-1]
    X = np.delete(feats, -1, axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, train_size=0.8)

    for i in range(1,6):
        if i == 1:
            clf = LinearSVC()
        elif i == 2:
            clf = SVC(gamma=2)
        elif i == 3:
            clf = RandomForestClassifier(max_depth=5, n_estimators=10)
        elif i == 4:
            clf = MLPClassifier(alpha=0.05)
        elif i == 5:
            clf = AdaBoostClassifier()

        clf.fit(X_train, y_train)
        y_predict = clf.predict(X_test)
        confuse = confusion_matrix(y_test, y_predict)
        acc = accuracy(confuse)

        if acc > iBest:
            iBest = i

        result = []
        result.append(i)
        result.append(acc)
        result.extend(recall(confuse))
        result.extend(precision(confuse))

        for j in range(confuse.shape[0]):
            result.extend(confuse[j,:])
        all_results.append(result)

    with open("a1_3.1.csv", "w") as file:
        writer = csv.writer(file)
        for row in all_results:
            writer.writerow(row)


    return (X_train, X_test, y_train, y_test,iBest)


def class32(X_train, X_test, y_train, y_test,iBest):
    ''' This function performs experiment 3.2

    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)

    Returns:
       X_1k: numPy array, just 1K rows of X_train
       y_1k: numPy array, just 1K rows of y_train
   '''

    sizes = [1000,5000,10000,15000,20000]
    acc = []
    clf = chooseBest(iBest)

    for i in sizes:
        idx = np.random.randint(X_train.shape[0], size=i)
        X_train_mod = X_train[idx,:]
        Y_train_mod = y_train[idx]

        clf.fit(X_train_mod,Y_train_mod)
        y_predict = clf.predict(X_test)
        confuse = confusion_matrix(y_test, y_predict)
        acc.append(accuracy(confuse))

        if i == 1000:
            X_1k = X_train_mod
            y_1k = Y_train_mod

    with open("a1_3.2.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(acc)

    return (X_1k, y_1k)


def class33(X_train, X_test, y_train, y_test, i, X_1k, y_1k):
    ''' This function performs experiment 3.3

    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)
       X_1k: numPy array, just 1K rows of X_train (from task 3.2)
       y_1k: numPy array, just 1K rows of y_train (from task 3.2)
    '''

    features = [5,10,20,30,40,50]
    all_results = []
    X_5_train = []
    X_5_test = []

    for feat in features:
        #32k
        selector = SelectKBest(f_classif,k=feat)
        X_new = selector.fit_transform(X_train, y_train)
        pp = selector.pvalues_

        #1k
        selector_1k = SelectKBest(f_classif, k=feat)
        X_new_1k = selector_1k.fit_transform(X_1k, y_1k)

        #get index num to get the top features index
        index = selector.get_support(indices=True)
        #print(index)
        index_1k = selector_1k.get_support(indices=True)
        #print(index_1k)

        temp = []
        temp.append(feat)
        for k in range(0,len(index)):
            temp.append(pp[index[k]])

        all_results.append(temp)

        if feat == 5:
            X_5_train = X_new
            X_5_test = X_test[:,index]
            #print(X_5_test.shape)
            #print(X_5_train.shape)
            X_5_train_1k = X_new_1k
            #print(X_5_train_1k.shape)

    #32k
    clf = chooseBest(i)
    clf.fit(X_5_train, y_train)
    y_predict = clf.predict(X_5_test)
    confuse = confusion_matrix(y_test, y_predict)
    acc = accuracy(confuse)

    #1k
    clf_1k = chooseBest(i)
    clf_1k.fit(X_5_train_1k, y_1k)
    y_predict_1k = clf_1k.predict(X_5_test)
    confuse_1k = confusion_matrix(y_test, y_predict_1k)
    acc_1k = accuracy(confuse_1k)

    all_results.append([acc_1k, acc])

    with open("a1_3.3.csv", "w") as file:
        writer = csv.writer(file)
        for row in all_results:
            writer.writerow(row)


def class34( filename, i ):
    ''' This function performs experiment 3.4

    Parameters
       filename : string, the name of the npz file from Task 2
       i: int, the index of the supposed best classifier (from task 3.1)
        '''
    all_results = []
    feats = np.load(filename)
    feats = feats[feats.files[0]]
    y = feats[:,-1]
    X = np.delete(feats, -1, axis=1)

    for j in range(1,6):
        clf = chooseBest(j)
        accs = []
        kfolds = KFold(n_splits=5, shuffle=True)
        for train_index, test_index in kfolds.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf.fit(X_train, y_train)
            y_predict = clf.predict(X_test)
            confuse = confusion_matrix(y_test, y_predict)
            accs.append(accuracy(confuse))

        all_results.append(accs)

    p_val = []
    a = np.array(all_results[i-1])

    for k in range(len(a)):
        if k != (i-1):
            b = np.array(all_results[k])
            p_val.append(stats.ttest_rel(a,b))

    all_results.append(p_val)
    with open("a1_3.4.csv", "w") as file:
        writer = csv.writer(file)
        for row in all_results:
            writer.writerow(row)


def chooseBest(iBest):
    if iBest == 1:
        clf = LinearSVC()
    elif iBest == 2:
        clf = SVC(gamma=2)
    elif iBest == 3:
        clf = RandomForestClassifier(max_depth=5, n_estimators=10)
    elif iBest == 4:
        clf = MLPClassifier(alpha=0.05)
    elif iBest == 5:
        clf = AdaBoostClassifier()

    return clf

def main(args):
    X_train, X_test, y_train, y_test,iBest = class31(args.input)
    X_1k, y_1k = class32(X_train, X_test, y_train, y_test,iBest)
    class33(X_train, X_test, y_train, y_test, iBest, X_1k, y_1k)
    class34(args.input,iBest)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='section 3')
    parser.add_argument("-i", "--input", help="the input npz file from Task 2", required=True)
    args = parser.parse_args()

    # TODO : complete each classification experiment, in sequence.
    main(args)
