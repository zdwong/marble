
import json
import time
from collections import defaultdict
import cv2
import os
import random
import numpy as np

annotation_path_file = 'instance_body.json'
images_original_path = 'img_path/'
img_path_det = 'res/'
img_path_background = 'background/'
foreground_mask_path = 'foreground_segmentation/'


class ForegroundMask:
    def __init__(self, anno_file_name=None, train_images_path=None,
                 foreground_mask_path=None, new_prefix=None):
        self.rnd_bg_num = 15
        self.window_size = 5
        self.threshold_val = 25
        self.anns = {}
        self.img_to_anns = defaultdict(list)
        self.id_to_img = defaultdict(list)
        self.images_original_path = train_images_path + '/'
        self.foreground_mask_path = foreground_mask_path + '/'

        if not os.path.exists(foreground_mask_path):
            os.makedirs(foreground_mask_path)

        if not anno_file_name == None:
            print('loading annotation into memory...')
            tic = time.time()
            dataset = json.load(open(anno_file_name, 'r'))
            assert type(dataset) == dict, 'annotation file format {} not supported'.format(type(dataset))
            print ('Done (t={:0.2f}s)'.format(time.time() - tic))
            self.dataset = dataset
            self.create_index(new_prefix)
            self.sorted_image_keys = sorted(self.img_to_anns.keys())

            background_img = self.get_background()
            self.process_foreground_mask(background_img)

    def create_index(self, new_prefix=None):

        if 'annotations' in self.dataset:
            for ann in self.dataset['annotations']:
                self.img_to_anns[new_prefix + ann['image_id']].append(ann)
                self.anns[ann['id']] = ann
        if 'images' in self.dataset:
            for img in self.dataset['images']:
                self.id_to_img[new_prefix + img['id']] = img

    @staticmethod
    def is_boxes_intersect(b1, b2):
        x1 = np.maximum(b1[0], b2[0])
        y1 = np.maximum(b1[1], b2[1])
        x2 = np.minimum(b1[2], b2[2])
        y2 = np.minimum(b1[3], b2[3])
        return x2 - x1 > 0 and y2 - y1 >0

    @staticmethod
    def external_rectangle(bboxes):
        bboxes = np.array(bboxes)
        x1 = np.amin(bboxes[:, 0])
        y1 = np.amin(bboxes[:, 1])
        x2 = np.amax(bboxes[:, 2])
        y2 = np.amax(bboxes[:, 3])
        bbox = [x1, y1, x2, y2]
        return bbox

    @staticmethod
    def img_process(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 5)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        return img

    def parse_bboxes(self, image_id):
        objs = self.img_to_anns[image_id]
        bboxes = []
        for obj in objs:
            bbox = obj['bbox']
            width = self.id_to_img[image_id]['width']
            height = self.id_to_img[image_id]['height']
            x1, y1, w, h = bbox
            x1 = np.clip(float(x1), 0, width)
            y1 = np.clip(float(y1), 0, height)
            w = np.clip(float(x1 + w), 0, width) - x1
            h = np.clip(float(y1 + h), 0, height) - y1
            if obj['area'] > 1 and w > 0 and h > 0 and w * h >= 4:
                bbox = [int(x1), int(y1), int(x1 + w), int(y1 + h)]
                bboxes.append(bbox)
        return bboxes

    def get_background(self):
        height = 0
        width = 0
        img_bgs = []
        image_idxs = np.random.choice(range(len(self.sorted_image_keys)), self.rnd_bg_num)

        for img_idx in image_idxs:
            image_id = self.sorted_image_keys[img_idx]
            image_path = self.images_original_path + image_id
            assert os.path.exists(image_path), image_path + ' not found'
            img = cv2.imread(image_path)

            bboxes = self.parse_bboxes(image_id)
            bbox = self.external_rectangle(bboxes)

            start_id = np.maximum(img_idx - self.window_size, 0)
            end_id = np.minimum(img_idx + self.window_size, len(self.sorted_image_keys))

            for other_image_idx in range(start_id, end_id):
                if other_image_idx == img_idx:
                    continue

                other_image_id = self.sorted_image_keys[other_image_idx]

                bbox_others = self.parse_bboxes(other_image_id)
                bbox_other = self.external_rectangle(bbox_others)

                if not self.is_boxes_intersect(bbox, bbox_other):
                    image_path_other = self.images_original_path + other_image_id
                    assert os.path.exists(image_path_other), image_path_other + ' not found'
                    img_other = cv2.imread(image_path_other)
                    img[bbox[1]:bbox[3], bbox[0]:bbox[2], :] = img_other[bbox[1]:bbox[3], bbox[0]:bbox[2], :]

                    # img_bg = self.img_process(img)
                    # height = img_bg.shape[0]
                    # width = img_bg.shape[1]
                    height = img.shape[0]
                    width = img.shape[1]

                    img_bg = np.reshape(img, height * width * 3)
                    img_bgs.append(img_bg)
                    break

        bg_lengths = len(img_bgs)

        # background_img = np.zeros(img_bgs[0].shape, dtype=np.int32)
        # for i in range(background_img.shape[0]):
        #     for j in range(background_img.shape[1]):
        #         sum = 0
        #         for img_bg in img_bgs:
        #             sum += img_bg[i][j]
        #         background_img[i][j] = np.round(sum / bg_lengths)

        # for img_bg in img_bgs:
        #     background_img[:, :] += img_bg[:, :]
        # background_img_mean = np.round(background_img[:, :] / bg_lengths)
        # background_img_mean = np.array(background_img_mean, dtype=np.uint8)
        #
        # height = background_img.shape[0]
        # width = background_img.shape[1]
        #
        # background_img_mean = np.reshape(background_img_mean, (height * width))
        # background_img = np.zeros((height*width), dtype=np.int32)
        #
        # for img_bg in img_bgs:
        #     img_bg = np.reshape(img_bg, height * width)
        #     change_idx = np.where(img_bg - 15 > background_img_mean)[0]
        #     img_bg[change_idx] = background_img_mean[change_idx]
        #     background_img[:] += img_bg
        #
        # background_img_mean = np.round(background_img[:] / bg_lengths)
        # background_img = np.array(background_img_mean, dtype=np.uint8).reshape((height, width))

        background_img = np.zeros(height * width * 3, dtype=np.int32)

        for idx in range(3):
            for img_bg_id, img_bg in enumerate(img_bgs):
                if idx > 0:
                    change_idx = np.where(img_bg - self.threshold_val > background_img_mean)[0]
                    img_bg[change_idx] = background_img_mean[change_idx]
                    img_bgs[img_bg_id] = img_bg
                background_img[:] += img_bg

            background_img_mean = np.round(background_img[:] / bg_lengths)
            background_img = np.zeros_like(background_img)

        background_img_formal = np.array(background_img_mean, dtype=np.uint8).reshape((height, width, 3))

        img_path_background_formal = self.foreground_mask_path + 'background_img.jpg'
        cv2.imwrite(img_path_background_formal, background_img_formal)

        return background_img_formal

    def process_foreground_mask(self, background_img_formal):
        for image_id in self.sorted_image_keys:
            image_path = self.images_original_path + image_id
            assert os.path.exists(image_path), image_path + ' not found'
            img = cv2.imread(image_path)

            img_gray = np.zeros((img.shape[0], img.shape[1]), dtype=np.int32)

            bboxes = self.parse_bboxes(image_id)
            bbox = self.external_rectangle(bboxes)

            img_partial = self.img_process(img[bbox[1]:bbox[3], bbox[0]:bbox[2], :])

            img_back_partial = background_img_formal[bbox[1]:bbox[3], bbox[0]:bbox[2]]

            difference = cv2.absdiff(img_partial, img_back_partial)
            difference = cv2.threshold(difference, self.threshold_val, 1, cv2.THRESH_BINARY)

            img_gray[bbox[1]:bbox[3], bbox[0]:bbox[2]] = difference[1]

            img_path_seg = self.foreground_mask_path + image_id
            cv2.imwrite(img_path_seg, img_gray)

            # image_origin_id = image_id.replace('ch00011', 'ch00011_origin')
            # img_path_seg = self.foreground_mask_path + image_origin_id
            # cv2.imwrite(img_path_seg, img)


# ForegroundMask(anno_file_name=annotation_path_file, train_images_path=images_original_path,
#                foreground_mask_path=foreground_mask_path)
