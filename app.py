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
        <input type="text" name="name"><br>

        <label>Email:</label><br>
        <input type="email" name="email"><br>

        <label>Telefone (somente números):</label><br>
        <input type="text" name="phone"><br>

        <label>CPF (somente números):</label><br>
        <input type="text" name="cpf"><br>

        <label>Valor (R$):</label><br>
        <input type="number" name="amount" step="0.01"><br>

        <label>Rua:</label><br>
        <input type="text" name="street"><br>

        <label>Número:</label><br>
        <input type="text" name="streetNumber"><br>

        <label>Bairro:</label><br>
        <input type="text" name="neighborhood"><br>

        <label>Cidade:</label><br>
        <input type="text" name="city"><br>

        <label>Estado (UF):</label><br>
        <input type="text" name="state"><br>

        <label>CEP:</label><br>
        <input type="text" name="zipCode"><br><br>

        <input type="submit" value="Gerar PIX">
    </form>
</body>
</html>
'''

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM)

@app.route("/gerar-pix", methods=["POST"])
def gerar_pix():
    data = request.form
    payload = {
        "amount": int(float(data.get("amount")) * 100),
        "paymentMethod": "pix",
        "pix": {"expiresInDays": 1},
        "items": [{
            "title": "dubai pedidos",
            "unitPrice": int(float(data.get("amount")) * 100),
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
        return jsonify({
            "status": "sucesso",
            "valor": result.get("amount") / 100,
            "copia_cola": result.get("pix", {}).get("qrcode"),
            "dados_completos": result
        })
    else:
        return jsonify({"status": "erro", "detalhes": response.text}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
