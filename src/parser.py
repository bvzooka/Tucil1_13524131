"""
parser.py digunakan untuk:
1. Membaca file .txt 
2. Ubah menjadi list 2D
3. Validasi input (harus N x N dan terisi semua koordinatnya)
"""

import os

def parser(filepath):
    """
    Menerima argumen filepath (path ke file .txt input).
    Mengembalikan tuple (grid, N) jika valid.
    Mengembalikan None jika input tidak valid atau file tidak ditemukan.
    """

    grid = []

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' tidak ditemukan.")
        return (None, None)
    
    try:
        with open(filepath, 'r') as f:
            # Membaca semua baris sekaligus menghapus spasi/enter
            lines = [line.rstrip() for line in f.readlines()]

            # Hapus baris kosong jika ada
            lines = [line for line in lines if line]

            if not lines:
                print("Error: File kosong.")
                return (None, None)
            
            N = len(lines)

            for i, line in enumerate(lines):
                # Validasi panjang setiap baris harus sama dengan N
                if len(line) != N:
                    print(f"Error Validasi: Baris ke-{i+1} memiliki panjang {len(line)}, seharusnya {N}")
                    print("Input harus berupa papan persegi (N x N).")
                    return (None, None)
                
                # Mengubah string menjadi list of karakter
                grid.append(list(line))

            return (grid, N)
        
    except Exception as e:
        print(f"Terjadi kesalahan saat membaca file: {e}.")
        return (None, None)

# Fungsi untuk menyimpan solusi yang didapatkan
def save_solution(filepath, grid, solution):
    try:
        output_grid = [row[:] for row in grid]

        # Posisi Queen ditandai dengan "#"
        for r, c in solution:
            output_grid[r][c] = '#'

        with open(filepath, 'w') as f:
            # Setiap baris dijadikan satu string dulu baru dipisah-pisah
            output_text = "\n".join("".join(row) for row in output_grid)
            f.write(output_text)

        return True
    
    except Exception as e:
        print(f"Gagal menyimpan file: {e}")
        return False

# Menampilkan solusi di CLI
def print_solution(grid):
    if not grid:
        return
    
    for row in grid:
        print("".join(row))