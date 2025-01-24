import os
import cv2
import shutil
import random
from tqdm import tqdm
from imutils import paths

# 원본 데이터셋 경로 및 저장할 경로
original_data_dir = "dataSet"
processed_data_dir = "balancedDataSet"

# 목표 데이터 개수 설정 (각도별 800장으로 균형화)
target_count = 800  

# 새로운 데이터 디렉토리 생성
if os.path.exists(processed_data_dir):
    shutil.rmtree(processed_data_dir)
os.makedirs(processed_data_dir)

# 전처리 및 균형화 함수
def preprocess_and_balance_images(image_paths, output_path, angle):
    processed_images = []

    for img_path in image_paths:
        image = cv2.imread(img_path)
        if image is None:
            continue

        # 상단 30% 크롭
        height = image.shape[0]
        crop_height = int(height * 0.3)
        cropped_image = image[crop_height:, :]

        # 크기 조정
        resized_image = cv2.resize(cropped_image, (224, 224))

        # 밝기 및 대비 조정
        adjusted_image = cv2.convertScaleAbs(resized_image, alpha=1.2, beta=-30)

        processed_images.append(adjusted_image)

    # 부족한 경우 랜덤 오버샘플링
    if len(processed_images) < target_count:
        while len(processed_images) < target_count:
            augmented_image = random.choice(processed_images)
            processed_images.append(augmented_image)

    # 넘치는 경우 랜덤 샘플링
    processed_images = random.sample(processed_images, target_count)

    # 이미지 저장 (각도 정보 포함)
    for idx, img in enumerate(processed_images):
        filename = os.path.join(output_path, f"angle_{angle}_{idx}.jpg")
        cv2.imwrite(filename, img)

# 모든 데이터를 하나의 폴더에 저장
all_images_folder = os.path.join(processed_data_dir, "all_images")
os.makedirs(all_images_folder, exist_ok=True)

# 데이터 전처리 및 균형화 실행
for angle_folder in os.listdir(original_data_dir):
    angle = angle_folder  # 각도 폴더 이름 사용
    input_folder = os.path.join(original_data_dir, angle_folder)

    image_paths = list(paths.list_images(input_folder))
    preprocess_and_balance_images(image_paths, all_images_folder, angle)

# 전처리된 데이터 압축
shutil.make_archive("dataset_balanced", 'zip', processed_data_dir)

print("데이터 전처리 및 균형화 완료. 파일명: dataset_balanced.zip")
