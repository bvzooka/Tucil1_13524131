import numpy as np
import math

from PIL import Image

# Banyak warna ada 26, ngikutin alfabet
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Batas kemiripan warna dianggap satu warna
# Dibuat kecil supaya warna yang shadenya beda tipis aja dianggap beda
COLOR_MERGE_THR = 25

# Buat ngitung jarak euclidean antara dua warna di gambar input
def rgb_dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)

# Kalau ada garis tebal atau garis yang berdekatan, gabungin
def _merge_positions(pos, merge_gap=3):
    if len(pos) == 0:
        return []

    pos = sorted(pos)
    groups = [[pos[0]]]
    for p in pos[1:]:
        if p - groups[-1][-1] <= merge_gap:
            groups[-1].append(p)
        else:
            groups.append([p])

    merged = [int(sum(g) / len(g)) for g in groups]
    return merged

# Filter garis grid supaya jaraknya konsisten
def pick_best_periodic_lines(lines):
    lines = sorted(lines)
    if len(lines) < 4:
        return lines

    # Hitung semua jarak antar tetangga (cari mediannya)
    diffs = [lines[i+1] - lines[i] for i in range(len(lines)-1)]
    step = int(np.median(diffs)) if len(diffs) else 0
    if step <= 0:
        return lines

    # Toleransi
    tol = max(2, int(step * 0.35))

    best = []

    # Cari sequence terpanjang yang memenuhi si step di atas
    for start in range(len(lines)):
        seq = [lines[start]]
        last = lines[start]
        for p in lines[start+1:]:
            if abs((p - last) - step) <= tol:
                seq.append(p)
                last = p
        if len(seq) > len(best):
            best = seq

    if len(best) >= 2:
        return best
    else:
        lines

# Buang frame/border hitam tebal supaya lebih gampang deteksi grid
def crop_inner_board(img_arr):
    dark = (img_arr[:, :, 0] < 80) & (img_arr[:, :, 1] < 80) & (img_arr[:, :, 2] < 80)
    h, w = dark.shape

    row_ratio = dark.mean(axis=1)
    col_ratio = dark.mean(axis=0)

    r_top = 0
    while r_top < h and row_ratio[r_top] > 0.25:
        r_top += 1

    r_bot = h - 1
    while r_bot >= 0 and row_ratio[r_bot] > 0.25:
        r_bot -= 1

    c_left = 0
    while c_left < w and col_ratio[c_left] > 0.25:
        c_left += 1

    c_right = w - 1
    while c_right >= 0 and col_ratio[c_right] > 0.25:
        c_right -= 1

    pad = 2
    r_top = max(0, r_top - pad)
    c_left = max(0, c_left - pad)
    r_bot = min(h - 1, r_bot + pad)
    c_right = min(w - 1, c_right + pad)

    # Validasi crop jangan sampai habis
    if r_bot - r_top < h * 0.5 or c_right - c_left < w * 0.5:
        return img_arr

    return img_arr[r_top:r_bot+1, c_left:c_right+1, :]

