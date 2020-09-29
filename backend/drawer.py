import collections
import csv
import os
import time
from ast import literal_eval

import PIL.Image as Image
import PIL.ImageColor as ImageColor
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
import cv2
import numpy
import numpy as np
from libs.database import *
from libs.pushing import pushMetric
from libs.pushing import pushTrigger
from libs.trigger import runTrigger
from libs.config import *
from libs.alerting import *
from libs.config import STANDARD_COLORS


def save_image(source_image):
    current_path = os.getcwd()
    cv2.imwrite(
        current_path + "/detected_objects/object" + str(len(object_count)) +
        ".png", source_image)
    object_count.insert(0, 1)


def getDate():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def count_objects(top, bottom, right, left, crop_img, olc_position, y_min, y_max, deviation):
    direction = "n.a."  # means not available, it is just initialization
    isInOLC = True  # is the object that is inside Region Of Interest
    update_csv = True

    if (abs(((bottom + top) / 2) - olc_position) < deviation):
        is_object_detected.insert(0, 1)
        save_image(crop_img)  # save detected object image

    if (bottom > bottom_position_of_detected_object[0]):
        direction = "down"
    else:
        direction = "up"

    bottom_position_of_detected_object.insert(0, (bottom))

    return direction, is_object_detected, update_csv


def getObjectXaxis(top, bottom, right, left, crop_img, olc_position, y_min, y_max, deviation):
    direction = "n.a."  # means not available, it is just initialization
    isInOLC = True  # is the object that is inside Region Of Interest
    update_csv = True

    if (abs(((right + left) / 2) - olc_position) < deviation):
        is_object_detected.insert(0, 1)
        update_csv = True
        save_image(crop_img)  # save detected object image

    if (bottom > bottom_position_of_detected_object[0]):
        direction = "down"
    else:
        direction = "up"

    bottom_position_of_detected_object.insert(0, (bottom))
    return direction, is_object_detected, update_csv


def getSpeed(bottom, current_frame_number, crop_img, olc_position):
    speed = 'n.a.'  # means not available, it is just initialization
    direction = 'n.a.'  # means not available, it is just initialization
    scale_constant = 1  # manual scaling because we did not performed camera calibration
    isInOLC = True  # is the object that is inside Region Of Interest
    update_csv = True
    if bottom < 250:
        # scale_constant is used for manual scaling because we did not performed camera calibration
        scale_constant = 1
    elif bottom > 250 and bottom < 320:
        # scale_constant is used for manual scaling because we did not performed camera calibration
        scale_constant = 2
    else:
        isInOLC = False

    if len(bottom_position_of_detected_object) != 0 and bottom - bottom_position_of_detected_object[0] > 0 and 205 < \
        bottom_position_of_detected_object[0] and bottom_position_of_detected_object[0] < 210 and olc_position[
            0] < bottom:
        is_object_detected.insert(0, 1)
        update_csv = True
        save_image(crop_img)  # save detected object image

    if bottom > bottom_position_of_detected_object[0]:
        direction = 'down'
    else:
        direction = 'up'

    if isInOLC:
        pixel_length = bottom - bottom_position_of_detected_object[0]
        # multiplied by 44 to convert pixel length to real length in meters (chenge 44 to get length in meters for your case)
        scale_real_length = pixel_length  # * 44
        total_time_passed = current_frame_number - current_frame_number_list[0]
        # get the elapsed total time for a object to pass through OLC area (24 = fps)
        scale_real_time_passed = total_time_passed  # * 25
        if scale_real_time_passed != 0:
            # performing manual scaling because we have not performed camera calibration
            speed = scale_real_length / scale_real_time_passed / scale_constant
            # use reference constant to get object speed prediction in kilometer unit
            speed = speed  # / 6 * 40
            current_frame_number_list.insert(0, current_frame_number)
            bottom_position_of_detected_object.insert(0, bottom)

    return (direction, speed, is_object_detected, update_csv)


