import os
import cv2
import shutil
import random
from tqdm import tqdm
from imutils import paths

# 원본 데이터셋 경로 및 저장할 경로
original_data_dir = "dataSet"
processed_data_dir = "dataSet"

# 목표 데이터 개수 설정 (모든 각도를 동일한 수로 맞춤)
target_count = 500  

# 새로운 데이터 디렉토리 생성
if os.path.exists(processed_data_dir):
    shutil.rmtree(processed_data_dir)
os.makedirs(processed_data_dir)

# 전처리 및 균형화 함수
def preprocess_and_balance_images(image_paths, output_path, angle):
    if len(image_paths) < target_count:
        # 데이터 증강 (부족한 경우 오버샘플링)
        augmented_images = []
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

            augmented_images.append(adjusted_image)

            # 데이터 증강 (좌우반전, 블러 추가)
            flipped = cv2.flip(adjusted_image, 1)
            blurred = cv2.GaussianBlur(adjusted_image, (5, 5), 0)

            augmented_images.extend([flipped, blurred])

            if len(augmented_images) >= target_count:
                break

        # 이미지 저장
        for idx, img in enumerate(augmented_images[:target_count]):
            filename = os.path.join(output_path, f"angle_{angle}_{idx}.jpg")
            cv2.imwrite(filename, img)

    else:
        # 데이터 언더샘플링 (넘치는 경우 일부만 사용)
        selected_images = random.sample(image_paths, target_count)
        for idx, img_path in enumerate(selected_images):
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

            filename = os.path.join(output_path, f"angle_{angle}_{idx}.jpg")
            cv2.imwrite(filename, adjusted_image)

# 데이터 균형화 실행
for angle_folder in os.listdir(original_data_dir):
    angle = angle_folder  # 각도 폴더 이름 사용
    input_folder = os.path.join(original_data_dir, angle_folder)
    output_folder = os.path.join(processed_data_dir, angle_folder)

    os.makedirs(output_folder, exist_ok=True)

    image_paths = list(paths.list_images(input_folder))
    preprocess_and_balance_images(image_paths, output_folder, angle)

# 전처리된 데이터 압축
shutil.make_archive("balanced_dataset", 'zip', processed_data_dir)

print("데이터 전처리 및 균형화 완료. 파일명: balanced_dataset.zip")
