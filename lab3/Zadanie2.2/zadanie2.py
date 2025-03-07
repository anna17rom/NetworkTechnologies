import time
import random

class Transmitter:
    def __init__(self, name, position, color, signal_length_left=5, signal_length_right=5):
        """
        Initialize a transmitter with specific attributes:
        - name: Identifier of the transmitter
        - position: Fixed position of the transmitter on the network
        - color: Used for visualization in console output
        - signal_length_left: Maximum distance the signal can travel to the left
        - signal_length_right: Maximum distance the signal can travel to the right
        Additional attributes manage the transmission state and collision handling.
        """
        self.name = name
        self.position = position
        self.color = color
        self.signal_length_left = signal_length_left
        self.signal_length_right = signal_length_right
        # Current active length of the signal in both directions.
        self.current_length_left = 0
        self.current_length_right = 0
        # Delay before the transmitter starts, to simulate asynchronous start.
        self.start_delay = random.randint(0, 10)
        # Time to wait after a collision before trying again.
        self.backoff_time = 0
        # Counts the number of collisions to adjust backoff time.
        self.collision_count = 0
        # Whether the transmitter is currently sending a signal.
        self.transmitting = False

    def propagate(self, network):
        """
        Handle the propagation of the signal in the network.
        - If starting or waiting due to backoff, decrement the respective counters.
        - Check for collisions and update the network accordingly.
        - Expand the signal reach if no collision is detected.
        Returns True if a collision occurred during this propagation cycle.
        """
        if self.start_delay > 0:
            self.start_delay -= 1
            return False

        if self.backoff_time > 0:
            self.backoff_time -= 1
            return False

        # List to collect changes to be made to the network representation.
        updates = []
        start_left = max(self.position - self.current_length_left, 0)
        end_left = self.position
        start_right = self.position + 1
        end_right = min(self.position + self.current_length_right + 1, len(network.network))

        collision = False
        # Mark the transmitter's position on the network.
        updates.append((self.position, self.color + self.name + '\033[0m'))
        # Update the network for the left and right expansions of the signal.
        for i in range(start_left, end_left):
            if network.network[i] != '0' and network.network[i] != self.color + self.name + '\033[0m':
                updates.append((i, '\033[31mX\033[0m'))
                collision = True
            else:
                updates.append((i, self.color + self.name + '\033[0m'))

        for i in range(start_right, end_right):
            if network.network[i] != '0' and network.network[i] != self.color + self.name + '\033[0m':
                updates.append((i, '\033[31mX\033[0m'))
                collision = True
            else:
                updates.append((i, self.color + self.name + '\033[0m'))

        # Apply updates to the network array.
        for index, value in updates:
            network.network[index] = value

        if collision:
            return True

        # Expand the signal reach incrementally until it reaches its max lengths.
        if self.current_length_left < self.signal_length_left:
            self.current_length_left += 1
        if self.current_length_right < self.signal_length_right:
            self.current_length_right += 1

        self.transmitting = True
        return False

    def handle_collision(self):
        """
        Handle a collision by stopping transmission, incrementing collision count,
        calculating a new backoff time, and resetting the signal lengths.
        """
        self.transmitting = False
        self.collision_count += 1
        self.backoff_time = random.randint(1, 2 ** min(self.collision_count, 10))
        print(f"{self.color}{self.name} backoff time: {self.backoff_time}\033[0m")
        self.current_length_left = 0
        self.current_length_right = 0

    def reset(self):
        """
        Reset the transmitter to initial state after a successful transmission
        or to prepare for a new attempt after collisions are resolved.
        """
        self.current_length_left = 0
        self.current_length_right = 0
        self.start_delay = self.backoff_time
        self.transmitting = False

class Network:
    def __init__(self, length, transmitters):
        """
        Initialize the network with a specified length and a list of transmitters.
        """
        self.network = ['0'] * length
        self.transmitters = transmitters
        self.collision_occurred = False

    def display(self):
        """
        Print the current state of the network, showing transmissions and collisions.
        """
        print(''.join([x if x != '0' else '0' for x in self.network]))

    def simulate(self):
        """
        Run the simulation of the network. This involves:
        - Clearing the network at the start of each cycle.
        - Letting each transmitter attempt to propagate its signal.
        - Handling collisions and successful transmissions.
        - Displaying the network state after each update.
        - Checking conditions for resetting the network after full transmissions or unresolved collisions.
        """
        while True:
            cycles = max(max(t.signal_length_left, t.signal_length_right) for t in self.transmitters) * 2
            for _ in range(cycles):
                self.clear_network()
                collision_occurred_this_cycle = False

                for transmitter in self.transmitters:
                    if transmitter.propagate(self):
                        collision_occurred_this_cycle = True

                if all(x != '0' and x != '\033[31mX\033[0m' for x in self.network):
                    print("Message was delivered successfully!")
                    self.reset_network()
                    break

                if collision_occurred_this_cycle:
                    self.collision_occurred = True

                if self.collision_occurred:
                    self.spread_collision()
                    print("COLLISION!!!")
                    for transmitter in self.transmitters:
                        if transmitter.transmitting:
                            transmitter.handle_collision()

                self.display()
                time.sleep(0.1)

                if self.collision_occurred and all(x == '\033[31mX\033[0m' for x in self.network):
                    self.reset_network()
                    break

    def spread_collision(self):
        """
        Spread the collision state throughout the network, indicating that a collision has occurred.
        """
        for i in range(len(self.network)):
            self.network[i] = '\033[31mX\033[0m'

    def clear_network(self):
        """
        Clear the network of all signals except for areas marked with collision.
        """
        for i in range(len(self.network)):
            if self.network[i] != '\033[31mX\033[0m':
                self.network[i] = '0'

    def reset_network(self):
        """
        Completely reset the network and all transmitters after collisions are resolved or a message has been fully transmitted.
        """
        self.network = ['0'] * len(self.network)
        self.collision_occurred = False
        for transmitter in self.transmitters:
            transmitter.reset()

if __name__ == "__main__":
    transmitters = [
        Transmitter("A", 30, "\033[33m", signal_length_left=30, signal_length_right=30),  # Yellow
        Transmitter("B", 10, "\033[36m", signal_length_left=10, signal_length_right=50),  # Cyan
        Transmitter("C", 50, "\033[32m", signal_length_left=50, signal_length_right=10)   # Green
    ]
    network = Network(60, transmitters)
    network.simulate()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

