#!/usr/bin/env python

from psychopy_util import *
from config import *


def show_one_trial(images, indexes, score, feedback, rating):
    presenter.show_fixation(1)
    i, j = indexes
    if random.randrange(2) == 0:
        i, j = j, i
    images[i].pos = presenter.LEFT_CENTRAL_POS
    images[j].pos = presenter.RIGHT_CENTRAL_POS
    # show images and get response
    stimuli = [images[i], images[j]]
    trial_info = presenter.select_from_stimuli(stimuli, (i, j), ('f', 'j'),
                                               post_selection_time=POST_SELECTION_TIME, highlight=highlight)
    selection = trial_info['response']
    trial_info['correct'] = selection <= i and selection <= j  # responded the smaller index == higher status
    # rating
    if rating:
        certainty = presenter.likert_scale(LIKERT_SCALE_QUESTION, num_options=3, option_labels=LIKERT_SCALE_LABELS)
        trial_info['certainty'] = certainty
    # feedback
    if feedback:
        if trial_info['correct']:
            stimuli.append(visual.TextStim(presenter.window, text=FEEDBACK_RIGHT.format(score), color=FEEDBACK_GREEN))
        else:
            stimuli.append(visual.TextStim(presenter.window, text=FEEDBACK_WRONG.format(score), color=FEEDBACK_RED))
        presenter.draw_stimuli_for_duration(stimuli, FEEDBACK_TIME)

    return trial_info


def show_one_block(block_i):
    points = 0
    # train
    presenter.show_instructions(INSTR_TRAIN)
    num_correct = 0
    for t in range(NUM_CYCLES_PER_BLOCK_TRAIN):
        random.shuffle(TRAIN_PAIRS)
        for pair in TRAIN_PAIRS:
            data = show_one_trial(images, pair, score=TRAIN_POINTS, feedback=True, rating=False)
            data['block'] = str(block_i) + '_train_' + str(t)
            dataLogger.write_data(data)
            points += (1 if data['correct'] else -1) * TRAIN_POINTS
            num_correct += 1 if data['correct'] else 0
    training_accuracy.append(float(num_correct) / (NUM_CYCLES_PER_BLOCK_TRAIN * len(TRAIN_PAIRS)))
    # test
    presenter.show_instructions(INSTR_TEST)
    for t in range(NUM_CYCLES_PER_BLOCK_TEST):
        random.shuffle(TEST_PAIRS)
        for pair in TEST_PAIRS:
            data = show_one_trial(images, pair, score=TEST_POINTS, feedback=True, rating=True)
            data['block'] = str(block_i) + '_test'
            dataLogger.write_data(data)
            points += (1 if data['correct'] else -1) * TEST_POINTS
    presenter.show_instructions('Your score is ' + str(points) + ' in this block.')
    dataLogger.write_data({'block_earnings': points})


def validation(items):
    # check empty field
    for key in items.keys():
        if items[key] is None or len(items[key]) == 0:
            return False, str(key) + ' cannot be empty.'
    # check age
    try:
        if int(items['Age']) <= 0:
            raise ValueError
    except ValueError:
        return False, 'Age must be a positive integer'
    # everything is okay
    return True, ''


if __name__ == '__main__':
    # subject ID dialog
    sinfo = {'ID': '', 'Gender': ['Female', 'Male'], 'Age': '', 'Mode': ['Exp', 'Test']}
    show_form_dialog(sinfo, validation, order=['ID', 'Gender', 'Age', 'Mode'])
    sid = int(sinfo['ID'])
    img_prefix = sinfo['Gender'][0]

    # create data file
    dataLogger = DataHandler(DATA_FOLDER, str(sid) + '.txt')
    # save info from the dialog box
    dataLogger.write_data({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # create window
    presenter = Presenter(fullscreen=(sinfo['Mode'] == 'Exp'))
    presenter.LIKERT_SCALE_OPTION_INTERVAL = 0.7
    dataLogger.write_data(presenter.expInfo)
    # load images
    images = presenter.load_all_images(IMG_FOLDER, '.jpg', img_prefix)
    highlight = visual.ImageStim(presenter.window, image=IMG_FOLDER + 'highlight.png')
    # randomize
    random.seed(sid)
    random.shuffle(images)  # status high -> low
    dataLogger.write_data({i: stim._imName for i, stim in enumerate(images)})

    # experiment starts
    presenter.show_instructions(INSTR_1)
    training_accuracy = []  # accuracy in each block
    for block in range(NUM_BLOCKS):
        show_one_block(block)
    # additional blocks
    num_additional_blocks = 0

    def low_accuracy():
        if training_accuracy[-1] < 0.85 and training_accuracy[-2] < 0.85:  # < 14/16
            return True
        if training_accuracy[-1] < 0.8 or training_accuracy[-2] < 0.8:  # < 13/16
            return True
        return False

    while low_accuracy() and num_additional_blocks < MAX_ADDITIONAL_BLOCKS:
        show_one_block(NUM_BLOCKS + num_additional_blocks)
        num_additional_blocks += 1
    # end
    presenter.show_instructions(INSTR_2)
    print 'training:', training_accuracy
