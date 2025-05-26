from django.shortcuts import render, get_object_or_404, redirect
from .models import Siswa, Wali, MataPelajaran, Kelas, TahunAjaran, Rapor,Guru, User, StatusSiswaTahunAjaran, SemesterAktif
from .forms import SiswaForm, WaliForm, MataPelajaranForm, KelasForm, TahunAjaranForm, RaporForm,GuruForm, ResetPasswordForm
from django.contrib import messages
from django.db.models import Prefetch
from django.db import IntegrityError
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import Group
from .decorators import *
from django.contrib import messages
from .forms import CustomUserCreationForm
import os
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

#====AUTH=3

def user_add(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User berhasil ditambahkan.")
            return redirect('daftar_user')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'back/user/tambah_user.html', {'form': form})

def user_list(request):
    users = User.objects.all()
    return render(request, 'back/user/list_user.html', {'users': users})

# ========== VIEW UNTUK SISWA ==========
#@login_required
#@user_passes_test(is_admin)
def daftar_siswa(request):
    siswa_list = Siswa.objects.all()
    return render(request, 'back/rapor/siswa/siswa_list.html', {'siswa_list': siswa_list})

#@login_required
##@user_passes_test(is_admin)
def detail_siswa(request, siswa_id):
    siswa = get_object_or_404(Siswa, id=siswa_id)

    # Ambil input filter dari query param
    kelas_id = request.GET.get('kelas')
    tahun_ajaran_id = request.GET.get('tahun_ajaran')
    semester_id = request.GET.get('semester')

    # Ambil tahun ajaran aktif
    tahun_ajaran_aktif = TahunAjaran.objects.filter(aktif=True).first()

    # Tentukan nilai default jika query param kosong
    if not tahun_ajaran_id and tahun_ajaran_aktif:
        tahun_ajaran_id = str(tahun_ajaran_aktif.id)

    if not semester_id:
        semester_id = "Ganjil"  # ganti sesuai dengan konstanta enum kamu, misalnya "1"

    if not kelas_id and tahun_ajaran_id:
        # Ambil kelas berdasarkan tahun ajaran aktif
        status_aktif = siswa.status_tahun_ajaran.filter(tahun_ajaran_id=tahun_ajaran_id).first()
        if status_aktif:
            kelas_id = str(status_aktif.kelas_id)

    # Filter rapor berdasarkan parameter (baik dari default maupun query param)
    rapor_list = Rapor.objects.filter(siswa=siswa)

    if kelas_id:
        rapor_list = rapor_list.filter(kelas_id=kelas_id)
    if tahun_ajaran_id:
        rapor_list = rapor_list.filter(tahun_ajaran_id=tahun_ajaran_id)
    if semester_id:
        rapor_list = rapor_list.filter(semester=semester_id)

    return render(request, 'back/rapor/siswa/detail_siswa.html', {
        'siswa': siswa,
        'rapor_list': rapor_list,
        'kelas_list': Kelas.objects.all(),
        'daftar_tahun_ajaran_list': TahunAjaran.objects.all(),
        'semester_choices': Rapor.SEMESTER_CHOICES,
        'kelas_id': kelas_id,
        'tahun_ajaran_id': tahun_ajaran_id,
        'semester_id': semester_id,
    })


def update_kelas_siswa(request, siswa_id):
    siswa = get_object_or_404(Siswa, pk=siswa_id)

    if request.method == "POST":
        kelas_baru_id = request.POST.get("kelas_baru")
        tahun_ajaran_id = request.POST.get("tahun_ajaran")

        if not kelas_baru_id or not tahun_ajaran_id:
            messages.error(request, "Kelas dan Tahun Ajaran harus dipilih.")
            return redirect("detail_siswa", siswa_id=siswa.id)

        kelas_baru = get_object_or_404(Kelas, pk=kelas_baru_id)
        tahun_ajaran = get_object_or_404(TahunAjaran, pk=tahun_ajaran_id)

        # Cek apakah entri untuk tahun ajaran ini sudah ada
        status_obj, created = StatusSiswaTahunAjaran.objects.update_or_create(
            siswa=siswa,
            tahun_ajaran=tahun_ajaran,
            defaults={
                "kelas": kelas_baru,
                "status": "aktif"  # atau sesuaikan status jika ada pilihan lain
            }
        )

        if created:
            messages.success(request, f"Data kelas siswa {siswa.nama} berhasil ditambahkan untuk tahun ajaran {tahun_ajaran}.")
        else:
            messages.success(request, f"Data kelas siswa {siswa.nama} berhasil diperbarui untuk tahun ajaran {tahun_ajaran}.")

    return redirect("detail_siswa", siswa_id=siswa.id)