# Ngedeteksi garis grid horizontal dan vertikal
def detect_grid_lines(img_arr):
    h, w, _ = img_arr.shape

    # Threshold gelap
    dark_thrs = [120, 140, 170, 200]
    # Ratio minimal panjang garis
    ratios = [0.08, 0.06, 0.04, 0.025]

    best_xs, best_ys = [], []

    for dark_thr in dark_thrs:
        dark = (img_arr[:, :, 0] < dark_thr) & (img_arr[:, :, 1] < dark_thr) & (img_arr[:, :, 2] < dark_thr)

        col_sum = dark.sum(axis=0)
        row_sum = dark.sum(axis=1)

        for ratio in ratios:
            col_thr = max(4, int(h * ratio))
            row_thr = max(4, int(w * ratio))

            x_candidates = np.where(col_sum >= col_thr)[0].tolist()
            y_candidates = np.where(row_sum >= row_thr)[0].tolist()

            xs = _merge_positions(x_candidates, merge_gap=max(2, w // 300))
            ys = _merge_positions(y_candidates, merge_gap=max(2, h // 300))

            # Minimal harus ada beberapa garis
            if len(xs) < 4 or len(ys) < 4:
                continue

            xs2 = pick_best_periodic_lines(xs)
            ys2 = pick_best_periodic_lines(ys)

            # Maksimalin jumlah garis yang banyak dan seimbang
            score = min(len(xs2), len(ys2)) * 10 - abs(len(xs2) - len(ys2)) * 3

            best_score = min(len(best_xs), len(best_ys)) * 10 - abs(len(best_xs) - len(best_ys)) * 3
            if score > best_score:
                best_xs, best_ys = xs2, ys2

    return best_xs, best_ys

# Ambil warna rata-rata cell
def sample_cell_color(img_arr, x1, x2, y1, y2):
    # Ambil area tengah
    cx1 = int(x1 + (x2 - x1) * 0.35)
    cx2 = int(x1 + (x2 - x1) * 0.65)
    cy1 = int(y1 + (y2 - y1) * 0.35)
    cy2 = int(y1 + (y2 - y1) * 0.65)

    patch = img_arr[cy1:cy2, cx1:cx2, :].reshape(-1, 3)
    if patch.size == 0:
        return (200, 200, 200)

    # Buang noise gelap
    keep = ~((patch[:, 0] < 80) & (patch[:, 1] < 80) & (patch[:, 2] < 80))
    patch2 = patch[keep]

    # Buang putih ekstrem
    if len(patch2) > 0:
        keep2 = ~((patch2[:, 0] > 245) & (patch2[:, 1] > 245) & (patch2[:, 2] > 245))
        patch2 = patch2[keep2]

    if len(patch2) < 10:
        patch2 = patch

    med = np.median(patch2, axis=0)
    return (int(med[0]), int(med[1]), int(med[2]))

# Kelompokin warna, yang unik bikin cluster baru
def cluster_colors(colors, merge_thr=COLOR_MERGE_THR, max_clusters=26):
    clusters = []

    for idx, rgb in enumerate(colors):
        # Coba masukin ke cluster yang udah ada
        best_i = -1
        best_d = float("inf")

        for i, cl in enumerate(clusters):
            d = rgb_dist(rgb, cl["centroid"])
            if d < best_d:
                best_d = d
                best_i = i

        if best_i != -1 and best_d <= merge_thr:
            cl = clusters[best_i]
            # Update centroid cluster yang udah ada
            c = cl["count"]
            cr, cg, cb = cl["centroid"]
            nr = int((cr * c + rgb[0]) / (c + 1))
            ng = int((cg * c + rgb[1]) / (c + 1))
            nb = int((cb * c + rgb[2]) / (c + 1))
            cl["centroid"] = (nr, ng, nb)
            cl["count"] += 1
        else:
            # Buat cluster baru
            clusters.append({"centroid": rgb, "count": 1, "first_idx": idx})

    # Kalau cluster kebanyakan, merge yang paling dekat
    while True:
        if len(clusters) <= max_clusters:
            # Cek apakah masih ada yang jaraknya sangat dekat walau jumlah cluster udah dikit
            pass 
        
        best_pair = None
        min_dist = float("inf")

        # Cari pasangan terdekat
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = rgb_dist(clusters[i]["centroid"], clusters[j]["centroid"])
                if d < min_dist:
                    min_dist = d
                    best_pair = (i, j)
        
        # Stop jika tidak ada yang perlu di-merge (jarak jauh semua) atau udah cukup
        if best_pair is None or (len(clusters) <= max_clusters and min_dist > merge_thr):
            break

        # Merge
        i, j = best_pair
        c1, c2 = clusters[i], clusters[j]
        
        total_count = c1["count"] + c2["count"]
        new_centroid = []
        for k in range(3):
            val = (c1["centroid"][k] * c1["count"] + c2["centroid"][k] * c2["count"]) / total_count
            new_centroid.append(int(val))
            
        c1["centroid"] = tuple(new_centroid)
        c1["count"] = total_count
        c1["first_idx"] = min(c1["first_idx"], c2["first_idx"])
        
        # Hapus cluster j
        clusters.pop(j)

    # Sort based on kemunculan pertama supaya urutan huruf konsisten
    clusters.sort(key=lambda x: x["first_idx"])
    return clusters

# Cari kelompok warna terdekat buat return hurufnya
def assign_letter(rgb, clusters):
    best_i = 0
    best_d = float("inf")
    for i, cl in enumerate(clusters):
        d = rgb_dist(rgb, cl["centroid"])
        if d < best_d:
            best_d = d
            best_i = i
    return LETTERS[best_i] if best_i < len(LETTERS) else "Z"

def process_image(filepath):
    try:
        img = Image.open(filepath).convert("RGB")
        img_arr0 = np.array(img)
        img_arr1 = crop_inner_board(img_arr0)

        # Coba deteksi grid di gambar asli banding gambar crop
        xs0, ys0 = detect_grid_lines(img_arr0)
        xs1, ys1 = detect_grid_lines(img_arr1)

        # Pilih yang paling "kotak" (N X N)
        def score(xs, ys):
            return min(len(xs), len(ys)) * 10 - abs(len(xs) - len(ys)) * 3

        if score(xs1, ys1) > score(xs0, ys0):
            img_arr = img_arr1
            xs, ys = xs1, ys1
        else:
            img_arr = img_arr0
            xs, ys = xs0, ys0

        N = min(len(xs), len(ys)) - 1
        print("Detected lines:", len(xs), len(ys), "=> N =", min(len(xs), len(ys)) - 1)

        if N <= 0:
            return (None, 0)

        # Sampling warna semua cell
        cell_colors = []
        for r in range(N):
            y1, y2 = ys[r], ys[r + 1]
            for c in range(N):
                x1, x2 = xs[c], xs[c + 1]
                rgb = sample_cell_color(img_arr, x1, x2, y1, y2)
                cell_colors.append(rgb)

        # Pengelompokan warna-warna
        clusters = cluster_colors(cell_colors, merge_thr=COLOR_MERGE_THR, max_clusters=26)

        # Ubah jadi huruf
        grid = []
        idx = 0
        for r in range(N):
            row_chars = []
            for c in range(N):
                ch = assign_letter(cell_colors[idx], clusters)
                row_chars.append(ch)
                idx += 1
            grid.append(row_chars)

        return (grid, N)

    except Exception as e:
        print(f"Error processing image: {e}")
        return (None, 0)
