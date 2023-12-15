import uuid

from captcha_preprocess.preprocess.preprocess import *
import torch
import numpy as np
import cv2
from ultralytics import YOLO
from captcha_resolver.yolov8 import YOLOv8
from captcha_resolver.init import init_models
from captcha_resolver.AI_models.ClassificationModel import AlexNet
import captcha_resolver.CONSTS as CONSTS
from captcha_resolver.models.capcha import *
from torchvision import transforms
from captcha_resolver.s3.s3_functions import *

segmentation_model: YOLO
detection_model: YOLO
segmentation_onnx_model: YOLOv8
detection_onnx_model: YOLOv8
alexNet: AlexNet

segmentation_model, detection_model, segmentation_onnx_model, detection_onnx_model, alexNet = init_models()

preprocess = transforms.Compose(
    [
        transforms.ToPILImage(),
        transforms.Resize((227, 227)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        ),
    ]
)


class Service:

    def get_coordinates_onnx(self, name, boxes, class_ids):
        for i in range(len(class_ids)):
            if (CONSTS.your_classes[class_ids[i]] == name):
                return (int(boxes[i][2]) + int(boxes[i][0])) / 2, (int(boxes[i][3]) + int(boxes[i][1])) / 2

        return None, None

    def get_onnx_inference(self, captcha, icons, model):
        sequence = []
        index = 1
        yolov8 = model
        boxes, scores, class_ids = yolov8(captcha)

        for icon in icons:
            name = self.classify_image(icon)
            x, y = self.get_coordinates_onnx(name, boxes, class_ids)
            sequence.append({"x": x, "y": y})
            index += 1

        return sequence

    def get_onnx_solver(self, data: RequestModel):
        captcha = b64_decode(data.body)

        icons = preprocess_captcha_sobel(icons=b64_decode(data.imginstructions))

        detections = self.get_onnx_inference(captcha, icons, detection_onnx_model)
        segmentations = self.get_onnx_inference(captcha, icons, segmentation_onnx_model)

        return self.merge(detections, segmentations, data.body, data.imginstructions)

    def get_boxes(self, result):
        boxes = []
        all_params = result[0].boxes
        for i in range(len(result[0].boxes.conf.cpu())):
            if np.array(all_params.conf.cpu()[i]) > 0.05:
                x_up, y_up = (
                    all_params.xyxy.cpu()[i][0].numpy(),
                    all_params.xyxy.cpu()[i][1].numpy(),
                )
                x_bottom, y_bottom = (
                    all_params.xyxy.cpu()[i][2].numpy(),
                    all_params.xyxy.cpu()[i][3].numpy(),
                )
                boxes.append([x_up, y_up, x_bottom, y_bottom])

        return boxes

    def get_boxes_detection(self, name, prediction, model):
        index = 0
        for box in self.get_boxes(prediction):
            if model.model.names[int(prediction[0].boxes.cls.cpu()[index])] == name:
                print(box)
                return (int(box[2]) + int(box[0])) / 2, (int(box[3]) + int(box[1])) / 2
            index += 1
        return None, None

    def detect_v2(self, captcha, model):
        prediction = model.predict(captcha)

        return prediction

    def predict_one_sample(self, model, inputs):
        with torch.no_grad():
            logit = model(inputs).cpu()
            probs = torch.nn.functional.softmax(logit, dim=-1).numpy()
        return probs

    def classify_image(self, image_input):

        input_tensor = preprocess(image_input).unsqueeze(0)
        probs = self.predict_one_sample(alexNet, input_tensor)
        predicted_class_idx = np.argmax(probs, axis=1)[0]
        return CONSTS.your_classes[predicted_class_idx]

    def get_captcha_solve_sequence_segmentation_sobel(self, captcha, icons):

        sequence = []
        index = 1
        prediction = self.detect_v2(captcha, segmentation_model)
        for icon in icons:
            name = self.classify_image(icon)
            x, y = self.get_boxes_detection(name, prediction, segmentation_model)

            sequence.append({"x": x, "y": y})
            index += 1

        return sequence

    def get_captcha_solve_sequence_hybrid_merge_business(self, request: RequestModel):
        captcha = b64_decode(request.body)
        icons = preprocess_captcha_sobel(icons=b64_decode(request.imginstructions))
        sequence = []
        index = 1
        filtered_captcha = sobel_filter(request.sobel_filter, captcha)
        prediction = self.detect_v2(filtered_captcha, detection_model)
        for icon in icons:
            name = self.classify_image(icon)
            x, y = self.get_boxes_detection(name, prediction, detection_model)
            sequence.append({"x": x, "y": y})
            index += 1

        segment = self.get_captcha_solve_sequence_segmentation_sobel(captcha, icons)

        return self.merge(sequence, segment, request.body, request.imginstructions)

    def merge(self, sequence: [dict], segment: [dict], captcha_base64, icons_base64):

        final_sequence = []

        error = False

        for i in range(len(sequence)):
            if segment[i].get("x") is None and sequence[i].get("x") is not None:
                final_sequence.append(sequence[i])
            else:
                final_sequence.append(segment[i])
        # print(len(final_sequence))
        for i in range(len(final_sequence)):
            if final_sequence[i].get("x") is None:
                error = True
                object_id = str(uuid.uuid4())
                put_object_to_s3("captchas_pairs/"+object_id+"/"+str(uuid.uuid4())+".txt", "captchas_pairs/"+object_id+"/"+str(uuid.uuid4())+".txt", captcha_base64, icons_base64)
                break

        return final_sequence, error

    def get_unresolved_captchas(self):
        get_batch()