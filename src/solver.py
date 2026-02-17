""" 
solver.py digunakan untuk:
1. Mencoba semua kemungkinan secara rekursif
2. Memvalidasi setiap kombinasi yang terjadi
"""

"""
Constraints:
1. Hanya satu Queen setiap baris
2. Hanya satu Queen setiap kolom
3. Hanya satu Queen setiap warna
4. Tidak boleh ada Queen yang bertetangga
"""

"""
Konsep solusi:
Mencari semua kemungkinan kombinasi, diisi terlebih dahulu sampai papan penuh, baru dicek validitasnya.
Dalam pengecekan validitas, dimanfaatkan list 1D yang berguna untuk menyimpan posisi Queen yang sedang ditempatkan.
Pengecekan constraints juga memanfaatkan operasi set dan aritmatika sederhana (absolut dan cek selisih).
"""

def solve_queens(grid, N, visualize_callback=None, should_stop=None):
    # Konfigurasi disimpan sebagai list 1D: index = baris dan value = kolom
    current_placement = [0] * N # Penanda Queen ada di baris mana dan kolom mana
    solution = []
    iterations = 0

    # Fungsi yang bertugas untuk memeriksa apakah kombinasi peletakan Queens dari papan saat ini valid
    def check_entire_board(placement):
        # Cek kolom sudah terpakai di baris lain atau belum
        # Kalau panjang set != panjang dimensi, ada angka yang duplikat dalam satu kolom 
        if len(set(placement)) != N:
            return False
            
        # Cek warna sudah terpakai atau belum
        used_colors = set()
        for r in range(N):
            c = placement[r]
            color_char = grid[r][c] 
            
            if color_char in used_colors:
                return False
            used_colors.add(color_char)
            
        # Cek tetangga ada yang bersebelahan atau tidak (membandingkan baris sekarang dengan baris sebelumnya)
        for r in range(1, N):
            curr_col = placement[r]
            prev_col = placement[r-1]
            
            # Jika selisih kolom <= 1, artinya bertetangga
            if abs(curr_col - prev_col) <= 1:
                return False
                
        return True

    # Fungsi yang berguna untuk iterasi seluruh kemungkinan kombinasi
    def generate(row):
        nonlocal iterations

        # Cek apakah harus berhenti mendadak
        if should_stop and should_stop():
            return False
        
        # Basis: sudah sampai baris paling bawah (papan penuh)
        if row == N:
            iterations += 1
            
            # Visualisasi setiap 100.000 iterasi
            if visualize_callback and iterations % 10000 == 0:
                 # Konversi dari list ke tuples [(r, c)] untuk koordinat
                 temp_sol = [(r, current_placement[r]) for r in range(N)]
                 visualize_callback(temp_sol, iterations)

            # Cek board kali ini valid atau ngga
            if check_entire_board(current_placement):
                # Kalau valid, simpan ke variabel luar (biar ga ilang karena rekursi)
                nonlocal solution
                # Konversi lagi
                solution = [(r, current_placement[r]) for r in range(N)]
                return True # Board valid, solusi ketemu, pencerian berhenti
            
            return False # Kalau gagal, mundur satu langkah terus cari lagi
            
        # Rekursif: coba semua kolom dari 0 sampai N-1
        for col in range(N):
            current_placement[row] = col

            # Diminta berhenti atau ngga
            if should_stop and should_stop():
                return False
            
            # Lanjutin sampe baris bawah
            if generate(row + 1):
                return True
                
        return False

    # Mulai pencarian dari baris pertama
    found = generate(0)
    
    if found:
        return solution, iterations
    else:
        return None, iterations