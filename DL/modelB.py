import os
import random

# 원본 이미지가 있는 폴더 경로
folder_path = r"C:\Users\USER\OneDrive\바탕 화면\RC_CAR\Right"

# 결과 이미지 파일명에 사용할 랜덤 번호 생성
def rename_images_randomly(folder_path):
    # 폴더 내의 파일 리스트 가져오기
    file_list = [file for file in os.listdir(folder_path) if file.endswith(('.png', '.jpg', '.jpeg'))]

    # 파일을 랜덤하게 섞기
    random.shuffle(file_list)

    # 번호를 순서대로 붙이며 파일명 변경
    for idx, filename in enumerate(file_list):
        # 파일 확장자 추출
        _, ext = os.path.splitext(filename)
        # 새로운 파일명 생성
        new_name = f"Right_{idx + 1}{ext}"
        # 기존 파일 경로와 새 파일 경로
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_name)
        # 파일명 변경
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_name}")

# 함수 실행
rename_images_randomly(folder_path)