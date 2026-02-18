# Tucil 1 - Queens LinkedIn Solver 👑

> Tugas Kecil 1 Strategi Algoritma (IF2211)
> Penyelesaian Permainan Queens LinkedIn dengan Algoritma Brute Force.

## 📌 About
Program ini adalah aplikasi GUI berbasis Python untuk menyelesaikan permainan Queens yang populer di LinkedIn. Permainan ini mirip dengan masalah N-Queens klasik, namun dengan tambahan batasan berupa daerah warna-warni.

Tujuan permainan adalah menempatkan N buah Ratu (Queens) pada papan berukuran N x N sehingga:
1.  Setiap baris memiliki tepat satu Queen.
2.  Setiap kolom memiliki tepat satu Queen.
3.  Setiap daerah warna memiliki tepat satu Queen.
4.  Tidak ada Queen yang bersentuhan dalam jarak 1 kotak.

Program ini dibuat menggunakan library Tkinter untuk halaman menu dan Pygame untuk halaman solver. Program ini juga mampu melakukan input dari image untuk membaca soal langsung dari gambar.

## ✨ Fitur Utama
* 🚀 **GUI**: Tampilan visual papan catur dan animasi pencarian solusi.
* 📂 **Format Input**: Menerima input file teks (`.txt`) maupun gambar (`.png`, `.jpg`, `.jpeg`).
* ⏱️ **Live Update**: Menampilkan durasi waktu eksekusi dan jumlah iterasi secara langsung.
* 💾 **Save Solution**: Menyimpan hasil solusi dalam bentuk gambar atau teks.

## ⚙️ Requirements & Installation

### Prasyarat Sistem
* **Bahasa Pemrograman**: Python 3.10 atau lebih baru.
* **Sistem Operasi**: Windows, macOS, atau Linux (termasuk WSL).

### Library Python
Program ini membutuhkan beberapa library eksternal. Untuk menginstalnya, dapat menggunakan `pip`.

Daftar dependensi:
* `pygame` (untuk GUI)
* `pillow` (untuk pemrosesan gambar)
* `numpy` (untuk operasi matriks pada gambar)
* `tkinter` (untuk dialog file)

**Cara Instalasi:**
Buka terminal atau command prompt, lalu jalankan perintah berikut:

```bash 
pip install pygame pillow numpy
```

Untuk sistem operasi Linux, maka dapat menggunakan perintah berikut:
```bash
sudo apt install python3-pygame
sudo apt install python3-tk
sudo apt install python3-pil
```

## ▶️ How to Run
Masuk ke folder src dengan menggunakan command:
```bash
cd src
```

Kemudian, jalankan program dengan menggunakan command:
```bash
python gui.py
```

Apabila di sistem operasi Linux, gunakan:
```bash
python3 gui.py
```

## 🔁 How to Use
1. Masukkan file masalah Queen yang ingin diselesaikan dalam format .txt atau image (.jpeg/.jpg/.png)
2. Apabila masukan valid, program akan lanjut ke halaman solver dan mulai mencari solusi
3. Program akan menampilkan live update selama dalam proses pencarian solusi
4. Jika ditemukan solusi yang valid, maka proses pencarian akan berhenti dan program menampilkan solusi, waktu, dan banyak iterasi
5. Pengguna dapat menyimpan solusi sebagai text atau image
6. Apabila tidak ada solusi yang memenuhi, maka akan ditampilkan status "GAGAL" dan tombol save tidak akan muncul

## 👤 Author
Nama Lengkap: Amanda Aurellia Salsabilla
NIM: 13524131
Kelas: K3