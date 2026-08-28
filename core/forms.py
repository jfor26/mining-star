from django import forms

from .models import Cliente, Empleado


# =========================================
# FORMULARIO CLIENTES
# =========================================

class ClienteForm(forms.ModelForm):

    class Meta:

        model = Cliente

        fields = [
            "documento",
            "nombre",
            "correo",
            "telefono",
            "empresa",
        ]

        widgets = {

            "documento": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Documento"
            }),

            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre completo"
            }),

            "correo": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Correo electrónico"
            }),

            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono"
            }),

            "empresa": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Empresa"
            }),

        }


# =========================================
# FORMULARIO EMPLEADOS
# =========================================

class EmpleadoForm(forms.ModelForm):

    class Meta:

        model = Empleado

        fields = "__all__"

        widgets = {

            "documento": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Documento"
            }),

            "nombres": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombres"
            }),

            "apellidos": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Apellidos"
            }),

            "correo": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Correo electrónico"
            }),

            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono"
            }),

            "cargo": forms.Select(attrs={
                "class": "form-control"
            }),

            "area": forms.Select(attrs={
                "class": "form-control"
            }),

            "estado": forms.Select(attrs={
                "class": "form-control"
            }),

        }