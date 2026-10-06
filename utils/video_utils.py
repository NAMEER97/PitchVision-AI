'''import cv2

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

def save_video(output_video_frames, output_video_path):
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(
        output_video_path,
        fourcc,
        24,
        (output_video_frames[0].shape[1], output_video_frames[0].shape[0]),
    )
    for frame in output_video_frames:
        out.write(frame)
    out.release()   '''
    


import cv2

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

def save_video(output_video_frames, output_video_path):
    # Use 'avc1' (Apple AVFoundation native H.264 encoder) for smooth, glitch-free macOS QuickTime playback
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(
        output_video_path,
        fourcc,
        24,
        (output_video_frames[0].shape[1], output_video_frames[0].shape[0])
    )
    if not out.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_video_path,
            fourcc,
            24,
            (output_video_frames[0].shape[1], output_video_frames[0].shape[0])
        )

    for frame in output_video_frames:
        out.write(frame)
    out.release()