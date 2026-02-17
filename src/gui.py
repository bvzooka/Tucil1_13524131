import pygame
import threading
import time
import sys
import os

from parser import parser, save_solution
from solver import solve_queens

# Konfigurasi layar
SCREEN_SIZE = 600
GRID_OFFSET = 50
FONT_SIZE = 30

# Daftar warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)

# Mapping karakter warna ke RGB
COLOR_MAP = {
    'A': (255, 100, 100), # Merah Muda (Light Red)
    'B': (100, 255, 100), # Hijau Muda (Light Green)
    'C': (100, 100, 255), # Biru Muda (Light Blue)
    'D': (255, 255, 100), # Kuning Cerah (Yellow)
    'E': (255, 100, 255), # Magenta/Ungu Terang
    'F': (100, 255, 255), # Cyan/Biru Langit
    'G': (255, 150, 50),  # Oranye (Orange)
    'H': (150, 100, 50),  # Coklat Tanah (Brown)
    'I': (128, 128, 128), # Abu-abu Medium (Grey)
    'J': (47, 79, 79),    # Dark Slate Gray (Abu Kehijauan Gelap)
    'K': (255, 215, 0),   # Kuning Emas (Gold)
    'L': (255, 140, 0),   # Oranye Gelap (Dark Orange)
    'M': (139, 69, 19),   # Coklat Kayu (Saddle Brown)
    'N': (50, 205, 50),   # Hijau Stabilo (Lime Green)
    'O': (0, 0, 128),     # Biru Dongker (Navy)
    'P': (0, 128, 128),   # Teal (Hijau Kebiruan)
    'Q': (128, 0, 0),     # Merah Hati (Maroon)
    'R': (255, 20, 147),  # Deep Pink (Merah Jambu Tua)
    'S': (128, 128, 0),   # Olive (Kuning Zaitun)
    'T': (147, 112, 219), # Medium Purple (Ungu Medium)
    'U': (210, 180, 140), # Tan (Coklat Muda/Krem)
    'V': (255, 127, 80),  # Coral (Merah Bata Muda)
    'W': (46, 139, 87),   # Sea Green (Hijau Laut)
    'X': (75, 0, 130),    # Indigo (Nila Gelap)
    'Y': (220, 20, 60),   # Crimson (Merah Darah)
    'Z': (70, 130, 180)   # Steel Blue (Biru Baja - sama kayak tombol)
}

# Warna Tombol
BTN_COLOR = (70, 130, 180)       # Steel Blue
BTN_HOVER_COLOR = (100, 149, 237) # Cornflower Blue (lebih terang pas di-hover)
TEXT_COLOR = (255, 255, 255)     # Putih

def get_color(char):
    """
    Mengambil warna dari map, handling kasus kalau hurufnya lowercase.
    Jika di luar A-Z, kembalikan warna default (GRAY).
    """
    key = char.upper()
    if char in COLOR_MAP:
        return COLOR_MAP[key]
    return GRAY

