from django.test import TestCase

from app.models import Lead, LeadState
from app.utils import StateManager


class TestStateManagement(TestCase):

    def setUp(self):
        for name in ('NEW', 'IN_PROGRESS', 'POSTPONED', 'DONE', ):
            LeadState.objects.create(name=name)

        Lead.objects.create(name="First lead", state_id=1)

    def do_forward(self,
                   transit: str,
                   state_manager: StateManager,
                   first_lead: Lead):
        state_manager.forward()
        self.assertEqual(first_lead.transit, transit)
        self.assertEqual(state_manager.state_id, first_lead.state.id)

    def do_switch(self,
                  transit: str,
                  state_manager: StateManager,
                  first_lead: Lead):
        state_manager.switch()
        self.assertEqual(first_lead.transit, transit)
        self.assertEqual(state_manager.state_id, first_lead.state.id)

    def test_one_state(self):
        first_lead = Lead.objects.get(name="First lead")
        state_manager = StateManager(first_lead)
        state_manager.state_id = 1

        with self.assertRaises(AttributeError):
            state_manager.switch()

        self.do_forward('1->2', state_manager, first_lead)

        self.do_switch('2->3', state_manager, first_lead)

        self.do_switch('3->2', state_manager, first_lead)

        self.do_forward('2->4', state_manager, first_lead)

        state_manager.state_id = 3

        self.do_forward('3->4', state_manager, first_lead)

        with self.assertRaises(AttributeError):
            state_manager.switch()

        with self.assertRaises(AttributeError):
            state_manager.forward()

    def test_state_multi(self):
        first_lead = Lead.objects.get(name="First lead")
        state_manager = StateManager(first_lead)
        state_manager.state_id = 1

        with self.assertRaises(AttributeError):
            StateManager(first_lead).switch()

        self.do_forward('1->2', StateManager(first_lead), first_lead)

        self.do_switch('2->3', StateManager(first_lead), first_lead)

        self.do_switch('3->2', StateManager(first_lead), first_lead)

        self.do_forward('2->4', StateManager(first_lead), first_lead)

        state_manager.state_id = 3

        self.do_forward('3->4', StateManager(first_lead), first_lead)

        with self.assertRaises(AttributeError):
            StateManager(first_lead).switch()

        with self.assertRaises(AttributeError):
            StateManager(first_lead).forward()
