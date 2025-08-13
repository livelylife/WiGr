import numpy as np
from scipy.io import loadmat

# The root directory path
root = '/home/guoq/shared_data/datasets/ARIL'

# Load train / test data
train_data = loadmat(root + '/train_data.mat')
test_data = loadmat(root + '/test_data.mat')

print(train_data.keys())
# Extract train data
train_data_amp = train_data['train_data_amp']
train_data_pha = train_data['train_data_pha']
train_label_instance = train_data['train_label_instance']
train_label_mask = train_data['train_label_mask']
train_label_time = train_data['train_label_time']
print(train_data_amp.shape)
print(train_data_pha.shape)
print(train_label_instance.shape)
print(train_label_mask.shape)
print(train_label_time.shape)
# Extract test data
test_data_amp = test_data['test_data_amp']
test_data_pha = test_data['test_data_pha']
test_label_instance = test_data['test_label_instance']
test_label_mask = test_data['test_label_mask']
test_label_time = test_data['test_label_time']

# 假设你已经加载了 train_label_instance 和 train_label_mask
unique_activities = np.unique(train_label_instance)
unique_locations = np.unique(train_label_mask)

print(f"Unique values in train_label_instance: {unique_activities}")
print(f"Unique values in train_label_mask: {unique_locations}")

# Save the train data in .npy format
# np.save(root + "/datatrain_activity_label.npy", train_label_instance[:,0])
# np.save(root + "/datatrain_data.npy", train_data_amp)
# np.save(root + "/datatrain_location_label.npy", train_label_mask[:,0])
#
# # Save the test data in .npy format
# np.save(root + "/datatest_activity_label.npy", test_label_instance[:,0])
# np.save(root + "/datatest_data.npy", test_data_amp)
# np.save(root + "/datatest_location_label.npy", test_label_mask[:,0])