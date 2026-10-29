# Previsão de Resultados de Jogos

Site estático em pt-BR para apresentar o projeto de previsão de resultados de seleções e demonstrar a conversão de gols esperados em probabilidades usando Poisson.

## Estrutura

- `index.html`: página única, sem dependências externas.
- `css/style.css`: tema escuro/claro, layout responsivo e componentes visuais.
- `js/main.js`: navegação, tema, animações acessíveis e copiar código.
- `js/simulador.js`: simulador Poisson independente da rede neural.
- `js/previsao.js`: integração do formulário com a API de previsões.
- `prever_jogos_v3.ipynb`: pipeline de dados e treinamento original.
- `backend/`: API FastAPI e runtime independente; o notebook não é alterado.
- `frontend/`: imagem Nginx e proxy `/api/` para o backend.
- `docker-compose.yml`: execução local completa.

## Rodar localmente

Não há build. Abra `index.html` diretamente ou sirva a pasta com qualquer servidor estático:

```bash
python -m http.server 8000
```

Acesse `http://localhost:8000`.

## Executar o site funcional com Docker

Pré-requisitos: Docker Desktop com Compose v2.

```bash
docker compose up --build
```

Abra `http://localhost:8080`. A API também fica disponível em `http://localhost:8000/docs` e `http://localhost:8000/health`.

O runtime carrega as planilhas do projeto dentro do container. Se não existir um pacote Keras em `backend/models/`, a API funciona em `baseline runtime`: usa Elo, forma recente e Poisson, informando esse modo na resposta. Isso permite testar o site sem fingir que uma rede neural foi carregada.

Para gerar o pacote Keras opcional, instale as dependências de ML e execute:

```bash
pip install -r backend/requirements-ml.txt
python backend/prepare_model.py
docker compose build api
docker compose up -d api
```

O script cria `backend/models/`, que é ignorado pelo Git, e não modifica `prever_jogos_v3.ipynb`, `base_jogos_limpa.xlsx` ou `ranking_elo_externo.xlsx`.

### Variáveis de ambiente

Copie `.env.example` para `.env` se quiser alterar portas:

```bash
copy .env.example .env
docker compose up --build
```

`CORS_ORIGINS` deve conter a origem pública do frontend quando a API for hospedada separadamente.

## Publicar no GitHub Pages

1. Faça push da pasta para o repositório.
2. No GitHub, abra **Settings > Pages**.
3. Em **Build and deployment**, selecione **Deploy from a branch**.
4. Escolha `main` e a pasta `/ (root)`.
5. Salve e aguarde a URL ser disponibilizada.

## Publicar no Cloudflare Pages

1. Crie um projeto em **Workers & Pages > Create application > Pages**.
2. Conecte o repositório GitHub.
3. Use a branch `main`.
4. Deixe o comando de build vazio e use `/` como diretório de saída.
5. Publique.

## QA antes de publicar

- [ ] Testar navegação e menu em 320px, 768px e desktop.
- [ ] Testar tema claro/escuro e persistência após recarregar.
- [ ] Testar simulador com valores baixos, altos e inválidos.
- [ ] Confirmar que heatmap e tabelas não criam rolagem horizontal na página.
- [ ] Navegar só com teclado e verificar foco visível.
- [ ] Testar com `prefers-reduced-motion`.
- [ ] Conferir links GitHub, sitemap e robots.
- [ ] Rodar Lighthouse em Performance, Acessibilidade, Boas práticas e SEO.
- [ ] Confirmar `GET /health` e `GET /teams`.
- [ ] Testar uma previsão real pelo formulário com `docker compose up --build`.
- [ ] Confirmar no resultado se o modo é `keras` ou `baseline`.

## Escopo do simulador

O simulador da página recebe somente dois valores de gols esperados e aplica a distribuição de Poisson. Ele não carrega o arquivo `.keras`, não treina modelos e não produz previsão específica para uma seleção. Para executar o modelo original, use o notebook no Colab ou Jupyter.
