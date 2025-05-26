# WDM Optical Network Simulator (Python)

This project simulates an optical WDM (Wavelength Division Multiplexing) network with 8 computer stations and a single server.

Each pair of stations shares one of four wavelengths (λ1–λ4). The network simulates packet arrival, transmission, collision handling, and queueing delays over multiple time slots.

## 📌 Features

- 8 stations divided into 4 wavelength groups (2 per λ)
- Time-slot-based simulation
- FIFO buffer with capacity of 5 packets per station
- Packet arrival with configurable probability `p ∈ [0.1, 1.0]`
- Transmission probability of 0.5
- Collision detection per wavelength
- Collection of key performance metrics:
  - Average packet delay
  - Throughput (successful transmissions per slot)
  - Packet loss rate

## 📁 Files

- `optical_simulation.py`: Main simulation script
- `results.txt`: Tabulated results per p value
- `average_delay.png`: Graph of average delay vs arrival probability
- `throughput.png`: Graph of throughput vs arrival probability
- `loss_rate.png`: Graph of packet loss vs arrival probability

## ▶️ How to Run

1. Install requirements (only matplotlib is needed):

```bash
pip install matplotlib