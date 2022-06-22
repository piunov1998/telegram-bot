from transitions import Machine
import random


class Bot:

    def __init__(self) -> None:
        self.number = 0
        self.states = ['idle', 'guess']

        self.machine = Machine(model=self, states=self.states, initial='idle')

        self.machine.add_transition(trigger='start', source='idle',
                                    dest='guess')

        self.machine.add_transition(trigger='idle', source='*', dest='idle')

    def chat(self, msg: str) -> str:

        choice = msg.lower().lstrip().removesuffix('.')
        match self.state:
            case 'idle':
                if choice == '/start':
                    self.start()
                    self.number = random.randint(1, 4) + random.random()
                    return 'Я загадал число от 1 до 5, попробуете угадать?'
                else:
                    return 'Отправьте /start для начала'

            case 'guess':
                self.idle()
                if choice.isdigit() and \
                   int(choice) == self.number:
                    return 'Молодец!'
                else:
                    return f'Неправильно, я загадал {self.number}'

    def get_answers(self) -> list:
        """
        Возвращает список вариантов ответа в зависимости от состояния
        """
        match self.state:
            case 'idle':
                return []
            case _:
                return []
