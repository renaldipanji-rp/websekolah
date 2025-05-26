from django import forms
from .models import Siswa, Wali, MataPelajaran, Kelas, TahunAjaran, Rapor, Guru
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth.forms import SetPasswordForm

# Fungsi untuk menambahkan class Bootstrap ke setiap field
#sori hardcode wwkwkwk
def apply_bootstrap(form):
    for field_name, field in form.fields.items():
        if isinstance(field.widget, forms.CheckboxInput) or isinstance(field.widget, forms.RadioSelect):
            field.widget.attrs.update({"class": "form-check-input"})
        elif isinstance(field.widget, forms.Textarea):
            field.widget.attrs.update({"class": "form-control", "rows": "4"})
        else:
            field.widget.attrs.update({"class": "form-control"})


class CustomUserCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Role/Group",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2', 'group']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)

        # Tambahan agar password field tetap punya class form-control
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            group = self.cleaned_data['group']
            user.groups.add(group)
        return user

# Form untuk Siswa
class SiswaForm(forms.ModelForm):
    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    jenis_kelamin = forms.ChoiceField(choices=JENIS_KELAMIN_CHOICES, widget=forms.Select())

    class Meta:
        model = Siswa
        fields = [
            "nisn", "nama", "tanggal_lahir", "jenis_kelamin", "alamat", "no_telepon",
            "foto", "tahun_masuk",
            "nama_ayah", "nama_ibu", "no_telepon_ortu"
        ]
        widgets = {
            "tanggal_lahir": forms.DateInput(attrs={"type": "date"}),
            "alamat": forms.Textarea(attrs={"rows": 3}),
            "foto": forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)

# Form untuk Wali
class WaliForm(forms.ModelForm):
    # field untuk buat user baru
    username = forms.CharField(required=False, label="Username (untuk user baru)")
    password = forms.CharField(widget=forms.PasswordInput(), required=False, label="Password (untuk user baru)")
    
    # field untuk pilih user existing, bisa kamu tambahkan secara manual
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, label="Pilih User yang sudah ada")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
        
        if self.instance and self.instance.pk:
            self.fields['siswa'].initial = self.instance.siswa.all()

    
    class Meta:
        model = Wali
        fields = ['nama', 'no_telepon', 'alamat', 'siswa']  # Jangan masukkan 'user' di sini, sudah manual di atas

# Form untuk Mata Pelajaran
class MataPelajaranForm(forms.ModelForm):
    class Meta:
        model = MataPelajaran
        fields = ["nama"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)

# Form untuk Kelas
class KelasForm(forms.ModelForm):
    class Meta:
        model = Kelas
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)

# Form untuk Tahun Ajaran
class TahunAjaranForm(forms.ModelForm):
    class Meta:
        model = TahunAjaran
        fields = '__all__'
        widgets = {
            'mulai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'selesai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tambahkan bootstrap class ke field lainnya
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.DateInput):  # agar tidak dobel class
                field.widget.attrs.update({'class': 'form-control'})

# Form untuk Rapor
class RaporForm(forms.ModelForm):
    class Meta:
        model = Rapor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)

# Form untuk Guru
class GuruForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150, required=False, label="Username Baru",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), required=False, label="Password Baru"
    )

    class Meta:
        model = Guru
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)

            # Disable field 'user' saat edit (instance sudah ada di database)
        if self.instance and self.instance.pk:
            self.fields['user'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = cleaned_data.get("user")

        if username and password and user:
            raise forms.ValidationError("Pilih user dari daftar atau buat user baru, jangan keduanya.")

        if not user and not (username and password):
            raise forms.ValidationError("Silakan pilih user yang sudah ada atau buat user baru.")

        return cleaned_data

    def save(self, commit=True):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            if User.objects.filter(username=username).exists():
                raise ValidationError("Username sudah digunakan. Gunakan username lain.")

            user = User.objects.create_user(username=username, password=password)
            self.instance.user = user

        return super().save(commit)

class ResetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})