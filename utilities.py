#
# Utilities for PsychoPy experiments
# Author: Meng Du
# Nov 16 2016
#

import os
import json
import random
from psychopy import gui, visual, core, event, info


# Positions
CENTER_POS = (0.0, 0.0)
LEFT_CENTRAL_POS = (-0.5, 0.0)
RIGHT_CENTRAL_POS = (0.5, 0.0)


def show_form_dialog(items, validation_func=None, reset_after_error=True, title='', order=[], tip=None):
    """
    Show a form to be filled within a dialog. The user input values will be stored in items.
    See wxgui.DlgFromDict
    :param items: a dictionary with item name strings as keys, e.g. {'Subject ID': ''}
    :param validation_func: a function that takes the items dictionary, checks whether inputs are valid,
                            and returns a tuple valid (a boolean), message (a string)
    :param reset_after_error: a boolean; if true, all filled values will be reset in case of error
    :param title: a string form title
    :param order: a list containing keys in items, indicating the order of the items
    :param tip: a dictionary of tips for the items
    """
    while True:
        original_items = items.copy()
        dialog = gui.DlgFromDict(dictionary=items, title=title, order=order, tip=tip)
        if dialog.OK:
            if validation_func is None:
                break
            # validate
            valid, message = validation_func(items)
            if valid:
                break
            else:
                print 'Error: ' + message
                if reset_after_error:
                    items = original_items
        else:
            print 'User cancelled'
            core.quit()


class Presenter:
    """
    Methods that help to draw stuff in a window
    """
    def __init__(self, fullscreen=True, window=None):
        """
        :param fullscreen: a boolean indicating either full screen or not
        :param window: an optional psychopy.visual.Window
                       a new full screen window will be created if this parameter is not provided
        """
        self.window = window if window is not None else visual.Window(fullscr=fullscreen)
        self.expInfo = info.RunTimeInfo(win=window, refreshTest=None, verbose=False)

    def load_all_images(self, img_path, img_extension):
        """
        Read all image files in img_path that end with img_extension, and create corresponding ImageStim.
        :param img_path: a string path which should end with '/'
        :param img_extension: a string of image file extension
        :return: a list of psychopy.visual.ImageStim
        """
        img_files = [img_path + filename for filename in os.listdir(img_path) if filename.endswith(img_extension)]
        img_stims = [visual.ImageStim(self.window, image=img_file) for img_file in img_files]
        return img_stims

    def draw_stimuli_for_duration(self, stimuli, duration=None):
        """
        :param stimuli: a list of psychopy.visual stimuli to draw
        :param duration: a float time duration in seconds
        """
        for stim in stimuli:
            if stim is not None:  # skipping "None"
                stim.draw()
        self.window.flip()
        if duration is not None:
            core.wait(duration)

    def draw_stimuli_for_response(self, stimuli, response_keys, escape=True):
        """
        :param stimuli: a list of psychopy.visual stimuli to draw
        :param response_keys: a list containing strings of response keys
        :param escape: a boolean that allows pressing esc to exit the program if True
        :return: a tuple (key_pressed, reaction_time_in_seconds)
        """
        self.draw_stimuli_for_duration(stimuli)
        response_keys.append('escape')
        response = event.waitKeys(keyList=response_keys, timeStamped=core.Clock())[0]
        if escape and response[0] == 'escape':
            core.quit()
        return response

    def show_instructions(self, key_to_continue, instructions, next_instr_stim=None):
        """
        Show a list of instructions strings
        :param instructions: an instruction string, or a list containing instruction strings
        :param key_to_continue: a string of the key to press
        :param next_instr_stim: an optional psychopy.visual.TextStim to show together with each instruction string
        """
        if type(instructions) is str:
            instructions = [instructions]
        for instr in instructions:
            instr_stim = visual.TextStim(self.window, text=instr)
            self.draw_stimuli_for_response([instr_stim, next_instr_stim], [key_to_continue])

    def show_fixation(self, duration):
        """
        Show a '+' for a specified duration
        :param duration: a time duration in seconds
        """
        plus_sign = visual.TextStim(self.window, text='+')
        self.draw_stimuli_for_duration([plus_sign], duration)

    def select_from_two_stimuli(self, left_stim, left_value, right_stim, right_value, post_selection_duration=1,
                                other_stim=[], random_side=True, response_keys=('f', 'j')):
        """
        Draw 2 stimuli on one screen and wait for a selection (key response). Once a stimulus is selected, the other
        stimulus will disappear. The value associated with the selected image (specified as parameters) will be
        returned.
        If either stimuli have a default central position (i.e. pos == (0, 0)), they will be assigned new positions.
        :param left_stim: A psychopy.visual stimulus
        :param left_value: an object to be returned when the left_stim is selected
        :param right_stim: Another psychopy.visual stimulus
        :param right_value: an object to be returned when the right_stim is selected
        :param post_selection_duration: the duration (in seconds) to display the selected stimulus only
        :param other_stim: an optional list of psychopy.visual stimuli to be displayed
        :param random_side: if True, the images will show on random sides
        :param response_keys: a list of two strings corresponds to left and right images
        :return: a tuple (value, reaction_time_in_seconds), where value is either left_value or right_value depending
                 on the response
        """
        # assign left/right side
        if random_side and random.randrange(2) == 0:  # swap positions
            left_stim, right_stim = right_stim, left_stim
            left_stim.pos, right_stim.pos = right_stim.pos, left_stim.pos
            left_value, right_value = right_value, left_value
        if left_stim.pos == (0, 0) or right_stim.pos == (0, 0):
            left_stim.pos = LEFT_CENTRAL_POS
            right_stim.pos = RIGHT_CENTRAL_POS

        # display stimuli and get response
        response = self.draw_stimuli_for_response(other_stim + [left_stim, right_stim], response_keys)
        key_pressed = response[0]
        rt = response[1]
        selection = left_value if key_pressed == response_keys[0] else right_value

        # post selection screen
        selected_stim = left_stim if selection == left_value else right_stim
        self.draw_stimuli_for_duration(selected_stim, post_selection_duration)

        return selection, rt


class DataHandler:
    def __init__(self, data_path, data_file):
        """
        :param data_path: a string ending with '/'
        :param data_file: a string file name
        """
        if not os.path.isdir(data_path):
            os.mkdir(data_path)
        elif os.path.isfile(data_path + data_file):
            raise IOError(data_path + data_file + ' already exists')

        self.dataFile = open(data_path + data_file, mode='w')

    def __del__(self):
        if hasattr(self, 'dataFile'):
            self.dataFile.close()

    def write_data(self, data):
        json.dump(data, self.dataFile)
        self.dataFile.write('\n')

    def load_data(self):
        return [json.loads(line) for line in self.dataFile]
