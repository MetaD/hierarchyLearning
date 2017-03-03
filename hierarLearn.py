#!/usr/bin/env python

from utilities import *
from config import *


def show_one_trial(images, adjacent, feedback, rating):
    presenter.show_fixation(1)
    # get random image indexes
    if adjacent:
        rand_i = random.randrange(len(images) - 1)
        rand_j = rand_i + 1
        if random.randrange(2) == 0:  # switch side
            rand_i, rand_j = rand_j, rand_i
    else:
        rand_i = rand_j = random.randrange(len(images))
        while rand_j == rand_i:
            rand_j = random.randrange(len(images))
    # define correctness
    def correctness(selection):
        return selection <= rand_i and selection <= rand_j  # responded the smaller index == higher status
    # feedback
    if feedback:
        feedback_stims = (visual.TextStim(presenter.window, text=FEEDBACK_RIGHT, color=FEEDBACK_GREEN),
                          visual.TextStim(presenter.window, text=FEEDBACK_WRONG, color=FEEDBACK_RED))
        # display, respond & feedback
        response = presenter.select_from_two_stimuli(images[rand_i], rand_i, images[rand_j], rand_j, random_side=False,
                                                     post_selection_time=0, correctness_func=correctness,
                                                     feedback_stims=feedback_stims, feedback_time=FEEDBACK_TIME)
        correct = response[2]
    else:
        # display & respond
        response = presenter.select_from_two_stimuli(images[rand_i], rand_i, images[rand_j], rand_j, random_side=False,
                                                     post_selection_time=POST_SELECTION_TIME)
        correct = correctness(response[0])
    # rating
    if rating:
        presenter.LIKERT_SCALE_OPTION_INTERVAL = 0.4
        certainty = presenter.likert_scale(LIKERT_SCALE_QUESTION, num_options=3, option_labels=LIKERT_SCALE_LABELS)
    # data
    result = {'images': (rand_i, rand_j),
              'response': response[:2],
              'correct': correct}
    if rating:
        result['certainty'] = certainty
    return result


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
    sinfo = {'ID': '', 'Gender': ['Female', 'Male'], 'Age': '', 'Mode': ['Test', 'Exp']}
    show_form_dialog(sinfo, validation, order=['ID', 'Gender', 'Age', 'Mode'])
    sid = int(sinfo['ID'])

    # create data file
    dataLogger = DataHandler(DATA_FOLDER, str(sid) + '.dat')
    # save info from the dialog box
    dataLogger.write_data({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # create window
    presenter = Presenter(fullscreen=(sinfo['Mode'] == 'Exp'))
    dataLogger.write_data(presenter.expInfo)
    # load images
    images = presenter.load_all_images(IMG_FOLDER, '.jpg', IMG_PREFIX)
    # randomize
    random.seed(sid)
    random.shuffle(images)  # status high -> low
    dataLogger.write_data({i: stim._imName for i, stim in enumerate(images)})

    # experiment starts
    presenter.show_instructions(INSTR_1)
    for block in range(NUM_BLOCKS):
        # train
        presenter.show_instructions(INSTR_TRAIN)
        for t in range(NUM_TRIALS_TRAIN):
            data = show_one_trial(images, adjacent=True, feedback=True, rating=False)
            data['trial_index'] = t
            dataLogger.write_data(data)
        # test
        presenter.show_instructions(INSTR_TEST)
        for t in range(NUM_TRIALS_TEST):
            data = show_one_trial(images, adjacent=False, feedback=False, rating=True)
            data['trial_index'] = t
            dataLogger.write_data(data)
    presenter.show_instructions(INSTR_3)
