from enum import Enum, auto

class BotState(Enum):
    """Bot states"""
    IDLE = auto()
    AWAITING_PATTERN = auto()
    AWAITING_CONFIRMATION = auto()
    IN_SETTINGS = auto()

class StateManager:
    def __init__(self):
        self.states = {}  # user_id -> BotState
    
    def get_state(self, user_id: int) -> BotState:
        """Get state for user"""
        return self.states.get(user_id, BotState.IDLE)
    
    def set_state(self, user_id: int, state: BotState):
        """Set state for user"""
        self.states[user_id] = state
    
    def clear_state(self, user_id: int):
        """Clear state for user"""
        if user_id in self.states:
            del self.states[user_id]