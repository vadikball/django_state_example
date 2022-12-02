from abc import abstractmethod

from django.db import transaction

from app.models import Lead, LeadState


class AbcState:
    """
    Абстрактный класс для переопределения обязательных методов
    """

    @abstractmethod
    def forward(self, *args, **kwargs):
        """
        Двигает к следующему состоянию.
        В порядке NEW->IN_PROGRESS->DONE
        или POSTPONED->DONE
        """
        pass

    @abstractmethod
    def switch(self, *args, **kwargs):
        """ Переключает состояние между IN_PROGRESS и POSTPONED """
        pass


class StateDone(AbcState):
    def forward(self, *args, **kwargs):
        raise AttributeError(
            f'{self.__class__.__name__} has not attribute "forward"'
        )

    def switch(self, *args, **kwargs):
        raise AttributeError(
            f'{self.__class__.__name__} has not attribute "switch"'
        )

    def generate_transit(self, lead: Lead, next_state: int):
        """
        Возвращает строку, которая отображает,
        с какого на какой State перешел Lead.
        Метод только для теста.
        """

        return '{0}->{1}'.format(str(lead.state.id), str(next_state))


class StateNew(StateDone):
    def forward(self, lead: Lead):
        # pseudocode to do something with lead
        lead.transit = self.generate_transit(lead, 2)
        lead.save()


class StateProgress(StateDone):
    def forward(self, lead: Lead):
        # pseudocode to do something with lead
        lead.transit = self.generate_transit(lead, 4)
        lead.save()

    def switch(self, lead: Lead):
        # pseudocode to do something with lead
        lead.transit = self.generate_transit(lead, 3)
        lead.save()


class StatePostponed(StateDone):
    def forward(self, lead: Lead):
        # pseudocode to do something with lead
        lead.transit = self.generate_transit(lead, 4)
        lead.save()

    def switch(self, lead: Lead):
        # pseudocode to do something with lead
        lead.transit = self.generate_transit(lead, 2)
        lead.save()


class StateManager:
    """ Класс для управления состояниями """

    states = {
        1: StateNew,
        2: StateProgress,
        3: StatePostponed,
        4: StateDone
    }

    def __init__(self, lead: Lead):
        self.lead = lead
        self._state_id = self.lead.state.id

    @property
    def state(self):
        """
        Возвращает необходимый класс State для текущего Lead
        """
        return self.states[self._state_id]

    @property
    def state_id(self):
        return self._state_id

    @state_id.setter
    def state_id(self, value: int):
        """
        обновляет LeadState для self.lead в соответствии с новым значением
        """

        if not 0 < value < 5:
            raise ValueError('State must be greater than 0 and less than 5')

        self._state_id = value
        self.lead.state = LeadState.objects.get(id=value)
        self.lead.save()

    def stepper(self):
        """ Двигает состояние вперед """

        if self.state_id != 4:
            if self.state_id % 2 == 0:
                self.state_id += 2
            else:
                self.state_id += 1

    def switcher(self):
        """ Переключает состояние между IN_PROGRESS(2) и POSTPONED(3) """
        if self.state_id in (2, 3, ):
            if self.state_id == 2:
                self.state_id += 1
            else:
                self.state_id -= 1

    @transaction.atomic
    def forward(self):
        """
        Двигает состояние вперед и
        выполняет бизнес логику внутри класса состояния
        """

        self.state().forward(self.lead)
        self.stepper()

    @transaction.atomic
    def switch(self):
        """
        Переключает состояние между IN_PROGRESS(2) и POSTPONED(3) и
        выполняет бизнес логику внутри класса состояния
        """

        self.state().switch(self.lead)
        self.switcher()
