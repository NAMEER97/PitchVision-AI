from ultralytics import YOLO

# Point to train-3 (or whichever folder returned from the ls command)
model = YOLO("runs/detect/train-3/weights/best.pt")

# Run prediction on test video
results = model.predict(
    source="../input/08fd33_4.mp4",  # Ensure this file exists inside football_analysis/input/
    save=True,
    conf=0.25,
    device="mps"
)

print("Inference completed! Check output in training/runs/detect/predict")