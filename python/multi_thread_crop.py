import os
import cv2
import queue
import tqdm
import threading

THREAD_NUM = 10
queueLock = threading.Lock()
mkdir_lock = threading.Lock()

dest_folder = 'crop_image_path'
prefix_len = len('path_prefix')

class ProcessThread(threading.Thread):
    def __init__(self, thread_id, q, func):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.q = q
        self.func = func

    def run(self):
        print("thread %d start" % self.threadID)
        process_center_crop(self.threadID, self.q, self.func)
        print("thread %d end" % self.threadID)

def process_center_crop(thread_id, queue, func):
    while not queue.empty():
        queueLock.acquire()
        if not queue.empty():
            line = queue.get()
            queueLock.release()
            func(line)
        else:
            queueLock.release()

def start_group_threads(lines, process_func):
    thread_list = []
    imgs_queue = queue.Queue()

    queueLock.acquire()
    for line in tqdm.tqdm(lines):
        imgs_queue.put(line)
    queueLock.release()

    for threadID in range(1, THREAD_NUM + 1):
        thread = ProcessThread(threadID, imgs_queue, process_func)
        thread.start()
        thread_list.append(thread)

    for t in thread_list:
        t.join()

    print("exist main Thread")

def center_crop_core(line):
    face_img_file = line.split(' ')[0]
    img = cv2.imread(face_img_file)
    img = img[50:250, 50:250]
    img = cv2.resize(img, (128, 128))
    dst_file_name = os.path.basename(face_img_file)
    behind_name = face_img_file[prefix_len:]
    middle_name = behind_name[:-len(dst_file_name)]
    prefix_path = os.path.join(dest_folder, middle_name)
    mkdir_lock.acquire()
    if not os.path.exists(prefix_path):
        os.mkdir(prefix_path)
    mkdir_lock.release()
    whole_file_name = os.path.join(prefix_path, dst_file_name)
    cv2.imwrite(whole_file_name, img)

def center_crop(face_id_file):
    with open(face_id_file) as face_fl:
        lines = face_fl.readlines()
        start_group_threads(lines, center_crop_core)

if __name__ == '__main__':
    train_list = 'train_list.list'
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)
    center_crop(wanda_train_list)

