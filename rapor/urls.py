from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # Login
    path('', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('users/add/', views.user_add, name='tambah_user'),
    path('users/', views.user_list, name='daftar_user'),


    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/guru', views.dashboard_guru, name='dashboard_guru'),
    path('dashboard/walikelas', views.dashboard_walikelas, name='dashboard_walikelas'),
    path('dashboard/walimurid', views.dashboard_walimurid, name='dashboard_walimurid'),

    # Siswa
    path('siswa/', views.daftar_siswa, name='daftar_siswa'),
    path('siswa/tambah/', views.tambah_siswa, name='tambah_siswa'),
    path('siswa/<int:siswa_id>/', views.detail_siswa, name='detail_siswa'),
    path('siswa/<int:siswa_id>/edit/', views.edit_siswa, name='edit_siswa'),
    path('siswa/<int:siswa_id>/hapus/', views.hapus_siswa, name='hapus_siswa'),
    path('siswa/<int:siswa_id>/update-kelas/', views.update_kelas_siswa, name='update_kelas_siswa'),
    path('status-siswa/<int:siswa_id>/update/', views.update_status_siswa, name='update_status_siswa'),
    path('status/<int:status_id>/hapus/', views.hapus_status_siswa, name='hapus_status_siswa'),

    # Wali Siswa
    path('wali/', views.daftar_wali, name='daftar_wali'),
    path('wali/tambah/', views.tambah_wali, name='tambah_wali'),
    path('wali/<int:wali_id>/edit/', views.edit_wali, name='edit_wali'),
    path('wali/hapus/<int:wali_id>/', views.hapus_wali, name='hapus_wali'),

    # Mata Pelajaran
    path('mapel/', views.daftar_mata_pelajaran, name='daftar_mata_pelajaran'),
    path('mapel/tambah/', views.tambah_mata_pelajaran, name='tambah_mata_pelajaran'),
    path('mapel/<int:mapel_id>/edit/', views.edit_mata_pelajaran, name='edit_mata_pelajaran'),
    path('mapel/<int:mapel_id>/hapus/', views.hapus_mata_pelajaran, name='hapus_mata_pelajaran'),

    # Kelas
    path('kelas/', views.daftar_kelas, name='daftar_kelas'),
    path('kelas/tambah/', views.tambah_kelas, name='tambah_kelas'),
    path('kelas/edit/<int:kelas_id>/', views.edit_kelas, name='edit_kelas'),
    path('kelas/hapus/<int:kelas_id>/', views.hapus_kelas, name='hapus_kelas'),
    path('kelas/detail/<int:kelas_id>/', views.detail_kelas, name='detail_kelas'),

    # Tahun Ajaran
    path('tahun_ajaran/', views.daftar_tahun_ajaran, name='daftar_tahun_ajaran'),
    path('tahun_ajaran/tambah/', views.tambah_tahun_ajaran, name='tambah_tahun_ajaran'),
    path('tahun_ajaran/<int:tahun_ajaran_id>/edit/', views.edit_tahun_ajaran, name='edit_tahun_ajaran'),
    path('tahun_ajaran/<int:tahun_ajaran_id>/hapus/', views.hapus_tahun_ajaran, name='hapus_tahun_ajaran'),
    path('tahun-ajaran/<int:pk>/set-aktif/', views.set_tahun_ajaran_aktif, name='set_tahun_ajaran_aktif'),
    
    # Semester
    path('semester/list/', views.daftar_semester, name='daftar_semester'),
    # path('semester/<int:semester_id>/aktifkan/', views.set_semester_aktif, name='set_semester_aktif'),
    path('semester/tambah/', views.tambah_semester, name='tambah_semester'),  # ini untuk tambah semester

    # Rapor (Nilai Siswa)
    path('rapor/wali/', views.daftar_rapor_wali, name='daftar_rapor_wali'),
    path('rapor/', views.daftar_rapor, name='daftar_rapor'),
    path('rapor/tambah/', views.tambah_rapor, name='tambah_rapor'),
    path('rapor/<int:rapor_id>/edit/', views.edit_rapor, name='edit_rapor'),
    path('rapor/<int:rapor_id>/hapus/', views.hapus_rapor, name='hapus_rapor'),
    path('rapor/input_nilai/<int:siswa_id>/', views.input_nilai, name='input_nilai'),
    path('edit_rapor/<int:siswa_id>/', views.edit_rapor, name='edit_rapor'),
    path('rapor/nilai_siswa/<int:siswa_id>/', views.tabel_nilai_siswa, name='tabel_nilai_siswa'),

    # Guru
    path('guru/', views.guru_list, name='guru_list'),
    path('guru/<int:id>/', views.guru_detail, name='guru_detail'),
    path('guru/tambah/', views.guru_create, name='guru_create'),
    path('guru/edit/<int:id>/', views.guru_update, name='guru_update'),
    path('guru/reset-password/<int:guru_id>/', views.guru_reset_password, name='guru_reset_password'),
    path('guru/hapus/<int:id>/', views.guru_delete, name='guru_delete'),

    # Input Nilai Guru (CRUD)
    path('guru/input-nilai/', views.input_nilai_guru, name='input_nilai_guru'),
    path('guru/input-nilai/<int:siswa_id>/', views.input_nilai_per_siswa, name='input_nilai_per_siswa'),

    #wali only
    path('wali-kelas/kelas_wali/<int:kelas_id>/', views.detail_kelas_wali, name='detail_kelas_wali'),
    path('wali-kelas/naik-kelas/<int:siswa_id>/', views.naik_kelas, name='naik_kelas'),
   path('wali-kelas/naik-kelas-batch/<int:kelas_id>/', views.naik_kelas_batch, name='naik_kelas_batch'),

    path('daftar-blog', views.daftar_blog, name='daftar_blog'),
    path('blogs/', views.list_blog, name='list_blog'),
    path('blog/detail/<int:pk>/', views.detail_blog, name='detail_blog'),
    path('blog/tambah/', views.tambah_blog, name='tambah_blog'),
    path('blog/edit/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('blog/hapus/<int:pk>/', views.hapus_blog, name='hapus_blog'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