def word_count(str):
    counts = dict()
    words = str.split()
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts


def drawBOXImageArray(current_frame_number,
                      image,
                      ymin,
                      xmin,
                      ymax,
                      xmax,
                      color='red',
                      thickness=4,
                      display_str_list=(),
                      use_normalized_coordinates=True):
    """Adds a bounding box to an image (numpy array).

    Args:
      image: a numpy array with shape [height, width, 3].
      ymin: ymin of bounding box in normalized coordinates (same below).
      xmin: xmin of bounding box.
      ymax: ymax of bounding box.
      xmax: xmax of bounding box.
      color: color to draw bounding box. Default is red.
      thickness: line thickness. Default value is 4.
      display_str_list: list of strings to display in box
                        (each to be shown on its own line).
      use_normalized_coordinates: If True (default), treat coordinates
        ymin, xmin, ymax, xmax as relative to the image.  Otherwise treat
        coordinates as absolute.
    """
    image_pil = Image.fromarray(np.uint8(image)).convert('RGB')
    is_object_detected, csv_line, update_csv = drawBoxImage(current_frame_number, image_pil, ymin, xmin,
                                                            ymax, xmax, color, thickness,
                                                            display_str_list, use_normalized_coordinates)
    np.copyto(image, np.array(image_pil))
    return is_object_detected, csv_line, update_csv


