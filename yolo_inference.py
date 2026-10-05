#from ultralytics import YOLO
'''model=YOLO('yolov8x')
results= model.predict('input/08fd33_4.mp4',save=True)
print(results[0])
print('==================================') 
for box in results[0]:
    print(box) '''
#------------------------------------------------------------------------------------------
'''
from ultralytics import YOLO

# Point to the latest trained run weights
model = YOLO("runs/detect/train-4/weights/best.pt")

# Run inference on your input video/image
results = model.predict(
    source="../input/test_video.mp4",  # Path to your test clip
    save=True,
    conf=0.25,
    device="mps"
)

print("Done! Output saved to runs/detect/predict"). '''

#-------------------------------------------------------------------------------------------

from pathlib import Path
from ultralytics import YOLO

# Resolve absolute path to custom trained weights
weights_path = Path("runs/detect/train-3/weights/best.pt").resolve()

# Load custom model
model = YOLO(str(weights_path))

# Run prediction
results = model.predict(
    source="../input/08fd33_4.mp4",
    save=True,
    conf=0.40,        # Increased confidence threshold to filter background/crowd noise
    device="mps"
)

print("Inference completed! Check output in training/runs/detect/predict")