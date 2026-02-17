"""
main.py digunakan untuk:
1. Meminta input nama file.
2. Memanggil parser untuk membaca file.
3. Memanggil solver untuk mencari solusi.
4. Menghitung jumlah kasus dan waktu eksekusi.
5. Menampilkan hasilnya ke layar (CLI).
"""

import time
import os

from parser import parser, save_solution
from solver import solve_queens

def print_solution_grid(grid, solution):
    """
    Menampilkan grid dari solusi.
    Queen ditandai dengan '#'.
    """
    # Salin grid supaya yang asli masih aman
    display_grid = [row[:] for row in grid]
    
    # Memasukkan Queen (#) ke koordinat solusi
    for r, c in solution:
        display_grid[r][c] = '#'
        
    # Print ke layar
    for row in display_grid:
        print("".join(row))

# Fungsi untuk live update
def print_live_board(solution, iterations, grid, N):
    # Bersihkan layar terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"Sedang mencari... (Iterasi: {iterations})")
    print("-" * (N + 2))
    
    # Bikin papan kosong sementara
    temp_grid = [['.' for _ in range(N)] for _ in range(N)]
    
    # Isi dengan posisi Queen saat ini
    for r, c in solution:
        temp_grid[r][c] = 'Q'
        
    # Print ke layar
    for row in temp_grid:
        print(" ".join(row))
    print("-" * (N + 2))

def main():
    print("=== Queens LinkedIn Solver ===")
    
    # Input nama file
    filename = input("Masukkan nama file test case: ")
    
    # Cek nama file termasuk path atau ngga (kalau beda folder dari src)
    if not os.path.isfile(filename):
        # Kalau beda folder, cari di ../test/input/
        filepath = os.path.join("..", "test", "input", filename)
    else:
        filepath = filename

    # Parsing file
    grid, N = parser(filepath)
    
    if grid is None:
        print("Gagal membaca file atau file tidak valid.")
        return

    print(f"\nMemproses papan ukuran {N}x{N}...")
    
    # Mulai perhitungan dan penyelesaian
    mode = input("Tampilkan Live Update di terminal? (Y/N): ").lower()
    
    start_time = time.time()
    
    # Fungsi callback (jembatan dari solve_queens ke print_live_board)
    callback_func = None
    if mode == 'y':
        # Lambda buat ngisi kekurangan argumen grid dan N
        callback_func = lambda sol, iter: print_live_board(sol, iter, grid, N)
    
    # Callbacknya dipakai dengan manggil solve_queens
    solution, iterations = solve_queens(grid, N, visualize_callback=callback_func)
    
    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000
    
    # Display hasil
    print("\n=== HASIL PENCARIAN ===")
    
    if solution:
        # Menampilkan hasil akhir papan
        print_solution_grid(grid, solution)
        print(f"\nWaktu pencarian: {execution_time_ms:.2f} ms")
        print(f"Banyak kasus yang ditinjau: {iterations} kasus")

        # Save solusi (CLI) ke folder output
        while True:
            choice = input("\nApakah Anda ingin menyimpan solusi? (Y/N): ").lower()
            
            if choice in ['ya', 'y']:
                filename = input("Masukkan nama file output: ")
                
                # Simpan ke .../test/output
                output_path = os.path.join("..", "test", "output", filename)
                
                # Memastikan foldernya ada
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                if save_solution(output_path, grid, solution):
                    print(f"Solusi berhasil disimpan di: {output_path}")
                break
                
            elif choice in ['tidak', 't', 'n', 'no']:
                print("Terima kasih. Program selesai.")
                break
            else:
                print("Input tidak valid. Ketik 'Y' atau 'N'.")
    else:
        print("TIDAK ADA SOLUSI yang ditemukan.")
        print(f"Waktu pencarian: {execution_time_ms:.2f} ms")
        print(f"Banyak kasus yang ditinjau: {iterations} kasus")

if __name__ == "__main__":
    main()