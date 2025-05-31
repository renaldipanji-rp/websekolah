from django.db import models
from django.contrib.auth.models import User

# Model Tahun Ajaran
class TahunAjaran(models.Model):
    tahun_ajaran = models.CharField(max_length=20)
    mulai = models.DateField()
    selesai = models.DateField()
    aktif = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.aktif:
            TahunAjaran.objects.exclude(pk=self.pk).update(aktif=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tahun_ajaran

# Model Semester Aktif (menggabungkan semester dan tahun ajaran)
class SemesterAktif(models.Model):
    SEMESTER_CHOICES = [
        ('Ganjil', 'Ganjil'),
        ('Genap', 'Genap'),
    ]

    tahun_ajaran = models.ForeignKey(TahunAjaran, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    aktif = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.aktif:
            SemesterAktif.objects.exclude(pk=self.pk).update(aktif=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tahun_ajaran} - {self.semester}"

    class Meta:
        verbose_name = "Semester Aktif"
        verbose_name_plural = "Semester Aktif"

# Model Mata Pelajaran
class MataPelajaran(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

# Model Guru
class Guru(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nama = models.CharField(max_length=100)
    nip = models.CharField(max_length=20, unique=True)
    no_telepon = models.CharField(max_length=15)
    alamat = models.TextField()
    foto_profil = models.ImageField(upload_to='guru_foto/', blank=True, null=True)
    mata_pelajaran = models.ManyToManyField(MataPelajaran, related_name='guru')

    def __str__(self):
        return self.nama

# Model Kelas
class Kelas(models.Model):
    nama_kelas = models.CharField(max_length=50)
    wali_kelas = models.ForeignKey(Guru, on_delete=models.SET_NULL, null=True, blank=True, related_name='kelas_wali')

    def __str__(self):
        return self.nama_kelas

# Model Siswa
class Siswa(models.Model):
    GENDER_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    nama = models.CharField(max_length=100)
    nisn = models.CharField(max_length=20, unique=True)
    tanggal_lahir = models.DateField()
    jenis_kelamin = models.CharField(max_length=1, choices=GENDER_CHOICES)
    alamat = models.TextField()
    no_telepon = models.CharField(max_length=15, blank=True, null=True)
    foto = models.ImageField(upload_to='foto_siswa/', blank=True, null=True)
    tahun_masuk = models.PositiveIntegerField()

    # Data Orang Tua
    nama_ayah = models.CharField(max_length=100, blank=True, null=True)
    nama_ibu = models.CharField(max_length=100, blank=True, null=True)
    no_telepon_ortu = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nama

    @property
    def kelas_terkini(self):
        status = self.status_tahun_ajaran.filter(tahun_ajaran__aktif=True).first()
        return status.kelas if status else None

    def status_terkini(self):
        return self.status_tahun_ajaran.order_by('-tahun_ajaran__mulai').first()

    def get_semester_terkini(self):
        semester_aktif = SemesterAktif.objects.filter(aktif=True).first()
        if not semester_aktif:
            return None
        return semester_aktif.semester

    class Meta:
        verbose_name = "Siswa"
        verbose_name_plural = "Data Siswa"

# Model Wali
class Wali(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)
    no_telepon = models.CharField(max_length=15)
    alamat = models.TextField()
    siswa = models.ManyToManyField(Siswa, related_name='wali')

    def __str__(self):
        return self.nama

# Model untuk menyimpan status siswa tiap tahun ajaran
class StatusSiswaTahunAjaran(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('naik', 'Naik Kelas'),
        ('tinggal', 'Tinggal Kelas'),
        ('lulus', 'Lulus'),
        ('keluar', 'Keluar'),
    ]
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name="status_tahun_ajaran")
    tahun_ajaran = models.ForeignKey(TahunAjaran, on_delete=models.CASCADE)
    kelas = models.ForeignKey(Kelas, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aktif')

    class Meta:
        unique_together = ('siswa', 'tahun_ajaran')

# Model Rapor
class Rapor(models.Model):
    SEMESTER_CHOICES = [
        ('Ganjil', 'Ganjil'),
        ('Genap', 'Genap'),
    ]

    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    mata_pelajaran = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE)
    nilai = models.DecimalField(max_digits=5, decimal_places=2)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    tahun_ajaran = models.ForeignKey(TahunAjaran, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('siswa', 'mata_pelajaran', 'kelas', 'semester', 'tahun_ajaran')

    def __str__(self):
        return f"{self.siswa.nama} - {self.mata_pelajaran.nama} - {self.nilai} - {self.kelas.nama_kelas}"

class Blog(models.Model):
    judul = models.CharField(max_length=200)
    isi = models.TextField()
    penulis = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    gambar = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    tanggal_diperbarui = models.DateTimeField(auto_now=True)
    publish = models.BooleanField(default=True)

    class Meta:
        ordering = ['-tanggal_dibuat']

    def __str__(self):
        return self.judul