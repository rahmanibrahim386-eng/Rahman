# M268 Executive Dashboard

Dashboard statis yang dibuat dari dataset Excel `M268 DATA DASHBOARD V1.zip` dan workbook di folder `extract/M268 DATA DASHBOARD`.

## Cara membuka secara lokal

1. Pastikan Python 3 tersedia.
2. Jalankan:

```bash
python dashboard_server.py
```

3. Buka browser ke `http://localhost:8000`.

Alias URL dashboard: `http://localhost:8000/Mr.RI`

Dashboard meminta kata sandi sebelum menampilkan halaman dan data. Kata sandi default adalah `rahman`. Untuk menggantinya, jalankan dengan environment variable:

```powershell
$env:DASHBOARD_PASSWORD = "kata-sandi-baru"
python dashboard_server.py
```

## Akses dari HP

Jalankan server pada komputer yang terhubung ke Wi-Fi yang sama dengan HP:

```bash
python dashboard_server.py
```

Cari alamat IPv4 komputer dengan `ipconfig`, lalu buka dari HP:

```text
http://ALAMAT-IP-KOMPUTER:8000/Mr.RI
```

Contoh: `http://192.168.1.10:8000/Mr.RI`. Jika Windows Firewall meminta izin, izinkan akses pada jaringan **Private**. Komputer dan HP harus berada pada jaringan Wi-Fi yang sama.

Dashboard membaca workbook saat endpoint data dipanggil, sehingga perubahan pada file sumber akan terlihat pada refresh berikutnya. Browser melakukan refresh otomatis setiap 10 menit.

## Akses internet saat laptop mati

Server yang berjalan di laptop tidak dapat melayani permintaan ketika laptop mati. Konfigurasi `render.yaml` dan `requirements.txt` disediakan untuk deployment ke Render. Setelah repository dihubungkan ke Render, buat environment variable `DASHBOARD_PASSWORD` dengan nilai yang diinginkan (default aplikasi tetap `rahman` bila variable tidak dibuat). Render menyediakan HTTPS dan menjaga service tetap online ketika laptop mati.

Karena server cloud membaca file Excel yang ada di repository, setiap perubahan workbook harus di-commit/push ke repository atau dihubungkan ke proses sinkronisasi cloud. Jangan memakai repository public untuk workbook yang berisi data rahasia.

Gunakan kolom pencarian untuk mencari nama sales seperti `Virginia`. Kata kunci `Rahman` menampilkan ringkasan seluruh tim, termasuk detail LOB, performa, dan estimasi insentif.

## File utama

- `index.html` — antarmuka dashboard
- `dashboard_data.js` — data KPI yang di-generate dari workbook
- `dashboard_server.py` — server lokal yang membaca ulang workbook
- `generate_dashboard.py` — script pembangkit data dashboard
