#!/usr/bin/env python

from utilities import *
from config import *


def show_one_trial(images, indexes, feedback, rating):
    presenter.show_fixation(1)
    i = indexes[0]
    j = indexes[1]
    # define correctness
    def correctness(selection):
        return selection <= i and selection <= j  # responded the smaller index == higher status
    # feedback
    if feedback:
        feedback_stims = (visual.TextStim(presenter.window, text=FEEDBACK_WRONG, color=FEEDBACK_RED),
                          visual.TextStim(presenter.window, text=FEEDBACK_RIGHT, color=FEEDBACK_GREEN))
        # display, respond & feedback
        trial_info = presenter.select_from_two_stimuli(images[i], i, images[j], j, post_selection_time=0,
                                                       highlight=highlight, correctness_func=correctness,
                                                       feedback_stims=feedback_stims, feedback_time=FEEDBACK_TIME)
    else:
        # display & respond
        trial_info = presenter.select_from_two_stimuli(images[i], i, images[j], j,
                                                       post_selection_time=POST_SELECTION_TIME, highlight=highlight)
        trial_info['correct'] = correctness(trial_info['response'])
    # rating
    if rating:
        certainty = presenter.likert_scale(LIKERT_SCALE_QUESTION, num_options=3, option_labels=LIKERT_SCALE_LABELS)
        trial_info['certainty'] = certainty

    return trial_info


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
    IMG_PREFIX = sinfo['Gender'][0]

    # create data file
    dataLogger = DataHandler(DATA_FOLDER, str(sid) + '.dat')
    # save info from the dialog box
    dataLogger.write_data({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # create window
    presenter = Presenter(fullscreen=(sinfo['Mode'] == 'Exp'))
    presenter.LIKERT_SCALE_OPTION_INTERVAL = 0.7
    dataLogger.write_data(presenter.expInfo)
    # load images
    images = presenter.load_all_images(IMG_FOLDER, '.jpg', IMG_PREFIX)
    highlight = visual.ImageStim(presenter.window, image=IMG_FOLDER + 'highlight.png')
    # randomize
    random.seed(sid)
    random.shuffle(images)  # status high -> low
    dataLogger.write_data({i: stim._imName for i, stim in enumerate(images)})

    # experiment starts
    presenter.show_instructions(INSTR_1)
    for block in range(NUM_BLOCKS):
        points = 0
        # train
        presenter.show_instructions(INSTR_TRAIN)
        for t in range(NUM_CYCLES_TRAIN):
            random.shuffle(TRAIN_PAIRS)
            for pair in TRAIN_PAIRS:
                data = show_one_trial(images, pair, feedback=True, rating=False)
                data['block'] = str(block) + '_train_' + str(t)
                dataLogger.write_data(data)
                points += (1 if data['correct'] else -1) * POINTS
        # test
        presenter.show_instructions(INSTR_TEST)
        for t in range(NUM_CYCLES_TEST):
            for pair in TEST_PAIRS:
                data = show_one_trial(images, pair, feedback=False, rating=True)
                data['block'] = str(block) + '_test'
                dataLogger.write_data(data)
                points += (1 if data['correct'] else -1) * POINTS
        presenter.show_instructions('You earned total of ' + str(points) + ' points in this block.')
        dataLogger.write_data({'block_earnings': points})
    presenter.show_instructions(INSTR_2)
