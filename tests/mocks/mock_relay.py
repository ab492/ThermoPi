from utils.relay_protocol import RelayProtocol

class MockRelay(RelayProtocol):
    
    ### Is Active
    value_to_return_for_is_active = False
    
    @property
    def is_active(self) -> bool:
        return self.value_to_return_for_is_active
        
    ### Turn On

    turn_on_call_count = 0
    
    def turn_on(self) -> None:
        self.turn_on_call_count += 1
        
    ### Turn Off

    turn_off_call_count = 0

    def turn_off(self) -> None:
        self.turn_off_call_count += 1
        
    ### Cleanup
    
    cleanup_call_count = 0

    def cleanup(self) -> None:
        self.cleanup_call_count += 1