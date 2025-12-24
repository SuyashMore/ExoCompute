import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from exocompute.orchestrator.manager import NodeManager
from exocompute.orchestrator.scheduler import TaskScheduler

class TestNodeManager(unittest.TestCase):
    def test_get_available_port(self):
        manager = NodeManager(9000, 9002)
        port1 = manager.get_available_port()
        self.assertEqual(port1, 9000)
        port2 = manager.get_available_port()
        self.assertEqual(port2, 9001)
        port3 = manager.get_available_port()
        self.assertIsNone(port3)

    def test_unregister(self):
        manager = NodeManager(9000, 9001)
        manager.get_available_port()
        self.assertIn(9000, manager.subscribers)
        manager.unregister_node(9000)
        self.assertNotIn(9000, manager.subscribers)

class TestTaskScheduler(unittest.IsolatedAsyncioTestCase):
    async def test_submit_task_no_nodes(self):
        manager = MagicMock()
        manager.get_nodes.return_value = {}
        scheduler = TaskScheduler(manager)
        scheduler.retry_limit = 1
        scheduler.retry_delay = 0.01

        with self.assertRaises(Exception) as cm:
            await scheduler.submit_task({})
        self.assertIn("No available subscribers", str(cm.exception))

    async def test_submit_task_success(self):
        manager = MagicMock()
        manager.get_nodes.return_value = {9000: False}
        scheduler = TaskScheduler(manager)
        scheduler.retry_limit = 1
        
        # Mock _send_to_port
        scheduler._send_to_port = AsyncMock(return_value=(9000, {"result": 42}))

        result = await scheduler.submit_task({"foo": "bar"})
        self.assertEqual(result["result"], 42)
        manager.mark_busy.assert_called_with(9000)
