from hardware_controls.relay_protocol import RelayProtocol

class MockRelay(RelayProtocol):
    
    @property
    def is_active(self) -> bool:
        return True
        
    def turn_on(self) -> None:
        """Energizes the relay."""
        
    def turn_off(self) -> None:
        """Turns off the relay."""

    def cleanup(self) -> None:
        """Performs cleanup logic on the relay pins."""