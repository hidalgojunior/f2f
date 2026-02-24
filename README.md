# F2F - Gerenciamento de presenças do Face a Face de Marília - SP

Aplicação Flask + Tailwind para controlar presença em reuniões usando QR codes.

## Tecnologias

- Python / Flask
- MySQL via SQLAlchemy
- Tailwind CSS (CDN)
- Docker/Docker Compose

## Executando o ambiente

A aplicação pode ser executada de duas formas:

### 1. Com Docker (recomendado)

1. Build e start:

   ```sh
   docker-compose up --build
   ```

   Isso iniciará o serviço `db` (MySQL) e `web` (Flask app) em `31.97.251.198:5000`.

2. No primeiro lançamento, crie as tabelas e o administrador original:

   ```sh
   docker-compose run web flask db upgrade   # aplica migrações
   docker-compose run web python seeds.py
   ```

   Usuário: `14981364342`, senha: `jr34139251`.

### 2. Localmente sem Docker (fallback para SQLite)

Se estiver executando o projeto fora de containers, a configuração padrão usa um
arquivo SQLite (`f2f.db`) no diretório do projeto quando `DATABASE_URL` não está
setado. O script `seeds.py` chama `db.create_all()` automaticamente para criar as
tabelas.

Basta ativar o ambiente virtual e executar:

```sh
python run.py
```

O banco será criado e você poderá usar o admin. Se preferir usar migrações em vez
desta abordagem, rode `flask db upgrade` antes de executar `seeds.py`.

Usuário inicial: `14981364342`, senha: `jr34139251`.

Abra o navegador em `http://31.97.251.198:5000/admin/login` e entre com as credenciais.

4. Use a interface de administração para cadastrar eventos, reuniões e gerar QR codes.
   - Cada reunião gerará um token; clique para visualizar o QR e abrir em outra aba para testar.
   - O link de leitura é `http://31.97.251.198:5000/scan/<token>`.

5. Escaneie o QR (ou acesse manualmente) e siga os passos na tela.
   - No primeiro acesso o telefone, nome e região são solicitados.
   - Em acessos subsequentes, se o telefone estiver cadastrado, a presença é confirmada imediatamente.

## Teste manual rápido

1. Após gerar um QR code, copie o link mostrado na tela de detalhes da reunião.
2. Acesse o link em uma aba diferente do navegador para simular a leitura.
3. Informe um número de telefone no formato `(xx) xxxxx-xxxx`.
4. Se for novo, faça o cadastro e confirme a presença.

## Scripts úteis

- `python seeds.py` - garante que o administrador inicial exista.

## Observações

- A aplicação já está localizada em português-BR e utiliza o fuso `America/Sao_Paulo`.
- A interface agora utiliza Bootstrap 5, oferecendo um visual mais profissional e responsivo. Algumas classes Tailwind ainda existem nos templates mas a biblioteca foi removida para evitar conflitos (como o bug de menu dropdown que fechava a tela toda). O dashboard administrativo foi redesenhado com cards e uma barra de navegação moderna.
- Integração com WhatsApp agora simplificada: a aplicação gera links diretos `wa.me` que podem ser abertos para iniciar conversas. Não há necessidade de nenhum serviço adicional ou dependência externa.
- Busca por região agora inclui também usuários que tinham apenas a cor preenchida; os migramos automaticamente para o campo `region_id` no primeiro acesso.
- O sistema expõe um conjunto simples de APIs sob `/api` protegido por token (`API_TOKEN` configurável). Disponíveis:
  * `GET /api/events?token=<token>` – lista eventos
  * `GET /api/users?token=<token>` – lista usuários e suas regiões
  * `POST /api/attendance` – registra presença (json com `token` do qrcode e `telefone`).
- Um painel **Configurações** permite gerar/alterar um `API_TOKEN` usado pelas rotas de API.

- Rotas JSON simples (sob `/api`) expõem dados:
  * `GET /api/events?token=<tok>` – lista eventos
  * `GET /api/users?token=<tok>` – lista usuários
  * `POST /api/attendance?token=<tok>` – registra presença (`json={"token": "<qrcode>", "telefone":"..."}`)
  Essas chamadas exigem o token de API configurado na tela de configurações.
- Eventos precisam de data inicial e final; o sistema fecha QR automaticamente após o término.
- Quando um novo QR é gerado para uma reunião, o antigo é desativado e quem usar o link antigo será redirecionado para o código ativo.
- Administradores podem excluir eventos inteiros (removendo também reuniões, qrcodes, presenças e equipes associadas).
- As interfaces usam ícones (📅, ✏️, 🗑️, 👥, etc.) para tornar ações e informações mais visuais.
- QR codes sempre apontam para o servidor definido em `SERVER_ADDRESS` (por padrão 31.97.251.198:5000), não para localhost.
- É possível filtrar usuários por nome ou por região na interface de administração.
- O administrador pode criar, editar e excluir regiões (as cores/nomes aparecem nos formulários de cadastro de usuário).
- Inscrições só são aceitas automaticamente se o QR for do dia; para reuniões de outros dias, o código deve ser lido entre 18h e 23h30, caso contrário a inscrição é rejeitada.
- Ao tentar registrar um telefone já presente em uma reunião, o sistema informa que o participante já está cadastrado.
- O painel de administração inclui gráficos simples (Chart.js) mostrando presenças por reunião. Os gráficos agora ocupam menos espaço e são responsivos, facilitando a visualização em telas menores. Também há um formulário de pesquisa que permite filtrar as estatísticas por participante (nome/telefone) ou por região.
- Telefone é único e obrigatório; nome completo e cor/região também.
- A máscara de telefone e transformação do nome para maiúsculas são aplicadas nos formulários.

---

Esse README serve para orientar testes e serve como referência inicial.# f2f
