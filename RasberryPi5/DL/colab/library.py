# 일반적으로 사용하는 라이브러리
import os
import random
import fnmatch
import datetime
import pickle

# 데이터 처리에 필요한 라이브러리
# data processing
import numpy as np
np.set_printoptions(formatter={'float_kind':lambda x: "%.4f" % x})

import pandas as pd
pd.set_option('display.width', 300)
pd.set_option('display.float_format', '{:.4f}'.format)
pd.set_option('display.max_colwidth', 200)

# 인공지능에 필요한 라이브러리
# tensorflow
import tensorflow as tf
import tensorflow.keras
from tensorflow.keras.models import Sequential  # V2 is tensorflow.keras.xxxx, V1 is keras.xxx
from tensorflow.keras.layers import Conv2D, MaxPool2D, Dropout, Flatten, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model

# 텐서플로 버전 출력
print(f'tf.__version__: {tf.__version__}')

# sklearn 라이브러리
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

# imaging
# 이미지 처리, 그래프 그리기에 필요한 라이브러리
import cv2
from imgaug import augmenters as img_aug
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
%matplotlib inline
from PIL import Image
