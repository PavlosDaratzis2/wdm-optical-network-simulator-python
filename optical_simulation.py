import random
import matplotlib.pyplot as plt

# -------------------- CLASS: PACKET --------------------
class Packet:
    def __init__(self, packet_id, arrival_time):
        self.id = packet_id
        self.arrival_time = arrival_time  # Time the packet was created


# -------------------- CLASS: STATION --------------------
class Station:
    def __init__(self, station_id, wavelength):
        self.id = station_id
        self.wavelength = wavelength       # λ1 to λ4
        self.queue = []                    # Packet buffer (FIFO queue)
        self.buffer_size = 5               # Max number of packets in queue
        self.total_packets_created = 0
        self.total_packets_lost = 0
        self.total_packets_sent = 0
        self.total_delay = 0

    # Attempts to generate a new packet based on arrival probability `p`
    def generate_packet(self, current_time, p, packet_counter):
        if random.random() < p:
            if len(self.queue) < self.buffer_size:
                packet = Packet(packet_counter, current_time)
                self.queue.append(packet)
                self.total_packets_created += 1
                return packet_counter + 1
            else:
                # Packet is lost because the buffer is full
                self.total_packets_lost += 1
                self.total_packets_created += 1
        return packet_counter

    # Checks if the station wants to transmit a packet this slot (with 50% probability)
    def wants_to_transmit(self):
        return len(self.queue) > 0 and random.random() < 0.5

    # Transmit (successfully) the first packet in the queue
    def successful_transmission(self, current_time):
        if self.queue:
            packet = self.queue.pop(0)
            delay = current_time - packet.arrival_time
            self.total_packets_sent += 1
            self.total_delay += delay


# -------------------- CLASS: OPTICAL SIMULATION --------------------
class OpticalSimulation:
    def __init__(self, total_slots=500000):
        self.total_slots = total_slots        # Total number of time slots
        self.stations = []                    # List of Station objects
        self.wavelength_groups = {}           # λ → list of stations sharing it
        self.packet_counter = 0               # Global unique packet ID

    # Create 8 stations and assign them to 4 wavelengths
    def setup_stations(self):
        wavelengths = ['λ1', 'λ2', 'λ3', 'λ4']
        self.stations.clear()
        self.wavelength_groups.clear()

        for i in range(8):
            wl = wavelengths[i // 2]  # Every 2 stations share the same wavelength
            station = Station(station_id=i+1, wavelength=wl)
            self.stations.append(station)
            if wl not in self.wavelength_groups:
                self.wavelength_groups[wl] = []
            self.wavelength_groups[wl].append(station)

    # Reset all station stats before each simulation run
    def reset_stations(self):
        for station in self.stations:
            station.queue.clear()
            station.total_packets_created = 0
            station.total_packets_lost = 0
            station.total_packets_sent = 0
            station.total_delay = 0

    # Run simulation for a given packet arrival probability `p`
    def run_simulation(self, arrival_prob):
        self.packet_counter = 0
        self.reset_stations()

        for t in range(self.total_slots):
            # Step 1: Try to generate packets at each station
            for station in self.stations:
                self.packet_counter = station.generate_packet(
                    current_time=t,
                    p=arrival_prob,
                    packet_counter=self.packet_counter
                )

            # Step 2: Determine which stations attempt to transmit
            transmitting_stations = {}
            for station in self.stations:
                if station.wants_to_transmit():
                    wl = station.wavelength
                    if wl not in transmitting_stations:
                        transmitting_stations[wl] = []
                    transmitting_stations[wl].append(station)

            # Step 3: Attempt transmissions or resolve collisions
            for wl, station_list in transmitting_stations.items():
                if len(station_list) == 1:
                    # Successful transmission (no collision)
                    station_list[0].successful_transmission(t)
                else:
                    # Collision – packets remain in queue
                    pass

        # Step 4: Collect simulation metrics
        total_created = sum(s.total_packets_created for s in self.stations)
        total_lost = sum(s.total_packets_lost for s in self.stations)
        total_sent = sum(s.total_packets_sent for s in self.stations)
        total_delay = sum(s.total_delay for s in self.stations)

        avg_delay = total_delay / total_sent if total_sent > 0 else 0
        throughput = total_sent / self.total_slots
        loss_rate = total_lost / total_created if total_created > 0 else 0

        return avg_delay, throughput, loss_rate


# -------------------- MAIN FUNCTION --------------------
def main():
    sim = OpticalSimulation(total_slots=500000)
    sim.setup_stations()

    p_values = [round(i * 0.1, 1) for i in range(1, 11)]  # Values from 0.1 to 1.0
    avg_delays = []
    throughputs = []
    loss_rates = []

    # Open results.txt to write results
    with open("results.txt", "w", encoding="utf-8") as f:
        f.write("Αποτελέσματα Προσομοίωσης – Οπτικό Δίκτυο με 8 Σταθμούς & 4 Μήκη Κύματος\n\n")
        f.write(f"Σύνολο slots = {sim.total_slots}, Πιθανότητα μετάδοσης ανά slot = 0.5\n")
        f.write("Buffer ανά σταθμό = 5 πακέτα\n\n")
        f.write("---------------------------------------------------------------------\n")
        f.write("|   p   |  Μέση Καθυστέρηση  |  Throughput  |  Ποσοστό Απώλειας  |\n")
        f.write("---------------------------------------------------------------------\n")

        # Run simulation for each p value
        for p in p_values:
            print(f"Running simulation for p = {p}...")
            avg_delay, throughput, loss_rate = sim.run_simulation(p)
            avg_delays.append(avg_delay)
            throughputs.append(throughput)
            loss_rates.append(loss_rate)

            f.write(f"| {p:<4} | {avg_delay:>8.2f} slots     |  {throughput:<8.3f}   |     {loss_rate*100:>5.2f}%        |\n")

    print("\nΗ προσομοίωση ολοκληρώθηκε. Τα αποτελέσματα αποθηκεύτηκαν στο 'results.txt'.")

    # Plot 1: Average Delay
    plt.figure()
    plt.plot(p_values, avg_delays, marker='o')
    plt.title("Μέση Καθυστέρηση Πακέτου")
    plt.xlabel("Πιθανότητα Άφιξης (p)")
    plt.ylabel("Μέση Καθυστέρηση (slots)")
    plt.grid(True)
    plt.savefig("average_delay.png")

    # Plot 2: Throughput
    plt.figure()
    plt.plot(p_values, throughputs, marker='o', color='green')
    plt.title("Throughput (Επιτυχείς Μεταδόσεις / slot)")
    plt.xlabel("Πιθανότητα Άφιξης (p)")
    plt.ylabel("Throughput")
    plt.grid(True)
    plt.savefig("throughput.png")

    # Plot 3: Packet Loss Rate
    plt.figure()
    plt.plot(p_values, loss_rates, marker='o', color='red')
    plt.title("Ρυθμός Απώλειας Πακέτων")
    plt.xlabel("Πιθανότητα Άφιξης (p)")
    plt.ylabel("Packet Loss Rate")
    plt.grid(True)
    plt.savefig("loss_rate.png")

    print("Τα γραφήματα αποθηκεύτηκαν.")

# Entry point of the program
if __name__ == "__main__":
    main()