import backbone
import cv2 as openCV
import drawer as drawing
import numpy as np
import tensorflow as tensor
from libs.database import *
from libs.inserter import *
from libs.config import host, user, passwd, db, csv_file


def objectGet(input_video, olc):
    total_passed_object = 0
    # input video
    deviation = 3  # the constant that represents the object counting area
    videoSource = openCV.VideoCapture(input_video)
    width = int(videoSource.get(openCV.CAP_PROP_FRAME_WIDTH))
    # print("Height: {0}\nWidth: {1}\nFPS: {2}")
    detection_graph, category_index = backbone.set_model(
        'ssd_mobilenet_v1_coco_2017_11_17')
    # counting_mode = "..."
    with detection_graph.as_default():
        with tensor.Session(graph=detection_graph) as sess:
            # Definite input and output Tensors for detection_graph
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            detection_boxes = detection_graph.get_tensor_by_name(
                'detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            detection_scores = detection_graph.get_tensor_by_name(
                'detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name(
                'detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name(
                'num_detections:0')
            # looping in all frames from camera or video stream
            while (videoSource.isOpened()):
                ret, frame = videoSource.read()
                if not ret:
                    print("Running Finished")
                    databaseInsert(host, user, passwd, db, csv_file)
                    break
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(frame, axis=0)
                # Actual detection.
                boxes, scores, classes, num = sess.run(
                    [detection_boxes, detection_scores,
                        detection_classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                # insert information text to video frame
                # Visualization of the results of a detection.
                counter, csv_line, counting_mode = drawing.visualizeBoxes(videoSource.get(1), frame, 2,
                                                                          np.squeeze(
                                                                              boxes),
                                                                          np.squeeze(classes).astype(
                                                                              np.int32),
                                                                          np.squeeze(
                                                                              scores), category_index,
                                                                          y_reference=olc, deviation=deviation,
                                                                          use_normalized_coordinates=True,
                                                                          line_thickness=4)

                # insert information text to video frame if mode debug is on
                print("---------------------------{0}".format(counter))
                if debug_Mode == "on":
                    # when the object passed over line and counted, make the color of OLC line green
                    if counter == 1:
                        openCV.line(frame, (0, olc),
                                    (width, olc), (0, 0xFF, 0), 5)
                    else:
                        openCV.line(frame, (0, olc),
                                    (width, olc), (0, 0, 0xFF), 5)
                    total_passed_object = total_passed_object + counter
                    font = openCV.FONT_HERSHEY_SIMPLEX
                    openCV.putText(frame, 'Total Objects: ' + str(total_passed_object), (10, 35), font, 0.8,
                                   (0, 0x00, 0xFF), 2, openCV.FONT_HERSHEY_SIMPLEX, )
                    openCV.putText(frame, 'OLC Line', (545, olc - 10),
                                   font, 0.6, (0, 0, 0xFF), 2, openCV.LINE_AA, )
                    openCV.imshow('object counting', frame)
                if openCV.waitKey(1) & 0xFF == ord('q'):
                    break
            videoSource.release()
            openCV.destroyAllWindows()
