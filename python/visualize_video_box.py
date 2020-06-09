import re
import sys
import json
import cv2

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.8

def show_video(video_path, json_path):
    with open(json_path, 'r') as json_file:
        tracks_json = json.load(json_file)

    frame_idx = 0
    frame_keys = tracks_json.keys()
    print(frame_keys)
    cap = cv2.VideoCapture(video_path)
    fps = 5
    sz = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video_write = cv2.VideoWriter()
    video_write.open('output.mp4', fourcc, fps, sz, True)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame_idx += 1
        str_frame_idx = str(frame_idx)
        if str_frame_idx not in frame_keys:
            continue
        else:
            list_objs = tracks_json[str_frame_idx]
            for obj in list_objs:
                body_box, track_id, head_box = obj
                cv2.putText(frame, str(track_id), (int(body_box[0]), int(body_box[1])), FONT, FONT_SCALE,
                            color=(0, 255, 0), lineType=cv2.LINE_AA, thickness=4)
                cv2.rectangle(frame, (int(body_box[0]), int(body_box[1])), (int(body_box[0] + body_box[2]),
                              int(body_box[1] + body_box[3])), color=(255, 0, 0), thickness=3)
                if head_box:
                    cv2.rectangle(frame, (head_box[0], head_box[1]),
                                  (head_box[0] + head_box[2], head_box[1] + head_box[3]),
                                  color=(0, 0, 255), thickness=3)
        if success and frame_idx < 10000:
            # cv2.imshow('video', frame)
            # cv2.waitKey(5)
            video_write.write(frame)
        else:
            break

    cap.release()
    video_write.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    video_path = 'video.mp4'
    json_path = 'video_box.json'
    show_video(video_path, json_path)
