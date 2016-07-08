import nose_parameterized

from bomber import dots
from bomber import exceptions
from bomber import tests


class DotTestCase(tests.BaseTestCase):
    def test_is_hidden_created_dot(self):
        dot = dots.Dot()
        self.assertTrue(dot.is_hidden)

    def test_open_hidden_dot(self):
        dot = dots.Dot()
        dot.open()
        self.assertFalse(dot.is_hidden)

    def test_is_singed_as_mine_created_dot(self):
        dot = dots.Dot()
        self.assertFalse(dot.is_mine_signed)

    def test_sign_as_mine(self):
        dot = dots.Dot()
        dot.sign_mine()
        self.assertTrue(dot.is_mine_signed)

    def test_sign_as_not_mine(self):
        dot = dots.Dot()
        dot.sign_mine()
        dot.sign_mine(False)
        self.assertFalse(dot.is_mine_signed)

    @nose_parameterized.parameterized.expand([
        ("bomb_square", dots.MineDot),
        ("empty_square", dots.EmptyDot),
        ("number_square", dots.NumberDot),
    ])
    def test_create_dot(self, _, dot_class):
        dot = dot_class()
        self.assertIsInstance(dot, dots.Dot)

    def test_number_dot_get_number(self):
        number = 1
        number_dot = dots.NumberDot(number)
        self.assertEqual(number, number_dot.number)

    def test_number_dot_set_number(self):
        number = 1
        number_dot = dots.NumberDot()
        number_dot.set_number(number)
        self.assertEqual(number, number_dot.number)

    @nose_parameterized.parameterized.expand([
        ("less", 0),
        ("upper", 9),
    ])
    def test_number_dot_set_number_raises_if_invalid_number(self, _, number):
        number_dot = dots.NumberDot()
        self.assertRaises(exceptions.InvalidNumberForNumberDot,
                          number_dot.set_number, number)
