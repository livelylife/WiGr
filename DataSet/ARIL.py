from __future__ import absolute_import, print_function
"""
ARILdata
"""
import torch
import torch.utils.data as data
from pathlib import Path
import os
import sys
sys.path.append('/home/yk/zx/Domain adaptation CSI V4/DataSet/')
import torch.nn as nn
import numpy as np
import itertools,functools
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from torch.utils.data import TensorDataset, DataLoader
from DataSet.CustomDataset import CustomIterDataset

def default_loader(root):   #root is the data storage path  eg. path = D:/CSI_Data/signfi_matlab2numpy/
    train_label_activity_path = root/"datatrain_activity_label.npy"
    train_amp_path = root/ "datatrain_data.npy"
    train_label_loc_path = root/"datatrain_location_label.npy"
    test_label_activity_path = root/"datatest_activity_label.npy"
    test_amp_path = root/"datatest_data.npy"
    test_label_loc_path = root/"datatest_location_label.npy"

    train_label_activity = np.load(train_label_activity_path)
    train_amp = np.load(train_amp_path)
    train_label_loc = np.load(train_label_loc_path)
    test_label_activity = np.load(test_label_activity_path)
    test_amp = np.load(test_amp_path)
    test_label_loc = np.load(test_label_loc_path)
    return train_label_activity,train_amp,train_label_loc,test_label_activity,test_amp,test_label_loc


def loader_all(root):   #root is the data storage path  eg. path = D:/CSI_Data/signfi_matlab2numpy/
    train_label_activity_path = root/"datatrain_activity_label.npy"
    train_amp_path = root/"datatrain_data.npy"
    train_label_loc_path = root/"datatrain_location_label.npy"
    test_label_activity_path = root/"datatest_activity_label.npy"
    test_amp_path = root / "datatest_data.npy"
    test_label_loc_path = root/ "datatest_location_label.npy"

    train_label_activity = np.load(train_label_activity_path)
    train_amp = np.load(train_amp_path)
    train_label_loc = np.load(train_label_loc_path)
    test_label_activity = np.load(test_label_activity_path)
    test_amp = np.load(test_amp_path)
    test_label_loc = np.load(test_label_loc_path)

    all_label_activity = np.concatenate((train_label_activity,test_label_activity))
    all_amp = np.concatenate((train_amp,test_amp))
    all_label_location = np.concatenate((train_label_loc, test_label_loc))
    return all_label_activity,all_label_location,all_amp


