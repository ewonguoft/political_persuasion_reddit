from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import confusion_matrix

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
        rec = recall(confuse)
        pre = precision(confuse)

        if acc > iBest:
            iBest = i

        result = []
        result.append(i)
        result.append(acc)
        result.extend(rec)
        result.extend(pre)

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
    print('TODO Section 3.2')

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
    print('TODO Section 3.3')

def class34( filename, i ):
    ''' This function performs experiment 3.4

    Parameters
       filename : string, the name of the npz file from Task 2
       i: int, the index of the supposed best classifier (from task 3.1)
        '''
    print('TODO Section 3.4')

def main(args):
    res = class31(args.input)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='section 3')
    parser.add_argument("-i", "--input", help="the input npz file from Task 2", required=True)
    args = parser.parse_args()

    # TODO : complete each classification experiment, in sequence.
    main(args)
