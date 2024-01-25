import unittest
import com2fun


class BasicTestCase(unittest.TestCase):
    def test1(self):
        @com2fun.com2fun
        def top(category: str, n) -> list[str]:
            """top n items"""

        top.add_example("continents", 3)(["Asia", "Africa", "North America"])
        r = top("fish", 5)
        self.assertTrue(isinstance(r, list))
