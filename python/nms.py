
import numpy as np


def cal_ious(box1, box2):
    x1 = np.max(box1[0], box2[:, 0])
    y1 = np.max(box1[1], box2[:, 1])
    x2 = np.min(box1[2], box2[:, 2])
    y2 = np.min(box2[3], box2[:, 3])

    overlap = (x2 - x1 + 1) * (y2 - y1 + 1)
    area1 = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    area2 = (box2[:, 2] - box2[:, 0] + 1) * (box2[:, 3] - box2[:, 1] + 1)
    ious = overlap / (area1 + area2 - overlap)

    return ious


def nms(boxes, scores, threshold=0.5):
    assert (boxes.shape[0] == scores.shape[0])
    rank_score_idxs = np.argsort(scores)[::-1]
    boxes = boxes[:, rank_score_idxs]
    nms_boxes_res = []
    while boxes.size() > 0:
        nms_boxes_res.append(boxes[0])
        ious = cal_ious(boxes[0], boxes[1:])
        remaind_idxs = np.where(ious < threshold)[0]
        boxes = boxes[:, remaind_idxs]

    return np.array(nms_boxes_res)


def nms_idxs(boxes, scores, threshold=0.5):
    assert (boxes.shape[0] == scores.shape[0])
    rank_score_idxs = np.argsort(scores)[::-1]
    expand_rank_score_idxs = np.expand_dims(rank_score_idxs, axis=1)
    boxes = np.concatenate((boxes, expand_rank_score_idxs), axis=1)
    boxes = boxes[:, rank_score_idxs]
    nms_boxes_idxs = []
    while boxes.size() > 0:
        nms_boxes_idxs.append(boxes[0, 4])
        ious = cal_ious(boxes[0], boxes[1:])
        remaind_idxs = np.where(ious < threshold)[0]
        boxes = boxes[:, remaind_idxs]

    return np.array(nms_boxes_idxs)


def softmax(x, class_num):
    x = x.reshape(-1, class_num)
    return np.exp(-x) / np.sum(np.exp(-x))


