import os

# 대상 폴더 경로
folder_path = r"C:\Users\USER\OneDrive\바탕 화면\process\images\Straight"

def rename_files_with_prefix_and_number(folder):
    try:
        # 폴더 내 파일 리스트 가져오기
        files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]

        # 파일 이름 변경 (순서대로)
        for index, file_name in enumerate(files, start=1):
            # 확장자 분리
            _, ext = os.path.splitext(file_name)

            # 새 파일 이름 생성
            new_name = f"Straight_{index}{ext}"
            
            # 경로 생성
            old_path = os.path.join(folder, file_name)
            new_path = os.path.join(folder, new_name)

            # 이름 변경
            os.rename(old_path, new_path)
            print(f"Renamed: {file_name} -> {new_name}")

        print("모든 파일의 이름이 성공적으로 변경되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

# 함수 실행
rename_files_with_prefix_and_number(folder_path)
