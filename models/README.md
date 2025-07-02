# 模型存储目录

此目录用于存储训练好的深度学习模型。

目录结构:
- 城市名/
  - 区域名/
    - dnn_model.pkl
    - lstm_model.pkl
    - prophet_model.pkl

模型会在首次预测时自动创建，并定期更新。
