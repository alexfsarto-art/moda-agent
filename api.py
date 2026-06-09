# Adicionar produto
curl -X POST https://seu-app.onrender.com/api/produtos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Vestido Azul","categoria":"Vestidos","preco":99.90}'

# Listar produtos
curl https://seu-app.onrender.com/api/produtos

# Ver estatísticas
curl https://seu-app.onrender.com/api/produtos/estatisticas
