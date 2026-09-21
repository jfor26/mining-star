"""
Formularios de Mining Star.

Un ModelForm valida los datos ANTES de tocar la base de datos: tipos,
longitudes, unicidad, formato de correo. Es lo que evita los errores 500
por IntegrityError y los datos basura que entran con request.POST.get().
"""

from django import forms

from .models import Cliente, Empleado, Producto, Proveedor, RegistroProduccion

# Clases CSS reutilizadas por todos los widgets.
INPUT = {"class": "form-control"}
SELECT = {"class": "form-control"}


# =========================================================
# CLIENTES
# =========================================================

class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ["documento", "nombre", "correo", "telefono", "empresa"]
        widgets = {
            "documento": forms.TextInput({**INPUT, "placeholder": "Documento"}),
            "nombre": forms.TextInput({**INPUT, "placeholder": "Nombre completo"}),
            "correo": forms.EmailInput({**INPUT, "placeholder": "Correo electronico"}),
            "telefono": forms.TextInput({**INPUT, "placeholder": "Telefono"}),
            "empresa": forms.TextInput({**INPUT, "placeholder": "Empresa"}),
        }


# =========================================================
# PROVEEDORES
# =========================================================

class ProveedorForm(forms.ModelForm):

    class Meta:
        model = Proveedor
        fields = [
            "nit", "empresa", "contacto",
            "correo", "telefono", "ciudad", "direccion",
        ]
        widgets = {
            "nit": forms.TextInput({**INPUT, "placeholder": "NIT"}),
            "empresa": forms.TextInput({**INPUT, "placeholder": "Empresa"}),
            "contacto": forms.TextInput({**INPUT, "placeholder": "Persona de contacto"}),
            "correo": forms.EmailInput({**INPUT, "placeholder": "Correo electronico"}),
            "telefono": forms.TextInput({**INPUT, "placeholder": "Telefono"}),
            "ciudad": forms.TextInput({**INPUT, "placeholder": "Ciudad"}),
            "direccion": forms.TextInput({**INPUT, "placeholder": "Direccion"}),
        }


# =========================================================
# PRODUCTOS
# =========================================================

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = [
            "codigo", "nombre", "categoria", "proveedor",
            "precio_compra", "precio_venta", "stock", "stock_minimo",
        ]
        widgets = {
            "codigo": forms.TextInput({**INPUT, "placeholder": "Codigo"}),
            "nombre": forms.TextInput({**INPUT, "placeholder": "Nombre del producto"}),
            "categoria": forms.TextInput({**INPUT, "placeholder": "Categoria"}),
            "proveedor": forms.Select(SELECT),
            "precio_compra": forms.NumberInput({**INPUT, "step": "0.01", "min": "0"}),
            "precio_venta": forms.NumberInput({**INPUT, "step": "0.01", "min": "0"}),
            "stock": forms.NumberInput({**INPUT, "min": "0"}),
            "stock_minimo": forms.NumberInput({**INPUT, "min": "0"}),
        }

    def clean(self):
        """Regla de negocio: no se puede vender por debajo del costo."""
        datos = super().clean()
        compra = datos.get("precio_compra")
        venta = datos.get("precio_venta")

        if compra is not None and venta is not None and venta < compra:
            self.add_error(
                "precio_venta",
                "El precio de venta no puede ser menor que el de compra.",
            )
        return datos


# =========================================================
# EMPLEADOS
# =========================================================

class EmpleadoForm(forms.ModelForm):

    class Meta:
        model = Empleado
        # Se listan los campos uno a uno en vez de usar "__all__".
        # Con "__all__", agregar manana un campo sensible al modelo
        # (por ejemplo "salario" o "es_admin") lo expondria automaticamente
        # al formulario publico. Esto se llama asignacion masiva.
        fields = [
            "documento", "nombres", "apellidos", "correo", "telefono",
            "cargo", "area", "estado", "fecha_ingreso",
        ]
        widgets = {
            "documento": forms.TextInput({**INPUT, "placeholder": "Documento"}),
            "nombres": forms.TextInput({**INPUT, "placeholder": "Nombres"}),
            "apellidos": forms.TextInput({**INPUT, "placeholder": "Apellidos"}),
            "correo": forms.EmailInput({**INPUT, "placeholder": "Correo electronico"}),
            "telefono": forms.TextInput({**INPUT, "placeholder": "Telefono"}),
            "cargo": forms.Select(SELECT),
            "area": forms.Select(SELECT),
            "estado": forms.Select(SELECT),
            "fecha_ingreso": forms.DateInput({**INPUT, "type": "date"}),
        }


# =========================================================
# VENTA RAPIDA (un producto por venta, como en el formulario actual)
# =========================================================

class VentaRapidaForm(forms.Form):

    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(SELECT),
        label="Cliente",
        empty_label="Seleccione un cliente",
    )

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.select_related("proveedor"),
        widget=forms.Select(SELECT),
        label="Producto",
        empty_label="Seleccione un producto",
    )

    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput({**INPUT, "min": "1", "placeholder": "Cantidad"}),
        label="Cantidad",
    )

    def clean(self):
        """No se puede vender mas unidades de las que hay en inventario."""
        datos = super().clean()
        producto = datos.get("producto")
        cantidad = datos.get("cantidad")

        if producto is not None and cantidad is not None:
            if cantidad > producto.stock:
                self.add_error(
                    "cantidad",
                    f"Stock insuficiente: solo quedan {producto.stock} "
                    f"unidades de {producto.nombre}.",
                )
        return datos


# =========================================================
# PRODUCCION DIARIA (HU-001)
# =========================================================

class ProduccionForm(forms.ModelForm):

    class Meta:
        model = RegistroProduccion
        fields = ["fecha", "turno", "material", "unidad", "cantidad", "supervisor", "observaciones"]
        widgets = {
            "fecha": forms.DateInput({**INPUT, "type": "date"}, format="%Y-%m-%d"),
            "turno": forms.Select(SELECT),
            "material": forms.Select(SELECT),
            "unidad": forms.Select(SELECT),
            "cantidad": forms.NumberInput({**INPUT, "step": "0.01", "min": "0.01", "max": "5000",
                                           "placeholder": "Cantidad extraída"}),
            "supervisor": forms.Select(SELECT),
            "observaciones": forms.TextInput({**INPUT, "maxlength": "300",
                                              "placeholder": "Frente de explotación, novedades..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo supervisores activos pueden figurar como responsables del turno.
        self.fields["supervisor"].queryset = Empleado.objects.filter(estado="Activo")
        self.fields["supervisor"].empty_label = "Seleccione el supervisor"
        # Texto de la opcion vacia en lugar de "---------".
        self.fields["turno"].choices = [("", "Seleccione el turno"), *RegistroProduccion.TURNOS]
        self.fields["material"].choices = [("", "Seleccione el material"), *RegistroProduccion.MATERIALES]
