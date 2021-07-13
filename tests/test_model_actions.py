import unittest
from concurrent.futures._base import Future
from threading import Lock

from experimentor.models import BaseModel
from experimentor.models.action import Action


class TestAction(unittest.TestCase):
    def setUp(self) -> None:
        class ModelAction(BaseModel):
            new_lock = Lock()
            @Action
            def simple_action(self):
                pass

            @Action()
            def another_simple_action(self):
                pass

            @Action(lock=new_lock)
            def locked_action(self):
                pass

        self.test_model = ModelAction

    def test_action_list(self):
        tm = self.test_model()
        self.assertEqual(len(tm.get_actions()), 3)
        self.assertIn('simple_action', tm.get_actions())
        self.assertIn('another_simple_action', tm.get_actions())

    def test_action_run(self):
        tm = self.test_model()
        future = tm.simple_action()
        self.assertTrue(isinstance(future, Future))

    def test_lock_action(self):
        tm = self.test_model()
        self.assertEqual(tm.new_lock, tm.locked_action.get_lock())
