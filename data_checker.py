import os
from data_utilities import *


DATA_FOLDER = 'data/'
CSV_TRAIN = 'learning_data_train.csv'
CSV_TEST = 'learning_data_test.csv'

all_trainings, all_tests = [], []
for datafile in os.listdir(DATA_FOLDER):
    if not datafile.endswith('.txt') or not datafile[0].isdigit():
        continue
    sdata = load_json(DATA_FOLDER + datafile, multiple_obj=True)
    training, test = [datafile[:-4]], [datafile[:-4]]
    for trial in sdata:
        if 'block' in trial:
            block_type = trial['block']
            data_list = training if 'train' in block_type else test
            correct = 1 if trial['correct'] else 0
            try:
                data_list[int(block_type.split('_')[0]) + 1] += correct
            except IndexError:
                data_list.append(correct)
    all_trainings.append(training)
    all_tests.append(test)


def write(csvname, data):
    with open(csvname, 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(['ID'] + ['block_' + str(i) for i in range(16)])
        for line in data:
            writer.writerow(line)

write(CSV_TRAIN, all_trainings)
write(CSV_TEST, all_tests)
