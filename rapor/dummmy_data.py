import random
from faker import Faker
from django.contrib.auth.models import User
from rapor.models import Guru, Siswa, Wali, MataPelajaran, Kelas, TahunAjaran, Rapor, StatusSiswaTahunAjaran

fake = Faker('id_ID')

# Hapus data lama (opsional)
User.objects.filter(username__startswith="guru").delete()
User.objects.filter(username__startswith="wali_").delete()
Guru.objects.all().delete()
Siswa.objects.all().delete()
Wali.objects.all().delete()
MataPelajaran.objects.all().delete()
Kelas.objects.all().delete()
TahunAjaran.objects.all().delete()
StatusSiswaTahunAjaran.objects.all().delete()
Rapor.objects.all().delete()

# Buat Mata Pelajaran
mata_pelajaran_list = []
for nama in ['Matematika', 'Bahasa Indonesia', 'IPA', 'IPS', 'Bahasa Inggris']:
    mata_pelajaran, _ = MataPelajaran.objects.get_or_create(nama=nama)
    mata_pelajaran_list.append(mata_pelajaran)

# Buat Tahun Ajaran (aktif)
tahun_ajaran, _ = TahunAjaran.objects.get_or_create(
    tahun_ajaran="2024/2025",
    defaults={"mulai": "2024-07-01", "selesai": "2025-06-30", "aktif": True}
)

# Buat Guru dan User
guru_list = []
for i in range(10):
    username = f"guru{i}"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("password123")
        user.save()

    guru = Guru.objects.create(
        user=user,
        nama=fake.name(),
        nip=fake.unique.numerify("##########"),
        no_telepon=fake.phone_number(),
        alamat=fake.address()
    )
    guru.mata_pelajaran.set(random.sample(mata_pelajaran_list, k=random.randint(1, 3)))
    guru_list.append(guru)

# Buat Kelas dari 1A sampai 6B dengan wali kelas random
kelas_list = []
for i in range(1, 7):  # Kelas 1 - 6
    for section in ['A', 'B']:
        kelas = Kelas.objects.create(
            nama_kelas=f"Kelas {i}{section}",
            wali_kelas=random.choice(guru_list)
        )
        kelas_list.append(kelas)

# Buat Siswa
siswa_list = []
for _ in range(60):
    siswa = Siswa.objects.create(
        nama=fake.name(),
        nisn=fake.unique.numerify("##########"),
        tanggal_lahir=fake.date_of_birth(minimum_age=6, maximum_age=12),
        jenis_kelamin=random.choice(['L', 'P']),
        alamat=fake.address(),
        no_telepon=fake.phone_number(),
        tahun_masuk=2024,
        nama_ayah=fake.name(),
        nama_ibu=fake.name(),
        no_telepon_ortu=fake.phone_number()
    )
    siswa_list.append(siswa)

# Set StatusSiswaTahunAjaran untuk setiap siswa (hubungkan ke kelas dan tahun ajaran)
for siswa in siswa_list:
    kelas = random.choice(kelas_list)
    status_choices = ['aktif', 'naik', 'tinggal', 'lulus', 'keluar']
    status = random.choice(status_choices)
    StatusSiswaTahunAjaran.objects.create(
        siswa=siswa,
        tahun_ajaran=tahun_ajaran,
        kelas=kelas,
        status=status
    )

# Buat Wali dan User untuk setiap siswa
for siswa in siswa_list:
    username = f"wali_{siswa.nisn}"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("password123")
        user.save()

    wali = Wali.objects.create(
        user=user,
        nama=fake.name(),  # biasanya nama wali, kalau mau pakai nama ayah, bisa juga siswa.nama_ayah
        no_telepon=fake.phone_number(),
        alamat=fake.address()
    )
    wali.siswa.add(siswa)

# Buat Rapor dengan nilai acak untuk setiap siswa, mata pelajaran, semester
for siswa in siswa_list:
    # Cari status siswa terbaru untuk ambil kelasnya
    status = StatusSiswaTahunAjaran.objects.filter(siswa=siswa, tahun_ajaran=tahun_ajaran).first()
    if not status or not status.kelas:
        continue

    for mata_pelajaran in mata_pelajaran_list:
        for semester in ["Ganjil", "Genap"]:
            Rapor.objects.create(
                siswa=siswa,
                mata_pelajaran=mata_pelajaran,
                kelas=status.kelas,
                nilai=round(random.uniform(50, 100), 2),
                semester=semester,
                tahun_ajaran=tahun_ajaran
            )

print("Data dummy berhasil dibuat!")