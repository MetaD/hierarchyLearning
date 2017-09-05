#!/usr/bin/env python

import time
from psychopy import iohub
from psychopy_util import *
from config import *


def press_select(img_indexes):
    # choose
    choose = visual.TextStim(presenter.window, INSTR_PRESS)
    presenter.draw_stimuli_for_duration(choose)
    start_time = core.getTime()
    # get a key press
    io.clearEvents('all')
    press = keyboard.waitForPresses(chars=[RESPONSE_CHAR])[0]
    data = {'stimuli': img_indexes, 'num_img_shown': 0, 'rt': press.time - start_time}
    # start the choosing loop
    while True:
        for i in img_indexes:
            data['num_img_shown'] += 1
            for t in range(NUM_REFRESHS_PER_IMG):
                fraction = float(1 + t) / NUM_REFRESHS_PER_IMG
                radius = fraction * (CIRCLE_RADIUS - IMG_HALF_SIDE) + IMG_HALF_SIDE
                circle = visual.Circle(presenter.window, units='pix', lineWidth=0, fillColor='#808080',
                                       edges=CIRCLE_EDGES, radius=radius, opacity=fraction)
                presenter.draw_stimuli_for_duration([circle_bg, circle, images[i]])
                releases = keyboard.getReleases(chars=[RESPONSE_CHAR])
                if len(releases) > 0:
                    data['response'] = i
                    data['key_press_duration'] = releases[0].duration
                    return data
                time.sleep(float(IMG_OPTION_TIME) / NUM_REFRESHS_PER_IMG)


def show_one_trial(indexes, score, feedback, rating):
    # randomize order
    indexes = list(indexes)
    random.shuffle(indexes)
    i, j = indexes
    # start trial
    presenter.show_fixation(FIXATION_TIME)
    presenter.draw_stimuli_for_duration(images[i], FIRST_IMG_TIME)
    presenter.show_blank_screen(IMG_INTERVAL)
    presenter.draw_stimuli_for_duration(images[j], SECOND_IMG_TIME)
    data = press_select(img_indexes=(i, j))
    # feedback
    selected_stim = images[data['response']]
    correct = data['response'] <= i and data['response'] <= j
    data['correct'] = correct
    if feedback:
        feedback_stim = visual.TextStim(presenter.window, text=FEEDBACK_RIGHT.format(score), color=FEEDBACK_GREEN) if correct else \
                        visual.TextStim(presenter.window, text=FEEDBACK_WRONG.format(score), color=FEEDBACK_RED)
        feedback_stim.pos = FEEDBACK_POSITION
        feedback_stim.height = 0.13
        presenter.draw_stimuli_for_duration([selected_stim, highlight, feedback_stim], FEEDBACK_TIME)
        # reinforcement
        words = ['FUL', 'LESS'] if i < j else ['LESS', 'FUL']
        presenter.show_instructions(INSTR_REINFORCE + words[0], position=TOP_INSTR_POSITION,
                                    other_stim=[images[i]], next_key=NEXT_PAGE_KEY)
        presenter.show_instructions(INSTR_REINFORCE + words[1], position=TOP_INSTR_POSITION,
                                    other_stim=[images[j]], next_key=NEXT_PAGE_KEY)
    else:
        presenter.draw_stimuli_for_duration([selected_stim, highlight], FEEDBACK_TIME)
    # rating
    if rating:
        certainty = presenter.likert_scale(LIKERT_SCALE_QUESTION, num_options=3, option_labels=LIKERT_SCALE_LABELS)
        data['certainty'] = certainty
    print data
    return data


def show_one_block(block_i):
    points = 0
    # train
    presenter.show_instructions(INSTR_TRAIN, next_key=NEXT_PAGE_KEY)
    num_correct = 0
    for t in range(NUM_CYCLES_PER_BLOCK_TRAIN):
        random.shuffle(TRAIN_PAIRS)
        for pair in TRAIN_PAIRS:
            data = show_one_trial(pair, score=TRAIN_POINTS, feedback=True, rating=False)
            data['block'] = str(block_i) + '_train_' + str(t)
            dataLogger.write_data(data)
            points += (1 if data['correct'] else -1) * TRAIN_POINTS
            num_correct += 1 if data['correct'] else 0
    training_accuracy.append(float(num_correct) / (NUM_CYCLES_PER_BLOCK_TRAIN * len(TRAIN_PAIRS)))
    # test
    presenter.show_instructions(INSTR_TEST, next_key=NEXT_PAGE_KEY)
    for t in range(NUM_CYCLES_PER_BLOCK_TEST):
        random.shuffle(TEST_PAIRS)
        for pair in TEST_PAIRS:
            data = show_one_trial(pair, score=TEST_POINTS, feedback=True, rating=True)
            data['block'] = str(block_i) + '_test'
            dataLogger.write_data(data)
            points += (1 if data['correct'] else -1) * TEST_POINTS
    presenter.show_instructions('Your score is ' + str(points) + ' in this block.', next_key=NEXT_PAGE_KEY)
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
    sinfo = {'ID': '', 'Gender': ['Female', 'Male'], 'Age': '', 'Mode': ['Test', 'Exp']}
    show_form_dialog(sinfo, validation, order=['ID', 'Gender', 'Age', 'Mode'])
    sid = int(sinfo['ID'])
    img_prefix = sinfo['Gender'][0]

    # create data file
    dataLogger = DataHandler(DATA_FOLDER, str(sid) + '.txt')
    # save info from the dialog box
    dataLogger.write_data({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # setup window and presenter
    io = iohub.launchHubServer(psychopy_monitor_name='default')
    keyboard = io.devices.keyboard
    presenter = Presenter(fullscreen=(sinfo['Mode'] == 'Exp'))
    dataLogger.write_data(presenter.expInfo)
    presenter.LIKERT_SCALE_OPTION_INTERVAL = 0.7
    # load images
    images = presenter.load_all_images(IMG_FOLDER, '.jpg', img_prefix)
    highlight = visual.ImageStim(presenter.window, image=IMG_FOLDER + 'highlight.png')
    # randomize
    random.seed(sid)
    random.shuffle(images)  # status high -> low
    dataLogger.write_data({i: stim._imName for i, stim in enumerate(images)})
    random.seed(time.time())
    # background circle
    circle_bg = visual.Circle(presenter.window, units='pix', fillColor='#fff', radius=CIRCLE_RADIUS,
                              edges=CIRCLE_EDGES)

    # experiment starts
    presenter.show_instructions(INSTR_1, next_key=NEXT_PAGE_KEY)
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
    presenter.show_instructions(INSTR_2, next_key=NEXT_PAGE_KEY)
    print 'training:', training_accuracy
