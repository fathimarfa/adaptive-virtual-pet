from transitions import Machine

STATES = ['idle', 'happy', 'sad', 'hungry', 'sleepy', 'excited']

TRANSITIONS = [
    {'trigger': 'feed',       'source': 'hungry',  'dest': 'happy'},
    {'trigger': 'play',       'source': 'idle',     'dest': 'excited'},
    {'trigger': 'play',       'source': 'happy',    'dest': 'excited'},
    {'trigger': 'play',       'source': 'sad',      'dest': 'happy'},
    {'trigger': 'rest',       'source': 'sleepy',   'dest': 'idle'},
    {'trigger': 'get_hungry', 'source': '*',        'dest': 'hungry'},
    {'trigger': 'get_sleepy', 'source': '*',        'dest': 'sleepy'},
    {'trigger': 'feel_sad',   'source': '*',        'dest': 'sad'},
    {'trigger': 'calm_down',  'source': 'sad',      'dest': 'idle'},
    {'trigger': 'calm_down',  'source': 'excited',  'dest': 'happy'},
]

class PetFSM:
    def __init__(self, initial_state='idle'):
        self.machine = Machine(
            model=self,
            states=STATES,
            transitions=TRANSITIONS,
            initial=initial_state,
            ignore_invalid_triggers=True
        )

    def get_state(self):
        return self.state
