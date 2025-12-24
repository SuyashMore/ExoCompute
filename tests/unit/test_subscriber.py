import unittest
from unittest.mock import MagicMock, patch
from exocompute.subscriber.core import SubscriberNode
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput

# Mock ComputeUnit for testing
class MockInput(ComputeInput):
    val: int

class MockOutput(ComputeOutput):
    res: int

class MockUnit(ComputeUnit):
    Input = MockInput
    Output = MockOutput
    def compute(self, input_obj):
        return MockOutput(res=input_obj.val * 2)

class TestSubscriberNode(unittest.TestCase):
    @patch('exocompute.subscriber.core.requests')
    def test_register(self, mock_requests):
        node = SubscriberNode()
        
        # Success case
        mock_requests.get.return_value.json.return_value = {"port": 9000}
        port = node.register()
        self.assertEqual(port, 9000)
        self.assertEqual(node.assigned_port, 9000)

        # Failure case
        mock_requests.get.side_effect = Exception("Fail")
        port = node.register()
        self.assertIsNone(port)

    def test_compute_logic(self):
        node = SubscriberNode()
        
        # We need to mock import_module to return our MockUnit
        with patch('exocompute.subscriber.core.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.MockUnit = MockUnit
            mock_import.return_value = mock_module
            
            # Since the code does getattr(module, unit_type), we need to ensure unit_type matches
            result = node.process_compute("MockUnit", {"val": 5})
            self.assertEqual(result["res"], 10)

    def test_compute_invalid_input(self):
         node = SubscriberNode()
         with patch('exocompute.subscriber.core.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.MockUnit = MockUnit
            mock_import.return_value = mock_module

            with self.assertRaises(ValueError):
                node.process_compute("MockUnit", {"wrong": 5})
