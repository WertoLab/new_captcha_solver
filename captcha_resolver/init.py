import os

from ultralytics import YOLO
from captcha_resolver.yolov8 import YOLOv8
from captcha_resolver.AI_models.ClassificationModel import AlexNet
import torch

instance_id: str = str(os.getpid())


def init_models():
    f = open('captcha_resolver/logs/' + str(instance_id) + '.txt', 'a')
    with open('captcha_resolver/logs/' + str(instance_id) + '.txt', 'a') as f:
        f.write('Instance with id: ' + str(instance_id) + ' has launched')

    print("Models initialization ...")
    segmentation_model = YOLO("captcha_resolver/AI_weights/captcha_segmentation_v2.pt")
    detection_model = YOLO("captcha_resolver/AI_weights/best_v3.pt")
    segmentation_onnx_model = YOLOv8("captcha_resolver/AI_weights/captcha_segmentation.onnx")
    detection_onnx_model = YOLOv8("captcha_resolver/AI_weights/best_v3.onnx")
    alexnet = AlexNet()
    alexnet.load_state_dict(
        torch.load(
            "captcha_resolver/AI_weights/smartsolver_weights_1_6.pth",
            map_location="cpu",
        )
    )
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)
    alexnet.eval()

    print("Models are initialized")
    return segmentation_model, detection_model, segmentation_onnx_model, detection_onnx_model, alexnet
