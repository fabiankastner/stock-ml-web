from django.test import TestCase

# Create your tests here.
class VisualizerTestCase(TestCase):
    def setUp(self):
        pass
    
    def test_test(self):
        test = "test"
        self.assertEqual(test, "test")