def split_array_bychunk(array, chunksize, include_residual=True):
    len_ = len(array) // chunksize * chunksize
    array, array_residual = array[:len_], array[len_:]
    # array = np.split(array, len_ // chunksize)
    array = [
        array[i * chunksize: (i + 1) * chunksize]
        for i in range(len(array) // chunksize)
    ]
    if include_residual:
        if len(array_residual) == 0:
            return array
        else:
            return array + [
                array_residual,
            ]
    else:
        if len(array_residual) == 0:
            return array, None
        else:
            return array, array_residual


class ARIL(CustomIterDataset):
    # def __init__(self, root, roomid=None,userid=None,location=None,orientation=None,receiverid=None,sampleid=None,
    #              data_shape=None,chunk_size=50,num_shot=1,batch_size=50,mode=None,loader=loader_all,trainmode=None,trainsize=0.8):
    #     """
    #     :param root: dataset storage path
    #     :param roomid: useless
    #     :param userid: useless
    #     :param location: choosing the location: {0,1,2,...,15}
    #     :param orientation: useless
    #     :param receiverid:useless
    #     :param sampleid:useless
    #     :param data_shape: if data_shape='split': we using repeat x chunck x 1 x subcarry data; else: '1D' we using the subcarry x time data; else '2D' we using the links X subcarry X time
    #     :param chunk_size:setting the length of every chunk on the time dimension.
    #     :param num_shot:the number of samples of each gesture(class) in the support set
    #     :param batch_size: the number of samples per class. hence that, the real_batch_size = batch_size * num_class
    #     :param mode: useless
    #     :param loader:
    #     """
    #
    #     super().__init__(trainmode,trainsize)
    #
    #
    #
    #     self.root = root
    #     self.load = loader
    #     self.data_shape = data_shape
    #     self.chunk_size = chunk_size
    #     self.batch_size = batch_size
    #     self.num_shot = num_shot
    #     self.num_class = 6
    #     self.batch_idx = 0
    #
    #     all_label_activity,  all_label_location, self.all_amp = loader_all(root)
    #     print(np.unique(all_label_activity),np.unique(all_label_location))
    #     self.all_label_activity = np.squeeze(all_label_activity)
    #     self.all_label_location = np.squeeze(all_label_location)
    #     self.total_samples = len(self.all_label_activity)
    #     self.loc_select = np.ones(self.total_samples, dtype=bool)
    #     index_temp = np.arange(self.total_samples)
    #
    #     if location is not None:
    #         self.loc_select = functools.reduce(np.logical_or,[*[self.all_label_location == j for j in location]])
    #
    #     self.index = index_temp[self.loc_select]
    #     np.random.shuffle(self.index)
    #
    #     # chosen_label = self.all_label_activity[self.index]
    #     # num_sample_per_class = []
    #     # self.sample_index_per_class = []
    #     # print("index shape",self.index.shape)
    #     # print("chosen label shape",chosen_label.shape)
    #     # for i in range(0,self.num_class):
    #     #     temp = self.index[np.where(chosen_label == i)]
    #     #     num_sample_per_class.append(len(temp))
    #     #     self.sample_index_per_class.append(temp)
    #     # self.min_num_sample_class = min(num_sample_per_class)  # find the minimal number of samples of all classes
    #     # self.num_batch = self.min_num_sample_class // self.batch_size
    #
    #     chosen_label = self.all_label_activity[self.index]
    #     print("index shape", self.index.shape)
    #     print("chosen label shape", chosen_label.shape)
    #
    #     # 1. 动态地从数据中找出所有实际存在的唯一类别标签
    #     self.present_classes = np.unique(chosen_label)
    #     # 2. 更新 self.num_class 为实际类别的数量，而不是硬编码的 6
    #     self.num_class = len(self.present_classes)
    #     print(f"[INFO] Classes actually present in this subset: {self.present_classes}")
    #
    #     num_sample_per_class = []
    #     self.sample_index_per_class = []
    #
    #     # 3. 只遍历实际存在的类别，而不是 range(0, 6)
    #     for class_label in self.present_classes:
    #         # 使用 (chosen_label == class_label) 作为布尔掩码，更高效且安全
    #         temp = self.index[chosen_label == class_label]
    #         num_sample_per_class.append(len(temp))
    #         self.sample_index_per_class.append(temp)
    #
    #     # 4. 安全地计算最小值，防止因列表为空而报错
    #     if not num_sample_per_class:
    #         self.min_num_sample_class = 0
    #     else:
    #         self.min_num_sample_class = min(num_sample_per_class)
    #
    #     self.num_batch = self.min_num_sample_class // self.batch_size
    #
    #     print(f"[DEBUG] Minimum samples per class: {self.min_num_sample_class}")
    #     print(f"[DEBUG] Batch size: {self.batch_size}")
    #     print(f"[DEBUG] Calculated number of batches: {self.num_batch}")
    #     if self.num_batch == 0 and self.min_num_sample_class > 0:
    #         raise ValueError(
    #             f"DataLoader will be empty. Your batch_size ({self.batch_size}) "
    #             f"is larger than the minimum number of samples per class ({self.min_num_sample_class}). "
    #             f"Please reduce the batch_size."
    #         )

    def __init__(self, root, roomid=None, userid=None, location=None, orientation=None, receiverid=None, sampleid=None,
                 data_shape=None, chunk_size=50, num_shot=1, batch_size=50, mode=None, loader=loader_all,
                 trainmode=None, trainsize=0.8):

        super().__init__(trainmode, trainsize)

        self.root = root
        self.load = loader
        self.data_shape = data_shape
        self.chunk_size = chunk_size
        self.batch_size = batch_size
        self.num_shot = num_shot
        self.batch_idx = 0

        # 1. 加载所有数据
        all_label_activity, all_label_location, self.all_amp = loader_all(root)
        self.all_label_activity = np.squeeze(all_label_activity)
        self.all_label_location = np.squeeze(all_label_location)
        self.total_samples = len(self.all_label_activity)
        index_temp = np.arange(self.total_samples)

        # 2. 根据 location 参数筛选数据
        # 如果 location 不为 None，则只保留指定位置的样本
        if location is not None:
            print(f"[INFO] Filtering dataset for location(s): {location}")
            self.loc_select = functools.reduce(np.logical_or, [*[self.all_label_location == j for j in location]])
            self.index = index_temp[self.loc_select]
        else:
            print("[INFO] Using all locations in the dataset.")
            self.index = index_temp

        np.random.shuffle(self.index)

        # 获取筛选后的活动标签
        chosen_label = self.all_label_activity[self.index]

        # 如果筛选后没有任何样本，直接报错
        if len(chosen_label) == 0:
            raise ValueError(f"No samples found for the specified location(s): {location}. Dataset is empty.")

        # ======================= BEGIN DIAGNOSTIC BLOCK =======================
        unique_labels, counts = np.unique(chosen_label, return_counts=True)
        label_distribution = dict(zip(unique_labels, counts))
        print("\n" + "=" * 60)
        print("DIAGNOSTIC REPORT: FINAL DATASET STATE BEFORE GROUPING")
        print(f"Total samples being processed in this run: {len(chosen_label)}")
        print("Distribution of activity labels in this subset:")
        for label, count in label_distribution.items():
            print(f"  - Class {label}: {count} samples")
        print("=" * 60 + "\n")
        # ======================== END DIAGNOSTIC BLOCK ========================

        # 3. 动态地从数据中找出所有实际存在的类别
        self.present_classes = np.unique(chosen_label)
        self.num_class = len(self.present_classes)  # 更新类别总数为实际数量
        print(f"[INFO] Classes actually present in this subset: {self.present_classes}")

        # 4. 只针对存在的类别，获取其样本数量
        num_sample_per_class = []
        self.sample_index_per_class = []
        for class_label in self.present_classes:
            temp = self.index[chosen_label == class_label]
            num_sample_per_class.append(len(temp))
            self.sample_index_per_class.append(temp)

        # 5. 计算最小样本数，并进行最终检查
        self.min_num_sample_class = min(num_sample_per_class)

        # 检查 batch_size 是否大于 num_shot
        if self.batch_size <= self.num_shot:
            raise ValueError(f"batch_size ({self.batch_size}) must be greater than num_shot ({self.num_shot}) "
                             f"to have at least one query sample.")

        self.num_batch = self.min_num_sample_class // self.batch_size

        print(f"[DEBUG] Minimum samples per class in this subset: {self.min_num_sample_class}")
        print(f"[DEBUG] Batch size for episodic training: {self.batch_size}")
        print(f"[DEBUG] Calculated number of batches (episodes): {self.num_batch}")

        # 这是最终的、也是最关键的检查
        if self.num_batch == 0:
            raise ValueError(
                f"DataLoader will be empty. Your batch_size ({self.batch_size}) is too large "
                f"for the minimum number of samples per class ({self.min_num_sample_class}).\n"
                f"SOLUTION: Either reduce batch_size to be <= {self.min_num_sample_class} or use a larger dataset (e.g., set location=None)."
            )

    def get_item(self, index):
        sample_index = index
        activity_label_index = self.all_label_activity[sample_index]

        ges_label = torch.tensor(activity_label_index).type(torch.LongTensor)
        data_index = self.all_amp[sample_index]  # shape [52,196]

        if self.data_shape == 'split':
            data_temp = np.swapaxes(data_index, 0, 1)  # shape [192,52]
            samp, samp_res = split_array_bychunk(data_temp, self.chunk_size,
                                                 include_residual=False)  # shape list{[chunk,52],repeat}
            samp += [data_temp[-self.chunk_size:], ]
            sample = torch.Tensor(np.array(samp))  # shape [repeat,chunk,52]
            sample = sample.unsqueeze(dim=1).type(torch.FloatTensor)  # shape [repeat,1,chunk,52]
        elif self.data_shape == '1D':
            sample = torch.from_numpy(data_index).type(torch.FloatTensor)  # shape [52,196]
        elif self.data_shape == '2D':
            sample = torch.from_numpy(data_index).type(torch.FloatTensor)  # shape [52,196]
            sample = sample.unsqueeze(0)  # shape [1,52,192]
        else:
            sample = torch.from_numpy(data_index).type(torch.FloatTensor)  # shape [52,196]

        return sample,ges_label,

    def metric_data(self):
        # sampling a batch data and split to supportset and training/testing set
        query_data=[]
        query_ges_label = []

        supports_data = []
        supports_ges_label = []
        for i in range(self.num_class):
            temp = self.sample_index_per_class[i][self.batch_idx*self.batch_size:(self.batch_idx+1)*self.batch_size]
            for j in range(0,self.batch_size-self.num_shot):
                sample, ges_label = self.get_item(temp[j])
                query_data.append(sample)
                query_ges_label.append(ges_label)
            for k in range(self.batch_size-self.num_shot,self.batch_size):
                sample, ges_label = self.get_item(temp[k])
                supports_data.append(sample)
                supports_ges_label.append(ges_label)

        self.batch_idx += 1
        return (query_data,query_ges_label),(supports_data,supports_ges_label)

    def __iter__(self):
        return self

    def __next__(self):
        if self.batch_idx > self.num_batch-1:
            self.batch_idx = 0
            raise StopIteration
        return self.metric_data()

    def __len__(self):
        return self.num_batch


if __name__ == "__main__":
    root = Path("../ARIL")
    a = ARIL(root=root,location=[13],chunk_size=30,num_shot=1,batch_size=5,data_shape='1D')

    print(a.num_batch)
    print(len(a.index))
    print(a.min_num_sample_class)

    tr_loader = DataLoader(dataset=a,collate_fn=lambda x:x,)
    for i,x in enumerate(tr_loader):
        x = x[0]
        print(len(x))  # query set , support set
        print(len(x[0]))  # query set : 2   (list.data,list.ges_label)
        print(len(x[1]))  # support set  : 2   (list.data,list.ges_label)
        print(len(x[1][0]))  # 12
        print(len(x[0][0]))  # 228
        print(x[0][0][0].shape)  # torch.Size([7, 1, 30, 52])
        print(x[0][1][0].shape)  # torch.Size([])
        print(x[0][0][0])
        break




