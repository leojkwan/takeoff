import unittest

from shipping import qualifies_for_free_shipping


class ShippingTests(unittest.TestCase):
    def test_fifty_dollar_order_ships_free(self) -> None:
        self.assertTrue(qualifies_for_free_shipping(5_000))
