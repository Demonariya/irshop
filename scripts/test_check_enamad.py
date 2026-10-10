import unittest

from check_enamad import (
    BadgeLinkParser,
    exact_domain_appears,
    is_official_enamad_url,
    normalized_host,
)


class EnamadHelperTests(unittest.TestCase):
    def test_accepts_official_verification_url(self):
        self.assertTrue(is_official_enamad_url("https://trustseal.enamad.ir/?id=12&Code=abc"))
        self.assertTrue(is_official_enamad_url("https://enamad.ir/DomainList.aspx"))

    def test_rejects_lookalike_hosts(self):
        self.assertFalse(is_official_enamad_url("https://trustseal.enamad.ir.example.com/"))
        self.assertFalse(is_official_enamad_url("https://fakeenamad.ir/"))

    def test_extracts_only_official_badge_links(self):
        html = """
        <a href="https://trustseal.enamad.ir/?id=12&Code=abc"><img alt="Enamad"></a>
        <a href="https://example.org/badge"><img alt="Other"></a>
        """
        parser = BadgeLinkParser("https://shop.example/")
        parser.feed(html)
        self.assertEqual(parser.links, ["https://trustseal.enamad.ir/?id=12&Code=abc"])

    def test_domain_normalization(self):
        self.assertEqual(normalized_host("https://www.Technolife.com/"), "technolife.com")
        self.assertEqual(normalized_host("shop.example.ir"), "shop.example.ir")

    def test_exact_domain_matching(self):
        self.assertTrue(exact_domain_appears("ثبت دامنه technolife.com", "www.technolife.com"))
        self.assertFalse(exact_domain_appears("مالک سایت fake-technolife.com", "technolife.com"))


if __name__ == "__main__":
    unittest.main()