class QueensGUI:
    def __init__(self, filename):
        pygame.init()
        self.screen_height = SCREEN_SIZE + 150 
        self.screen = pygame.display.set_mode((SCREEN_SIZE, self.screen_height))
        pygame.display.set_caption("Queens LinkedIn Solver")
        self.font = pygame.font.SysFont('Arial', 24)
        self.btn_font = pygame.font.SysFont('Arial', 20, bold=True)
        
        # Load data
        self.grid, self.N = parser(filename)
        if not self.grid:
            print("Gagal membaca file!")
            sys.exit()

        # Hitung ukuran kotak
        self.cell_size = (SCREEN_SIZE - 2 * GRID_OFFSET) // self.N

        # Variabel-variabel state terkini
        self.current_solution = []
        self.iterations = 0
        self.is_solving = True
        self.start_time = time.time()
        self.elapsed_time = 0
        self.found_solution = False

        # Multithreading buat solver dan GUI berjalan di thread terpisah
        self.solver_thread = threading.Thread(target=self.run_solver)
        self.solver_thread.daemon = True
        self.solver_thread.start()

        # Konfigurasi tombol (x, y, lebar, tinggi)
        button_y = SCREEN_SIZE + 80
        self.btn_save_img = pygame.Rect(50, button_y, 200, 40)
        self.btn_save_txt = pygame.Rect(300, button_y, 200, 40)

    # Konektor antara solver.py dengan gui.py
    def update_visual(self, solution, iterations):
        self.current_solution = solution
        self.iterations = iterations

    # Fungsi untuk menjalankan solver di thread
    def run_solver(self):
        print("Solver dimulai di background thread...")
        final_sol, total_iter = solve_queens(self.grid, self.N, visualize_callback=self.update_visual)
        
        self.is_solving = False
        self.iterations = total_iter
        if final_sol:
            self.current_solution = final_sol
            self.found_solution = True
            print("Solusi Ditemukan!")
        else:
            print("Tidak ada solusi.")

    # Gambar papan dengan kotak-kotak sesuai input
    def draw_board(self):
        for r in range(self.N):
            for c in range(self.N):
                color_char = self.grid[r][c]
                color = get_color(color_char)
                
                # Koordinat layar
                x = GRID_OFFSET + c * self.cell_size
                y = GRID_OFFSET + r * self.cell_size
                
                # Gambar kotak
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))
                # Gambar garis pinggir kotak
                pygame.draw.rect(self.screen, BLACK, (x, y, self.cell_size, self.cell_size), 1)

    # Menggambar Queen di papan (bentuk lingkaran)
    def draw_queens(self):
        # Copy supaya tidak error ketika sedang update thread
        queens = list(self.current_solution) 
        
        for r, c in queens:
            x = GRID_OFFSET + c * self.cell_size + self.cell_size // 2
            y = GRID_OFFSET + r * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 3
            
            # Gambar lingkaran Queen
            pygame.draw.circle(self.screen, BLACK, (x, y), radius) # outline
            pygame.draw.circle(self.screen, WHITE, (x, y), radius - 2)

    # Menampilkan informasi interasi dan waktu
    def draw_info(self):
        # Update waktu kalau masih solving
        if self.is_solving:
            self.elapsed_time = (time.time() - self.start_time) * 1000
            status_text = "Status: Mencari..."
        else:
            status_text = "Status: SELESAI" if self.found_solution else "Status: GAGAL"

        # Proses teks
        text_iter = self.font.render(f"Iterasi: {self.iterations}", True, BLACK)
        text_time = self.font.render(f"Waktu: {self.elapsed_time:.0f} ms", True, BLACK)
        text_status = self.font.render(status_text, True, RED if not self.found_solution else GREEN)

        # Taruh di layar bagian bawah
        base_y = SCREEN_SIZE + 10
        self.screen.blit(text_status, (20, base_y))
        self.screen.blit(text_iter, (20, base_y + 30))
        self.screen.blit(text_time, (300, base_y + 30))

    # Tombol
    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Tombol save gambar
        # Cek apakah mouse lagi di atas tombol
        if self.btn_save_img.collidepoint(mouse_pos):
            color_img = BTN_HOVER_COLOR
        else:
            color_img = BTN_COLOR
            
        pygame.draw.rect(self.screen, color_img, self.btn_save_img, border_radius=10)
        
        # Teks pada tombol
        text_img = self.btn_font.render("Simpan Gambar (PNG)", True, TEXT_COLOR)
        # Supaya teks centered di dalam tombol
        text_rect_img = text_img.get_rect(center=self.btn_save_img.center)
        self.screen.blit(text_img, text_rect_img)

        # Tombol save text
        if self.btn_save_txt.collidepoint(mouse_pos):
            color_txt = BTN_HOVER_COLOR
        else:
            color_txt = BTN_COLOR
            
        pygame.draw.rect(self.screen, color_txt, self.btn_save_txt, border_radius=10)
        
        text_txt = self.btn_font.render("Simpan Text (.txt)", True, TEXT_COLOR)
        text_rect_txt = text_txt.get_rect(center=self.btn_save_txt.center)
        self.screen.blit(text_txt, text_rect_txt)

    # Loop utama selama GUI dijalankan
    def run(self):
        running = True
        while running:
            # Menangani input user
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Cek ada mouse click atau ngga
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = event.pos
                        # Hanya bisa save kalau solusi sudah ketemu
                        if self.found_solution:
                            # Cek klik tombol save as image
                            if self.btn_save_img.collidepoint(mouse_pos):
                                timestamp = int(time.time())
                                filename = f"../test/output/solution_{timestamp}.png"
                                os.makedirs(os.path.dirname(filename), exist_ok=True)
                                
                                # Simpan layar (tapi bagian papan aja, sisanya dicrop)
                                sub_surface = self.screen.subsurface((0, 0, SCREEN_SIZE, SCREEN_SIZE))
                                pygame.image.save(sub_surface, filename)
                                print(f"Gambar disimpan: {filename}")

                            # Cek klik tombol save as text
                            if self.btn_save_txt.collidepoint(mouse_pos):
                                timestamp = int(time.time())
                                filename = f"../test/output/solution_{timestamp}.txt"
                                os.makedirs(os.path.dirname(filename), exist_ok=True)
                                
                                if save_solution(filename, self.grid, self.current_solution):
                                    print(f"Text disimpan: {filename}")
                        else:
                            # Kalau diklik tapi belum selesai solving
                            if self.btn_save_img.collidepoint(mouse_pos) or self.btn_save_txt.collidepoint(mouse_pos):
                                print("Tunggu pencarian selesai dulu...")

            # Gambar ulang layar
            self.screen.fill(WHITE)
            self.draw_board()
            self.draw_queens()
            self.draw_info()
            self.draw_buttons()

            # Update display
            pygame.display.flip()
            
            # FPS dibatasi sampai 60 fps
            pygame.time.Clock().tick(60)

        pygame.quit()
        sys.exit()

# Jalankan GUI
if __name__ == "__main__":
    filename = "../test/input/tc1.txt" 
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    if os.path.exists(filename):
        app = QueensGUI(filename)
        app.run()
    else:
        # Coba cari relatif kalau ga ketemu
        alt_path = os.path.join("..", "test", "input", filename)
        if os.path.exists(alt_path):
            app = QueensGUI(alt_path)
            app.run()
        else:
            print(f"File {filename} tidak ditemukan.")