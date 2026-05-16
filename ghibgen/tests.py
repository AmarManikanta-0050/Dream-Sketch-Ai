# ghibgen/tests.py
from django.test import TestCase
from django.urls import reverse

class Smoke(TestCase):
    def test_home_renders(self):
        resp = self.client.get(reverse("ghibgen:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Create Image")
