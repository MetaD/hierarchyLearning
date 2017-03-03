# Numbers
NUM_BLOCKS = 2  # 12
NUM_TRIALS_TRAIN = 3  # 8
NUM_TRIALS_TEST = 3  # 8
# Paths
IMG_FOLDER = 'img/'
DATA_FOLDER = 'data/'
IMG_PREFIX = 'F'  # 'M'
# Times
FIXATION_TIME = 1.5
CHOICE_TIME = 3  # TODO
POST_SELECTION_TIME = 1
FEEDBACK_TIME = 1  # 2
# Colors
FEEDBACK_RED = '#ff807c'
FEEDBACK_GREEN = '#84ff84'
# Strings
INSTR_1 = ['We\'re interested in individual differences in how people learn about social information.',
           'You\'re going to see pictures we\'ve taken of 9 different individuals who are all members of an ' +
           'organization.',
           'There are 2 parts to this experiment. In the first phase, you will need to learn which individuals have ' +
           'more power in the organization.',
           'In the second phase, you will have to use the knowledge you acquired during phase 1 to make judgments ' +
           'about individuals.']
INSTR_3 = 'Thank you for participating!'

INSTR_TRAIN = ['Get ready for Training trials.',
               'Press F if you think the person on the left has more power.\n' +
               'Press J if you think the person on the right has more power.\n' +
               'If you respond correctly, you\'ll win 20 points. If you respond incorrectly, you\'ll lose 20 points.']
INSTR_TEST = ['Get ready for Test trials',
              'In test trials, press F or J to choose the person who you think has more power.\n' +
              'Then, rate on a scale of 1 to 3 your confidence in your decision:\n' +
              '1 = You\'re guessing entirely\n' +
              '2 = You have some idea but are not sure\n' +
              '3 = You\'re more than 90% certain\n' +
              'Your confidence ratings will not affect your final payout, but try to answer as accurately as possible.']

FEEDBACK_RIGHT = '+ 20 points'
FEEDBACK_WRONG = '- 20 points'

LIKERT_SCALE_QUESTION = 'Please rate your confidence'
LIKERT_SCALE_LABELS = ('Guessing entirely', 'Not sure but have some idea', '90%-100% certain')