def drawBoxImage(current_frame_number,
                 image,
                 ymin,
                 xmin,
                 ymax,
                 xmax,
                 color='red',
                 thickness=4,
                 display_str_list=(),
                 use_normalized_coordinates=True):
    """Adds a bounding box to an image.

    Each string in display_str_list is displayed on a separate line above the
    bounding box in black text on a rectangle filled with the input 'color'.
    If the top of the bounding box extends to the edge of the image, the strings
    are displayed below the bounding box.

    Args:
      image: a PIL.Image object.
      ymin: ymin of bounding box.
      xmin: xmin of bounding box.
      ymax: ymax of bounding box.
      xmax: xmax of bounding box.
      color: color to draw bounding box. Default is red.
      thickness: line thickness. Default value is 4.
      display_str_list: list of strings to display in box
                        (each to be shown on its own line).
      use_normalized_coordinates: If True (default), treat coordinates
        ymin, xmin, ymax, xmax as relative to the image.  Otherwise treat
        coordinates as absolute.
    """
    csv_line = ""  # to create new csv line consists of object type, predicted_speed, color and predicted_direction
    # update csv for a new object that are passed from OLC - just one new line for each objects
    update_csv = True
    is_object_detected = [0]
    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size
    if use_normalized_coordinates:
        (left, right, top, bottom) = (xmin * im_width,
                                      xmax * im_width, ymin * im_height, ymax * im_height)
    else:
        (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
    draw.line([(left, top), (left, bottom), (right, bottom),
               (right, top), (left, top)], width=thickness, fill=color)

    predicted_direction = "n.a."  # means not available, it is just initialization

    image_temp = numpy.array(image)
    detected_object_image = image_temp[int(
        top):int(bottom), int(left):int(right)]

    if (bottom > OLC_POSITION[0]):
        predicted_direction, predicted_speed, is_object_detected, update_csv = getSpeed(bottom, current_frame_number,
                                                                                        detected_object_image,
                                                                                        OLC_POSITION)
        if is_object_detected:
            if not predicted_speed == 'n.a.':
                csv_line = "%s,%s" % (predicted_direction, predicted_speed)

    if (x_axis[0] == 1):
        predicted_direction, is_object_detected, update_csv = getObjectXaxis(top, bottom, right, left,
                                                                             detected_object_image, OLC_POSITION[0],
                                                                             OLC_POSITION[0] +
                                                                             DEVIATION[0],
                                                                             OLC_POSITION[0] + (
                                                                                 DEVIATION[0] * 2),
                                                                             DEVIATION[0])
    elif (mode_number[0] == 2):
        predicted_direction, is_object_detected, update_csv = count_objects(top, bottom, right, left,
                                                                            detected_object_image, OLC_POSITION[0],
                                                                            OLC_POSITION[0] +
                                                                            DEVIATION[0],
                                                                            OLC_POSITION[0] + (
                                                                                DEVIATION[0] * 2),
                                                                            DEVIATION[0])

    try:
        font = ImageFont.truetype('arial.ttf', 16)
    except IOError:
        font = ImageFont.load_default()

    display_str_heights = [font.getsize(ds)[1] for ds in display_str_list]

    # Each display_str has a top and bottom margin of 0.05x.
    total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

    if top > total_display_str_height:
        text_bottom = top
    else:
        text_bottom = bottom + total_display_str_height

    # Reverse list and print from bottom to top.
    for display_str in display_str_list[::-1]:
        text_width, text_height = font.getsize(display_str)
        margin = np.ceil(0.05 * text_height)
        draw.rectangle([(left, text_bottom - text_height - 2 * margin),
                        (left + text_width, text_bottom)], fill=color)
        draw.text((left + margin, text_bottom - text_height - margin),
                  display_str, fill='black', font=font)
        text_bottom -= text_height - 2 * margin
        return is_object_detected, csv_line, update_csv


def draw_keypoints_on_image_array(image, keypoints, color='red', radius=2, use_normalized_coordinates=True):
    """Draws keypoints on an image (numpy array).

    Args:
      image: a numpy array with shape [height, width, 3].
      keypoints: a numpy array with shape [num_keypoints, 2].
      color: color to draw the keypoints with. Default is red.
      radius: keypoint radius. Default value is 2.
      use_normalized_coordinates: if True (default), treat keypoint values as
        relative to the image.  Otherwise treat them as absolute.
    """
    image_pil = Image.fromarray(np.uint8(image)).convert('RGB')
    draw_keypoints_on_image(image_pil, keypoints, color, radius,
                            use_normalized_coordinates)
    np.copyto(image, np.array(image_pil))


def draw_keypoints_on_image(image,
                            keypoints,
                            color='red',
                            radius=2,
                            use_normalized_coordinates=True):
    """Draws keypoints on an image.

    Args:
      image: a PIL.Image object.
      keypoints: a numpy array with shape [num_keypoints, 2].
      color: color to draw the keypoints with. Default is red.
      radius: keypoint radius. Default value is 2.
      use_normalized_coordinates: if True (default), treat keypoint values as
        relative to the image.  Otherwise treat them as absolute.
    """
    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size
    keypoints_x = [k[1] for k in keypoints]
    keypoints_y = [k[0] for k in keypoints]
    if use_normalized_coordinates:
        keypoints_x = tuple([im_width * x for x in keypoints_x])
        keypoints_y = tuple([im_height * y for y in keypoints_y])
    for keypoint_x, keypoint_y in zip(keypoints_x, keypoints_y):
        draw.ellipse([(keypoint_x - radius, keypoint_y - radius), (keypoint_x + radius, keypoint_y + radius)],
                     outline=color, fill=color)


def draw_mask_on_image_array(image, mask, color='red', alpha=0.7):
    """Draws mask on an image.

    Args:
      image: uint8 numpy array with shape (img_height, img_height, 3)
      mask: a uint8 numpy array of shape (img_height, img_height) with
        values between either 0 or 1.
      color: color to draw the keypoints with. Default is red.
      alpha: transparency value between 0 and 1. (default: 0.7)

    Raises:
      ValueError: On incorrect data type for image or masks.
    """
    if image.dtype != np.uint8:
        raise ValueError('`image` not of type np.uint8')
    if mask.dtype != np.uint8:
        raise ValueError('`mask` not of type np.uint8')
    if np.any(np.logical_and(mask != 1, mask != 0)):
        raise ValueError('`mask` elements should be in [0, 1]')
    rgb = ImageColor.getrgb(color)
    pil_image = Image.fromarray(image)
    solid_color = np.expand_dims(np.ones_like(
        mask), axis=2) * np.reshape(list(rgb), [1, 1, 3])
    pil_solid_color = Image.fromarray(np.uint8(solid_color)).convert('RGBA')
    pil_mask = Image.fromarray(np.uint8(255.0 * alpha * mask)).convert('L')
    pil_image = Image.composite(pil_solid_color, pil_image, pil_mask)
    np.copyto(image, np.array(pil_image.convert('RGB')))


def visualizeBoxes(
        current_frame_number,
        image,
        mode,
        boxes,
        classes,
        scores,
        category_index,
        targeted_objects=None,
        y_reference=None,
        deviation=None,
        instance_masks=None,
        keypoints=None,
        use_normalized_coordinates=False,
        max_boxes_to_draw=20,
        min_score_thresh=.5,
        agnostic_mode=False,
        line_thickness=4):
    """Overlay labeled boxes on an image with formatted scores and label names.

    This function groups boxes that correspond to the same location
    and creates a display string for each detection and overlays these
    on the image. Note that this function modifies the image in place, and returns
    that same image.

    Args:
      image: uint8 numpy array with shape (img_height, img_width, 3)
      boxes: a numpy array of shape [N, 4]
      classes: a numpy array of shape [N]. Note that class indices are 1-based,
        and match the keys in the label map.
      scores: a numpy array of shape [N] or None.  If scores=None, then
        this function assumes that the boxes to be plotted are groundtruth
        boxes and plot all boxes as black with no classes or scores.
      category_index: a dict containing category dictionaries (each holding
        category index `id` and category name `name`) keyed by category indices.
      instance_masks: a numpy array of shape [N, image_height, image_width], can
        be None
      keypoints: a numpy array of shape [N, num_keypoints, 2], can
        be None
      use_normalized_coordinates: whether boxes is to be interpreted as
        normalized coordinates or not.
      max_boxes_to_draw: maximum number of boxes to visualize.  If None, draw
        all boxes.
      min_score_thresh: minimum score threshold for a box to be visualized
      agnostic_mode: boolean (default: False) controlling whether to evaluate in
        class-agnostic mode or not.  This mode will display scores but ignore
        classes.
      line_thickness: integer (default: 4) controlling line width of the boxes.

    Returns:
      uint8 numpy array with shape (img_height, img_width, 3) with overlaid boxes.
    """
    # Create a display string (and color) for every box location, group any boxes
    # that correspond to the same location.
    csv_line_util = "not_available"
    counter = 0
    OLC_POSITION.insert(0, y_reference)
    DEVIATION.insert(0, deviation)
    is_object_detected = []
    mode_number.insert(0, mode)
    box_to_display_str_map = collections.defaultdict(list)
    box_to_color_map = collections.defaultdict(str)
    box_to_instance_masks_map = {}
    box_to_keypoints_map = collections.defaultdict(list)
    if not max_boxes_to_draw:
        max_boxes_to_draw = boxes.shape[0]
    for i in range(min(max_boxes_to_draw, boxes.shape[0])):
        if scores is None or scores[i] > min_score_thresh:
            box = tuple(boxes[i].tolist())
            if instance_masks is not None:
                box_to_instance_masks_map[box] = instance_masks[i]
            if keypoints is not None:
                box_to_keypoints_map[box].extend(keypoints[i])
            if scores is None:
                box_to_color_map[box] = 'black'
            else:
                if not agnostic_mode:
                    if classes[i] in category_index.keys():
                        class_name = category_index[classes[i]]['name']
                    else:
                        class_name = 'N/A'
                    display_str = '{}: {}%'.format(
                        class_name, int(100 * scores[i]))
                else:
                    display_str = 'score: {}%'.format(int(100 * scores[i]))

                box_to_display_str_map[box].append(display_str)
                if agnostic_mode:
                    box_to_color_map[box] = 'DarkOrange'
                else:
                    box_to_color_map[box] = STANDARD_COLORS[classes[i] % len(
                        STANDARD_COLORS)]

    if (mode == 2):
        counting_mode = ""
    # Draw all boxes onto image.
    for box, color in box_to_color_map.items():
        dateTime = getDate()
        ymin, xmin, ymax, xmax = box
        display_str_list = box_to_display_str_map[box]
        if (mode == 2 and targeted_objects == None):
            counting_mode = counting_mode + str(display_str_list)

        elif (mode == 2 and targeted_objects in display_str_list[0]):
            counting_mode = counting_mode + str(display_str_list)

        if ((targeted_objects != None)
                and (targeted_objects in display_str_list[0])):
            if instance_masks is not None:
                draw_mask_on_image_array(
                    image, box_to_instance_masks_map[box], color=color)

            is_object_detected, csv_line, update_csv = drawBOXImageArray(current_frame_number, image,
                                                                         ymin, xmin, ymax, xmax,
                                                                         color=color,
                                                                         thickness=line_thickness,
                                                                         display_str_list=box_to_display_str_map[box],
                                                                         use_normalized_coordinates=use_normalized_coordinates)

            if keypoints is not None:
                draw_keypoints_on_image_array(image, box_to_keypoints_map[box], color=color, radius=line_thickness / 2,
                                              use_normalized_coordinates=use_normalized_coordinates)

        elif (targeted_objects == None):
            if instance_masks is not None:
                draw_mask_on_image_array(
                    image, box_to_instance_masks_map[box], color=color)
            is_object_detected, csv_line, update_csv = drawBOXImageArray(current_frame_number, image,
                                                                         ymin, xmin, ymax, xmax,
                                                                         color=color,
                                                                         thickness=line_thickness,
                                                                         display_str_list=box_to_display_str_map[box],
                                                                         use_normalized_coordinates=use_normalized_coordinates)
            if is_object_detected and csv_line:
                Csv_line_util = class_name + "," + csv_line
                pushMetric("stat3", Csv_line_util, dashingURL)
                sendEmail(Csv_line_util, camera_id)
                Csv_line_util = Csv_line_util + "," + dateTime
                splitObject = str(Csv_line_util).split(",")[0]
                if triggerObject != "None":
                    if splitObject == triggerObject:
                        print(triggerObject)
                        runTrigger(triggerObject, dateTime)
                with open('object_counting_report.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerows([Csv_line_util.split(',')])
                print(Csv_line_util)
                pushTrigger("trigger3", triggerURL)
            if keypoints is not None:
                draw_keypoints_on_image_array(image, box_to_keypoints_map[box], color=color, radius=line_thickness / 2,
                                              use_normalized_coordinates=use_normalized_coordinates)

    if (1 in is_object_detected):
        counter = 1
        del is_object_detected[:]
        is_object_detected = []
        csv_line_util = class_name + "," + csv_line

    if (mode == 2):
        counting_mode = counting_mode.replace(
            "['", " ").replace("']", " ").replace("%", "")
        counting_mode = ''.join(
            [i for i in counting_mode.replace("['", " ").replace("']", " ").replace("%", "") if not i.isdigit()])
        counting_mode = str(word_count(counting_mode))
        pushName = literal_eval(counting_mode)
        counting_mode = counting_mode.replace("{", "").replace("}", "")
        if wildRange == True:
            print(wildRange)
            if triggerObject in counting_mode:
                print("Wild detection ON")
                runTrigger(triggerObject, dateTime)
        pushMetric("stat1", counting_mode, dashingURL)
        pushMetric("stat2", "System Status", dashingURL)
        if 'person' in counting_mode and 'car' in counting_mode:
            pushTrigger("trigger1", triggerURL)
        elif 'car' in counting_mode:
            pushTrigger("trigger2", triggerURL)
        print("Current Object in the frames are: %s" % counting_mode)
        return counter, csv_line_util, counting_mode
    else:
        return counter, csv_line_util
