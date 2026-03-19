from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["legal"])


@router.get("/privacy-policy")
def privacy_policy() -> HTMLResponse:
    html = """
    <html>
        <head>
            <meta charset='utf-8' />
            <meta name='viewport' content='width=device-width, initial-scale=1' />
            <title>Politica de Privacidad - Asuna WhatsApp Bot</title>
        </head>
        <body style='font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.5;'>
            <h1>Politica de Privacidad</h1>
            <p>Asuna WhatsApp Bot procesa datos de contacto y contenido de mensajes con el unico fin de enviar notificaciones transaccionales desde el ERP del negocio.</p>
            <h2>Datos que procesamos</h2>
            <ul>
                <li>Numero de telefono del destinatario.</li>
                <li>Contenido del mensaje enviado por el ERP.</li>
                <li>Registros tecnicos de envio (estado, fecha y errores).</li>
            </ul>
            <h2>Finalidad</h2>
            <p>Enviar notificaciones de eventos operativos (por ejemplo, venta registrada, factura emitida o compra recibida).</p>
            <h2>Conservacion</h2>
            <p>Los registros se conservan para auditoria operativa y resolucion de incidentes.</p>
            <h2>Contacto</h2>
            <p>Para consultas de privacidad o eliminacion de datos, escribir a: soporte@asuna.local</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)


@router.get("/data-deletion")
def data_deletion() -> HTMLResponse:
    html = """
    <html>
        <head>
            <meta charset='utf-8' />
            <meta name='viewport' content='width=device-width, initial-scale=1' />
            <title>Eliminacion de Datos - Asuna WhatsApp Bot</title>
        </head>
        <body style='font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.5;'>
            <h1>Eliminacion de Datos</h1>
            <p>Si deseas solicitar la eliminacion de tus datos, envia una solicitud al correo: soporte@asuna.local</p>
            <p>Incluye el numero de telefono y una descripcion de la solicitud para poder ubicar los registros.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