def hapus_status_siswa(request, status_id):
    status = get_object_or_404(StatusSiswaTahunAjaran, id=status_id)
    siswa_id = status.siswa.id
    if request.method == "POST":
        status.delete()
        messages.success(request, "Riwayat status berhasil dihapus.")
    return redirect('detail_siswa', siswa_id=siswa_id)

#@login_required
#@user_passes_test(is_admin)
def tambah_siswa(request):
    if request.method == "POST":
        form = SiswaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('daftar_siswa')
    else:
        form = SiswaForm()
    return render(request, 'back/rapor/siswa/tambah_siswa.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def edit_siswa(request, siswa_id):
    siswa = get_object_or_404(Siswa, id=siswa_id)
    old_foto_path = siswa.foto.path if siswa.foto else None

    if request.method == "POST":
        form = SiswaForm(request.POST, request.FILES, instance=siswa)
        if form.is_valid():
            # Cek apakah foto dihapus (clear)
            foto = form.cleaned_data.get('foto')
            if not foto and old_foto_path and os.path.isfile(old_foto_path):
                # Hapus file fisik foto lama
                os.remove(old_foto_path)

            form.save()
            messages.success(request, "Data Siswa berhasil diedit")
            return redirect('detail_siswa', siswa_id=siswa.id)
    else:
        form = SiswaForm(instance=siswa)

    return render(request, 'back/rapor/siswa/edit_siswa.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def hapus_siswa(request, siswa_id):
    siswa = get_object_or_404(Siswa, id=siswa_id)
    if request.method == "POST":
        # Hapus file foto dulu jika ada
        if siswa.foto and siswa.foto.path:
            import os
            if os.path.isfile(siswa.foto.path):
                os.remove(siswa.foto.path)
        siswa.delete()
        return redirect('daftar_siswa')
    return redirect('daftar_siswa')


def update_status_siswa(request, siswa_id):
    if request.method == 'POST':
        status_obj = get_object_or_404(StatusSiswaTahunAjaran, pk=siswa_id)
        status_baru = request.POST.get('status')
        if status_baru in dict(StatusSiswaTahunAjaran.STATUS_CHOICES):
            status_obj.status = status_baru
            status_obj.save()
            messages.success(request, f"Status siswa tahun ajaran {status_obj.tahun_ajaran} berhasil diupdate.")
        else:
            messages.error(request, "Status tidak valid.")
    return redirect('detail_siswa', siswa_id=status_obj.siswa.pk)


# ========== VIEW UNTUK WALI ==========
#@login_required
#@user_passes_test(is_admin)
def daftar_wali(request):
    wali_list = Wali.objects.all()
    
    return render(request, 'back/rapor/wali/daftar_wali.html', {'wali_list': wali_list})

#@login_required
#@user_passes_test(is_admin)

def tambah_wali(request):
    if request.method == "POST":
        form = WaliForm(request.POST)
        user_option = request.POST.get('user_option')

        if form.is_valid():
            wali = form.save(commit=False)

            if user_option == 'new':
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                if username and password:
                    user = User.objects.create_user(username=username, password=password)
                    group, _ = Group.objects.get_or_create(name='wali')
                    user.groups.add(group)
                    wali.user = user
                else:
                    messages.error(request, "Username dan password harus diisi untuk user baru.")
                    return render(request, 'back/rapor/wali/tambah_wali.html', {'form': form})
            elif user_option == 'existing':
                user = form.cleaned_data.get('user')
                if user:
                    wali.user = user  # **JANGAN LUPA SET USER DI SINI**
                else:
                    messages.error(request, "Pilih user yang sudah ada atau buat user baru.")
                    return render(request, 'back/rapor/wali/tambah_wali.html', {'form': form})

            wali.save()
            messages.success(request, "Data wali berhasil ditambahkan.")
            return redirect('daftar_wali')
        else:
            messages.error(request, "Formulir tidak valid.")
    else:
        form = WaliForm()

    return render(request, 'back/rapor/wali/tambah_wali.html', {'form': form})


#@login_required
#@user_passes_test(is_admin)
def edit_wali(request, wali_id):
    wali = get_object_or_404(Wali, pk=wali_id)
    if request.method == 'POST':
        form = WaliForm(request.POST, instance=wali)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data wali berhasil diperbarui.')
            return redirect('daftar_wali')
    else:
        form = WaliForm(instance=wali)

    return render(request, 'back/rapor/wali/edit_wali.html', {'form': form})


#@login_required
#@user_passes_test(is_admin)
def hapus_wali(request, wali_id):
    wali = get_object_or_404(Wali, id=wali_id)
    
    if request.method == "POST":
        hapus_user = request.POST.get('hapus_user') == 'true'
        
        if hapus_user and wali.user:
            # Hapus user terkait sebelum hapus wali
            wali.user.delete()
        else:
            # Jika tidak hapus user, cukup hapus wali saja
            wali.delete()

        messages.success(request, f"Wali '{wali.nama}' berhasil dihapus.")
        return redirect('daftar_wali')

    # Kalau ada GET request, bisa redirect atau tampilkan pesan error
    messages.error(request, "Metode request tidak valid.")
    return redirect('daftar_wali')


# ========== VIEW UNTUK MATA PELAJARAN ==========
#@login_required
#@user_passes_test(is_admin)
def daftar_mata_pelajaran(request):
    mapel_list = MataPelajaran.objects.all()
    return render(request, 'back/mapel/daftar_mapel.html', {'mapel_list': mapel_list})
#@login_required
#@user_passes_test(is_admin)
def tambah_mata_pelajaran(request):
    if request.method == "POST":
        form = MataPelajaranForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('daftar_mata_pelajaran')
    else:
        form = MataPelajaranForm()
    return render(request, 'back/mapel/tambah_mapel.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def edit_mata_pelajaran(request, mapel_id):
    mapel = get_object_or_404(MataPelajaran, id=mapel_id)
    if request.method == "POST":
        form = MataPelajaranForm(request.POST, instance=mapel)
        if form.is_valid():
            form.save()
            return redirect('daftar_mata_pelajaran')
    else:
        form = MataPelajaranForm(instance=mapel)
    return render(request, 'back/mapel/edit_mapel.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def hapus_mata_pelajaran(request, mapel_id):
    mapel = get_object_or_404(MataPelajaran, id=mapel_id)
    if request.method == "POST":
        mapel.delete()
        return redirect('daftar_mata_pelajaran')
    return render(request, 'mapel/hapus_mata_pelajaran.html', {'mapel': mapel})


# ========== VIEW UNTUK KELAS ==========
#@login_required
#@user_passes_test(is_admin)
def daftar_kelas(request):
    kelas_list = Kelas.objects.all()
    return render(request, 'back/kelas/daftar_kelas.html', {'kelas_list': kelas_list})

#@login_required
#@user_passes_test(is_admin)
def tambah_kelas(request):
    if request.method == "POST":
        form = KelasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil ditambah.")
            return redirect('daftar_kelas')
    else:
        form = KelasForm()
    return render(request, 'back/kelas/tambah_kelas.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def edit_kelas(request, kelas_id):
    kelas = get_object_or_404(Kelas, id=kelas_id)
    if request.method == "POST":
        form = KelasForm(request.POST, instance=kelas)
        if form.is_valid():
            form.save()
            return redirect('daftar_kelas')
    else:
        form = KelasForm(instance=kelas)
    return render(request, 'back/kelas/edit_kelas.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def hapus_kelas(request, kelas_id):
    kelas = get_object_or_404(Kelas, id=kelas_id)
    if request.method == "POST":
        kelas.delete()
        messages.success(request, "Data berhasil dihapus.")
        return redirect('daftar_kelas')
    return render(request, 'back/kelas/daftar_kelas.html', {'kelas': kelas})

#@login_required
#@user_passes_test(is_admin)
def detail_kelas(request, kelas_id):
    kelas = get_object_or_404(Kelas, id=kelas_id)
    siswa_list = kelas.siswa_set.all()  # Mengambil semua siswa yang terkait dengan kelas ini
    return render(request, 'back/kelas/detail_kelas.html', {'kelas': kelas, 'siswa_list': siswa_list})

# ========== VIEW UNTUK TAHUN AJARAN ==========
#@login_required
#@user_passes_test(is_admin)
def daftar_tahun_ajaran(request):
    tahun_ajaran_list = TahunAjaran.objects.all()
    return render(request, 'back/tahunajaran/tahun_list.html', {'tahun_ajaran_list': tahun_ajaran_list})

def set_tahun_ajaran_aktif(request, pk):
    if request.method == 'POST':
        tahun_ajaran_baru = get_object_or_404(TahunAjaran, pk=pk)
        
        # Set semua tahun ajaran jadi non aktif dulu
        TahunAjaran.objects.filter(aktif=True).update(aktif=False)
        
        # Set tahun ajaran yang dipilih jadi aktif
        tahun_ajaran_baru.aktif = True
        tahun_ajaran_baru.save()
        
        messages.success(request, f"Tahun ajaran {tahun_ajaran_baru.tahun_ajaran} berhasil dijadikan aktif.")
    
    return redirect('daftar_tahun_ajaran')  # Ganti dengan nama url daftar tahun ajaran kamu

#@login_required
#@user_passes_test(is_admin)
def tambah_tahun_ajaran(request):
    if request.method == "POST":
        form = TahunAjaranForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil ditambahkan.")
            return redirect('daftar_tahun_ajaran')
    else:
        form = TahunAjaranForm()
    return render(request, 'back/tahunajaran/tahun_tambah.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def edit_tahun_ajaran(request, tahun_ajaran_id):
    tahun_ajaran = get_object_or_404(TahunAjaran, id=tahun_ajaran_id)
    if request.method == "POST":
        form = TahunAjaranForm(request.POST, instance=tahun_ajaran)
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil diedit.")
            return redirect('daftar_tahun_ajaran')
    else:
        form = TahunAjaranForm(instance=tahun_ajaran)
    return render(request, 'back/tahunajaran/tahun_edit.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def hapus_tahun_ajaran(request, tahun_ajaran_id):
    tahun_ajaran = get_object_or_404(TahunAjaran, id=tahun_ajaran_id)
    if request.method == "POST":
        tahun_ajaran.delete()
        messages.success(request, "Data berhasil dihapus.")
        return redirect('daftar_tahun_ajaran')
    return render(request, 'back/tahunajaran/tahun_hapus.html', {'tahun_ajaran': tahun_ajaran})



def daftar_semester(request):
    semesters = SemesterAktif.objects.all()

    if request.method == 'POST':
        semester_id = request.POST.get('semester')
        if semester_id:
            SemesterAktif.objects.update(aktif=False)  # matikan semua dulu
            SemesterAktif.objects.filter(pk=semester_id).update(aktif=True)
            return redirect('set_semester_aktif')

    return render(request, 'back/semester/semester_list.html', {'semesters': semesters})

# ========== VIEW UNTUK Semester ==========

def tambah_semester(request):
    if request.method == 'POST':
        tahun_ajaran_id = request.POST.get('tahun_ajaran')
        nama_semester = request.POST.get('nama_semester')
        aktif = request.POST.get('aktif') == 'true'

        # Validasi input sederhana
        if not tahun_ajaran_id or not nama_semester:
            messages.error(request, "Tahun Ajaran dan Nama Semester wajib diisi.")
            return redirect('tambah_semester')

        tahun_ajaran = TahunAjaran.objects.filter(id=tahun_ajaran_id).first()
        if not tahun_ajaran:
            messages.error(request, "Tahun Ajaran tidak ditemukan.")
            return redirect('tambah_semester')

        # Jika checkbox aktif dicentang, nonaktifkan semester aktif lain di tahun ajaran yang sama
        if aktif:
            SemesterAktif.objects.filter(tahun_ajaran=tahun_ajaran, aktif=True).update(aktif=False)

        # Buat semester baru
        SemesterAktif.objects.create(
            tahun_ajaran=tahun_ajaran,
            nama_semester=nama_semester,
            aktif=aktif
        )
        messages.success(request, f'Semester "{nama_semester}" berhasil ditambahkan.')
        return redirect('daftar_semester')

    tahun_ajaran_list = TahunAjaran.objects.all().order_by('-mulai')
    return render(request, 'back/semester/semester_tambah.html', {'tahun_ajaran_list': tahun_ajaran_list})


# ========== VIEW UNTUK RAPOR ==========
#@login_required
#@user_passes_test(is_admin)
def daftar_rapor(request):
    # Ambil tahun ajaran aktif
    tahun_ajaran_aktif = TahunAjaran.objects.filter(aktif=True).first()

    # Ambil semua siswa dan prefetch rapor terkait (bisa filter rapor sesuai kebutuhan)
    siswa_list = Siswa.objects.all().prefetch_related(
        Prefetch('rapor_set', queryset=Rapor.objects.all())
    )

    # Tambahkan atribut semester_rapor di tiap siswa
    for siswa in siswa_list:
        semesters = siswa.rapor_set.values_list('semester', flat=True).distinct()
        siswa.semester_rapor = ", ".join(semesters) if semesters else "-"

    context = {
        'siswa_list': siswa_list,
        'tahun_ajaran_aktif': tahun_ajaran_aktif,
    }
    return render(request, 'back/rapor/report/raport_daftar.html', context)

def daftar_rapor_wali(request):
    # Ambil user saat ini
    user = request.user

    # Ambil objek Wali dari user
    wali = get_object_or_404(Wali, user=user)

    # Ambil tahun ajaran aktif
    tahun_ajaran_aktif = TahunAjaran.objects.filter(aktif=True).first()

    # Ambil siswa yang diwali oleh wali ini
    siswa_list = wali.siswa.all().prefetch_related(
        Prefetch('rapor_set', queryset=Rapor.objects.all())
    )

    # Tambahkan atribut semester_rapor di tiap siswa
    for siswa in siswa_list:
        semesters = siswa.rapor_set.values_list('semester', flat=True).distinct()
        siswa.semester_rapor = ", ".join(semesters) if semesters else "-"

    context = {
        'wali': wali,
        'siswa_list': siswa_list,
        'tahun_ajaran_aktif': tahun_ajaran_aktif,
    }
    return render(request, 'back/rapor/report/raport_daftar_wali.html', context)


#@login_required
#@user_passes_test(is_admin)
def tambah_rapor(request):
    if request.method == "POST":
        form = RaporForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('daftar_rapor')
    else:
        form = RaporForm()
    return render(request, 'rapor/tambah_rapor.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def edit_rapor(request, rapor_id):
    rapor = get_object_or_404(Rapor, id=rapor_id)
    if request.method == "POST":
        form = RaporForm(request.POST, instance=rapor)
        if form.is_valid():
            form.save()
            return redirect('daftar_rapor')
    else:
        form = RaporForm(instance=rapor)
    return render(request, 'rapor/edit_rapor.html', {'form': form})

#@login_required
#@user_passes_test(is_admin)
def hapus_rapor(request, rapor_id):
    rapor = get_object_or_404(Rapor, id=rapor_id)
    if request.method == "POST":
        rapor.delete()
        return redirect('daftar_rapor')
    return render(request, 'rapor/hapus_rapor.html', {'rapor': rapor})

def input_nilai(request, siswa_id):
    siswa = get_object_or_404(Siswa, id=siswa_id)
    mata_pelajaran_list = MataPelajaran.objects.all()
    
    # Ambil tahun ajaran yang aktif
    tahun_ajaran_aktif = TahunAjaran.objects.filter(aktif=True).first()
    
    # Pastikan tahun ajaran aktif tersedia
    if not tahun_ajaran_aktif:
        messages.error(request, "Tidak ada tahun ajaran yang aktif.")
        return redirect('daftar_rapor')

    # Ambil kelas terkini berdasarkan tahun ajaran aktif
    status = siswa.status_tahun_ajaran.filter(tahun_ajaran=tahun_ajaran_aktif).first()
    kelas_terkini = status.kelas if status else None

    if not kelas_terkini:
        messages.error(request, "Siswa belum memiliki kelas pada tahun ajaran aktif.")
        return redirect('daftar_rapor')

    if request.method == 'POST':
        semester = request.POST.get('semester')
        errors = []

        for mata_pelajaran in mata_pelajaran_list:
            nilai = request.POST.get(f'nilai_{mata_pelajaran.id}')
            if nilai:
                exists = Rapor.objects.filter(
                    siswa=siswa,
                    mata_pelajaran=mata_pelajaran,
                    kelas=kelas_terkini,
                    semester=semester,
                    tahun_ajaran=tahun_ajaran_aktif
                ).exists()

                if exists:
                    errors.append(f"Nilai untuk {mata_pelajaran.nama} sudah ada.")
                else:
                    Rapor.objects.create(
                        siswa=siswa,
                        mata_pelajaran=mata_pelajaran,
                        kelas=kelas_terkini,
                        nilai=nilai,
                        semester=semester,
                        tahun_ajaran=tahun_ajaran_aktif
                    )

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            messages.success(request, "Nilai berhasil disimpan.")
            return redirect('daftar_rapor')

    return render(request, 'back/rapor/report/inputnilai.html', {
        'siswa': siswa,
        'mata_pelajaran_list': mata_pelajaran_list,
        'tahun_ajaran_aktif': tahun_ajaran_aktif
    })
    
def edit_rapor(request, siswa_id):
    siswa = get_object_or_404(Siswa, id=siswa_id)
    rapor_list = Rapor.objects.filter(siswa=siswa)

    # Mengambil tahun ajaran aktif
    tahun_ajaran_aktif = TahunAjaran.objects.filter(mulai__lte=timezone.now(), selesai__gte=timezone.now()).first()

    if request.method == 'POST':
        semester = request.POST.get('semester')
        
        for rapor in rapor_list:
            nilai = request.POST.get(f'nilai_{rapor.mata_pelajaran.id}')
            if nilai:  # Jika nilai diisi
                rapor.nilai = nilai
                rapor.semester = semester
                rapor.save()

        return redirect('daftar_rapor')  # Mengarahkan ke halaman daftar rapor setelah berhasil

    return render(request, 'back/rapor/report/raport_edit.html', {
        'siswa': siswa,
        'rapor_list': rapor_list,
        'tahun_ajaran_aktif': tahun_ajaran_aktif
    })

def tabel_nilai_siswa(request, siswa_id):
    user = request.user
    is_wali = user.groups.filter(name='wali').exists()

    # Cek apakah user termasuk group 'wali'
    if user.groups.filter(name='wali').exists():
        # Jika wali, pastikan siswa yang diminta adalah anak didik wali tersebut
        # Ambil daftar siswa yang diawali oleh wali ini
        siswa_wali_ids = user.wali.siswa.values_list('id', flat=True)
        if int(siswa_id) not in siswa_wali_ids:
            # Jika siswa bukan anak didik wali, bisa lempar error 403 atau redirect
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Anda tidak memiliki akses ke data siswa ini.")

    siswa = get_object_or_404(Siswa, id=siswa_id)

    daftar_kelas = Kelas.objects.all()
    daftar_tahun_ajaran = TahunAjaran.objects.all()
    daftar_semester = Rapor.SEMESTER_CHOICES

    tahun_ajaran_aktif = TahunAjaran.objects.filter(aktif=True).first()

    kelas_id = request.GET.get('kelas') or (str(siswa.kelas_terkini.id) if siswa.kelas_terkini else None)
    tahun_ajaran_id = request.GET.get('tahun_ajaran') or (str(tahun_ajaran_aktif.id) if tahun_ajaran_aktif else None)
    semester = request.GET.get('semester') or 'Ganjil'

    rapor_list = Rapor.objects.filter(siswa=siswa)

    if kelas_id:
        rapor_list = rapor_list.filter(kelas_id=kelas_id)
    if tahun_ajaran_id:
        rapor_list = rapor_list.filter(tahun_ajaran_id=tahun_ajaran_id)
    if semester:
        rapor_list = rapor_list.filter(semester=semester)

    context = {
        'siswa': siswa,
        'rapor_list': rapor_list,
        'daftar_kelas': daftar_kelas,
        'daftar_tahun_ajaran': daftar_tahun_ajaran,
        'daftar_semester': daftar_semester,
        'kelas_id': kelas_id,
        'tahun_ajaran_id': tahun_ajaran_id,
        'semester': semester,
        'is_wali': is_wali,
    }

    return render(request, 'back/rapor/report/nilai.html', context)


# crud Guru
def guru_list(request):
    guru = Guru.objects.all()
    return render(request, 'back/guru/guru_list.html', {'guru': guru,'user': request.user,})

from django.contrib.auth.models import Group

def guru_create(request):
    if request.method == "POST":
        form = GuruForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                guru = form.save(commit=False)

                # Jika user baru dibuat di form
                user = guru.user
                if user:
                    # Pastikan group "guru" ada, kalau belum buat
                    group, created = Group.objects.get_or_create(name='guru')
                    # Tambahkan user ke group
                    user.groups.add(group)
                    user.save()

                guru.save()
                form.save_m2m()  # Simpan ManyToManyField

                messages.success(request, "Guru berhasil ditambahkan.")
                return redirect('guru_list')
            except Exception as e:
                messages.error(request, f"Gagal menyimpan data: {str(e)}")
        else:
            messages.error(request, "Terdapat kesalahan pada formulir. Periksa kembali.")

    else:
        form = GuruForm()

    return render(request, 'back/guru/guru_tambah.html', {
        'form': form
    })


    # Ambil daftar User dan Mata Pelajaran untuk dropdown
    users = User.objects.all()
    mata_pelajaran = MataPelajaran.objects.all()

    return render(request, 'back/guru/guru_tambah.html', {
        'form': form,
        'users': users,
        'mata_pelajaran': mata_pelajaran
    })

def guru_update(request, id):
    guru = get_object_or_404(Guru, pk=id)

    if request.method == 'POST':
        form = GuruForm(request.POST, request.FILES, instance=guru)
        if form.is_valid():
            form.instance.user = guru.user  # pastikan user tidak terganti
            form.save()
            messages.success(request, "Data guru berhasil diperbarui.")
            return redirect('guru_list')
    else:
        form = GuruForm(instance=guru)

    return render(request, 'back/guru/guru_edit.html', {
        'form': form
    })

def guru_reset_password(request, guru_id):
    guru = get_object_or_404(Guru, pk=guru_id)
    user = guru.user

    if request.method == 'POST':
        form = ResetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password berhasil di-reset.')
            return redirect('guru_update', guru.id)
    else:
        form = ResetPasswordForm(user)

    return render(request, 'back/guru/guru_reset_password.html', {
        'form': form,
        'guru': guru,
    })

def guru_delete(request, id):
    guru = get_object_or_404(Guru, id=id)
    hapus_user = request.POST.get('hapus_user_input') == '1'

    if hapus_user and guru.user:
        guru.user.delete()

    guru.delete()
    messages.success(request, 'Guru berhasil dihapus' + (' bersama akun user.' if hapus_user else '.'))
    return redirect('guru_list')

def guru_detail(request, id):
    guru = get_object_or_404(Guru, id=id)
    return render(request, 'back/guru/guru_details.html', {'guru': guru})


#dashboard
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            # Set grup pengguna ke dalam session
            groups = user.groups.values_list('name', flat=True)
            if groups:
                request.session['user_group'] = groups[0]  # Ambil grup pertama jika ada lebih dari satu
            else:
                request.session['user_group'] = None  # Atau nilai default lainnya

            # Redirect ke next_url jika ada
            if next_url:
                return redirect(next_url)

            # Cek grup dan redirect ke dashboard yang sesuai
            if user.groups.filter(name='admin').exists():
                return redirect('dashboard')
            elif user.groups.filter(name='guru').exists():
                return redirect('dashboard_guru')
            elif user.groups.filter(name='wali').exists():
                return redirect('dashboard_walimurid')
            else:
                return redirect('dashboard')  # default kalau grup tidak dikenali
        else:
            error = 'Username atau password salah'
            return render(request, 'gate/login.html', {'error': error})
    else:
        return render(request, 'gate/login.html')
#dashboard
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_siswa = Siswa.objects.count()
    total_kelas = Kelas.objects.count()
    total_mata_pelajaran = MataPelajaran.objects.count()
    total_wali = Wali.objects.count()

    tahun_ajaran_aktif = TahunAjaran.objects.filter(aktif=True).first()


    # Ambil 5 siswa terbaru, misalnya urut berdasarkan id descending
    siswa_terbaru = Siswa.objects.order_by('-id')[:5]

    context = {
        'total_siswa': total_siswa,
        'total_kelas': total_kelas,
        'total_mapel': total_mata_pelajaran,
        'total_wali': total_wali,
        'tahun_ajaran_aktif': tahun_ajaran_aktif,
        'siswa_terbaru': siswa_terbaru,
        'user': request.user,
    }

    return render(request, 'back/dashboard.html', context)


#dashboard guru
def dashboard_guru(request):
    guru = get_object_or_404(Guru, user=request.user)  
    return render(request, 'front/guru/dashboard_guru.html', {'guru': guru})


#dashboord wali kelas
#@login_required
def dashboard_walikelas(request):
    return render(request, 'front/walikelas/dashboard_walikelas.html', {})
# dashboard wali murid
def dashboard_walimurid(request):
    wali = get_object_or_404(Wali, user=request.user)
    anak_list = wali.siswa.all()  # Ambil semua siswa yang diasuh oleh wali ini

    return render(request, 'front/walimurid/dashboard_walimurid.html', {
        'wali': wali,
        'anak_list': anak_list
    })

#fitur guru only

# Fungsi untuk input nilai
#@login_required
def input_nilai_guru(request):
    # Cari objek Guru berdasarkan user yang login
    guru = Guru.objects.filter(user=request.user).first()

    # Pastikan user adalah seorang guru
    if not guru:
        messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect('dashboard_guru')

    # Ambil semua mata pelajaran yang diajar oleh guru ini
    mata_pelajaran_list = guru.mata_pelajaran.all()

    # Ambil semua kelas yang ada
    kelas_list = guru.kelas_wali.all()

    # Ambil semua tahun ajaran
    tahun_ajaran_list = TahunAjaran.objects.all()

    # Cek jika ada filter yang dipilih
    kelas_terpilih = request.GET.get('kelas')
    semester_terpilih = request.GET.get('semester')

    siswa_list = None
    if kelas_terpilih and semester_terpilih:
        # Ambil semua siswa dalam kelas tersebut
        tahun_ajaran_aktif = TahunAjaran.objects.filter(aktif=True).first()

        siswa_list = Siswa.objects.filter(
            status_tahun_ajaran__kelas_id=kelas_terpilih,
            status_tahun_ajaran__tahun_ajaran=tahun_ajaran_aktif
        ).distinct()

    # Handle form input nilai
    if request.method == 'POST':
        siswa_id = request.POST.get('siswa_id')
        mata_pelajaran_id = request.POST.get('mata_pelajaran')
        nilai = request.POST.get('nilai')
        tahun_ajaran_id = request.POST.get('tahun_ajaran')

        siswa = get_object_or_404(Siswa, id=siswa_id)
        mata_pelajaran = get_object_or_404(MataPelajaran, id=mata_pelajaran_id)
        tahun_ajaran = get_object_or_404(TahunAjaran, id=tahun_ajaran_id)

        # Simpan nilai
        Rapor.objects.create(
            siswa=siswa,
            mata_pelajaran=mata_pelajaran,
            kelas=siswa.kelas_terkini,
            nilai=nilai,
            semester=semester_terpilih,
            tahun_ajaran=tahun_ajaran
        )

        messages.success(request, f"Nilai untuk {siswa.nama} berhasil ditambahkan!")
        return redirect('input_nilai_guru')

    context = {
        'guru': guru,
        'mata_pelajaran_list': mata_pelajaran_list,
        'kelas_list': kelas_list,
        'siswa_list': siswa_list,
        'kelas_terpilih': kelas_terpilih,
        'semester_terpilih': semester_terpilih,
        'tahun_ajaran_list': tahun_ajaran_list,  # Kirimkan tahun ajaran ke template
    }

    return render(request, 'front/guru/input_nilai.html', context)
#@login_required
def input_nilai_per_siswa(request, siswa_id):
    siswa = get_object_or_404(Siswa, id=siswa_id)
    guru = get_object_or_404(Guru, user=request.user)
    mata_pelajaran_list = guru.mata_pelajaran.all()
    tahun_ajaran_aktif = TahunAjaran.objects.filter(aktif=True).first()
    error_message = None

    if request.method == 'POST':
        mata_pelajaran_id = request.POST.get('mata_pelajaran')
        nilai = request.POST.get('nilai')
        tahun_ajaran_id = request.POST.get('tahun_ajaran')
        semester = request.POST.get('semester')

        mata_pelajaran = get_object_or_404(MataPelajaran, id=mata_pelajaran_id)
        tahun_ajaran = get_object_or_404(TahunAjaran, id=tahun_ajaran_id)

        try:
            Rapor.objects.create(
                siswa=siswa,
                mata_pelajaran=mata_pelajaran,
                kelas=siswa.kelas_terkini,
                nilai=nilai,
                semester=semester,
                tahun_ajaran=tahun_ajaran
            )
            messages.success(request, f"Nilai untuk {siswa.nama} untuk mapel {mata_pelajaran} berhasil ditambahkan!")
            return redirect('input_nilai_per_siswa', siswa_id=siswa.id)
        except IntegrityError:
            error_message = "Nilai untuk mata pelajaran ini pada semester dan tahun ajaran tersebut sudah ada."

    return render(request, 'front/guru/input_nilai_per_siswa.html', {
        'siswa': siswa,
        'mata_pelajaran_list': mata_pelajaran_list,
        'kelas': siswa.kelas_terkini,
        'tahun_ajaran_list': TahunAjaran.objects.filter(aktif=True),
        'error_message': error_message,
    })
    
#@login_required
def naik_kelas(request, siswa_id):
    siswa = get_object_or_404(Siswa, id=siswa_id)

    # Pastikan siswa yang akan dinaikkan kelasnya adalah siswa dalam kelas yang diampu oleh wali kelas
    if siswa.kelas.wali_kelas.user != request.user:
        return redirect('dashboard_walikelas')  # Redireksi jika bukan wali kelas

    # Naikkan kelas siswa
    siswa.naik_kelas_manual()

    # Redirect ke halaman detail kelas
    return redirect('detail_kelas_wali', kelas_id=siswa.kelas.id)

#@login_required     
def naik_kelas_batch(request, kelas_id):
    # Ambil kelas berdasarkan ID
    kelas = get_object_or_404(Kelas, id=kelas_id)

    # Pastikan guru yang sedang login adalah wali kelas dari kelas ini
    if kelas.wali_kelas.user != request.user:
        return redirect('dashboard_walikelas')  # Redireksi jika bukan wali kelas

    # Ambil semua siswa dalam kelas
    siswa_list = Siswa.objects.filter(kelas=kelas)

    # Naikkan kelas untuk semua siswa
    for siswa in siswa_list:
        siswa.naik_kelas_manual()

    # Redirect ke halaman detail kelas
    return redirect('detail_kelas_wali', kelas_id=kelas.id)

#@login_required
def detail_kelas_wali (request, kelas_id):
    # Ambil kelas berdasarkan ID
    kelas = get_object_or_404(Kelas, id=kelas_id)

    # Pastikan guru yang sedang login adalah wali kelas dari kelas ini
    if kelas.wali_kelas.user != request.user:
        return redirect('dashboard_walikelas')  # Redireksi jika bukan wali kelas

    # Ambil siswa yang ada dalam kelas
    siswa_list = Siswa.objects.filter(kelas=kelas)

    return render(request, 'front/walikelas/detail_kelas.html', {
        'kelas': kelas,
        'siswa_list': siswa_list,
    })
