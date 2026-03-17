forread/
├── .cache/              # 存放生成的转换文件和日志
├── tests/               # 测试代码目录
│   ├── __init__.py
│   ├── test_engine.py   # 核心算法测试
│   └── test_app.py      # UI 逻辑测试
├── screens/
│   ├── __init__.py
│   ├── processor.py     # 核心处理屏幕
│   └── selector.py      # 文件选择屏幕
├── __init__.py
├── main.py              # 应用入口
├── engine.py            # 数字转单词逻辑
├── models.py            # 自定义消息类
└── constants.py         # 转换常量