import tensorflow as tf

# .h5 파일 경로
h5_model_path = "C:/Users/USER/Downloads/autonomous_car_model.h5"
saved_model_dir = "C:/Users/USER/Downloads/autonomous_car_model"

# 모델 로드 및 변환
model = tf.keras.models.load_model(h5_model_path)
model.save(saved_model_dir)
print(f"모델이 SavedModel 형식으로 변환되어 저장되었습니다: {saved_model_dir}")

