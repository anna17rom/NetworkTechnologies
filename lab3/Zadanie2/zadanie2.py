import threading
import time
import random


def simulate_csma_cd():
    class Transmitter:
        def __init__(self, name, position, color, propagation_ranges):
            self.name = name
            self.position = position
            self.color = color
            self.collision_count = 0
            self.propagation_ranges = propagation_ranges
            self.active = True
            self.backoff_time = 0
            self.is_transmitting = False  # Track if currently transmitting
            self.jam_signal = False  # Jam signal flag
            self.jam_sig_name = "X"
            self.jam_sig_color = "\033[31m"

        def transmit(self, network):
            while self.active:
                self.is_transmitting = False
                time.sleep(random.randint(1, 5))  # Wait before trying to transmit
                if self.sense_medium(network) and not self.jam_signal:
                    self.is_transmitting = True
                    with line_lock:
                        if self.attempt_to_propagate_signal(network):
                            print(f"{self.color}{self.name} has successfully sent a message")
                            self.clear_signal(network)
                        else:
                            self.handle_collision(network)
                else:
                    self.handle_collision(network)

        def sense_medium(self, network):
            return all(x == '0' for x in network.network)

        def attempt_to_propagate_signal(self, network):
            if self.sense_medium(network):
                for step in range(1, max(abs(self.position - limit) for _, limit in self.propagation_ranges) + 1):
                    for direction, limit in self.propagation_ranges:
                        next_position = self.position + step * direction
                        if 0 <= next_position < len(network.network):
                            if network.network[next_position] != '0':
                                network.network[next_position] = self.jam_sig_color + self.jam_sig_name
                                self.handle_collision_at_position(network, next_position, step, direction)
                                return False
                            else:
                                network.network[next_position] = self.color + self.name
                                self.display_network(network)
                                time.sleep(0.01)
                return True
            else:
                return False

        def handle_collision_at_position(self, network, position, step, direction):
            with line_lock:
                # Broadcast jam signal to the network
                self.jam_signal = True
                self.is_transmitting = False  # Stop transmitting
                self.send_jam_signal(network)
                self.handle_collision(network)
                self.jam_signal = False

        def send_jam_signal(self, network):
            for t in network.transmitters:
                t.jam_signal = True

        def handle_collision(self, network):
            with line_lock:
                network.do_backoff()
                time.sleep(self.backoff_time)
                self.is_transmitting = False

        def clear_signal(self, network):
            for i in range(len(network.network)):
                if network.network[i] == self.color + self.name or self.jam_sig_color + self.jam_sig_name in \
                        network.network[i]:
                    network.network[i] = '0'
            self.display_network(network)
            self.is_transmitting = False

        def display_network(self, network):
            print('\r' + ''.join([x if x != '0' else '-' for x in network.network]).replace('\033[0m', '') + '\033[0m',
                  end='', flush=True)

    class Network:
        def __init__(self, size, transmitters):
            self.network = ['0'] * size
            self.transmitters = transmitters
            self.collision_counter = 0  # Global collision counter

        def simulate(self):
            threads = []
            for transmitter in self.transmitters:
                thread = threading.Thread(target=transmitter.transmit, args=(self,))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

        def do_backoff(self):
            self.collision_counter += 1
            print(f"Global collision count: {self.collision_counter}")
            for transmitter in self.transmitters:
                if not transmitter.is_transmitting:
                    transmitter.collision_count += 1
                    transmitter.backoff_time = random.randint(0, 2 ** min(transmitter.collision_count, 10) - 1) * 0.1
                    print(f"{transmitter.name} backing off for {transmitter.backoff_time}s")

    line_lock = threading.Lock()
    transmitters = [
        Transmitter("A", 8, "\033[33m", [(-1, 0), (1, 59)]),
        Transmitter("B", 20, "\033[36m", [(-1, 0), (1, 59)]),
        Transmitter("C", 30, "\033[32m", [(-1, 0), (1, 59)])
    ]
    network = Network(60, transmitters)
    network.simulate()


if __name__ == "__main__":
    simulate_csma_cd()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

