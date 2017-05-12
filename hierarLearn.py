#!/usr/bin/env python

from utilities import *
from config import *
import time


def show_one_trial(images, indexes, feedback, rating):
    presenter.show_fixation(FIXATION_TIME)
    indexes = list(indexes)
    random.shuffle(indexes)
    i = indexes[0]
    j = indexes[1]
    choose = visual.TextStim(presenter.window, 'Choose')
    data = {'stimuli': (i, j), 'no_response_loops': 0}
    # images & selection
    while True:
        presenter.draw_stimuli_for_duration(images[i], FIRST_IMG_TIME)
        presenter.show_blank(IMG_INTERVAL)
        presenter.draw_stimuli_for_duration(images[j], SECOND_IMG_TIME)
        response = presenter.draw_stimuli_for_response(choose, IMG_RESPONSE_KEYS, max_wait=MAX_WAIT_TIME)
        if response is None:
            data['no_response_loops'] += 1
        else:
            data.update(response)
            break
    # feedback
    selected_stim = images[i] if response['response'] == IMG_RESPONSE_KEYS[0] else images[j]
    correct = i < j if response['response'] == IMG_RESPONSE_KEYS[0] else j < i
    data['correct'] = correct
    if feedback:
        feedback_stim = visual.TextStim(presenter.window, text=FEEDBACK_RIGHT, color=FEEDBACK_GREEN) if correct else \
                        visual.TextStim(presenter.window, text=FEEDBACK_WRONG, color=FEEDBACK_RED)
        feedback_stim.pos = FEEDBACK_POSITION
        feedback_stim.height = 0.13
        presenter.draw_stimuli_for_duration([selected_stim, highlight, feedback_stim], FEEDBACK_TIME)
        # reinforcement
        words = ['MORE', 'LESS'] if i < j else ['LESS', 'MORE']
        presenter.show_instructions(INSTR_REINFORCE[0] + words[0] + INSTR_REINFORCE[1], position=TOP_INSTR_POSITION,
                                    other_stim=[images[i]])
        presenter.show_instructions(INSTR_REINFORCE[0] + words[1] + INSTR_REINFORCE[1], position=TOP_INSTR_POSITION,
                                    other_stim=[images[j]])
    else:
        presenter.draw_stimuli_for_duration([selected_stim, highlight], FEEDBACK_TIME)
    # rating
    if rating:
        certainty = presenter.likert_scale(LIKERT_SCALE_QUESTION, num_options=3, option_labels=LIKERT_SCALE_LABELS)
        data['certainty'] = certainty

    return data


def show_one_block(block_i):
    points = 0
    # train
    presenter.show_instructions(INSTR_TRAIN)
    num_correct = 0
    for t in range(NUM_CYCLES_PER_BLOCK_TRAIN):
        random.shuffle(TRAIN_PAIRS)
        for pair in TRAIN_PAIRS:
            data = show_one_trial(images, pair, feedback=True, rating=False)
            data['block'] = str(block_i) + '_train_' + str(t)
            dataLogger.write_data(data)
            points += (1 if data['correct'] else -1) * POINTS
            num_correct += 1 if data['correct'] else 0
    training_accuracy.append(float(num_correct) / (NUM_CYCLES_PER_BLOCK_TRAIN * len(TRAIN_PAIRS)))
    # test
    presenter.show_instructions(INSTR_TEST)
    for t in range(NUM_CYCLES_PER_BLOCK_TEST):
        for pair in TEST_PAIRS:
            data = show_one_trial(images, pair, feedback=False, rating=True)
            data['block'] = str(block_i) + '_test'
            dataLogger.write_data(data)
            points += (1 if data['correct'] else -1) * POINTS
    presenter.show_instructions('Your score is ' + points + ' in this block.')
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
    random.seed(time.time())

    # experiment starts
    presenter.show_instructions(INSTR_1)
    training_accuracy = []  # accuracy in each block
    for block in range(NUM_BLOCKS):
        show_one_block(block)
    # additional blocks
    num_additional_blocks = 0
    while (training_accuracy[-1] < PASSING_ACCURACY or training_accuracy[-2] < PASSING_ACCURACY) \
            and num_additional_blocks < MAX_ADDITIONAL_BLOCKS:
        show_one_block(NUM_BLOCKS + num_additional_blocks)
        num_additional_blocks += 1
    # end
    presenter.show_instructions(INSTR_2)
    print 'training:', training_accuracy
