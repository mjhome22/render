from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Gerar PIX</title>
</head>
<body>
    <h2>Formulário para Gerar PIX</h2>
    <form action="/gerar-pix" method="post">
        <label>Nome:</label><br>
        <input type="text" name="name" required><br>

        <label>Email:</label><br>
        <input type="email" name="email" required><br>

        <label>Telefone (somente números):</label><br>
        <input type="text" name="phone" required><br>

        <label>CPF (somente números):</label><br>
        <input type="text" name="cpf" required><br>

        <label>Valor (R$):</label><br>
        <input type="text" name="amount" placeholder="Ex: 100.50" required><br>

        <label>Rua:</label><br>
        <input type="text" name="street" required><br>

        <label>Número:</label><br>
        <input type="text" name="streetNumber" required><br>

        <label>Bairro:</label><br>
        <input type="text" name="neighborhood" required><br>

        <label>Cidade:</label><br>
        <input type="text" name="city" required><br>

        <label>Estado (UF):</label><br>
        <input type="text" name="state" required><br>

        <label>CEP:</label><br>
        <input type="text" name="zipCode" required><br><br>

        <input type="submit" value="Gerar PIX">
    </form>
</body>
</html>
'''

HTML_RESULT = '''
<!DOCTYPE html>
<html>
<head>
    <title>PIX Gerado</title>
    <script>
    function copiarCodigo() {
        var texto = document.getElementById("pixcode");
        navigator.clipboard.writeText(texto.innerText).then(function() {
            alert("Código copiado!");
        });
    }
    </script>
</head>
<body>
    <h2>PIX Gerado com Sucesso!</h2>
    <p><strong>Valor:</strong> R$ {{ valor }}</p>
    <p><strong>Código Copia e Cola:</strong></p>
    <pre id="pixcode">{{ copia_cola }}</pre>
    <button onclick="copiarCodigo()">Copiar Código</button>
    <br><br>
    <p><strong>QR Code:</strong></p>
    <img src="https://api.qrserver.com/v1/create-qr-code/?data={{ copia_cola }}&size=250x250" alt="QR Code PIX">
</body>
</html>
'''

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM)

@app.route("/gerar-pix", methods=["POST"])
def gerar_pix():
    data = request.form
    amount_str = data.get("amount").replace(",", ".")
    amount_float = float(amount_str)
    amount_cents = int(amount_float * 100)

    payload = {
        "amount": amount_cents,
        "paymentMethod": "pix",
        "pix": {"expiresInDays": 1},
        "items": [{
            "title": "dubai pedidos",
            "unitPrice": amount_cents,
            "quantity": 1,
            "tangible": True
        }],
        "shipping": {
            "address": {
                "street": data.get("street"),
                "streetNumber": data.get("streetNumber"),
                "neighborhood": data.get("neighborhood"),
                "city": data.get("city"),
                "state": data.get("state"),
                "zipCode": data.get("zipCode"),
                "country": "BR"
            },
            "fee": 0
        },
        "customer": {
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "document": {
                "type": "cpf",
                "number": data.get("cpf")
            }
        }
    }

    headers = {
        "accept": "application/json",
        "authorization": "Basic cGtfSlhBU3JZMlJMV254TVQtNDJ2Ump2bWZMcXZyUVFmZWphSUFPd3NxekwtbnBxa0FNOnNrX3BUdFg0emVWTnhzalNuOEV2clVDRjkxMlRtZkVCVllvYVBab0ttcjV1X2dUeGhaWQ==",
        "content-type": "application/json"
    }

    response = requests.post("https://api.paynuxpayments.com.br/v1/transactions", json=payload, headers=headers)
    if response.ok:
        result = response.json()
        copia_cola = result.get("pix", {}).get("qrcode")
        valor = result.get("amount") / 100
        return render_template_string(HTML_RESULT, copia_cola=copia_cola, valor=valor)
    else:
        return jsonify({"status": "erro", "detalhes": response.text}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
