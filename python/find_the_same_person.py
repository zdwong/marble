import os
import cv2
import shutil
from collections import defaultdict
from collections import OrderedDict


def parse_sparsedis_file(sparsedis_path_file, top_n):
    with open(sparsedis_path_file, 'r') as f:
        lines = f.readlines()
        top_n_dis_ptks_map = defaultdict(list)
        for line in lines:
            words = line.strip().split()
            if len(words) == 0:
                continue
            search_ptk = words[0]
            pb_ptks = words[1::2]
            pb_dises = words[2::2]
            if len(pb_ptks) < top_n:
                top_n = len(pb_ptks)
            for i in range(top_n):
                top_n_dis_ptks_map[search_ptk].append((pb_ptks[i], pb_dises[i]))
        return top_n_dis_ptks_map


def process(data_faces_dir, root_sparsedis_file, res_dir, top_n):
    sparsedis_files = os.listdir(root_sparsedis_file)
    all_top_n_dis_ptks_map = defaultdict(list)
    for spd_file in sparsedis_files:
        if 'this_one' not in spd_file:
            continue
        top_n_dis_ptks_map = parse_sparsedis_file(root_sparsedis_file + spd_file, top_n)
        for search_ptk, near_ptks in top_n_dis_ptks_map.items():
            all_top_n_dis_ptks_map[search_ptk] += near_ptks

    # each search
    each_res_dir = os.path.join(res_dir, 'each_top' + str(top_n))
    if not os.path.exists(each_res_dir):
        os.mkdir(each_res_dir)
    for search_ptk, near_ptks in all_top_n_dis_ptks_map.items():
        ptk_res_dir = os.path.join(each_res_dir, search_ptk)
        if not os.path.exists(ptk_res_dir):
            os.mkdir(ptk_res_dir)
        ptk_res_list = os.path.join(each_res_dir, search_ptk + '.list')
        with open(ptk_res_list, 'w') as f:
            sort_near_ptks = sorted(near_ptks, key=lambda x: x[1])
            top_count = 1
            for info_ptk in sort_near_ptks:
                ptk = info_ptk[0]
                distance = info_ptk[1]
                f.write(ptk + ',' + distance + '\n')
                date = ptk[-8:]
                #root_path = data_faces_dir + date + '/face/'
                root_path = data_faces_dir 
                shutil.copy(os.path.join(root_path, ptk + '.jpg'),
                            os.path.join(ptk_res_dir, ptk + '_' + distance + '.jpg'))
                if top_count >= top_n:
                    break
                top_count += 1
            f.close()

    # union
    union_map = {}
    for search_ptk, near_ptks in all_top_n_dis_ptks_map.items():
        for info_ptk in near_ptks:
            ptk = info_ptk[0]
            distance = info_ptk[1]
            if ptk in union_map.keys():
                if union_map[ptk] > distance:
                    union_map[ptk] = distance
            else:
                union_map[ptk] = distance

    sort_union_map = OrderedDict(sorted(union_map.items(), key=lambda x: x[1]))
    ptk_res_dir = os.path.join(res_dir, 'union_top' + str(top_n))
    if not os.path.exists(ptk_res_dir):
        os.mkdir(ptk_res_dir)
    ptk_res_list = os.path.join(res_dir, 'union_top' + str(top_n) + '.list')
    top_count = 1
    with open(ptk_res_list, 'w') as f:
        for ptk, distance in sort_union_map.items():
            f.write(ptk + ',' + distance + '\n')
            date = ptk[-8:]
            #root_path = data_faces_dir + date + '/face/'
            root_path = data_faces_dir 
            shutil.copy(os.path.join(root_path, ptk + '.jpg'),
                        os.path.join(ptk_res_dir, ptk + '_' + distance + '.jpg'))
            if top_count >= top_n:
                break
            top_count += 1
        f.close()

    # intersection
    search_ptks_lists = []
    for search_ptk, near_ptks in all_top_n_dis_ptks_map.items():
        ptk_list = []
        for info_ptk in near_ptks:
            ptk = info_ptk[0]
            ptk_list.append(ptk)
        search_ptks_lists.append(ptk_list)

    intersect_ptks = []
    if len(search_ptks_lists) > 0:
        intersect_ptks = search_ptks_lists[0]
    for i in range(1, len(search_ptks_lists)):
        intersect_ptks = list(set(intersect_ptks) & set(search_ptks_lists[i]))

    intersect_map = {}
    for ptk in intersect_ptks:
        intersect_map[ptk] = union_map[ptk]
    sort_intersect_map = OrderedDict(sorted(intersect_map.items(), key=lambda x: x[1]))
    ptk_res_dir = os.path.join(res_dir, 'intersect_top' + str(top_n))
    if not os.path.exists(ptk_res_dir):
        os.mkdir(ptk_res_dir)
    ptk_res_list = os.path.join(res_dir, 'intersect_top' + str(top_n) + '.list')
    top_count = 1
    with open(ptk_res_list, 'w') as f:
        for ptk, distance in sort_intersect_map.items():
            f.write(ptk + ',' + distance + '\n')
            date = ptk[-8:]
            #root_path = data_faces_dir + date + '/face/'
            root_path = data_faces_dir 
            shutil.copy(os.path.join(root_path, ptk + '.jpg'),
                        os.path.join(ptk_res_dir, ptk + '_' + distance + '.jpg'))
            if top_count >= top_n:
                break
            top_count += 1
        f.close()


if __name__ == '__main__':
    data_faces_dir = './image/face/'
    root_sparsedis_file = './sparsedis_res_file/'
    res_dir = './res/'
    top_n =10 
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)
    process(data_faces_dir, root_sparsedis_file, res_dir, top_n)

