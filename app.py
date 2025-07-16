from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# Chave secreta do gateway (NÃO compartilhe publicamente)
GATEWAY_API_KEY = "sk_pTtX4zeVNxsjSn8EvrUCF912TmfEBVYoaPZoKmr5u_gTxhZY"
GATEWAY_ENDPOINT = "https://api.asaas.com/v3/payments"  # ajuste conforme o gateway real

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

        <label>CPF/CNPJ:</label><br>
        <input type="text" name="taxId"><br>

        <label>Valor (R$):</label><br>
        <input type="number" name="amount" step="0.01"><br>

        <label>Descrição do Produto:</label><br>
        <input type="text" name="description"><br><br>

        <input type="submit" value="Gerar PIX">
    </form>
</body>
</html>
'''

@app.route("/", methods=["GET"])
def form():
    return render_template_string(HTML_FORM)

@app.route("/gerar-pix", methods=["POST"])
def gerar_pix():
    name = request.form.get("name")
    email = request.form.get("email")
    taxId = request.form.get("taxId")
    amount = float(request.form.get("amount")) * 100  # convertendo para centavos
    description = request.form.get("description")

    payload = {
        "billingType": "PIX",
        "customer": {
            "name": name,
            "email": email,
            "cpfCnpj": taxId
        },
        "value": amount / 100,
        "description": description,
        "dueDate": "2025-12-31"
    }

    headers = {
        "Content-Type": "application/json",
        "access_token": GATEWAY_API_KEY
    }

    try:
        response = requests.post(GATEWAY_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        return jsonify({
            "status": "sucesso",
            "valor": result.get("value"),
            "copia_cola": result.get("pixCopyPaste"),
            "qr_code": result.get("invoiceUrl")
        })

    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
