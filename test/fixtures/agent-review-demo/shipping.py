FREE_SHIPPING_MINIMUM_CENTS = 5_000


def qualifies_for_free_shipping(subtotal_cents: int) -> bool:
    return subtotal_cents >= FREE_SHIPPING_MINIMUM_CENTS
