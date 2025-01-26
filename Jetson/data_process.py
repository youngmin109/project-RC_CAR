import os
import cv2
import random
import shutil
from glob import glob

# 원본 데이터셋 폴더 및 전처리 후 데이터셋 저장 폴더
BASE_DIR = "dataset2"  # 기존 데이터셋 폴더
OUTPUT_DIR = "processed_dataset2"  # 전처리된 데이터셋 저장 폴더
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 목표 이미지 개수 및 크기 설정
TARGET_COUNT = 1000
TARGET_SIZE = (64, 64)  # 이미지 크기 조정

# 1. 크기 조정 및 전처리 함수
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"이미지를 열 수 없습니다: {image_path}")
        return None
    # 상단 20% 크롭
    height = img.shape[0]
    crop_height = int(height * 0.1)  # 상단 20% 제거
    cropped_img = img[crop_height:, :]

    # 크기 조정
    resized_img = cv2.resize(cropped_img, TARGET_SIZE, interpolation=cv2.INTER_AREA)

    # 밝기 및 대비 조정
    adjusted_img = cv2.convertScaleAbs(resized_img, alpha=1.2, beta=-30)

    return adjusted_img

# 2. 데이터 균형화 및 전처리 수행
def balance_and_preprocess_data():
    print(f"모든 폴더의 이미지를 {TARGET_COUNT}장으로 맞춥니다.")
    folders = [os.path.join(BASE_DIR, d) for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

    for folder in folders:
        image_files = glob(os.path.join(folder, "*.jpg"))
        folder_name = os.path.basename(folder)
        output_folder = os.path.join(OUTPUT_DIR, folder_name)
        os.makedirs(output_folder, exist_ok=True)

        # 랜덤 샘플링 (언더샘플링)
        if len(image_files) > TARGET_COUNT:
            image_files = random.sample(image_files, TARGET_COUNT)
        
        # 랜덤 복제 (오버샘플링)
        while len(image_files) < TARGET_COUNT:
            image_files.append(random.choice(image_files))

        # 이미지 처리 및 저장
        for idx, img_path in enumerate(random.sample(image_files, TARGET_COUNT)):
            processed_img = preprocess_image(img_path)
            if processed_img is not None:
                new_filename = f"{folder_name}_{idx}.jpg"
                cv2.imwrite(os.path.join(output_folder, new_filename), processed_img)

    print("데이터 전처리 및 균형 맞추기 완료!")

# 3. 폴더별 이미지 개수 확인 함수
def count_images_in_folders(folder_path):
    folders = [os.path.join(folder_path, d) for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
    image_counts = {os.path.basename(folder): len(glob(os.path.join(folder, "*.jpg"))) for folder in folders}
    return image_counts

# 4. 데이터 분포 출력 함수
def print_image_distribution(image_counts):
    print("폴더별 이미지 개수:")
    for folder, count in image_counts.items():
        print(f"{folder}: {count}")

# 5. 압축 함수
def compress_dataset(output_zip_name="processed_dataset2.zip"):
    shutil.make_archive(output_zip_name.replace(".zip", ""), 'zip', OUTPUT_DIR)
    print(f"데이터셋이 압축되었습니다: {output_zip_name}")

# 6. 통합 실행
if __name__ == "__main__":
    # 전처리 전 데이터 분포 확인
    print("전처리 전 데이터 분포 확인 중...")
    pre_counts = count_images_in_folders(BASE_DIR)
    print_image_distribution(pre_counts)

    # 데이터 전처리 및 균형 조정 수행
    print("데이터 전처리 및 균형화 수행 중...")
    balance_and_preprocess_data()

    # 전처리 후 데이터 분포 확인
    print("전처리 후 데이터 분포 확인 중...")
    post_counts = count_images_in_folders(OUTPUT_DIR)
    print_image_distribution(post_counts)

    # 데이터 압축
    compress_dataset()

    print("모든 데이터 전처리 작업이 완료되었습니다.")
