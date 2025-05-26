from django.contrib import admin
from .models import (
    TahunAjaran, MataPelajaran, Guru, Kelas, Siswa, Wali,
    StatusSiswaTahunAjaran, Rapor, SemesterAktif
)

@admin.register(TahunAjaran)
class TahunAjaranAdmin(admin.ModelAdmin):
    list_display = ('tahun_ajaran', 'mulai', 'selesai', 'aktif')
    list_filter = ('aktif',)
    search_fields = ('tahun_ajaran',)
    ordering = ('-mulai',)

@admin.register(MataPelajaran)
class MataPelajaranAdmin(admin.ModelAdmin):
    search_fields = ('nama',)

@admin.register(Guru)
class GuruAdmin(admin.ModelAdmin):
    list_display = ('nama', 'nip', 'no_telepon')
    search_fields = ('nama', 'nip')
    filter_horizontal = ('mata_pelajaran',)

@admin.register(Kelas)
class KelasAdmin(admin.ModelAdmin):
    list_display = ('nama_kelas', 'wali_kelas')
    search_fields = ('nama_kelas',)
    raw_id_fields = ('wali_kelas',)

@admin.register(Siswa)
class SiswaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'nisn', 'jenis_kelamin', 'tahun_masuk', 'kelas_terkini')
    list_filter = ('jenis_kelamin', 'tahun_masuk')
    search_fields = ('nama', 'nisn')
    readonly_fields = ('kelas_terkini',)

    def kelas_terkini(self, obj):
        status = obj.status_tahun_ajaran.filter(tahun_ajaran__aktif=True).first()
        return status.kelas if status else '-'
    kelas_terkini.short_description = 'Kelas Terkini'

@admin.register(Wali)
class WaliAdmin(admin.ModelAdmin):
    list_display = ('nama', 'no_telepon')
    search_fields = ('nama',)
    filter_horizontal = ('siswa',)

@admin.register(StatusSiswaTahunAjaran)
class StatusSiswaTahunAjaranAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'tahun_ajaran', 'kelas', 'status')
    list_filter = ('tahun_ajaran', 'status', 'kelas')
    search_fields = ('siswa__nama',)

@admin.register(Rapor)
class RaporAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'mata_pelajaran', 'kelas', 'nilai', 'semester', 'tahun_ajaran')
    list_filter = ('semester', 'tahun_ajaran', 'kelas')
    search_fields = ('siswa__nama', 'mata_pelajaran__nama')
    ordering = ('-tahun_ajaran', 'siswa')

@admin.register(SemesterAktif)
class SemesterAktifAdmin(admin.ModelAdmin):
    list_display = ('semester', 'aktif')
    list_filter = ('aktif',)



