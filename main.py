import json
import os
import csv
from datetime import datetime

DATA_FILE = "data.json"

# struktur data yang disimpan
data = {
    "saldo": 0,
    "total_pemasukan": 0,
    "total_pengeluaran": 0,
    "transaksi": []
}

def load_data():
    global data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"saldo": 0, "total_pemasukan": 0, "total_pengeluaran": 0, "transaksi": []}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# helper untuk format rupiah
def fmt(n):
    return f"Rp {n:,.2f}"

# Warna terminal dan style
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"

def print_table(headers, rows):
    # hitung lebar kolom
    cols = len(headers)
    widths = [len(h) for h in headers]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], len(str(c)))

    sep = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    # header
    print(sep)
    head = "|" + "|".join([f" {headers[i]:<{widths[i]}} " for i in range(cols)]) + "|"
    print(head)
    print(sep)
    for r in rows:
        row = "|" + "|".join([f" {str(r[i]):<{widths[i]}} " for i in range(cols)]) + "|"
        print(row)
    print(sep)

def tambah_pemasukan():
    teks = input("Masukkan jumlah pemasukan: ")
    try:
        jumlah = float(teks)
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0")
            return
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return

    catatan = input("Deskripsi / catatan (opsional): ")
    tanggal = input("Tanggal transaksi (YYYY-MM-DD) kosong=hari ini: ").strip()
    if tanggal:
        try:
            d = datetime.fromisoformat(tanggal)
        except Exception:
            print(RED + "Format tanggal salah. Gunakan YYYY-MM-DD." + RESET)
            return
    else:
        d = datetime.now()

    data["saldo"] = data.get("saldo", 0) + jumlah
    data["total_pemasukan"] = data.get("total_pemasukan", 0) + jumlah
    data["transaksi"].append({
        "tipe": "pemasukan",
        "jumlah": jumlah,
        "catatan": catatan,
        "waktu": d.isoformat()
    })
    save_data()
    print(GREEN + "✅ Berhasil menambahkan pemasukan: " + fmt(jumlah) + RESET)

def tambah_pengeluaran():
    teks = input("Masukkan jumlah pengeluaran: ")
    try:
        jumlah = float(teks)
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0")
            return
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return

    if jumlah > data.get("saldo", 0):
        print(RED + "⚠️  Saldo tidak cukup untuk pengeluaran ini." + RESET)
        return

    catatan = input("Deskripsi / catatan (opsional): ")
    tanggal = input("Tanggal transaksi (YYYY-MM-DD) kosong=hari ini: ").strip()
    if tanggal:
        try:
            d = datetime.fromisoformat(tanggal)
        except Exception:
            print(RED + "Format tanggal salah. Gunakan YYYY-MM-DD." + RESET)
            return
    else:
        d = datetime.now()

    data["saldo"] = data.get("saldo", 0) - jumlah
    data["total_pengeluaran"] = data.get("total_pengeluaran", 0) + jumlah
    data["transaksi"].append({
        "tipe": "pengeluaran",
        "jumlah": jumlah,
        "catatan": catatan,
        "waktu": d.isoformat()
    })
    save_data()
    print(RED + "✅ Berhasil menambahkan pengeluaran: " + fmt(jumlah) + RESET)

def lihat_saldo():
    print(BLUE + BOLD + "--- Saldo Saat Ini ---" + RESET)
    rows = [["Saldo", fmt(data.get("saldo", 0))]]
    print_table(["Keterangan", "Nilai"], rows)

def lihat_laporan():
    print("--- Laporan Keuangan ---")
    transaksi = data.get("transaksi", [])
    if not transaksi:
        print("Belum ada transaksi.")
        return

    print("(Filter berdasarkan tahun dan bulan. Kosong untuk semua)")
    tahun = input("Tahun (YYYY, kosong=semua): ").strip()
    bulan = input("Bulan (1-12, kosong=semua): ").strip()
    try:
        tahun_i = int(tahun) if tahun else None
    except ValueError:
        print("Format tahun salah.")
        return
    try:
        bulan_i = int(bulan) if bulan else None
        if bulan_i and not 1 <= bulan_i <= 12:
            raise ValueError
    except ValueError:
        print("Format bulan salah. Gunakan 1-12.")
        return

    total_in = 0
    total_out = 0
    rows = []
    for i, t in enumerate(transaksi, start=1):
        waktu_iso = t.get("waktu", "")
        try:
            tt = datetime.fromisoformat(waktu_iso)
        except Exception:
            continue
        if tahun_i and tt.year != tahun_i:
            continue
        if bulan_i and tt.month != bulan_i:
            continue
        tipe = t.get("tipe", "-")
        jumlah = t.get("jumlah", 0)
        cat = t.get("catatan", "")
        waktu = tt.strftime("%Y-%m-%d")
        emo = "📈" if tipe == "pemasukan" else "📉"
        amt = fmt(jumlah)
        if tipe == "pemasukan":
            amt = GREEN + amt + RESET
            total_in += jumlah
        else:
            amt = RED + amt + RESET
            total_out += jumlah
        rows.append([str(i), waktu, emo + " " + tipe, amt, cat])

    if not rows:
        print("Tidak ada transaksi sesuai filter.")
        return

    print_table(["No", "Tanggal", "Tipe", "Jumlah", "Catatan"], rows)
    print(BOLD + "Ringkasan:" + RESET)
    print(f"{GREEN}Total pemasukan : {fmt(total_in)}{RESET}")
    print(f"{RED}Total pengeluaran: {fmt(total_out)}{RESET}")
    print(f"{BLUE}Saldo saat ini   : {fmt(data.get('saldo',0))}{RESET}")

def export_csv():
    transaksi = data.get("transaksi", [])
    if not transaksi:
        print("Tidak ada transaksi untuk diekspor.")
        return
    fname = input("Nama file CSV (default report.csv): ").strip() or "report.csv"
    try:
        with open(fname, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["waktu", "tipe", "jumlah", "catatan"])
            for t in transaksi:
                writer.writerow([t.get("waktu",""), t.get("tipe",""), t.get("jumlah",0), t.get("catatan","")])
        print(f"Berhasil mengekspor transaksi ke {fname}")
    except Exception as e:
        print("Gagal mengekspor CSV:", e)

def reset_data():
    konfirm = input("Yakin reset semua data? KETIK 'YA' untuk konfirmasi: ")
    if konfirm == "YA":
        data.clear()
        data.update({"saldo": 0, "total_pemasukan": 0, "total_pengeluaran": 0, "transaksi": []})
        save_data()
        print("Data berhasil direset.")
    else:
        print("Reset dibatalkan.")

def menu():
    print(BLUE + BOLD + "=== Aplikasi Pengelola Uang Saku 💰 ===" + RESET)
    print("1. ➕ Tambah pemasukan")
    print("2. ➖ Tambah pengeluaran")
    print("3. 🧾 Lihat saldo")
    print("4. 📊 Lihat laporan (dengan filter)")
    print("5. 📤 Ekspor laporan ke CSV")
    print("6. 🗑️  Reset data")
    print("7. 🚪 Keluar")

if __name__ == "__main__":
    load_data()
    while True:
        menu()
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_pemasukan()
        elif pilihan == "2":
            tambah_pengeluaran()
        elif pilihan == "3":
            lihat_saldo()
        elif pilihan == "4":
            lihat_laporan()
        elif pilihan == "5":
            export_csv()
        elif pilihan == "6":
            reset_data()
        elif pilihan == "7":
            print("Terima kasih!")
            break
        else:
            print("Pilihan tidak valid")