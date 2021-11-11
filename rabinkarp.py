
import unittest

def rabin_karp(text, pattern):

    m = len(text)
    n = len(pattern)
    hs = 0
    hh = 0
    
    if m == 0:
        return []
    if n == 0:
        return list(range(m - n))
    for q in range(n):
        hs = hs+id(pattern[q])
        hh = hh+id(text[q])
    result = []

    for b in range(m - n):
        t = text[b:b+n]
        if hh == hs:
            if t == pattern:
                result.append(b)
        hh += -id(text[b]) + id(text[b+n])
    t = text[b+1:b+n+1]
    if hh == hs:
        if t == pattern:
            result.append(b+1)         
    return result

class RabinKarpTest(unittest.TestCase):

    def setUp(self):
        self.text1 = 'axaxaxax'
        self.pattern1 = 'xax'
        self.text2 = 'bababab'
        self.pattern2 = 'bab'

    def test_return_type(self):
        """Проверка того, что функция возвращает список"""
        self.assertIsInstance(
            rabin_karp(self.text1, "x"), list,
            msg="Функция должна возвращать список"
        )

    def test_returns_empty(self):
        """Проверка того, что функция, когда следует, возвращает пустой список"""
        self.assertEqual(
            [], rabin_karp(self.text1, "z"),
            msg="Функция должна возвращать пустой список, если нет вхождений"
        )
        self.assertEqual(
            [], rabin_karp("", self.pattern1),
            msg="Функция должна возвращать пустой список, если текст пустой"
        )
        self.assertEqual(
            [], rabin_karp("", ""),
            msg="Функция должна возвращать пустой список, если текст пустой, даже если образец пустой"
        )

    def test_finds(self):
        """Проверка того, что функция ищет все вхождения непустых образцов"""
        self.assertEqual(
            [1, 3, 5], rabin_karp(self.text1, self.pattern1),
            msg="Функция должна искать все вхождения"
        )
        self.assertEqual(
            [0, 2, 4], rabin_karp(self.text2, self.pattern2),
            msg="Функция должна искать все вхождения"
        )

    def test_finds_all_empties(self):
        """Проверка того, что функция ищет все вхождения пустого образца"""
        self.assertEqual(
            list(range(len(self.text1))), rabin_karp(self.text1, ""),
            msg="Пустая строка должна находиться везде"
        )

if __name__ == '__main__':
    unittest.main()
