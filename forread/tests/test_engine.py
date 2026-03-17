import pytest
from forread.engine import number_to_words, convert_ordinal_to_word

def test_basic_ordinal():
    assert convert_ordinal_to_word(1) == "first"
    assert convert_ordinal_to_word(2) == "second"
    assert convert_ordinal_to_word(3) == "third"
    assert convert_ordinal_to_word(10) == "tenth"
    assert convert_ordinal_to_word(11) == "eleventh"
    assert convert_ordinal_to_word(20) == "twentieth"
    assert convert_ordinal_to_word(21) == "twenty first"

def test_large_ordinal():
    assert convert_ordinal_to_word(100) == "one hundredth"
    assert convert_ordinal_to_word(1000) == "one thousandth"
    assert convert_ordinal_to_word(10000) == "ten thousandth"

def test_basic_numbers():
    assert number_to_words(0) == "zero"
    assert number_to_words(5) == "five"
    assert number_to_words(13) == "thirteen"
    assert number_to_words(21) == "twenty one"
    assert number_to_words(100) == "one hundred"
    assert number_to_words(203) == "two hundred three"

def test_large_numbers():
    assert number_to_words(100) == "one hundred"
    assert number_to_words(1005) == "one thousand five"
    assert number_to_words(1234567) == "one million two hundred thirty four thousand five hundred sixty seven"

def test_negative_numbers():
    assert number_to_words(-10) == "minus ten"
    assert number_to_words(-256) == "minus two hundred fifty six"

def test_edge_cases():
    # 测试 TENS 的边界
    assert number_to_words(20) == "twenty"
    assert number_to_words(90) == "ninety"