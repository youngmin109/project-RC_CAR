import tensorflow as tf

# 기존 Keras 모델 로드
model = tf.keras.models.load_model('autonomous_car_model.h5')

# TFLite 모델로 변환
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# 모델 저장
with open('autonomous_car_model.tflite', 'wb') as f:
    f.write(tflite_model)
