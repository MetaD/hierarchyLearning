# Numbers
NUM_BLOCKS = 12
NUM_CYCLES_TRAIN = 2
NUM_CYCLES_TEST = 1
TRAIN_PAIRS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)]
TEST_PAIRS = [(1, 3), (1, 4), (2, 4), (2, 5), (3, 5), (3, 6), (4, 6), (4, 7)]
POINTS = 20
# Paths
IMG_FOLDER = 'img/'
DATA_FOLDER = 'data/'
# Times
FIXATION_TIME = 1.5
POST_SELECTION_TIME = 1
FEEDBACK_TIME = 1  # 2
# Colors
FEEDBACK_RED = '#FF0000'
FEEDBACK_GREEN = '#84ff84'
# Strings
INSTR_1 = ['We\'re interested in individual differences in how people learn about social information.',
           'You\'re going to see pictures we\'ve taken of 9 different individuals who are all members of an ' +
           'organization.',
           'There are 2 parts to this experiment. In the first phase, you will need to learn which individuals have ' +
           'more power in the organization.',
           'In the second phase, you will have to use the knowledge you acquired during phase 1 to make judgments ' +
           'about individuals.']
INSTR_2 = 'Thank you for participating!'

INSTR_TRAIN = ['Get ready for Training trials.',
               'In training trials, press F if you think the person on the left has more power.\n\n' +
               'Press J if you think the person on the right has more power.\n\n' +
               'If you respond correctly, you\'ll win 20 points. If you respond incorrectly, you\'ll lose 20 points.']
INSTR_TEST = ['Get ready for Test trials',
              'In test trials, press F or J to choose the person who you think has more power.\n\n' +
              'You\'ll notice that there will be pairs presented together that aren\'t presented during training ' +
              'trials - here you\'ll have to use your judgement to choose the correct one.\n\n' +
              'Feedback is not provided in test trials, however, your responses count just as training trials for ' +
              'computing your pay.',
              'You will also be asked to rate your confidence in your choices during test trials on a scale of 1-3:\n' +
              '\n1 = You\'re guessing entirely\n' +
              '2 = You have some idea but are not sure\n' +
              '3 = You\'re more than 90% certain\n\n' +
              'Your confidence ratings will not affect your final payout, but try to answer as accurately as possible.']

FEEDBACK_RIGHT = '+ ' + str(POINTS) + ' points'
FEEDBACK_WRONG = '- ' + str(POINTS) + ' points'

LIKERT_SCALE_QUESTION = 'Please rate your confidence'
LIKERT_SCALE_LABELS = ('Guessing entirely', 'Not sure but have some idea', '90%-100% certain')
