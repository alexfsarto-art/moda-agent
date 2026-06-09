from flask import Flask, jsonify, request, render_template, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__)

# ========== ROTAS PRINCIPAIS ==========

@app.route('/')
def home():
    """Página inicial - vai mostrar que o servidor está funcionando"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Moda Agent - Agente de Tendências</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .emoji {
                font-size: 3em;
                margin-bottom: 20px;
            }
            .status {
                background: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 10px;
                margin: 20px 0;
                font-weight: bold;
            }
            .info {
                background: #f0f0f0;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: left;
            }
            .endpoint {
                background: #e0e0e0;
                padding: 8px;
                margin: 8px 0;
                border-radius: 5px;
                font-family: monospace;
                font-size: 14px;
            }
            .footer {
                margin-top: 20px;
                color: #666;
                font-size: 12px;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
                font-size: 14px;
            }
            button:hover {
                background: #764ba2;
            }
            pre {
                background: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                font-size: 12px;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🛍️👗</div>
            <h1>Moda Agent</h1>
            <p>Agente de Tendências de Moda e Vendas</p>
            
            <div class="status">
                ✅ Servidor rodando perfeitamente!
            </div>
            
            <div class="info">
                <strong>📊 Endpoints disponíveis:</strong>
                <div class="endpoint">GET / → Página inicial</div>
                <div class="endpoint">GET /health → Verificar saúde do servidor</div>
                <div class="endpoint">GET /api/status → Status da API</div>
                <div class="endpoint">GET /api/trends → Lista de tendências (mock)</div>
                <div class="endpoint">POST /api/analyze → Analisar produtos</div>
            </div>
            
            <button onclick="testarAPI()">Testar API</button>
            <button onclick="carregarTendencias()">Ver Tendências</button>
            
            <div id="resultado" style="margin-top: 20px; display: none;">
                <div class="info">
                    <strong>📡 Resultado da requisição:</strong>
                    <pre id="resultado-conteudo"></pre>
                </div>
            </div>
            
            <div class="footer">
                Moda Agent v1.0 | Rodando no Render 🚀
            </div>
        </div>
        
        <script>
            async function testarAPI() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    mostrarResultado(JSON.stringify(data, null, 2));
                } catch (error) {
                    mostrarResultado('Erro: ' + error.message);
                }
            }
            
            async function carregarTendencias() {
                try {
                    const response = await fetch('/api/trends');
                    const data = await response.json();
                    mostrarResultado(JSON.stringify(data, null, 2));
                } catch (error) {
                    mostrarResultado('Erro: ' + error.message);
                }
            }
            
            function mostrarResultado(conteudo) {
                const divResultado = document.getElementById('resultado');
                const preConteudo = document.getElementById('resultado-conteudo');
                preConteudo.textContent = conteudo;
                divResultado.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Endpoint para verificar se o servidor está saudável"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Moda Agent'
    })

@app.route('/api/status')
def status():
    """Retorna o status da API"""
    return jsonify({
        'success': True,
        'message': 'API do Moda Agent está funcionando!',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            '/',
            '/health',
            '/api/status',
            '/api/trends',
            '/api/analyze'
        ]
    })

@app.route('/api/trends')
def get_trends():
    """Retorna tendências de moda (dados mock para exemplo)"""
    trends = {
        'success': True,
        'data': [
            {'categoria': 'Vestido Verão', 'tendencia': 'alta', 'score': 95},
            {'categoria': 'Tênis Casual', 'tendencia': 'média', 'score': 78},
            {'categoria': 'Bolsa Feminina', 'tendencia': 'alta', 'score': 88},
            {'categoria': 'Jaqueta Jeans', 'tendencia': 'baixa', 'score': 45}
        ],
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(trends)

@app.route('/api/analyze', methods=['POST'])
def analyze_products():
    """Endpoint para análise de produtos"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Nenhum dado fornecido'}), 400
        
        # Mock de análise
        result = {
            'success': True,
            'analysis': 'Análise concluída com sucesso',
            'products_analyzed': len(data.get('products', [])),
            'recommendations': [
                'Foco em produtos com alta tendência',
                'Ajustar preços para melhor competitividade',
                'Investir em categorias em alta'
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test')
def test():
    """Endpoint simples para teste rápido"""
    return jsonify({'message': 'API está respondendo!', 'status': 'ok'})

# ========== MANIPULAÇÃO DE ERROS ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado',
        'message': 'Verifique os endpoints disponíveis em /'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor'
    }), 500

# ========== INICIALIZAÇÃO DO SERVIDOR ==========

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    # Configuração para o Render
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,  # Importante: False em produção
        threaded=True
    )
#=================== TESTE CONEXÃO ==============
@app.route('/debug/env')
def debug_env():
    """Verifica se as variáveis estão configuradas (remova em produção!)"""
    return jsonify({
        "MARITACA_API_KEY_SET": bool(os.environ.get("MARITACA_API_KEY")),
        "MARITACA_BASE_URL": os.environ.get("MARITACA_BASE_URL", "não configurada")
    })
