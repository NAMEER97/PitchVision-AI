import cv2

cap = cv2.VideoCapture("output_videos/output_video.mp4")
cap.set(cv2.CAP_PROP_POS_FRAMES, 50)
ret, frame = cap.read()
if ret:
    cv2.imwrite("/Users/nameer/.gemini/antigravity-ide/brain/69659026-67f5-4c01-aa88-9c4b90d48bbe/test_avc1_output.jpg", frame)
    print("Frame 50 extracted successfully!")
else:
    print("Failed to read frame")
cap.release()
