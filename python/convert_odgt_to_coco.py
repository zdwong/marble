# coding: utf-8

import os
import json
import argparse
from PIL import Image

def load_file(fpath):
    assert os.path.exists(fpath)
    with open(fpath,'r') as fid:
        lines = fid.readlines()
    records = [json.loads(line.strip('\n')) for line in lines]
    return records

def crowdhuman_to_coco(odgt_file, image_path, output_json_file):
    records = load_file(odgt_file)

    json_dict = {"images": [], "annotations": [], "categories": []}
    image_id = 1
    instance_id = 1
    image = {}
    annotation = {}
    categories = {}
    record_list = len(records)
    print(record_list)

    for i in range(record_list):
        file_name = records[i]['ID'] + '.jpg'
        image_id = records[i]['ID'] + '.jpg'
        im = Image.open(image_path + '/' + file_name)

        image = {
                 'file_name': file_name, 
                 'height': im.size[1], 
                 'width': im.size[0],
                 'id': image_id
                }

        json_dict['images'].append(image)

        gt_box = records[i]['gtboxes']
        gt_box_len = len(gt_box)
        for j in range(gt_box_len):
            category = gt_box[j]['tag']
            if category not in categories and category != 'mask':
                new_id = len(categories) + 1
                categories[category] = new_id
   
            # category_id = categories[category]
            category_id = 1 

            fbox = gt_box[j]['fbox']
            x1, y1, f_w, f_h = fbox

            vbox = gt_box[j]['vbox']
            x2, y2, v_w, v_h = vbox

            hbox = gt_box[j]['hbox']
            x3, y3, h_w, h_h = hbox

            ignore = 0

            #if "ignore" in gt_box[j]['head_attr'] and gt_box[j]['head_attr']['ignore']:
            #    ignore = gt_box[j]['head_attr']['ignore']

            if "ignore" in gt_box[j]['extra'] and gt_box[j]['extra']['ignore']:
                 ignore = gt_box[j]['extra']['ignore']
            if category == 'mask':
                ignore = 1

            # if ignore:
            #   continue

            annotation = {
                          'area': fbox[2] * fbox[3], 
            #              'area': vbox[2] * vbox[3], 
            #              'area': hbox[2] * hbox[3], 
                          'iscrowd': ignore, 
                          'image_id': image_id,
                          'bbox': gt_box[j]['fbox'], 
            #              'bbox': gt_box[j]['vbox'], 
            #              'bbox': gt_box[j]['hbox'], 
                          'hbox': gt_box[j]['hbox'], 
                          'vbox': gt_box[j]['vbox'],
                          'fbox': gt_box[j]['fbox'], 
            #              'category_id': category_id, 
                          'category_id': 1, 
                          'id': instance_id, 
                          'ignore': ignore, 
                          'segmentation': [], 
                          'height': f_h, 
                          'vis_ratio': (v_w * v_h) / (f_w * f_h) 
            #              'vis_ratio': 1 
                         }

            json_dict['annotations'].append(annotation)

            instance_id += 1

    for cate, cid in categories.items():
        #cat = {'id': cid, 'name': cate}
        cat = {'id': 1, 'name': cate}
        json_dict['categories'].append(cat)

    with open(output_json_file, 'w') as f:
        json.dump(json_dict, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--odgt_file', type=str, help='odgt annotation file',
                        default='annotations/annotation_val.odgt')
    parser.add_argument('--image_path', type=str, help='corresponding image path',
                        default='Images')
    parser.add_argument('--output_json_file', type=str, help='JSON format annotation file',
                        default='annotations/instances_val_full_new.json')

    args = parser.parse_args()
    crowdhuman_to_coco(args.odgt_file, args.image_path, args.output_json_file)
