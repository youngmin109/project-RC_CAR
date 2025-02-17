import os

def rename_files_by_keyword(folder_path):
    """
    폴더 내 파일 이름에서 'Left' 또는 'Right'를 포함한 파일만 변경하는 함수

    Parameters:
        folder_path (str): 파일이 저장된 폴더 경로

    Returns:
        None
    """
    try:
        # 폴더 내 파일 목록 가져오기
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        # 'Left'와 'Right'를 위한 카운터 초기화
        left_count = 1
        right_count = 1
        
        # 파일 이름 변경
        for file_name in files:
            # 확장자 분리
            _, ext = os.path.splitext(file_name)

            if "Left" in file_name:
                new_name = f"Left {left_count}{ext}"
                left_count += 1
            elif "Right" in file_name:
                new_name = f"Right {right_count}{ext}"
                right_count += 1
            else:
                continue  # 'Left'나 'Right'가 없는 경우 건너뜀

            # 파일 경로 지정
            old_file = os.path.join(folder_path, file_name)
            new_file = os.path.join(folder_path, new_name)

            # 파일 이름 변경
            os.rename(old_file, new_file)
            print(f"파일 이름 변경: {file_name} -> {new_name}")

    except Exception as e:
        print(f"파일 이름 변경 중 오류 발생: {e}")

# 예제 실행
folder_path = r"C:\Users\USER\OneDrive\바탕 화면\process\images"  # 파일이 저장된 폴더 경로
rename_files_by_keyword(folder_path)
