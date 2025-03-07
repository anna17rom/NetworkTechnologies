import random
import re

class CRC32:
    def __init__(self):
        # Inicjalizacja obiektu CRC32 poprzez wygenerowanie tablicy CRC.
        self.crc_table = self.generate_crc_table()

    def generate_crc_table(self):
        # Definicja wielomianu użytego do obliczeń CRC i inicjalizacja pustej tablicy.
        polynomial = 0xEDB88320
        crc_table = []
        # Generowanie tablicy CRC dla każdej możliwej wartości bajtu.
        for i in range(256):
            crc = i
            for _ in range(8):
                # Obliczenie CRC dla pojedynczego bajtu.
                if crc & 1:
                    crc = (crc >> 1) ^ polynomial
                else:
                    crc >>= 1
            crc_table.append(crc)
        return crc_table

    def calculate_crc(self, data):
        # Inicjalizacja wartości początkowej CRC.
        crc = 0xFFFFFFFF
        # Obliczenie CRC dla całego ciągu danych.
        for byte in data:
            crc = (crc >> 8) ^ self.crc_table[(crc ^ byte) & 0xFF]
        # Końcowe XORowanie, aby uzyskać końcową wartość CRC.
        return crc ^ 0xFFFFFFFF

def bit_stuffing(data):
    # Dodanie '0' do sekwencji '11111' w danych, aby uniknąć problemów z markierami.
    return data.replace('11111', '111110')

def unbit_stuffing(data):
    # Usunięcie dodatkowego '0' po sekwencji '11111' w danych.
    return data.replace('111110', '11111')


def frame_data(data, frame_size):
    framed_data = []
    crc_calculator = CRC32()
    for i in range(0, len(data), frame_size):
        frame = data[i:i+frame_size]
        crc = crc_calculator.calculate_crc(frame.encode('utf-8'))
        crc_bits = f"{crc:032b}"
        stuffed_frame = bit_stuffing(frame)
        framed_data.append('01111110' + stuffed_frame + crc_bits + '01111110')
    return framed_data

def corrupt_frame(frame, corruption_probability=0.3):
    # Funkcja do symulacji korupcji danych w ramce z określonym prawdopodobieństwem.
    if random.random() < corruption_probability:
        bit_to_corrupt = random.randint(8, len(frame) - 41)
        corrupted_frame = frame[:bit_to_corrupt] + ('0' if frame[bit_to_corrupt] == '1' else '1') + frame[bit_to_corrupt + 1:]
        return corrupted_frame
    return frame

def verify_frame(frame):
    # Weryfikacja, czy ramka jest poprawna; sprawdzenie CRC i markierów.
    if frame.startswith('01111110') and frame.endswith('01111110'):
        data_part = frame[8:-40]
        crc_part = frame[-40:-8]
        expected_crc = int(crc_part, 2)
        data_part_unstuffed = unbit_stuffing(data_part)
        actual_crc = CRC32().calculate_crc(data_part_unstuffed.encode('utf-8'))
        print(f"Expected CRC: {expected_crc}, Actual CRC: {actual_crc}, Data Unstuffed: {data_part_unstuffed}")
        return actual_crc == expected_crc, data_part_unstuffed
    else:
        return False, frame

def process_frames(frames):
    # Proces weryfikacji ramek; zliczanie uszkodzonych i naprawianie poprawnych.
    repaired_data = []
    damaged_frames_count = 0
    for frame in frames:
        is_valid, data = verify_frame(frame)
        if is_valid:
            repaired_data.append(data)
        else:
            damaged_frames_count += 1

    return repaired_data, damaged_frames_count

def write_frames(frames, file_path):
    # Zapis ramki do pliku.
    with open(file_path, 'w') as file:
        for frame in frames:
            file.write(f"{frame}\n")

# Tworzenie losowych danych źródłowych
source_data = ''.join(random.choice('01') for _ in range(500))
with open('start_data.txt', 'w') as file:
    for i in range(0, len(source_data), 100):
        chunk = source_data[i:i+100]  # pobierz kolejne 100 znaków
        file.write(f"{chunk}\n")
# Dzielenie na ramki i dodanie CRC oraz markerów
framed_data = frame_data(source_data, 100)

# Losowo psujemy niektóre ramki
corrupted_frames = [corrupt_frame(frame) for frame in framed_data]

# Zapisujemy uszkodzone ramki do pliku
write_frames(corrupted_frames, 'corrupted_data.txt')

# Odczytujemy uszkodzone ramki, weryfikujemy i naprawiamy
repaired_frames, damaged_frames_count = process_frames(corrupted_frames)

# Zapisujemy poprawne ramki do nowego pliku
write_frames(repaired_frames, 'repaired_data.txt')

print(f"Poprawne ramki: {len(repaired_frames)}")
print(f"Uszkodzone ramki: {damaged_frames_count}")
#01111110 110110 10101010101010101010101010101010 01111110
#| Marker | Dane  |               CRC               | Marker |

