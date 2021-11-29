from unittest import TestCase


class Test_import(TestCase):
               
    def test_import(self):
        b = True
        try:
            from partsgenie_client import PartsGenieClient
            client = PartsGenieClient('https://partsgenie.micalis.inrae.fr')
        except Exception as e:
            b = False
            print(e)
        self.assertTrue(b)