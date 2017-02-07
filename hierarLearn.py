#!/usr/bin/env python

from utilities import *
from config import *


def show_one_trial(images):
    rand_i = rand_j = random.randrange(len(images))
    while rand_j == rand_i:
        rand_j = random.randrange(len(images))
    response = presenter.select_from_two_stimuli(images[rand_i], rand_i, images[rand_j], rand_j)
    correct = (response[0] >= rand_i and response[0] >= rand_j)  # responded the larger index
    feedback = FEEDBACK_RIGHT if correct else FEEDBACK_WRONG
    feedback_stim = visual.TextStim(presenter.window, text=feedback)
    presenter.draw_stimuli_for_duration(feedback_stim, duration=FEEDBACK_DURATION)

    return {'images': (rand_i, rand_j),
            'response': response,
            'correct': correct}


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
    images = presenter.load_all_images(IMG_FOLDER, '.png')
    random.shuffle(images)
    dataLogger.write_data({i: stim._imName for i, stim in enumerate(images)})

    # experiment starts
    presenter.show_instructions(INSTR_1)
    for t in range(NUM_TRIALS):
        data = show_one_trial(images)
        data['trial_index'] = t
        dataLogger.write_data(data)
    presenter.show_instructions(INSTR_2)
