from ultralytics import YOLO

model = YOLO("yolov8n.yaml")
result = model.train(data="4_yolo_dataset/data.yaml", epochs=25, imgsz=640)