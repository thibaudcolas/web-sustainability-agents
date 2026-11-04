import unittest

from audit.disclosures import interpret, summarize


class DisclosureReviewTests(unittest.TestCase):
    def test_domain_validity_and_certificate_links_do_not_become_verification(self):
        result = interpret(
            {
                "version": "0.6",
                "org": {
                    "certification_schemes": [
                        {"id": "scheme", "url": "https://cert.test"}
                    ],
                    "disclosures": [
                        {
                            "url": "https://site.test/old-report",
                            "doc_type": "annual-report",
                            "domain": "site.test",
                            "valid_until": "2024-12-31",
                            "certification_schemes": ["scheme", "missing"],
                        },
                        {
                            "url": "https://parent.test/policy",
                            "doc_type": "sustainability-page",
                            "domain": "parent.test",
                        },
                    ],
                },
                "upstream": {
                    "services": [
                        {"domain": "provider.test", "service_type": ["hosting", "cdn"]}
                    ]
                },
            },
            "https://site.test",
            "2026-11-04T10:00:00Z",
        )
        first, second = result["disclosures"]
        self.assertEqual(first["domainScope"], "exact_host_match")
        self.assertEqual(first["validityAtCapture"], "past_declared_validity")
        self.assertEqual(first["unresolvedCertificationReferences"], ["missing"])
        self.assertEqual(second["domainScope"], "different_or_invalid_declared_host")
        self.assertFalse(first["claimsVerified"])
        self.assertFalse(result["providers"][0]["greenHostingVerified"])
        self.assertFalse(result["schemaValidated"])

    def test_malformed_and_future_schema_stay_inspectable(self):
        result = interpret(
            {
                "version": "99",
                "org": {
                    "disclosures": [
                        None,
                        {"url": "https://[bad", "valid_until": "oops"},
                    ],
                    "certification_schemes": "wrong",
                },
                "upstream": {"services": "wrong"},
            },
            "https://site.test",
            "2026-11-04T10:00:00Z",
        )
        self.assertEqual(result["declaredVersion"], "99")
        self.assertGreater(len(result["structuralIssues"]), 2)
        self.assertFalse(result["disclosures"][0]["usableUrl"])
        self.assertEqual(
            result["disclosures"][0]["validityAtCapture"], "unrecognized_date"
        )

    def test_presence_without_links_and_failed_retrieval_remain_distinct(self):
        result = summarize(
            {
                "site": "https://site.test",
                "carbonAttempts": [
                    {
                        "declarations": {
                            "version": "0.6",
                            "org": {
                                "disclosures": [
                                    {
                                        "url": "https://site.test/report",
                                        "doc_type": "annual-report",
                                    }
                                ]
                            },
                        }
                    }
                ],
                "documents": [{"url": "https://site.test/report", "status": 404}],
            }
        )
        self.assertEqual(result["presence"], "present")
        self.assertEqual(
            result["records"][0]["review"]["disclosures"][0]["retrievalEvidence"][0][
                "status"
            ],
            404,
        )
        empty = summarize(
            {
                "site": "https://site.test",
                "carbonAttempts": [{"declarations": {"version": "0.6"}}],
            }
        )
        self.assertEqual(empty["presence"], "present")
        self.assertTrue(empty["records"][0]["review"]["structuralIssues"])
