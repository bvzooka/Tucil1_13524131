import pygame
import threading
import time
import sys
import os
import tkinter as tk

from parser import parser, save_solution
from solver import solve_queens
from tkinter import filedialog
from imageloader import process_image

# Konfigurasi layar
BOARD_W = 900
BOARD_H = 560
BOTTOM_H = 150
WINDOW_WIDTH = BOARD_W
WINDOW_HEIGHT = BOARD_H + BOTTOM_H
GRID_OFFSET = 50

# Daftar warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)

# Mapping karakter warna ke RGB
COLOR_MAP = {
    'A': (255, 100, 100),
    'B': (100, 255, 100),
    'C': (100, 100, 255),
    'D': (255, 255, 100),
    'E': (255, 100, 255),
    'F': (100, 255, 255),
    'G': (255, 150, 50),
    'H': (150, 100, 50),
    'I': (128, 128, 128),
    'J': (47, 79, 79),
    'K': (255, 215, 0),
    'L': (255, 140, 0),
    'M': (139, 69, 19),
    'N': (50, 205, 50),
    'O': (0, 0, 128),
    'P': (0, 128, 128),
    'Q': (128, 0, 0),
    'R': (255, 20, 147),
    'S': (128, 128, 0),
    'T': (147, 112, 219),
    'U': (210, 180, 140),
    'V': (255, 127, 80), 
    'W': (46, 139, 87),
    'X': (75, 0, 130),
    'Y': (220, 20, 60),
    'Z': (70, 130, 180)
}

# Warna Tombol
BTN_COLOR = (46, 139, 87)
BTN_HOVER_COLOR = (60, 179, 113)
TEXT_COLOR = (255, 255, 255)

def get_color(char):
    """
    Mengambil warna dari map, handling kasus kalau hurufnya lowercase.
    Jika di luar A-Z, kasih warna default (GRAY).
    """
    key = char.upper()
    if char in COLOR_MAP:
        return COLOR_MAP[key]
    return GRAY

class QueensGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Queens LinkedIn Solver")
        
        # Font
        self.title_font = pygame.font.SysFont('centurygothic', 35, bold=True)
        self.font = pygame.font.SysFont('centurygothic', 24)
        self.btn_font = pygame.font.SysFont('centurygothic', 18, bold=True)
        
        # State variables
        self.grid = None
        self.N = 0
        self.filename = ""

        # Variabel-variabel buat state solver
        self.current_solution = []
        self.iterations = 0
        self.is_solving = False
        self.found_solution = False
        self.start_time = 0
        self.elapsed_time = 0
        self.cell_size = 0
        self.solver_thread = None
        self.stop_solver_flag = threading.Event()

        # Inisialisasi layout page menu dan solver
        self.layout_menu()
        self.layout_solver()

        # Buat logo
        self.logo_img = None
        try:
            raw_img = pygame.image.load(os.path.join("..", "doc", "crown.png"))
            
            # Ubah ukuran gambar supaya pas
            self.logo_img = pygame.transform.scale(raw_img, (120, 120))
            
        except FileNotFoundError:
            print("ERROR: File 'crown.png' tidak ditemukan. Gagal load logo.")

    # Tombol di halaman menu
    def layout_menu(self):
        center_x = WINDOW_WIDTH // 2
        y = WINDOW_HEIGHT // 2 + 120

        btn_w = 320
        btn_h = 60
        gap = 20

        self.btn_load_txt = pygame.Rect(0, 0, btn_w, btn_h)
        self.btn_load_img = pygame.Rect(0, 0, btn_w, btn_h)

        self.btn_load_txt.center = (center_x - (btn_w // 2 + gap // 2), y)
        self.btn_load_img.center = (center_x + (btn_w // 2 + gap // 2), y)

    # Tombol di halaman solver
    def layout_solver(self):
        pad = 16

        # Tombol reset
        self.btn_reset = pygame.Rect(pad, pad, 140, 40)

        # Tombol save
        btn_w = 220
        btn_h = 46
        gap = 16
        y_btn = BOARD_H + BOTTOM_H - pad - btn_h - 40

        total_w = btn_w * 2 + gap
        x0 = (WINDOW_WIDTH - total_w) // 2

        self.btn_save_txt = pygame.Rect(x0, y_btn, btn_w, btn_h)
        self.btn_save_img = pygame.Rect(x0 + btn_w + gap, y_btn, btn_w, btn_h)

    # Layout papan supaya centered dengan menghitung (x, y) pojok kiri atas papan
    def board_origin(self):
        board_px = self.cell_size * self.N
        x0 = (BOARD_W - board_px) // 2
        y0 = (BOARD_H - board_px) // 2
        return x0, y0

    # Load file
    def open_file_dialog(self, file_type):
        root = tk.Tk()
        root.withdraw()
        
        if file_type == 'txt':
            filetypes = [("Text Files", "*.txt")]
        else:
            filetypes = [("Images", "*.png;*.jpg;*.jpeg")]

        path = filedialog.askopenfilename(filetypes=filetypes)
        root.destroy()
        return path

    # Ketika tombol load ditekan
    def load_input(self, input_type):
        path = self.open_file_dialog(input_type)
        if not path: 
            return

        try:
            # Reset visual sebelum load baru
            self.current_solution = []
            self.found_solution = False

            # Load kalau input as text
            if input_type == 'txt':
                self.grid, self.N = parser(path)
                
            # Load kalau input image
            elif input_type == 'img':
                print(f"Loading image dari: {path}")
   
                self.grid, self.N = process_image(path)

                if not self.grid:
                    print("Gagal mendeteksi grid dari gambar!")
                    return

            # Kalau berhasil load
            if self.grid and self.N > 0:
                self.filename = os.path.basename(path)

                # Hitung cell_size berdasarkan area board
                usable = min(BOARD_W, BOARD_H) - 2 * GRID_OFFSET
                self.cell_size = usable // self.N

                self.start_solver()
            else:
                print("Gagal load file.")

        except Exception as e:
            print(f"Error load: {e}")

    # Kembali ke halaman menu
    def reset_state(self):
        self.stop_solver_flag.set()
        self.is_solving = False
        self.grid = None
        self.N = 0
        self.current_solution = []
        self.found_solution = False
        self.iterations = 0
        self.elapsed_time = 0

    # Mulai solver
    def start_solver(self):
        self.stop_solver_flag.clear()
        self.is_solving = True
        self.found_solution = False
        self.iterations = 0
        self.start_time = time.time()
        self.solver_thread = threading.Thread(target=self.run_solver)
        self.solver_thread.daemon = True
        self.solver_thread.start()

    # Konektor antara solver.py dengan gui.py
    def update_visual(self, solution, iterations):
        self.current_solution = solution
        self.iterations = iterations

    # Fungsi untuk menjalankan solver di thread
    def run_solver(self):
        print("Solver dimulai di background...")
        final_sol, total_iter = solve_queens(self.grid, self.N, visualize_callback=self.update_visual, should_stop=self.stop_solver_flag.is_set)
        
        if self.stop_solver_flag.is_set():
            print("Solver dihentikan. Kembali ke menu utama.")
            return

        self.is_solving = False
        self.iterations = total_iter
        self.elapsed_time = (time.time() - self.start_time) * 1000
        
        if final_sol:
            self.current_solution = final_sol
            self.found_solution = True
            print("Solusi Ditemukan!")
        else:
            print("Tidak ada solusi.")

    # Helper gambar tombol
    def draw_btn(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        color = BTN_HOVER_COLOR if rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        
        txt_surf = self.btn_font.render(text, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=rect.center)
        self.screen.blit(txt_surf, txt_rect)

    # Gambar halaman menu
    def draw_menu_screen(self):
        center_x = WINDOW_WIDTH // 2

        # Judul
        title = self.title_font.render("Queens LinkedIn Solver", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(center_x, 120)))

        # Deskripsi
        desc = self.font.render("Selamat datang! Silakan input file yang ingin diselesaikan.", True, (70, 70, 70))
        self.screen.blit(desc, desc.get_rect(center=(center_x, 180)))

        # Logo
        if self.logo_img:
            logo_rect = self.logo_img.get_rect(center=(center_x, 300))
            self.screen.blit(self.logo_img, logo_rect)
        else:
            text = self.font.render("[Logo Missing]", True, RED)
            self.screen.blit(text, text.get_rect(center=(center_x, 300)))

        # Tombol load
        self.draw_btn(self.btn_load_txt, "Load text file (.txt)")
        self.draw_btn(self.btn_load_img, "Load image file (JPEG/JPG/PNG)")

    # Gambar papan dengan kotak-kotak sesuai input
    def draw_board(self):
        x0, y0 = self.board_origin()

        for r in range(self.N):
            for c in range(self.N):
                color_char = self.grid[r][c]
                color = get_color(color_char)

                # Koordinat layar
                x = x0 + c * self.cell_size
                y = y0 + r * self.cell_size

                # Gambar kotak
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))
                # Gambar garis pinggir kotak
                pygame.draw.rect(self.screen, BLACK, (x, y, self.cell_size, self.cell_size), 1)
    
    # Menggambar Queen di papan (bentuk lingkaran)
    def draw_queens(self):
        # Copy supaya tidak error ketika sedang update thread
        queens = list(self.current_solution)

        x0, y0 = self.board_origin()

        for r, c in queens:
            x = x0 + c * self.cell_size + self.cell_size // 2
            y = y0 + r * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 3

            # Gambar lingkaran Queen
            pygame.draw.circle(self.screen, BLACK, (x, y), radius)
            pygame.draw.circle(self.screen, WHITE, (x, y), radius - 2)

    # Menampilkan informasi interasi dan waktu
    def draw_info(self):
        x0, y0 = self.board_origin()
        board_px = self.cell_size * self.N
        info_y = y0 + board_px + 10

        if self.is_solving:
            self.elapsed_time = (time.time() - self.start_time) * 1000
            status_text = "Status: Mencari..."
            color = RED
        elif self.found_solution:
            status_text = "Status: SELESAI"
            color = GREEN
        else:
            status_text = "Status: GAGAL"
            color = RED

        cx = WINDOW_WIDTH // 2
        # Status solver saat ini
        txt_st = self.font.render(status_text, True, color)
        self.screen.blit(txt_st, txt_st.get_rect(center=(cx, info_y + 15)))
        
        # Tampilin banyak iterasi dan waktu
        txt_iter = self.font.render(f"Iterasi: {self.iterations}", True, BLACK)
        txt_time = self.font.render(f"Waktu: {self.elapsed_time:.0f} ms", True, BLACK)
        
        self.screen.blit(txt_iter, txt_iter.get_rect(center=(cx - 120, info_y + 55)))
        self.screen.blit(txt_time, txt_time.get_rect(center=(cx + 120, info_y + 55)))

    # Tombol
    def draw_buttons(self):
        # Reset selalu muncul
        self.draw_btn(self.btn_reset, "Menu Awal")

        # Save cuma muncul kalau selesai dan ada solusi
        if self.found_solution:
            self.draw_btn(self.btn_save_txt, "Save as TXT")
            self.draw_btn(self.btn_save_img, "Save as PNG")

    # Loop utama selama GUI dijalankan
    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()

            # Menangani input user
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.is_solving = False
                    self.stop_solver_flag.set()

                # Cek ada mouse click atau ngga
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Ketika di halaman menu
                    if self.grid is None:
                        if self.btn_load_txt.collidepoint(mouse_pos):
                            self.load_input('txt')
                        elif self.btn_load_img.collidepoint(mouse_pos):
                            self.load_input('img')

                    # Ketika di halaman solver
                    else:
                        if self.btn_reset.collidepoint(mouse_pos):
                            self.reset_state()

                        if self.found_solution:
                            # Simpan sebagai image
                            if self.btn_save_img.collidepoint(mouse_pos):
                                ts = int(time.time())
                                os.makedirs("../test/output", exist_ok=True)
                                fname = f"../test/output/solution_{ts}.png"

                                # Simpan hanya foto papan
                                x0, y0 = self.board_origin()
                                board_px = self.cell_size * self.N
                                sub = self.screen.subsurface((x0, y0, board_px, board_px))
                                pygame.image.save(sub, fname)
                                print(f"Saved IMG: {fname}")
                            
                            # Simpan sebagai text
                            elif self.btn_save_txt.collidepoint(mouse_pos):
                                ts = int(time.time())
                                os.makedirs("../test/output", exist_ok=True)
                                fname = f"../test/output/solution_{ts}.txt"
                                save_solution(fname, self.grid, self.current_solution)
                                print(f"Saved TXT: {fname}")

            # Gambar ulang layar
            self.screen.fill(WHITE)
            
            # Switch tampilan berdasarkan status Grid
            if self.grid is None:
                self.draw_menu_screen()
            else:
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
    app = QueensGUI()
    app.run()