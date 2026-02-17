from PIL import Image
import numpy as np
import math

# GUI kamu punya A-Z (26). Kita pakai itu sebagai label output.
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Threshold buat ngelompokkan warna yang "mirip"
# Kalau gambar input banyak noise JPG, naikin dikit (misal 40-55).
COLOR_MERGE_THR = 45


def rgb_dist(a, b):
    """Jarak Euclidean RGB."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def _merge_positions(pos, merge_gap=3):
    """Gabungkan posisi garis yang berdekatan (garis tebal bisa ke-detect berkali-kali)."""
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

def pick_best_periodic_lines(lines, target_count=None):
    """
    Ambil subset garis yang paling konsisten jaraknya (grid periodik).
    Kalau target_count dikasih (misal 10), dia akan cari sekuens panjang itu.
    """
    lines = sorted(lines)
    if len(lines) < 4:
        return lines

    # hitung semua jarak antar tetangga
    diffs = [lines[i+1] - lines[i] for i in range(len(lines)-1)]
    step = int(np.median(diffs)) if len(diffs) else 0
    if step <= 0:
        return lines

    # toleransi (gridline bisa geser beberapa px)
    tol = max(2, int(step * 0.35))

    best = []
    # coba mulai dari tiap index, bangun sekuens yang mengikuti step
    for start in range(len(lines)):
        seq = [lines[start]]
        last = lines[start]
        for p in lines[start+1:]:
            if abs((p - last) - step) <= tol:
                seq.append(p)
                last = p
        if len(seq) > len(best):
            best = seq

    # kalau user/board biasanya butuh count tertentu (N+1), potong/ambil yang paling pas
    if target_count is not None and len(best) >= target_count:
        # pilih window ukuran target_count yang paling konsisten
        best_window = best[:target_count]
        best_score = float("inf")
        for i in range(0, len(best) - target_count + 1):
            window = best[i:i+target_count]
            wd = [window[k+1] - window[k] for k in range(len(window)-1)]
            score = np.std(wd)  # makin kecil makin bagus
            if score < best_score:
                best_score = score
                best_window = window
        return best_window

    return best



def crop_inner_board(img_arr):
    """
    Buang frame/border hitam tebal (rounded) supaya deteksi grid stabil.
    Cocok untuk output board seperti yang kamu kirim.
    """
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

    if r_bot - r_top < h * 0.5 or c_right - c_left < w * 0.5:
        return img_arr

    return img_arr[r_top:r_bot+1, c_left:c_right+1, :]


def detect_grid_lines(img_arr):
    """
    Robust gridline detection:
    - coba beberapa threshold gelap (buat JPEG / garis abu2)
    - coba beberapa threshold panjang garis (buat garis tipis)
    """
    h, w, _ = img_arr.shape

    # beberapa kandidat threshold gelap (makin besar = makin sensitif)
    dark_thrs = [120, 140, 170, 200]
    # beberapa kandidat ratio minimal panjang garis
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

            # minimal harus ada beberapa garis
            if len(xs) < 4 or len(ys) < 4:
                continue

            # jangan hardcode 10 di sini — biarkan adaptif untuk N berapa pun
            xs2 = pick_best_periodic_lines(xs, target_count=None)
            ys2 = pick_best_periodic_lines(ys, target_count=None)

            # scoring: lebih baik yang lebih banyak & seimbang
            score = min(len(xs2), len(ys2)) * 10 - abs(len(xs2) - len(ys2)) * 3

            best_score = min(len(best_xs), len(best_ys)) * 10 - abs(len(best_xs) - len(best_ys)) * 3
            if score > best_score:
                best_xs, best_ys = xs2, ys2

    return best_xs, best_ys



def sample_cell_color(img_arr, x1, x2, y1, y2):
    """
    Ambil warna sel via median patch tengah,
    buang pixel gelap (gridline/crown) + buang putih ekstrem (highlight).
    """
    cx1 = int(x1 + (x2 - x1) * 0.35)
    cx2 = int(x1 + (x2 - x1) * 0.65)
    cy1 = int(y1 + (y2 - y1) * 0.35)
    cy2 = int(y1 + (y2 - y1) * 0.65)

    patch = img_arr[cy1:cy2, cx1:cx2, :].reshape(-1, 3)
    if patch.size == 0:
        return (200, 200, 200)

    # buang dark
    keep = ~((patch[:, 0] < 80) & (patch[:, 1] < 80) & (patch[:, 2] < 80))
    patch2 = patch[keep]

    # buang putih ekstrem
    if len(patch2) > 0:
        keep2 = ~((patch2[:, 0] > 245) & (patch2[:, 1] > 245) & (patch2[:, 2] > 245))
        patch2 = patch2[keep2]

    if len(patch2) < 10:
        patch2 = patch  # fallback

    med = np.median(patch2, axis=0)
    return (int(med[0]), int(med[1]), int(med[2]))


def cluster_colors(colors, merge_thr=COLOR_MERGE_THR, max_clusters=26):
    """
    Cluster sederhana:
    - assign warna ke cluster terdekat jika jarak < merge_thr
    - kalau lebih dari 26, merge cluster terdekat sampai 26
    Return: list of clusters (centroid, members_count)
    """
    clusters = []  # each: {"centroid": (r,g,b), "count": int, "first_idx": int}

    for idx, rgb in enumerate(colors):
        best_i = -1
        best_d = float("inf")

        for i, cl in enumerate(clusters):
            d = rgb_dist(rgb, cl["centroid"])
            if d < best_d:
                best_d = d
                best_i = i

        if best_i != -1 and best_d <= merge_thr:
            cl = clusters[best_i]
            # update centroid by running average (biar stabil)
            c = cl["count"]
            cr, cg, cb = cl["centroid"]
            nr = int((cr * c + rgb[0]) / (c + 1))
            ng = int((cg * c + rgb[1]) / (c + 1))
            nb = int((cb * c + rgb[2]) / (c + 1))
            cl["centroid"] = (nr, ng, nb)
            cl["count"] += 1
        else:
            clusters.append({"centroid": rgb, "count": 1, "first_idx": idx})

    # kalau cluster kebanyakan, merge yang paling dekat
    while len(clusters) > max_clusters:
        best_pair = None
        best_d = float("inf")

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = rgb_dist(clusters[i]["centroid"], clusters[j]["centroid"])
                if d < best_d:
                    best_d = d
                    best_pair = (i, j)

        i, j = best_pair
        a = clusters[i]
        b = clusters[j]

        # merge b into a (weighted)
        ca, cb = a["count"], b["count"]
        ar, ag, ab_ = a["centroid"]
        br, bg, bb_ = b["centroid"]
        nr = int((ar * ca + br * cb) / (ca + cb))
        ng = int((ag * ca + bg * cb) / (ca + cb))
        nb = int((ab_ * ca + bb_ * cb) / (ca + cb))

        a["centroid"] = (nr, ng, nb)
        a["count"] = ca + cb
        a["first_idx"] = min(a["first_idx"], b["first_idx"])

        clusters.pop(j)

    # sort cluster by first appearance (deterministic)
    clusters.sort(key=lambda x: x["first_idx"])
    return clusters


def assign_letter(rgb, clusters):
    """Cari cluster terdekat, balikin hurufnya."""
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

        xs0, ys0 = detect_grid_lines(img_arr0)
        xs1, ys1 = detect_grid_lines(img_arr1)

        # pilih yang lebih banyak & seimbang
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
            return None, 0

        # --- 1) SAMPLE warna semua sel ---
        cell_colors = []
        for r in range(N):
            y1, y2 = ys[r], ys[r + 1]
            for c in range(N):
                x1, x2 = xs[c], xs[c + 1]
                rgb = sample_cell_color(img_arr, x1, x2, y1, y2)
                cell_colors.append(rgb)

        # --- 2) CLUSTER warna -> huruf ---
        clusters = cluster_colors(cell_colors, merge_thr=COLOR_MERGE_THR, max_clusters=26)
        # print("Clusters:", len(clusters))  # debug kalau mau

        # --- 3) BUILD grid huruf ---
        grid = []
        idx = 0
        for r in range(N):
            row_chars = []
            for c in range(N):
                ch = assign_letter(cell_colors[idx], clusters)
                row_chars.append(ch)
                idx += 1
            grid.append(row_chars)

        return grid, N

    except Exception as e:
        print(f"Error processing image: {e}")
        return None, 0
