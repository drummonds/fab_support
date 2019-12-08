import os
import unittest

from selenium import webdriver
from selenium.common.exceptions import WebDriverException


class TestSeleniumVersion(unittest.TestCase):
    """
    Just make sure selenium runs ok
    """

    def test_geckodriver_on_path(self):
        # Find geckodriver.exe
        found = False
        path = ""
        for p in os.environ["PATH"].split(";"):
            for r, d, f in os.walk(p):
                for files in f:
                    if files == "geckodriver.exe":
                        found = True
                        path = f"{os.path.join(r, files)}"
        self.assertTrue(found, "Didn't find geckodriver.exe on path")

    def test_selenium_get(self):
        try:
            self.browser = webdriver.Firefox()
            self.browser.get("https://bbc.co.uk/")
            self.assertIn(
                "BBC", self.browser.title, "Should be looking at the Django home page"
            )
        except WebDriverException:
            self.assertTrue(False, "You may need to install or updated geckodriver")
        finally:
            try:
                self.browser.close()
            except AttributeError:  # Problem created browser
                pass
