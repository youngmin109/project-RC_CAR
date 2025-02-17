import cv2
 # 카메라 객체 생성 (카메라 ID 0: 기본 카메라)
cap = cv2.VideoCapture(0)
 # 영상이 제대로 열렸는지 확인
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()
 # 무한 루프를 통해 실시간으로 프레임 캡처
while True:
    # 카메라로부터 프레임 읽기
    ret, frame = cap.read()
    
    # 프레임을 제대로 읽었다면 화면에 표시
    if not ret:
        print("프레임을 받아올 수 없습니다.")
        break
    
    # 프레임을 화면에 표시
    cv2.imshow('Live Camera', frame)
    
    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 # 리소스 해제
cap.release()
cv2.destroyAllWindows()