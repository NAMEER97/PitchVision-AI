import yaml
from pathlib import Path
from roboflow import Roboflow
from ultralytics import YOLO

# 1. Download dataset
rf = Roboflow(api_key="SFnAaSo61CRwL5R0u2rc")
project = rf.workspace("roboflow-jvuqo").project("football-players-detection-3zvbc")
version = project.version(1)
dataset = version.download("yolov5")

# 2. Fix data.yaml paths directly
dataset_path = Path(dataset.location).resolve()
yaml_path = dataset_path / "data.yaml"

with open(yaml_path, "r") as f:
    data_config = yaml.safe_load(f)

data_config["path"] = str(dataset_path)
data_config["train"] = "train/images"
data_config["val"] = "valid/images"
if "test" in data_config:
    data_config["test"] = "test/images"

with open(yaml_path, "w") as f:
    yaml.dump(data_config, f)

# 3. Train model with light memory footprint
model = YOLO("yolov8m.pt")

results = model.train(
    data=str(yaml_path),
    epochs=50,
    imgsz=640,
    batch=4,
    workers=2,
    device="mps"
)