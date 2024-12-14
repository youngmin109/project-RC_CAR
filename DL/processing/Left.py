import os

# 폴더 경로 설정
folder_path = "C:/Users/USER/Downloads/images/Right"  # 여기에 폴더 경로를 입력하세요
prefix = "Right_"  # 파일 이름 앞에 붙일 접두사 ("Left_" 또는 "Right_" 등)

# 폴더 내 파일 이름 변경
def rename_files_in_folder(folder_path, prefix):
    try:
        files = os.listdir(folder_path)  # 폴더 내 모든 파일 목록 가져오기
        for filename in files:
            # 기존 파일 경로
            old_file_path = os.path.join(folder_path, filename)
            
            # 디렉토리가 아니라 파일일 경우에만 진행
            if os.path.isfile(old_file_path):
                # 새로운 파일 이름 생성
                new_filename = prefix + filename
                new_file_path = os.path.join(folder_path, new_filename)
                
                # 파일 이름 변경
                os.rename(old_file_path, new_file_path)
                print(f"{filename} -> {new_filename}")
    except Exception as e:
        print("오류 발생:", e)

# 실행
rename_files_in_folder(folder_path, prefix)
