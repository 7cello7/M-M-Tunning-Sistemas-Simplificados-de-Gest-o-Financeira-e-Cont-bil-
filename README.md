M&M Tunning - Sistema Gerenciador de Mecânica Automotiva

📌 Sobre o Projeto

O M&M Tunning é um sistema didático de gestão para oficinas mecânicas automotivas, desenvolvido em Python.
Ele simula o fluxo de uma oficina moderna, com foco em cadastro de clientes, veículos (carros e motos), peças, ferramentas, ordens de serviço e faturamento.

Foi criado como exercício educacional, atendendo requisitos de interface, banco de dados e funcionalidades reais de gestão de oficina.

⚙️ Funcionalidades

✅ Login com diferenciação de usuários (Administrador e Cliente)
✅ Cadastro de usuários, peças, ferramentas, carros e motos
✅ Dashboard interativo com estatísticas da oficina
✅ Gestão de ordens de serviço no estilo "carrinho de compras"
✅ Controle de estoque de peças com baixa automática no faturamento
✅ Emissão de faturas vinculadas a serviços
✅ Suporte a dados de demonstração (já carregados no banco)
✅ Interface em modo Full Screen, tema escuro e logo aplicado em todas as telas

🖼️ Telas do Sistema

O sistema contém 12 telas principais:

Tela de Boas-vindas

Login

Registro de Cliente

Dashboard

Cadastro de Peças

Cadastro de Ferramentas

Cadastro de Carros

Cadastro de Motos

Gestão de Usuários (Admin)

Serviços (Ordens de Serviço)

Faturamento / Notas

Relatórios / Sobre / Ajuda

🛠️ Tecnologias Utilizadas

Python 3.x

Tkinter (Interface gráfica)

SQLite (Banco de dados local)

PIL (Pillow) (Manipulação de imagens e logo)

📂 Estrutura do Projeto
├── main.py          # Código principal da aplicação
├── mmtunning.db     # Banco de dados SQLite (com dados de exemplo)
├── logo.png         # Logo da oficina
├── Descrição        # Documento explicativo do projeto
└── README.md        # Documentação do repositório

▶️ Como Executar

Clone o repositório:

git clone https://github.com/seu-usuario/mmtunning.git
cd mmtunning


Instale as dependências:

pip install pillow


Execute o sistema:

python main.py

👥 Usuários de Demonstração

Para testar, você pode usar os seguintes logins já cadastrados:

Admin:
Usuário: admin
Senha: admin123

Clientes:

Usuário: corredor_r | Senha: cli456

Usuário: piloto_j | Senha: cli789

Usuário: turbo_m | Senha: cli101

📧 Contato

M&M Tunning - Mecânica Automotiva
📍 São Paulo - SP
📞 (11) 99999-0000
✉️ contato@mmtunning.com

⚠️ Aviso: Este sistema é didático e não deve ser usado em produção. Todos os dados de clientes, veículos e serviços são fictícios.
