from flask import Flask, render_template_string
from loteria_core import obtener_sugerencias

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Lotería Nuevos Tiempos</title>
    <style>
        body { 
            font-family: Arial; 
            background: #0f172a; 
            color: #e5e7eb; 
            text-align: center; 
            margin: 0;
            padding-bottom: 80px;
        }
        h1 { color: #38bdf8; }
        .num { 
            display: inline-block;
            background: #1e293b;
            padding: 15px;
            margin: 6px;
            border-radius: 10px;
            font-size: 22px;
            width: 60px;
        }
        footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background: #020617;
            color: #94a3b8;
            padding: 12px 0;
            font-size: 14px;
        }
        footer span {
            color: #38bdf8;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>🎰 Nuevos Tiempos</h1>
    <p>15 números más probables</p>

    {% for n in numeros %}
        <div class="num">{{ n }}</div>
    {% endfor %}

    <footer>
        Creado por <span>Mistral Hernández Salas</span><br>
        Análisis estadístico – Nuevos Tiempos (Costa Rica)
    </footer>
</body>
</html>
"""

@app.route("/")
def home():
    numeros = obtener_sugerencias()
    return render_template_string(HTML, numeros=numeros)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

