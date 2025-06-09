import argparse
import sys
import time
import cv2
import numpy as np


LABEL_SIZE = 0.4


def run(
    model_path: str,
    label_path: str,
    camera_id: int,
    width: int,
    height: int,
    threshold: int,
    runtime_only: bool,
) -> None:

    # load proper runtime
    if runtime_only:
        from picamera2 import Picamera2
        from ai_edge_litert.interpreter import Interpreter

        interpreter = Interpreter(model_path=model_path)
    else:
        import tensorflow as tf

        interpreter = tf.lite.Interpreter(model_path=model_path)

    # Variables to calculate FPS
    counter, fps = 0, 0
    fps_avg_frame_count = 10
    start_time = time.time()

    # Start capturing video input from the camera
    if runtime_only:
        cam = Picamera2()
        height = height
        width = width
        cam.configure(
            cam.create_video_configuration(
                main={"format": "RGB888", "size": (width, height)}
            )
        )
        cam.start()

    else:
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # prepare interpreter and read in/out details
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    _, input_height, input_width, _ = interpreter.get_input_details()[0]["shape"]

    # read label file
    with open(label_path, "r") as f:
        labels = [line.strip() for line in f.readlines()]
    colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")

    # Continuously capture images from the camera and run inference
    if runtime_only:
        is_open = True
    else:
        is_open = cap.isOpened()

    # main loop
    while is_open:
        time.sleep(0.2)
        counter += 1

        # capture image
        if runtime_only:
            img = cam.capture_array()
        else:
            _, img = cap.read()

        # pad image with proper sizes
        img_height, img_width = img.shape[:2]
        pad = abs(img_width - img_height) // 2
        x_pad = pad if img_height > img_width else 0
        y_pad = pad if img_width > img_height else 0
        img_padded = cv2.copyMakeBorder(
            img,
            top=y_pad,
            bottom=y_pad,
            left=x_pad,
            right=x_pad,
            borderType=cv2.BORDER_CONSTANT,
            value=(0, 0, 0),
        )
        img_height, img_width = img_padded.shape[:2]

        img_rgb = cv2.cvtColor(img_padded, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(
            img_rgb, (input_width, input_height), interpolation=cv2.INTER_AREA
        )
        input_data = np.expand_dims(img_resized, axis=0)

        # invoke prediction
        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()

        # get objects detection details
        boxes = interpreter.get_tensor(output_details[0]["index"])[0]
        classes = interpreter.get_tensor(output_details[1]["index"])[0]
        scores = interpreter.get_tensor(output_details[2]["index"])[0]

        # prepare and print boxes and labels
        for score, box, class_ in zip(scores, boxes, classes):
            if score < threshold:
                continue

            color = [int(c) for c in colors[int(class_)]]
            text_color = (255, 255, 255) if sum(color) < 144 * 3 else (0, 0, 0)

            min_y = round(box[0] * img_height)
            min_x = round(box[1] * img_width)
            max_y = round(box[2] * img_height)
            max_x = round(box[3] * img_width)
            cv2.rectangle(img_padded, (min_x, min_y), (max_x, max_y), color, 2)

            class_name = labels[int(class_)]
            label = f"{class_name}: {score*100:.2f}%"
            labelSize, baseLine = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, LABEL_SIZE, 1
            )

            cv2.rectangle(
                img_padded,
                (min_x, min_y + baseLine),
                (min_x + labelSize[0], min_y - baseLine - labelSize[1]),
                color,
                cv2.FILLED,
            )
            cv2.putText(
                img_padded,
                label,
                (min_x, min_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                LABEL_SIZE,
                text_color,
                1,
            )

        # Calculate the FPS
        if counter % fps_avg_frame_count == 0:
            end_time = time.time()
            fps = fps_avg_frame_count / (end_time - start_time)
            start_time = time.time()

        # Show the FPS
        fps_text = "FPS = {:.1f}".format(fps)
        fps_text_location = (50, 100)
        fps_text_color = (0, 0, 255)  # red
        fps_font_size = 1
        fps_font_thickness = 1
        cv2.putText(
            img_padded,
            fps_text,
            fps_text_location,
            cv2.FONT_HERSHEY_PLAIN,
            fps_font_size,
            fps_text_color,
            fps_font_thickness,
        )

        # show final image
        img_show = img_padded[y_pad : img_height - y_pad, x_pad : img_width - x_pad]
        cv2.namedWindow("Object detection", cv2.WINDOW_NORMAL)
        cv2.resizeWindow(
            "Object detection",
            1024 if img_width > img_height else round(1024 * img_width / img_height),
            1024 if img_height > img_width else round(1024 * img_height / img_width),
        )
        cv2.imshow("Object detection", img_show)

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            break

    if not runtime_only:
        cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--model_path",
        help="Path of the object detection model.",
        required=False,
        default="./model/ssd_mobilenet_v1_1_metadata_2.tflite",
    )
    parser.add_argument(
        "--label_path",
        help="Path of the model labels.",
        required=False,
        default="./model/labelmap.txt",
    )
    parser.add_argument(
        "--cameraId", help="Id of camera.", required=False, type=int, default=0
    )
    parser.add_argument(
        "--frameWidth",
        help="Width of frame to capture from camera.",
        required=False,
        type=int,
        default=640,
    )
    parser.add_argument(
        "--frameHeight",
        help="Height of frame to capture from camera.",
        required=False,
        type=int,
        default=640,
    )
    parser.add_argument(
        "--threshold",
        help="Object detection threshold.",
        required=False,
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--runtimeOnly",
        help="Whether to run with runtime only.",
        action="store_true",
        required=False,
        default=False,
    )

    args = parser.parse_args()

    run(
        args.model_path,
        args.label_path,
        int(args.cameraId),
        args.frameWidth,
        args.frameHeight,
        float(args.threshold),
        bool(args.runtimeOnly),
    )


if __name__ == "__main__":
    main()
