import pytest
from pathlib import Path
from forread.main import ManualProcessorApp

@pytest.mark.asyncio
async def test_app_startup():
    """测试 App 是否能正常启动并显示初始屏幕"""
    app = ManualProcessorApp()
    async with app.run_test() as pilot:
        # 检查初始按钮是否存在
        assert app.query_one("#open-btn") is not None
        # 检查标题
        assert "Manual Number-to-Word" in app.query_one("#welcome").content

def test_file_processing_logic(tmp_path):
    """测试处理逻辑是否能正确生成 processed_lines"""
    from forread.screens.processor import FileProcessorScreen
    
    test_lines = ["I have 9 eggs.", "In 2024 it happened."]
    screen = FileProcessorScreen(test_lines, "test.txt")
    
    # 模拟处理逻辑：手动模式下初始 processed_lines 应该等于 lines
    assert screen.lines == test_lines
    assert screen.processed_lines == test_lines