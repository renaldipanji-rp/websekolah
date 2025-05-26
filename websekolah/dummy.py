import os
import django
import random
from datetime import date, timedelta
from django.contrib.auth.models import User
from rapor.models import Guru, Siswa, Wali, MataPelajaran, Kelas, TahunAjaran, Rapor

# Jika menjalankan sebagai file Python, aktifkan Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websekolah.settings")
django.setup()

print("🚀 Memulai pembuatan data dummy...\n")

# 🔹 1. Buat User Dummy untuk Guru & Wali
user_guru = User.objects.create_user(username="guru1", password="password123")
user_wali = User.objects.create_user(username="wali1", password="password123")

# 🔹 2. Buat Mata Pelajaran
mapel_list = ["Matematika", "Bahasa Indonesia", "IPA", "IPS", "Bahasa Inggris"]
mata_pelajaran_objs = [MataPelajaran.objects.create(nama=mapel) for mapel in mapel_list]

print("✅ Mata Pelajaran berhasil dibuat.")

# 🔹 3. Buat Tahun Ajaran
tahun_ajaran = TahunAjaran.objects.create(
    tahun_ajaran="2024/2025",
    mulai=date(2024, 7, 1),
    selesai=date(2025, 6, 30)
)

print("✅ Tahun Ajaran 2024/2025 berhasil dibuat.")

# 🔹 4. Buat Guru
guru = Guru.objects.create(
    user=user_guru,
    nama="Budi Santoso",
    nip="123456789",
    no_telepon="081234567890",
    alamat="Jl. Pendidikan No. 10"
)
guru.mata_pelajaran.set(mata_pelajaran_objs)  # Tambahkan mata pelajaran yang diajar

print("✅ Guru Budi Santoso berhasil dibuat.")

# 🔹 5. Buat Kelas
kelas = Kelas.objects.create(nama_kelas="Kelas 5A", wali_kelas=guru)

print("✅ Kelas 5A berhasil dibuat.")

# 🔹 6. Buat Siswa
siswa = Siswa.objects.create(
    nama="Ahmad Fauzan",
    nisn="987654321",
    tanggal_lahir=date(2013, 5, 20),
    jenis_kelamin="L",
    alamat="Jl. Merdeka No. 5",
    no_telepon="081234567891",
    kelas=kelas,
    tahun_masuk=2020,
    tahun_ajaran=tahun_ajaran,
    naik_kelas=False,
    nama_ayah="Samsul Hadi",
    nama_ibu="Rina Wati",
    no_telepon_ortu="081298765432"
)

print("✅ Siswa Ahmad Fauzan berhasil dibuat.")

# 🔹 7. Buat Wali Siswa
wali = Wali.objects.create(
    user=user_wali,
    nama="Samsul Hadi",
    no_telepon="081298765432",
    alamat="Jl. Merdeka No. 5"
)
wali.siswa.add(siswa)

print("✅ Wali Samsul Hadi berhasil dibuat.")

# 🔹 8. Buat Rapor Siswa
for mapel in mata_pelajaran_objs:
    Rapor.objects.create(
        siswa=siswa,
        mata_pelajaran=mapel,
        kelas=kelas,
        nilai=round(random.uniform(60, 100), 2),  # Nilai acak antara 60 dan 100
        semester="Ganjil",
        tahun_ajaran=tahun_ajaran
    )

print("✅ Rapor siswa Ahmad Fauzan berhasil dibuat.")

print("\n🎉 Semua data dummy berhasil dibuat!")
