# src/interfaces/i_mediator_handler.py

class IMediatorHandler():
    def load_mediator(self):
        """Load and initialize a mediator."""
        pass

    def update_mediator(self, update_info):
        """Update the mediator's logic or state based on given information."""
        pass

    def process_input(self, input_data):
        """Process input through the mediator and return the output."""
        pass

    def generate_output(self):
        """Generate output based on the mediator's current state and input history."""
        pass
