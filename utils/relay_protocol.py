from typing import Protocol

class RelayProtocol(Protocol):
    
    @property
    def is_active(self) -> bool:
        """Determines if the relay is currently active."""
        
    def turn_on(self) -> None:
        """Energizes the relay."""
        
    def turn_off(self) -> None:
        """Turns off the relay."""

    def cleanup(self) -> None:
        """Performs cleanup logic on the relay pins."""