@echo off
echo 正在安装深度学习依赖...
.\.venv\Scripts\pip install tensorflow>=2.6.0 prophet>=1.1.1 scikit-learn>=1.0.0 joblib>=1.1.0
echo 安装完成！
pause
