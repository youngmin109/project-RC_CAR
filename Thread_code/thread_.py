import threading

def control_rc_car():
    """
    RC 자동차의 동작을 제어하는 함수.
    키보드 입력을 받아 모터와 서보모터를 제어
    """

def capture_video():
    """
    웹캠에서 실시간 영상을 캡처하고 파일로 저장하는 함수
    """

def main():
    """
    메인 실행 함수.
    - RC 자동차 제어: 메인 스레드에서 실행.
    - 웹캠 촬영 및 저장: 별도 스레드에서 병렬 실행.
    """

    video_thread = threading.Thread(target=capture_video)
    video_thread.start()

    control_rc_car()

    video_thread.join()
    print("Program has ended.")

if __name__ == "__main__":
    main()