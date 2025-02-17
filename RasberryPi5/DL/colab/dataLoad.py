# 데이터 디렉토리 경로 설정
data_dir = '/content/video'

# 디렉토리 내 파일 목록 저장
file_list = os.listdir(data_dir)

# 이미지 경로와 조향 각도를 저장할 리스트 초기화
image_paths = []
steering_angles = []

# .png 파일을 필터링하기 위한 패턴 설정
pattern = "*.png"

# 디렉토리 내 파일 반복 처리
for filename in file_list:
    if fnmatch.fnmatch(filename, pattern):  # .png 파일만 처리
        # 이미지 파일 경로 추가
        image_paths.append(os.path.join(data_dir, filename))
        # 파일명에서 조향 각도를 추출 (예: 파일명이 train_00006_090.png일 경우 90을 추출)
        angle = int(filename[-7:-4])
        # 조향 각도 리스트에 추가
        steering_angles.append(angle)

# 특정 인덱스(예: 20번 데이터)의 이미지를 시각화하고 출력
image_index = 20
plt.imshow(Image.open(image_paths[image_index]))
print("image_path: %s" % image_paths[image_index])  # 이미지 경로 출력
print("steering_Angle: %d" % steering_angles[image_index])  # 조향 각도 출력

# 데이터프레임 생성
df = pd.DataFrame()
df['ImagePath'] = image_paths  # 이미지 경로 열 추가
df['Angle'] = steering_angles  # 각도 열 추가