NUMBER_TO_WROD = {
        "1":"one",
        "2":"two",
        "3":"three",
        "4":"four",
        "5":"five",
        "6":"six",
        "7":"seven",
        "8":"eight",
        "9":"nine",
        "0":"zero",
        ".":"point",
        }

def one_number_one_word(number):
    res = [NUMBER_TO_WROD[code] for code in number]
    return " ".join(res)


if __name__ == "__main__":
    import unittest
    class BaseTestCase(unittest.TestCase):
        def test_one_number_one_word(self):
            for val,res in (
                    ("1","one"),
                    ("12","one two"),
                    ("32","three two"),
                    ):
                self.assertEqual(res,one_number_one_word(val))
    unittest.main()
