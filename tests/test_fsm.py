from app.pet.fsm import PetFSM

def test_feed_transition():
    pet = PetFSM(initial_state='hungry')
    pet.feed()
    assert pet.get_state() == 'happy'

def test_play_transition():
    pet = PetFSM(initial_state='idle')
    pet.play()
    assert pet.get_state() == 'excited'
