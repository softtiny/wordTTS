import pytest
from forread.tracker import SpanRecord

def test_span_record():
    text = "订单号12345共有3件商品，总价299.9元，预计2024-06-15送达。"
    rec = SpanRecord(text)
    rec.extract_numbers()
    rec.display()
    print(rec.highlight())
    span = rec.spans[0]
    print(f"修改前: {span}")
    rec.update_span(0, new_end=span.end + 1)
    print(f"修改后: {span}")

    rec2 = SpanRecord(text)
    rec2.add(start=10, end=11, label="3")   # 手动添加 "订单号"
    rec2.display()
    
    rec3 = SpanRecord(text)
    rec3.extract_numbers()
    hits = rec3.at_position(5)
    print(f"位置 5 处的区间: {hits}")