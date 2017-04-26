import json
import pandas as pd
import numpy as np

f = open('data/georgia.txt', 'r')

train_data, test_data = [], []
for ln_num, ln in enumerate(f):

    # load in data file
    jdict = json.loads(ln)

    # extract demographic variables from relevant line
    if ("Gender" in jdict):
        demographics = jdict

    # extract experiment info from relevant line
    elif ("psychopyVersion" in jdict) or (ln_num == 1):
        exp_info = jdict

    # extract this participant's stimulus hierarchy order
    elif "0" in jdict:
        stim_ordering = jdict

    # extract data ouput from training and testing blocks separately
    elif "block" in jdict:
        block_type = jdict["block"].split('_')
        if block_type[1] == 'train':
            jdict['train_block#'] = block_type[0]
            train_data.append(jdict)
        elif block_type[1] == 'test':
            jdict['test_block#'] = block_type[0]
            test_data.append(jdict)
        else:
            raise Exception("Error: ooooops!")

    # don't need to load in block earnings (redundant)
    elif "block_earnings" in jdict:
        pass

    else:
        raise Exception("Error: something unexpected!")

# load training and testing blocks data into Pandas data frames
train_data_df = pd.DataFrame.from_records(train_data)
test_data_df = pd.DataFrame.from_records(test_data)

# char -> integer
train_data_df["train_block#"] = train_data_df["train_block#"].astype(int)
test_data_df["test_block#"] = test_data_df["test_block#"].astype(int)

# omit some colulmns for simplicity of output during piloting
train_data_df = train_data_df.drop(["response", "rt"], axis=1)
test_data_df = test_data_df.drop(["response", "rt"], axis=1)

# to get sum of correct responses per block
a = train_data_df.groupby("train_block#")
training_trial_summary = a.aggregate(np.sum)
print training_trial_summary

b = test_data_df.groupby("test_block#")
test_data_summary = b.aggregate(np.sum)
print test_data_summary
