import unittest

from parse_price import detect_availability, parse_price


class ParsePriceTests(unittest.TestCase):
    def test_persian_digits_and_thousands_separator(self):
        result = parse_price("۹۶٬۵۰۰٬۰۰۰ تومان")
        self.assertEqual(result["amount"], 96500000)
        self.assertEqual(result["currency"], "toman")
        self.assertEqual(result["price_toman"], 96500000)
        self.assertEqual(result["price_status"], "ok")

    def test_arabic_indic_digits(self):
        result = parse_price("٩٦٬٥٠٠٬٠٠٠ تومان")
        self.assertEqual(result["price_toman"], 96500000)

    def test_explicit_rials_are_converted(self):
        result = parse_price("۱٬۲۰۰٬۰۰۰ ریال")
        self.assertEqual(result["currency"], "rial")
        self.assertEqual(result["price_toman"], 120000)

    def test_unitless_amount_is_not_guessed(self):
        result = parse_price("۹۶٬۵۰۰٬۰۰۰")
        self.assertEqual(result["price_toman"], None)
        self.assertEqual(result["price_status"], "unit_unknown")

    def test_explicit_context_can_assume_toman(self):
        result = parse_price("۹۶٬۵۰۰٬۰۰۰", assume_toman=True)
        self.assertEqual(result["price_toman"], 96500000)

    def test_million_multiplier(self):
        result = parse_price("۹۶٫۵ میلیون تومان")
        self.assertEqual(result["price_toman"], 96500000)

    def test_dotted_thousands(self):
        result = parse_price("96.500.000 تومان")
        self.assertEqual(result["price_toman"], 96500000)

    def test_missing_price(self):
        result = parse_price("تماس بگیرید")
        self.assertIsNone(result["price_toman"])
        self.assertEqual(result["price_status"], "missing")

    def test_out_of_stock_wins_over_purchase_text(self):
        self.assertEqual(
            detect_availability("افزودن به سبد — فعلاً موجود نیست"),
            "out_of_stock",
        )

    def test_positive_stock_signal(self):
        self.assertEqual(detect_availability("موجود است"), "in_stock")

    def test_unknown_stock_is_not_inferred(self):
        self.assertEqual(detect_availability("قیمت: ۵۰۰٬۰۰۰ تومان"), "unknown")


if __name__ == "__main__":
    unittest.main()
