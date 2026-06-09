from flask import Flask, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

# ========== BANCO DE DADOS EM MEMÓRIA (para teste) ==========
# Em produção, use um banco de dados real como PostgreSQL
produtos_db = []
produto_id_counter = 1

# ========== ROTAS EXISTENTES (MANTENHA AS QUE VOCÊ JÁ TEM) ==========

@app.route('/')
def home():
    return "Moda Agent está funcionando! Acesse /api/status para verificar."

@app.route('/api/status')
def status():
    return jsonify({
        'success': True,
        'message': 'API do Moda Agent está funcionando!',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trends')
def get_trends():
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

@app.route('/debug/env')
def debug_env():
    return jsonify({
        "MARITACA_API_KEY_SET": bool(os.environ.get("MARITACA_API_KEY")),
        "MARITACA_BASE_URL": os.environ.get("MARITACA_BASE_URL", "não configurada"),
        "PORT": os.environ.get("PORT", "não configurada")
    })

# ========== NOVAS ROTAS PARA GERENCIAR PRODUTOS ==========
# (adicione TODO o código abaixo)

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    """Lista todos os produtos (com filtros opcionais)"""
    
    # Filtros opcionais via query string
    categoria = request.args.get('categoria')
    plataforma = request.args.get('plataforma')
    min_preco = request.args.get('min_preco', type=float)
    max_preco = request.args.get('max_preco', type=float)
    
    resultados = produtos_db.copy()
    
    # Aplicar filtros
    if categoria:
        resultados = [p for p in resultados if p['categoria'].lower() == categoria.lower()]
    if plataforma:
        resultados = [p for p in resultados if p['plataforma'].lower() == plataforma.lower()]
    if min_preco:
        resultados = [p for p in resultados if p['preco'] >= min_preco]
    if max_preco:
        resultados = [p for p in resultados if p['preco'] <= max_preco]
    
    return jsonify({
        'success': True,
        'total': len(resultados),
        'produtos': resultados,
        'filtros_aplicados': {
            'categoria': categoria,
            'plataforma': plataforma,
            'min_preco': min_preco,
            'max_preco': max_preco
        }
    })

@app.route('/api/produtos', methods=['POST'])
def adicionar_produto():
    """Adiciona um novo produto"""
    global produto_id_counter
    
    try:
        dados = request.get_json()
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['nome', 'categoria', 'preco']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório faltando: {campo}'
                }), 400
        
        # Criar produto
        produto = {
            'id': produto_id_counter,
            'nome': dados['nome'],
            'categoria': dados['categoria'],
            'preco': float(dados['preco']),
            'preco_original': dados.get('preco_original', float(dados['preco']) * 1.3),
            'plataforma': dados.get('plataforma', 'Manual'),
            'url': dados.get('url', ''),
            'score_tendencia': dados.get('score_tendencia', 50),
            'data_adicionado': datetime.now().isoformat(),
            'disponivel': dados.get('disponivel', True)
        }
        
        produtos_db.append(produto)
        produto_id_counter += 1
        
        return jsonify({
            'success': True,
            'message': 'Produto adicionado com sucesso!',
            'produto': produto
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/produtos/<int:produto_id>', methods=['GET'])
def buscar_produto(produto_id):
    """Busca um produto específico pelo ID"""
    produto = next((p for p in produtos_db if p['id'] == produto_id), None)
    
    if produto:
        return jsonify({'success': True, 'produto': produto})
    else:
        return jsonify({'success': False, 'error': 'Produto não encontrado'}), 404

@app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    """Atualiza um produto existente"""
    produto = next((p for p in produtos_db if p['id'] == produto_id), None)
    
    if not produto:
        return jsonify({'success': False, 'error': 'Produto não encontrado'}), 404
    
    try:
        dados = request.get_json()
        
        # Atualizar campos permitidos
        campos_permitidos = ['nome', 'categoria', 'preco', 'preco_original', 
                            'plataforma', 'url', 'score_tendencia', 'disponivel']
        
        for campo in campos_permitidos:
            if campo in dados:
                if campo == 'preco' or campo == 'preco_original' or campo == 'score_tendencia':
                    produto[campo] = float(dados[campo])
                else:
                    produto[campo] = dados[campo]
        
        produto['data_atualizacao'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Produto atualizado com sucesso!',
            'produto': produto
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def remover_produto(produto_id):
    """Remove um produto"""
    global produtos_db
    produto = next((p for p in produtos_db if p['id'] == produto_id), None)
    
    if not produto:
        return jsonify({'success': False, 'error': 'Produto não encontrado'}), 404
    
    produtos_db = [p for p in produtos_db if p['id'] != produto_id]
    
    return jsonify({
        'success': True,
        'message': f'Produto "{produto["nome"]}" removido com sucesso!'
    })

@app.route('/api/produtos/batch', methods=['POST'])
def adicionar_multiplos_produtos():
    """Adiciona vários produtos de uma vez"""
    global produto_id_counter
    
    try:
        dados = request.get_json()
        produtos = dados.get('produtos', [])
        
        if not produtos:
            return jsonify({'success': False, 'error': 'Nenhum produto fornecido'}), 400
        
        produtos_adicionados = []
        for produto_data in produtos:
            produto = {
                'id': produto_id_counter,
                'nome': produto_data['nome'],
                'categoria': produto_data['categoria'],
                'preco': float(produto_data['preco']),
                'preco_original': produto_data.get('preco_original', float(produto_data['preco']) * 1.3),
                'plataforma': produto_data.get('plataforma', 'Manual'),
                'url': produto_data.get('url', ''),
                'score_tendencia': produto_data.get('score_tendencia', 50),
                'data_adicionado': datetime.now().isoformat(),
                'disponivel': produto_data.get('disponivel', True)
            }
            produtos_db.append(produto)
            produtos_adicionados.append(produto)
            produto_id_counter += 1
        
        return jsonify({
            'success': True,
            'message': f'{len(produtos_adicionados)} produtos adicionados com sucesso!',
            'produtos': produtos_adicionados
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/produtos/estatisticas', methods=['GET'])
def estatisticas_produtos():
    """Retorna estatísticas dos produtos"""
    if not produtos_db:
        return jsonify({
            'success': True,
            'message': 'Nenhum produto cadastrado ainda',
            'estatisticas': {
                'total_produtos': 0,
                'preco_medio': 0,
                'categorias': [],
                'plataformas': []
            }
        })
    
    precos = [p['preco'] for p in produtos_db]
    categorias = list(set([p['categoria'] for p in produtos_db]))
    plataformas = list(set([p['plataforma'] for p in produtos_db]))
    
    # Produtos com maior score de tendência
    top_tendencias = sorted(produtos_db, key=lambda x: x['score_tendencia'], reverse=True)[:5]
    
    return jsonify({
        'success': True,
        'estatisticas': {
            'total_produtos': len(produtos_db),
            'preco_medio': round(sum(precos) / len(precos), 2),
            'preco_minimo': min(precos),
            'preco_maximo': max(precos),
            'categorias': categorias,
            'plataformas': plataformas
        },
        'top_tendencias': top_tendencias
    })

@app.route('/admin/produtos')
def admin_produtos():
    """Interface administrativa para gerenciar produtos"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Moda Agent</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
            h1 { color: #333; }
            .form-group { margin: 10px 0; }
            input, select { padding: 8px; margin: 5px; width: 200px; }
            button { background: #4CAF50; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; }
            button:hover { background: #45a049; }
            .produto { border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 5px; background: #f9f9f9; }
            .produto button { background: #f44336; margin-left: 10px; }
            .produto button:hover { background: #da190b; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #4CAF50; color: white; }
            .filtros { margin: 20px 0; padding: 10px; background: #e0e0e0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📦 Gerenciar Produtos - Moda Agent</h1>
            
            <div class="form-group">
                <h3>➕ Adicionar Produto</h3>
                <input type="text" id="nome" placeholder="Nome do produto">
                <input type="text" id="categoria" placeholder="Categoria">
                <input type="number" id="preco" placeholder="Preço">
                <input type="text" id="plataforma" placeholder="Plataforma">
                <input type="number" id="score" placeholder="Score tendência (0-100)">
                <button onclick="adicionarProduto()">Adicionar</button>
            </div>
            
            <div class="filtros">
                <h3>🔍 Filtros</h3>
                <input type="text" id="filtroCategoria" placeholder="Filtrar por categoria">
                <input type="text" id="filtroPlataforma" placeholder="Filtrar por plataforma">
                <input type="number" id="filtroMinPreco" placeholder="Preço mínimo">
                <input type="number" id="filtroMaxPreco" placeholder="Preço máximo">
                <button onclick="carregarProdutos()">Aplicar Filtros</button>
                <button onclick="limparFiltros()">Limpar</button>
            </div>
            
            <div id="estatisticas"></div>
            <div id="lista-produtos"></div>
        </div>
        
        <script>
            function carregarProdutos() {
                let url = '/api/produtos?';
                const categoria = document.getElementById('filtroCategoria').value;
                const plataforma = document.getElementById('filtroPlataforma').value;
                const minPreco = document.getElementById('filtroMinPreco').value;
                const maxPreco = document.getElementById('filtroMaxPreco').value;
                
                if (categoria) url += `categoria=${categoria}&`;
                if (plataforma) url += `plataforma=${plataforma}&`;
                if (minPreco) url += `min_preco=${minPreco}&`;
                if (maxPreco) url += `max_preco=${maxPreco}&`;
                
                fetch(url)
                    .then(r => r.json())
                    .then(data => {
                        const div = document.getElementById('lista-produtos');
                        if (data.produtos.length === 0) {
                            div.innerHTML = '<p>Nenhum produto cadastrado.</p>';
                            return;
                        }
                        
                        let html = '<h3>📋 Produtos Cadastrados:</h3>';
                        html += '<table>';
                        html += '<tr><th>ID</th><th>Nome</th><th>Categoria</th><th>Preço</th><th>Plataforma</th><th>Score</th><th>Ações</th></tr>';
                        
                        data.produtos.forEach(p => {
                            html += `
                                <tr>
                                    <td>${p.id}</td>
                                    <td><strong>${p.nome}</strong></td>
                                    <td>${p.categoria}</td>
                                    <td>R$ ${p.preco.toFixed(2)}</td>
                                    <td>${p.plataforma}</td>
                                    <td>${p.score_tendencia}</td>
                                    <td>
                                        <button onclick="removerProduto(${p.id})">Remover</button>
                                        <button onclick="editarProduto(${p.id})">Editar</button>
                                    </td>
                                </tr>
                            `;
                        });
                        
                        html += '</table>';
                        div.innerHTML = html;
                    });
                
                // Carregar estatísticas
                fetch('/api/produtos/estatisticas')
                    .then(r => r.json())
                    .then(data => {
                        const statsDiv = document.getElementById('estatisticas');
                        if (data.estatisticas.total_produtos > 0) {
                            statsDiv.innerHTML = `
                                <div class="filtros">
                                    <h3>📊 Estatísticas</h3>
                                    <p>Total de produtos: ${data.estatisticas.total_produtos}</p>
                                    <p>Preço médio: R$ ${data.estatisticas.preco_medio}</p>
                                    <p>Preço mínimo: R$ ${data.estatisticas.preco_minimo}</p>
                                    <p>Preço máximo: R$ ${data.estatisticas.preco_maximo}</p>
                                    <p>Categorias: ${data.estatisticas.categorias.join(', ')}</p>
                                </div>
                            `;
                        }
                    });
            }
            
            function adicionarProduto() {
                const produto = {
                    nome: document.getElementById('nome').value,
                    categoria: document.getElementById('categoria').value,
                    preco: parseFloat(document.getElementById('preco').value),
                    plataforma: document.getElementById('plataforma').value || 'Manual',
                    score_tendencia: parseInt(document.getElementById('score').value) || 50
                };
                
                if (!produto.nome || !produto.categoria || !produto.preco) {
                    alert('Preencha nome, categoria e preço!');
                    return;
                }
                
                fetch('/api/produtos', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(produto)
                }).then(response => response.json())
                  .then(data => {
                    if (data.success) {
                        alert('Produto adicionado com sucesso!');
                        document.getElementById('nome').value = '';
                        document.getElementById('categoria').value = '';
                        document.getElementById('preco').value = '';
                        document.getElementById('plataforma').value = '';
                        document.getElementById('score').value = '';
                        carregarProdutos();
                    } else {
                        alert('Erro: ' + data.error);
                    }
                });
            }
            
            function removerProduto(id) {
                if (confirm('Tem certeza que deseja remover este produto?')) {
                    fetch(`/api/produtos/${id}`, {method: 'DELETE'})
                        .then(() => carregarProdutos());
                }
            }
            
            function editarProduto(id) {
                const novoPreco = prompt('Digite o novo preço:');
                if (novoPreco) {
                    fetch(`/api/produtos/${id}`, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({preco: parseFloat(novoPreco)})
                    }).then(() => carregarProdutos());
                }
            }
            
            function limparFiltros() {
                document.getElementById('filtroCategoria').value = '';
                document.getElementById('filtroPlataforma').value = '';
                document.getElementById('filtroMinPreco').value = '';
                document.getElementById('filtroMaxPreco').value = '';
                carregarProdutos();
            }
            
            // Carregar produtos ao iniciar
            carregarProdutos();
        </script>
    </body>
    </html>
    '''

# ========== MANIPULADOR DE ERRO 404 ==========
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado',
        'message': 'Verifique os endpoints disponíveis em /'
    }), 404

# ========== INICIALIZAÇÃO DO SERVIDOR ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
