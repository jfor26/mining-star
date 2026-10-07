"""
Pasarela de pagos de Mining Star (Stripe).

Funciona en dos modos, segun exista o no la llave secreta en el .env:

- "stripe": crea una sesion de Stripe Checkout. El cliente paga en la
  pagina segura de Stripe (los datos de la tarjeta NUNCA pasan por nuestro
  servidor) y vuelve al aplicativo. Con llaves de prueba (sk_test_...) se
  usan tarjetas de prueba como 4242 4242 4242 4242.
- "simulado": sin llaves configuradas, el pago se aprueba desde el propio
  aplicativo. Sirve para demostrar el flujo completo en clase sin cuenta de
  Stripe. Nunca debe usarse en produccion.

Toda la comunicacion con Stripe esta aqui: si se cambia de pasarela
(PayU, Wompi, Mercado Pago), solo se toca este archivo.
"""

from decimal import Decimal

from django.conf import settings


def modo():
    return "stripe" if getattr(settings, "STRIPE_SECRET_KEY", "") else "simulado"


def _stripe():
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def a_unidad_minima(valor):
    """Stripe recibe los montos en la unidad minima de la moneda.

    El peso colombiano se maneja en Stripe con dos decimales, asi que
    $185.000 COP se envian como 18500000.
    """
    return int((Decimal(valor) * 100).quantize(Decimal("1")))


def crear_sesion(pedido, url_exito, url_cancelacion):
    """Crea la sesion de pago y devuelve (referencia, url_a_la_que_redirigir)."""
    stripe = _stripe()
    sesion = stripe.checkout.Session.create(
        mode="payment",
        success_url=url_exito,
        cancel_url=url_cancelacion,
        client_reference_id=str(pedido.pk),
        customer_email=pedido.cliente.correo or None,
        metadata={"pedido": str(pedido.pk)},
        line_items=[
            {
                "quantity": item.cantidad,
                "price_data": {
                    "currency": settings.STRIPE_MONEDA,
                    "unit_amount": a_unidad_minima(item.precio_unitario),
                    "product_data": {"name": f"{item.producto.nombre} ({item.producto.codigo})"},
                },
            }
            for item in pedido.items.select_related("producto")
        ],
    )
    return sesion.id, sesion.url


def sesion_pagada(referencia):
    """Consulta a Stripe si la sesion ya fue pagada."""
    sesion = _stripe().checkout.Session.retrieve(referencia)
    return sesion.payment_status == "paid"


def leer_evento_webhook(cuerpo, firma):
    """Valida la firma del aviso que envia Stripe y devuelve el evento.

    Sin esta validacion cualquiera podria llamar al webhook diciendo que un
    pedido fue pagado. Lanza ValueError o SignatureVerificationError si la
    firma no corresponde.
    """
    stripe = _stripe()
    return stripe.Webhook.construct_event(cuerpo, firma, settings.STRIPE_WEBHOOK_SECRET)
