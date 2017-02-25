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
    # display & respond
    response = presenter.select_from_two_stimuli(images[rand_i], rand_i, images[rand_j], rand_j, random_side=False)
    # feedback
    correct = (response[0] >= rand_i and response[0] >= rand_j)  # responded the larger index
    if feedback:
        feedback = FEEDBACK_RIGHT if correct else FEEDBACK_WRONG
        feedback_color = FEEDBACK_GREEN if correct else FEEDBACK_RED
        feedback_stim = visual.TextStim(presenter.window, text=feedback, color=feedback_color)
        presenter.draw_stimuli_for_duration(feedback_stim, duration=FEEDBACK_DURATION)
    # rating
    certainty = presenter.likert_scale('How sure?', num_options=3, side_labels=('Meh', 'So sure')) if rating else None

    return {'images': (rand_i, rand_j),
            'response': response,
            'correct': correct,
            'certainty': certainty}


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
    random.shuffle(images)
    dataLogger.write_data({i: stim._imName for i, stim in enumerate(images)})

    # experiment starts
    presenter.show_instructions(INSTR_1)
    # train
    for t in range(NUM_TRIALS_TRAIN):
        data = show_one_trial(images, adjacent=True, feedback=True, rating=False)
        data['trial_index'] = t
        dataLogger.write_data(data)
    presenter.show_instructions(INSTR_2)
    # test
    for t in range(NUM_TRIALS_TEST):
        data = show_one_trial(images, adjacent=False, feedback=False, rating=True)
        data['trial_index'] = t
        dataLogger.write_data(data)
    presenter.show_instructions(INSTR_3)
