import unittest

from experimentor.models import BaseModel
from experimentor.models.action import Action


class TestAction(unittest.TestCase):
    def setUp(self) -> None:
        class ModelAction(BaseModel):
            @Action
            def simple_action(self):
                pass

            @Action()
            def another_simple_action(self):
                pass

        self.test_model = ModelAction

    def test_action_list(self):
        self.tm = self.test_model()
        self.assertEqual(len(self.tm.get_actions()), 2)
        self.assertIn('simple_action', self.tm.get_actions())
        self.assertIn('another_simple_action', self.tm.get_actions())
