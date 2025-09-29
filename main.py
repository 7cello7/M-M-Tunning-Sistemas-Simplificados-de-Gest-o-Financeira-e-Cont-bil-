"""
M&M Tunning - Sistema Gerenciador de Mecânica Automotiva (versão didática)
Requisitos atendidos (resumo):
- GUI em Tkinter com 12 telas/janelas distintas
- Login e diferenciação de usuários: cliente x administrador
- Cadastro de usuários, peças, ferramentas, CARROS e MOTOS.
- Integração com banco SQLite (cria DB e insere dados de exemplo)
- Dashboard com algumas sugestões simples (indicador financeiro básico)
- Todas as telas podem exibir imagens (use placeholder/logo)
- Nome da oficina: "M&M Tunning"

Modificações de Interface Gráfica para o tema M&M Tunning:
- Reorganização do Dashboard.
- **NOVAS TELAS:** Cadastro de Carros e Cadastro de Motos (foco na Placa como chave de busca/cadastro).
- **REMOÇÃO:** Telas de Fluxograma e Wireframe.
- Nomes das tabelas no SQLite padronizados para o inglês (`users`, `parts`, etc.).
- **ATUALIZAÇÃO:** Inclusão de 3 carros e 3 motos de exemplo.
- **DASHBOARD:** Adicionada a contagem de Carros e Motos Cadastradas nos cards de estatísticas.
- **CORREÇÃO:** Ajustada a cor do texto das caixas de entrada para branco, corrigindo o 'bug' de texto invisível no Dark Mode.
- **AJUSTE DE TEXTO:** Trocado "username" por "usuário" na tela de Serviços.
- **FLUXO DE OS E ESTOQUE:** Implementado o sistema de itens na OS e baixa de estoque no Faturamento.
- **FLUXO COESO (NOVO):** A OS agora requer a PLACA do veículo e a tabela 'services' foi refatorada.
- **VISUALIZAÇÃO DE CADASTROS (NOVO):** Adicionadas colunas na tabela de Carros e Motos para exibir todos os dados cadastrados (Ano, Cor, Motor).
- **FLUXO OPERACIONAL (NOVO):** Tela de Serviços refatorada para funcionar como um "Carrinho de compras" em uma única janela.
- **COMPORTAMENTO DE JANELA (NOVO):** Tela principal em Full Screen e janelas secundárias modais.
- **AJUSTE DE JANELAS (NOVO):** Todas as janelas modais agora abrem em Full Screen.
- **CONTATO (NOVO):** Informações de contato atualizadas com base no cartão de visita.
- **REMOÇÃO (NOVO):** Removida a funcionalidade de 'Registrar Uso de Ferramentas' da OS, incluindo a tabela de relacionamento `service_tools`.
- **LOGO (NOVO):** Inserção do logo em todos os cantos superiores (esquerdo e direito) das telas modais.
- **MANUAL (ATUALIZADO):** Revisão completa do Manual Rápido para refletir o fluxo de OS, Veículos e Faturamento.
- **DADOS DE DEMONSTRAÇÃO (NOVO):** Incluída uma OS completa e uma fatura para demonstração na inicialização.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import sqlite3
import os
import datetime

# --- CONFIGURAÇÕES DO PROJETO ---
PROJECT_NAME = "M&M Tunning"
DB_NAME = "mmtunning.db"
LOGO_PATH = "logo.png"

# --- CONSTANTES DE ESTILO ---
PRIMARY_COLOR = "#00FFFF"  # Azul Neon/Ciano (Destaque)
BG_COLOR = "#29313A"  # Cinza Escuro (Fundo Principal)
HEADER_COLOR = "#1E2A3A"  # Cinza Quase Preto (Header/Menu)
TEXT_COLOR = "#FFFFFF"  # Branco (Texto Principal)


# ---------- Banco de Dados ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabelas base
    c.execute('''
              CREATE TABLE IF NOT EXISTS users
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  username
                  TEXT
                  UNIQUE,
                  password
                  TEXT,
                  fullname
                  TEXT,
                  email
                  TEXT,
                  phone
                  TEXT,
                  role
                  TEXT, -- 'admin' ou 'client'
                  photo
                  TEXT
              )
              ''')
    c.execute('''
              CREATE TABLE IF NOT EXISTS parts
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  name
                  TEXT,
                  sku
                  TEXT
                  UNIQUE,
                  qty
                  INTEGER,
                  price
                  REAL,
                  description
                  TEXT
              )
              ''')
    c.execute('''
              CREATE TABLE IF NOT EXISTS tools
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  name
                  TEXT,
                  code
                  TEXT
                  UNIQUE,
                  available
                  INTEGER,
                  description
                  TEXT
              )
              ''')

    # NOVAS TABELAS PARA VEÍCULOS
    c.execute('''
              CREATE TABLE IF NOT EXISTS cars
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  client_id
                  INTEGER,
                  license_plate
                  TEXT
                  UNIQUE,
                  brand
                  TEXT,
                  model
                  TEXT,
                  year
                  INTEGER,
                  color
                  TEXT,
                  engine
                  TEXT,
                  FOREIGN
                  KEY
              (
                  client_id
              ) REFERENCES users
              (
                  id
              )
                  )
              ''')
    c.execute('''
              CREATE TABLE IF NOT EXISTS motorcycles
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  client_id
                  INTEGER,
                  license_plate
                  TEXT
                  UNIQUE,
                  brand
                  TEXT,
                  model
                  TEXT,
                  year
                  INTEGER,
                  engine_cc
                  INTEGER,
                  FOREIGN
                  KEY
              (
                  client_id
              ) REFERENCES users
              (
                  id
              )
                  )
              ''')

    # Tabela de Serviços/Financeiro - REFATORADA PARA NOVOS CAMPOS
    c.execute('''
              CREATE TABLE IF NOT EXISTS services
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  client_id
                  INTEGER,
                  vehicle_plate
                  TEXT, -- NOVO: Placa do veículo em serviço
                  description
                  TEXT,
                  labor_price
                  REAL, -- NOVO: Preço da Mão de Obra
                  final_total
                  REAL, -- NOVO: Total final após faturamento (inclui labor_price + peças)
                  date
                  TEXT,
                  status
                  TEXT,
                  seller_name
                  TEXT, -- Vendedor/Atendente que abriu a OS
                  FOREIGN
                  KEY
              (
                  client_id
              ) REFERENCES users
              (
                  id
              )
                  )
              ''')

    # NOVAS TABELAS DE RELACIONAMENTO OS <-> ESTOQUE
    c.execute('''
              CREATE TABLE IF NOT EXISTS service_parts
              (
                  service_id
                  INTEGER,
                  part_id
                  INTEGER,
                  qty_used
                  INTEGER,
                  price_unit
                  REAL,
                  FOREIGN
                  KEY
              (
                  service_id
              ) REFERENCES services
              (
                  id
              ),
                  FOREIGN KEY
              (
                  part_id
              ) REFERENCES parts
              (
                  id
              ),
                  PRIMARY KEY
              (
                  service_id,
                  part_id
              )
                  )
              ''')

    # ATENÇÃO: A tabela service_tools foi removida para simplificar o fluxo.

    c.execute('''
              CREATE TABLE IF NOT EXISTS invoices
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  service_id
                  INTEGER,
                  total
                  REAL,
                  date
                  TEXT,
                  paid
                  INTEGER,
                  FOREIGN
                  KEY
              (
                  service_id
              ) REFERENCES services
              (
                  id
              )
                  )
              ''')

    # --- DADOS INICIAIS ---

    # 1. Usuários (Admin e Clientes)
    users_data = [
        ("admin", "admin123", "Mestre Tunning", "admin@mmtunning.com", "11999990000", "admin", ""),
        ("corredor_r", "cli456", "Rafael Rossi", "rafael.rossi@mail.com", "11981234567", "client", ""),
        ("piloto_j", "cli789", "Juliana Santos", "ju.santos@mail.com", "11989876543", "client", ""),
        ("turbo_m", "cli101", "Márcio Oliveira", "marcio.oli@mail.com", "11977771111", "client", "")
    ]
    for data in users_data:
        try:
            c.execute(
                "INSERT INTO users(username,password,fullname,email,phone,role,photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                data)
        except sqlite3.IntegrityError:
            pass

    # --- INSERÇÃO DE VEÍCULOS DE EXEMPLO ---

    # Busca IDs dos clientes para FK

    c.execute("SELECT id FROM users WHERE username='corredor_r'")
    row_r = c.fetchone()
    id_corredor_r = row_r[0] if row_r else 2

    c.execute("SELECT id FROM users WHERE username='piloto_j'")
    row_j = c.fetchone()
    id_piloto_j = row_j[0] if row_j else 3

    c.execute("SELECT id FROM users WHERE username='turbo_m'")
    row_m = c.fetchone()
    id_turbo_m = row_m[0] if row_m else 4

    # Carros
    cars_data = [
        (id_corredor_r, "ABC-1234", "Subaru", "WRX STI", 2019, "Azul", "2.5L Turbo"),
        (id_piloto_j, "DEF-5678", "Honda", "Civic SI", 2022, "Vermelha", "1.5L VTEC"),
        (id_turbo_m, "GHI-9012", "VW", "Golf GTI", 2023, "Branco", "2.0L TSI")
    ]
    for data in cars_data:
        try:
            c.execute(
                "INSERT INTO cars(client_id, license_plate, brand, model, year, color, engine) VALUES (?, ?, ?, ?, ?, ?, ?)",
                data)
        except sqlite3.IntegrityError:
            pass

    # Motos
    motorcycles_data = [
        (id_corredor_r, "MNO-3456", "Yamaha", "R3", 2021, 321),
        (id_piloto_j, "PQR-7890", "Kawasaki", "Ninja 400", 2023, 400),
        (id_turbo_m, "STU-1234", "Triumph", "Street Triple", 2024, 765)
    ]
    for data in motorcycles_data:
        try:
            c.execute(
                "INSERT INTO motorcycles(client_id, license_plate, brand, model, year, engine_cc) VALUES (?, ?, ?, ?, ?, ?)",
                data)
        except sqlite3.IntegrityError:
            pass

    # 3. Peças (Mais focadas em Performance)
    parts_data = [
        ("Vela Iridium Performance", "P-IGN-005", 30, 95.0, "Velas de ignição para alto desempenho."),
        ("Filtro Ar Esportivo K&N", "P-FIL-010", 15, 450.0, "Filtro cônico lavável, alto fluxo."),
        ("Óleo Sintético 5W40", "P-OIL-050", 40, 65.0, "Óleo totalmente sintético para motores turbo.")
    ]
    for data in parts_data:
        try:
            c.execute("INSERT INTO parts(name,sku,qty,price,description) VALUES (?, ?, ?, ?, ?)", data)
        except sqlite3.IntegrityError:
            pass

    # 4. Ferramentas
    tools_data = [
        ("Scanner de Diagnóstico OBD-II", "T-SCA-001", 1, "Leitura e calibração de ECU."),
        ("Medidor de Pressão Turbo", "T-BOO-002", 3, "Para ajuste fino de turbinas."),
        ("Torquímetro Digital 1/2", "T-TOR-003", 2, "Chave de torque de alta precisão.")
    ]
    for data in tools_data:
        try:
            c.execute("INSERT INTO tools(name,code,available,description) VALUES (?, ?, ?, ?)", data)
        except sqlite3.IntegrityError:
            pass

    # --- DADOS DE DEMONSTRAÇÃO DO FLUXO COMPLETO (OS + FATURA) ---
    try:
        # Busca IDs de peças (P-FIL-010 e P-OIL-050)
        c.execute("SELECT id, price FROM parts WHERE sku='P-FIL-010'")
        part1_id, part1_price = c.fetchone()
        c.execute("SELECT id, price FROM parts WHERE sku='P-OIL-050'")
        part2_id, part2_price = c.fetchone()

        # Calcula o total da OS para preencher o final_total
        mo_price = 150.00
        qty1 = 1
        qty2 = 5
        parts_total = (qty1 * part1_price) + (qty2 * part2_price)
        final_total = mo_price + parts_total

        current_date = datetime.date.today().isoformat()

        # 1. Insere a OS (Status Fechado, Total Final Calculado)
        c.execute(
            "INSERT INTO services(client_id, vehicle_plate, description, labor_price, final_total, date, status, seller_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (id_corredor_r, "ABC-1234", "Serviço Completo de Troca de Óleo e Filtros - Demonstração", mo_price,
             final_total, current_date, "Fechado", "Mestre Tunning"))
        service_id_demo = c.lastrowid

        # 2. Insere as Peças Usadas (service_parts)
        c.execute("INSERT INTO service_parts (service_id, part_id, qty_used, price_unit) VALUES (?, ?, ?, ?)",
                  (service_id_demo, part1_id, qty1, part1_price))
        c.execute("INSERT INTO service_parts (service_id, part_id, qty_used, price_unit) VALUES (?, ?, ?, ?)",
                  (service_id_demo, part2_id, qty2, part2_price))

        # 3. Insere a Fatura (Invoices)
        c.execute("INSERT INTO invoices(service_id, total, date, paid) VALUES (?, ?, ?, ?)",
                  (service_id_demo, final_total, current_date, 1))  # 1 = Pago

        # 4. Dá Baixa no Estoque para as Peças Usadas na Demonstração
        c.execute("UPDATE parts SET qty = qty - ? WHERE id=?", (qty1, part1_id))
        c.execute("UPDATE parts SET qty = qty - ? WHERE id=?", (qty2, part2_id))

    except Exception as e:
        # Ignora erros de integridade se o dado já existir ou se as peças/clientes não forem encontrados
        print(f"Erro ao inserir dados de demonstração (pode ser ignorado se o BD já existir): {e}")

    conn.commit()
    conn.close()


# ---------- Utilitários ----------
def format_currency(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------- App UI ----------
class MM_Tunning_App:
    def __init__(self, root):
        self.root = root
        root.title(f"{PROJECT_NAME} - Sistema Gerenciador de Mecânica")
        # CONFIGURAÇÃO PARA TELA CHEIA (FULL SCREEN)
        root.attributes('-fullscreen', True)
        root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))  # Adiciona ESC para sair do full screen

        self.conn = sqlite3.connect(DB_NAME)
        self.user = None
        self.logo_img = None

        # O cache de imagem DEVE estar na instância da aplicação para funcionar
        self.logo_img_cache = {}

        # Estrutura temporária para o "carrinho" de Peças
        # Formato: {part_id: {'name': name, 'sku': sku, 'qty': qty, 'price': price}}
        self.os_cart = {}

        # --- NOVA CONFIGURAÇÃO DE ESTILO E TEMA ---
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        self.root.configure(bg=BG_COLOR)
        self.style.configure('.', font=("Inter", 10), background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TCheckbutton', background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TLabelframe', background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TLabelframe.Label', background=BG_COLOR, foreground=PRIMARY_COLOR)

        # Estilo para Treeview (Tabela) - fundo escuro
        self.style.configure("Treeview",
                             background="#3C4855",
                             foreground=TEXT_COLOR,
                             fieldbackground="#3C4855",
                             font=("Inter", 10))
        self.style.map("Treeview",
                       background=[('selected', PRIMARY_COLOR)],
                       foreground=[('selected', '#000000')])

        # Ajuste de Treeview Header
        self.style.configure("Treeview.Heading",
                             font=("Inter", 10, 'bold'),
                             background=HEADER_COLOR,
                             foreground=PRIMARY_COLOR)
        self.style.map("Treeview.Heading",
                       background=[('active', '#444444')])

        # Estilo para Botões Primários (Ação) - Usado nos botões de formulários
        self.style.configure('Primary.TButton',
                             background=PRIMARY_COLOR,
                             foreground='#000000',
                             font=("Inter", 10, "bold"),
                             padding=[15, 8])
        self.style.map('Primary.TButton',
                       background=[('active', '#00FFFF'), ('pressed', '#00BFFF')])

        # Estilo para Botões Padrão (Nav Grid)
        self.style.configure('TButton',
                             background=HEADER_COLOR,
                             foreground=TEXT_COLOR,
                             font=("Inter", 10, "bold"),
                             padding=[15, 8])
        self.style.map('TButton',
                       background=[('active', '#444444'), ('pressed', HEADER_COLOR)])

        # Estilo para Títulos Grandes
        self.style.configure('Title.TLabel',
                             font=("Inter", 24, "bold"),
                             foreground=PRIMARY_COLOR,
                             background=BG_COLOR)

        # Estilo para Títulos Menores
        self.style.configure('Subtitle.TLabel',
                             font=("Inter", 14),
                             foreground=TEXT_COLOR,
                             background=BG_COLOR)

        # Estilo para o Menu/Header
        self.style.configure('Menu.TFrame', background=HEADER_COLOR)

        # Tela principal: Welcome -> Login
        self.build_welcome_screen()

    # --- helpers para imagens (logo/placeholder) ---
    def load_logo(self, w=247, h=186):
        # Tenta carregar a imagem real
        if os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
            except Exception:
                img = Image.new("RGB", (w, h), (50, 50, 50))
        else:
            # Placeholder se não encontrar a imagem
            img = Image.new("RGB", (w, h), (41, 53, 65))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            draw.text((w / 2, h / 2), "M&M LOGO", font=font, fill=PRIMARY_COLOR, anchor="mm")

        img = img.resize((w, h))
        self.logo_img = ImageTk.PhotoImage(img)
        return self.logo_img

    def setup_modal_window(self, win, title, geometry=None):
        """Configura uma janela Toplevel para ser modal e em Full Screen."""
        win.title(title)

        # JANELA MODAL EM FULL SCREEN
        win.attributes('-fullscreen', True)
        win.bind('<Escape>', lambda e: win.attributes('-fullscreen', False))  # Permite sair do full screen com ESC

        win.configure(bg=self.root.cget('bg'))
        win.transient(self.root)  # Faz a janela depender da principal
        win.grab_set()  # Impede interação com outras janelas
        self.root.wait_window(win)  # Espera a janela fechar

    def insert_header_logo(self, parent_frame):
        """Insere o logo reduzido no topo esquerdo e direito de um frame, com o título no centro.
           CORREÇÃO: Salva a referência da imagem no frame pai para evitar GC."""

        # Cria um frame container para o header inteiro
        header_container = ttk.Frame(parent_frame, style='Menu.TFrame', padding="10 10 10 10")
        header_container.pack(fill=tk.X, anchor=tk.N)

        logo_key = "header_logo_80x30"

        # 1. Carrega/Obtém a imagem (80x30)
        if logo_key not in self.logo_img_cache:
            self.logo_img_cache[logo_key] = self.load_logo(80, 30)
        img_ref = self.logo_img_cache[logo_key]

        # --- LADO ESQUERDO: LOGO + NOME ---

        # Cria o Label para exibir a imagem (ESQUERDA)
        l_left = ttk.Label(header_container, image=img_ref, style='Menu.TFrame')
        l_left.image = img_ref  # Solução CRÍTICA de cache
        l_left.pack(side=tk.LEFT, padx=10)

        # Título ao lado da logo
        ttk.Label(header_container, text=PROJECT_NAME, font=("Inter", 14, "bold"), background=HEADER_COLOR,
                  foreground=PRIMARY_COLOR).pack(side=tk.LEFT, padx=10)

        # --- LADO DIREITO: SOMENTE LOGO ---

        # Cria o Label para exibir a imagem (DIREITA)
        l_right = ttk.Label(header_container, image=img_ref, style='Menu.TFrame')
        l_right.image = img_ref  # Solução CRÍTICA de cache
        l_right.pack(side=tk.RIGHT, padx=10)

        # CORREÇÃO DEFINITIVA: Salvar a referência no frame principal da janela modal (parent_frame)
        # Isso garante que a imagem não seja descartada enquanto a janela estiver aberta.
        parent_frame.logo_ref_left = l_left.image
        parent_frame.logo_ref_right = l_right.image

    def center_window(self, win, geometry):
        """Método não mais necessário para janelas full screen, mas mantido por segurança."""
        pass

        # 1) Tela de Boas-vindas (Welcome)

    def build_welcome_screen(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding="40 80 40 40")
        frame.pack(fill=tk.BOTH, expand=True)

        logo = self.load_logo()
        logo_frame = ttk.Frame(frame);
        logo_frame.pack(pady=20)
        lbl_logo = ttk.Label(logo_frame, image=logo)
        lbl_logo.image = logo
        lbl_logo.pack()

        title = ttk.Label(frame, text=f"Bem-vindo(a) ao {PROJECT_NAME}", style='Title.TLabel')
        title.pack(pady=10)

        desc = ttk.Label(frame, text="Sistema de gerenciamento de performance e mecânica automotiva.",
                         style='Subtitle.TLabel', wraplength=700)
        desc.pack(pady=10)

        btn_login = ttk.Button(frame, text="Entrar (Login)", style='Primary.TButton', command=self.build_login_screen)
        btn_login.pack(pady=15)
        btn_register = ttk.Button(frame, text="Registrar Cliente", command=self.build_register_screen)
        btn_register.pack(pady=5)

        # Quick sample buttons (Nav Frame) - Atualizado para refletir a nova ordem
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(pady=20)
        ttk.Label(nav_frame, text="Navegação Rápida:", font=("Inter", 10, "bold"), foreground=PRIMARY_COLOR).grid(row=0,
                                                                                                                  column=0,
                                                                                                                  columnspan=4,
                                                                                                                  pady=8)
        ttk.Button(nav_frame, text="Dashboard", command=self.build_dashboard).grid(row=1, column=0, padx=6)
        ttk.Button(nav_frame, text="Cadastrar Peças", command=self.build_parts_screen).grid(row=1, column=1, padx=6)
        ttk.Button(nav_frame, text="Cadastrar Ferramentas", command=self.build_tools_screen).grid(row=1, column=2,
                                                                                                  padx=6)
        ttk.Button(nav_frame, text="Serviços", command=self.build_services_screen).grid(row=1, column=3, padx=6)

        footer = ttk.Label(frame, text=f"{PROJECT_NAME} • Simulação educacional • Dados fictícios", font=("Inter", 8),
                           foreground='#AAAAAA')
        footer.pack(side=tk.BOTTOM, pady=8)

    # 2) Tela de Login
    def build_login_screen(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding="40 80 40 40")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Acesso ao Sistema", style='Title.TLabel').pack(pady=10)
        ttk.Label(frame, text="Entre com suas credenciais de usuário.", style='Subtitle.TLabel').pack(pady=10)

        form = ttk.Frame(frame, padding=15)
        form.pack(pady=20, padx=20)

        # Ajuste: Configuração de cor do Entry
        entry_style = {'background': '#4A5360', 'foreground': TEXT_COLOR, 'insertbackground': PRIMARY_COLOR}
        self.style.configure('TEntry', **entry_style)

        ttk.Label(form, text="Usuário:", font=("Inter", 11)).grid(row=0, column=0, sticky=tk.W, padx=10, pady=8)
        # BUG FIX: Definindo foreground (cor do texto) diretamente no widget Entry
        user_entry = tk.Entry(form, width=30, **entry_style)
        user_entry.grid(row=0, column=1, pady=8, padx=10)

        ttk.Label(form, text="Senha:", font=("Inter", 11)).grid(row=1, column=0, sticky=tk.W, padx=10, pady=8)
        # BUG FIX: Definindo foreground (cor do texto) diretamente no widget Entry
        pass_entry = tk.Entry(form, show="*", width=30, **entry_style)
        pass_entry.grid(row=1, column=1, pady=8, padx=10)

        def attempt_login():
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            c = self.conn.cursor()
            c.execute("SELECT id,username,fullname,email,phone,role,photo FROM users WHERE username=? AND password=?",
                      (username, password))
            row = c.fetchone()
            if row:
                self.user = {
                    "id": row[0], "username": row[1], "fullname": row[2],
                    "email": row[3], "phone": row[4], "role": row[5], "photo": row[6]
                }
                messagebox.showinfo("Login", f"Bem-vindo(a), {self.user['fullname']} ({self.user['role']})")
                self.build_dashboard()
            else:
                messagebox.showerror("Login", "Usuário ou senha inválidos.")

        ttk.Button(frame, text="Entrar", style='Primary.TButton', command=attempt_login).pack(pady=15)
        ttk.Button(frame, text="Voltar", command=self.build_welcome_screen).pack()

    # 3) Tela de Registro de Cliente
    def build_register_screen(self):
        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20)  # Aumentar padding para full screen
        frame.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Registrar Novo Cliente", style='Subtitle.TLabel').pack(pady=10,
                                                                                      anchor=tk.W)  # Ajustar pady

        content_frame = ttk.Frame(frame);
        content_frame.pack(fill=tk.BOTH, expand=True)

        form = ttk.Frame(content_frame)
        form.pack(pady=8)

        # Ajuste: Configuração de cor do Entry
        entry_style = {'background': '#4A5360', 'foreground': TEXT_COLOR, 'insertbackground': PRIMARY_COLOR}

        labels = ["Usuário", "Senha", "Nome Completo", "Email", "Telefone", "Caminho Foto"]
        entries = []
        for i, lab in enumerate(labels):
            ttk.Label(form, text=lab + ":").grid(row=i, column=0, sticky=tk.E, padx=4, pady=4)
            # BUG FIX: Usando tk.Entry e aplicando o estilo diretamente
            e = tk.Entry(form, width=40, **entry_style)
            e.grid(row=i, column=1, pady=4)
            entries.append(e)

        def browse_photo():
            path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.gif"), ("Todos", "*.*")])
            if path:
                entries[5].delete(0, tk.END)
                entries[5].insert(0, path)

        ttk.Button(form, text="Procurar Foto", command=browse_photo).grid(row=5, column=2, padx=6)

        def register_client():
            vals = [e.get().strip() for e in entries]
            if not all(vals[:5]):
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.")
                return
            try:
                c = self.conn.cursor()
                c.execute(
                    "INSERT INTO users(username,password,fullname,email,phone,role,photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (vals[0], vals[1], vals[2], vals[3], vals[4], "client", vals[5]))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Cliente registrado com sucesso.")
                win.destroy()
                self.build_login_screen()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Usuário já existe.")

        ttk.Button(content_frame, text="Registrar", style='Primary.TButton', command=register_client).pack(pady=8)
        ttk.Button(content_frame, text="Fechar", command=win.destroy).pack()

        self.setup_modal_window(win, f"Registrar Cliente - {PROJECT_NAME}")

    # 4) Dashboard (após login)
    def build_dashboard(self):
        self.clear_root()

        # Header/Top Bar (Já tem logo)
        header = ttk.Frame(self.root, style='Menu.TFrame', padding="10 10 10 10")
        header.pack(fill=tk.X)

        logo = self.load_logo(120, 50)
        l = ttk.Label(header, image=logo, style='Menu.TFrame')
        l.image = logo
        l.pack(side=tk.LEFT, padx=10)

        user_str = f"Convidado" if not self.user else f"{self.user['fullname']} ({self.user['role']})"
        ttk.Label(header, text=f"DASHBOARD | Usuário: {user_str}", font=("Inter", 12, "bold"),
                  background=self.style.lookup('Menu.TFrame', 'background'), foreground=PRIMARY_COLOR).pack(
            side=tk.LEFT, padx=20, pady=5)
        ttk.Button(header, text="Sair", command=self.logout, width=10).pack(side=tk.RIGHT, padx=10)

        # Main Content Frame
        main_content = ttk.Frame(self.root, padding=20)
        main_content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_content, text="Visão Geral do Sistema", style='Title.TLabel').pack(pady=10, anchor=tk.W)

        # Stats Cards
        stats_frame = ttk.Frame(main_content)
        stats_frame.pack(fill=tk.X, pady=15)
        c = self.conn.cursor()

        # Consultas de dados
        c.execute("SELECT COUNT(*) FROM parts")
        parts_n = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM tools")
        tools_n = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users")
        users_n = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM services WHERE status='Aberto'")
        services_open_n = c.fetchone()[0]
        # NOVAS CONSULTAS PARA CARROS E MOTOS
        c.execute("SELECT COUNT(*) FROM cars")
        cars_n = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM motorcycles")
        motorcycles_n = c.fetchone()[0]

        def create_stat_card(parent, title, value, row, col):
            card = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1, padding=10, style='StatCard.TFrame')
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")  # Ajustado padx para 10
            parent.grid_columnconfigure(col, weight=1)
            ttk.Label(card, text=title, font=("Inter", 10), background='#3C4855', foreground='#AAAAAA').pack(
                anchor=tk.W)
            ttk.Label(card, text=str(value), font=("Inter", 20, "bold"), foreground=PRIMARY_COLOR,
                      background='#3C4855').pack(anchor=tk.W)

        self.style.configure('StatCard.TFrame', background='#3C4855', borderwidth=0, relief=tk.FLAT)

        # Layout com 6 Cards em 2 Linhas
        # Linha 1
        create_stat_card(stats_frame, "Peças Cadastradas", parts_n, 0, 0)
        create_stat_card(stats_frame, "Ferramentas em Estoque", tools_n, 0, 1)
        create_stat_card(stats_frame, "Usuários Totais", users_n, 0, 2)

        # Linha 2
        create_stat_card(stats_frame, "Carros Cadastrados", cars_n, 1, 0)  # NOVO
        create_stat_card(stats_frame, "Motos Cadastradas", motorcycles_n, 1, 1)  # NOVO
        create_stat_card(stats_frame, "Serviços Abertos", services_open_n, 1, 2)

        # Garante que a frame de estatísticas ocupe a largura total
        stats_frame.columnconfigure((0, 1, 2), weight=1)

        # Alerts
        c.execute("SELECT name, qty FROM parts ORDER BY qty ASC LIMIT 5")
        low = c.fetchall()
        sugg_frame = ttk.LabelFrame(main_content, text="⚠️ Alertas de Estoque Baixo", padding=15)
        sugg_frame.pack(fill=tk.X, padx=5, pady=20)
        lines = []
        for name, qty in low:
            if qty <= 5:
                lines.append(f"• Repor peça '{name}' (estoque: {qty} unidades)")
        if lines:
            ttk.Label(sugg_frame, text="\n".join(lines), foreground='#FF5555', font=("Inter", 10, 'bold'),
                      wraplength=700, justify=tk.LEFT).pack(padx=6, pady=6, anchor=tk.W)
        else:
            ttk.Label(sugg_frame, text="Estoque saudável no momento. Nenhum alerta pendente.",
                      foreground='#00FF00').pack(padx=6, pady=6, anchor=tk.W)

        # Navigation grid - LAYOUT ORIGINAL MANTIDO
        ttk.Label(main_content, text="Acessar Módulos", font=("Inter", 14, "bold"), foreground=TEXT_COLOR).pack(pady=10,
                                                                                                                anchor=tk.W)

        nav_grid = ttk.Frame(main_content, padding=10)
        nav_grid.pack(pady=10)

        # Ordem dos botões atualizada
        button_specs = [
            ("1. Cadastro de Peças", self.build_parts_screen),
            ("2. Cadastro de Ferramentas", self.build_tools_screen),
            ("3. Cadastro de Carros", self.build_car_screen),
            ("4. Cadastro de Motos", self.build_motorcycle_screen),
            ("5. Gestão de Usuários", self.build_user_management),
            ("6. Serviços (Ordens)", self.build_services_screen),
            ("7. Faturamento / Notas", self.build_invoices_screen),
            ("8. Relatórios de Gestão", self.build_reports_screen),
            ("9. Sobre / Contato", self.build_about_screen),
            ("10. Configurações", self.build_settings_screen),
            ("11. Ajuda / FAQ", self.build_help_screen),
        ]

        # Criando botões em 3 colunas
        for i, (text, command) in enumerate(button_specs):
            row = i // 3
            col = i % 3
            ttk.Button(nav_grid, text=text, width=30, command=command, style='TButton').grid(row=row, column=col,
                                                                                             padx=10, pady=8)

        footer = ttk.Label(main_content, text=f"© {PROJECT_NAME} - Sistema Didático 2025", font=("Inter", 8),
                           foreground='#AAAAAA')
        footer.pack(side=tk.BOTTOM, pady=10)

    # 5) Tela de cadastro de peças
    def build_parts_screen(self):
        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Gestão de Estoque de Peças", style='Title.TLabel').pack(pady=10, anchor=tk.W)

        content_frame = ttk.Frame(frame);
        content_frame.pack(fill=tk.BOTH, expand=True)  # Criar novo frame para conteúdo

        left = ttk.Frame(content_frame, padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right = ttk.Frame(content_frame, padding=10)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tree = ttk.Treeview(left, columns=("sku", "qty", "price"), show="headings")
        tree.heading("sku", text="SKU")
        tree.column("sku", width=120, anchor=tk.CENTER)
        tree.heading("qty", text="Qtd")
        tree.column("qty", width=80, anchor=tk.CENTER)
        tree.heading("price", text="Preço")
        tree.column("price", width=100, anchor=tk.E)
        tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_parts_tree(tree)

        # form in right
        ttk.Label(right, text="Adicionar / Atualizar Peça", style='Subtitle.TLabel').pack(pady=10)
        f_entries = {}
        form_fields = ["Nome", "SKU", "Quantidade", "Preço", "Descrição"]
        form_frame = ttk.Frame(right)
        form_frame.pack()

        # Ajuste: Configuração de cor do Entry
        entry_style = {'background': '#4A5360', 'foreground': TEXT_COLOR, 'insertbackground': PRIMARY_COLOR}

        for i, label in enumerate(form_fields):
            ttk.Label(form_frame, text=label + ":", font=("Inter", 10, 'bold')).grid(row=i, column=0, sticky=tk.W,
                                                                                     padx=5, pady=5)
            # BUG FIX: Usando tk.Entry e aplicando o estilo directamente
            e = tk.Entry(form_frame, width=35, **entry_style)
            e.grid(row=i, column=1, pady=5, padx=5)
            f_entries[label.lower()] = e

        def add_part():
            try:
                name = f_entries["nome"].get().strip()
                sku = f_entries["sku"].get().strip()
                qty = int(f_entries["quantidade"].get())
                price = float(f_entries["preço"].get().replace(",", "."))
                desc = f_entries["descrição"].get().strip()
                if not name or not sku:
                    raise ValueError("Nome e SKU obrigatórios.")
                c = self.conn.cursor()
                c.execute("INSERT INTO parts(name,sku,qty,price,description) VALUES (?, ?, ?, ?, ?)",
                          (name, sku, qty, price, desc))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Peça adicionada.")
                self.refresh_parts_tree(tree)
                for entry in f_entries.values(): entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(right, text="Adicionar Peça", style='Primary.TButton', command=add_part).pack(pady=15, fill=tk.X)
        ttk.Button(right, text="Fechar Janela", command=win.destroy).pack(pady=5, fill=tk.X)

        self.setup_modal_window(win, f"Cadastro de Peças - {PROJECT_NAME}")

    def refresh_parts_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute("SELECT name,sku,qty,price FROM parts")
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[1], row[2], format_currency(row[3])), text=row[0])

    # 6) Tela de cadastro de ferramentas
    def build_tools_screen(self):
        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Gestão de Ferramentas", style='Subtitle.TLabel').pack(pady=10, anchor=tk.W)

        tree = ttk.Treeview(frame, columns=("code", "available"), show="headings")
        tree.heading("code", text="Código")
        tree.column("code", width=120, anchor=tk.CENTER)
        tree.heading("available", text="Disponível")
        tree.column("available", width=100, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # form
        form = ttk.Frame(win, padding=10)
        form.pack(pady=6)

        # Ajuste: Configuração de cor do Entry
        entry_style = {'background': '#4A5360', 'foreground': TEXT_COLOR, 'insertbackground': PRIMARY_COLOR}

        ttk.Label(form, text="Nome:").grid(row=0, column=0, padx=4, pady=4, sticky=tk.W)
        # BUG FIX: Usando tk.Entry e aplicando o estilo diretamente
        name_e = tk.Entry(form, width=30, **entry_style);
        name_e.grid(row=0, column=1)

        ttk.Label(form, text="Código:").grid(row=1, column=0, padx=4, pady=4, sticky=tk.W)
        # BUG FIX: Usando tk.Entry e aplicando o estilo directamente
        code_e = tk.Entry(form, width=30, **entry_style);
        code_e.grid(row=1, column=1)

        ttk.Label(form, text="Quantidade:").grid(row=2, column=0, padx=4, pady=4, sticky=tk.W)
        # BUG FIX: Usando tk.Entry e aplicando o estilo directamente
        qty_e = tk.Entry(form, width=30, **entry_style);
        qty_e.grid(row=2, column=1)

        def add_tool():
            try:
                name = name_e.get().strip()
                code = code_e.get().strip()
                qty = int(qty_e.get())
                if not name or not code:
                    raise ValueError("Nome e código obrigatórios.")
                c = self.conn.cursor()
                c.execute("INSERT INTO tools(name,code,available,description) VALUES (?, ?, ?, ?)",
                          (name, code, qty, ""))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Ferramenta adicionada.")
                self.refresh_tools_tree(tree)
                name_e.delete(0, tk.END);
                code_e.delete(0, tk.END);
                qty_e.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(form, text="Adicionar Ferramenta", style='Primary.TButton', command=add_tool).grid(row=3, column=0,
                                                                                                      columnspan=2,
                                                                                                      pady=10)
        ttk.Button(form, text="Fechar", command=win.destroy).grid(row=4, column=0, columnspan=2, pady=4)
        self.refresh_tools_tree(tree)

        self.setup_modal_window(win, f"Cadastro de Ferramentas - {PROJECT_NAME}")

    def refresh_tools_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute("SELECT name,code,available FROM tools")
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[1], row[2]), text=row[0])

    # 7) Tela de Cadastro de Carros (NOVA)
    def build_car_screen(self):
        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20);
        frame.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Cadastro de Carros", style='Title.TLabel').pack(pady=10, anchor=tk.W)
        ttk.Label(frame, text="A Placa é a chave única do veículo e está atrelada ao ID numérico do cliente.",
                  font=("Inter", 10)).pack(pady=5, anchor=tk.W)  # Informação para o usuário

        # Treeview para exibir carros
        tree = ttk.Treeview(frame, columns=("client", "plate", "model", "year", "color", "engine"),
                            show="headings")  # NOVAS COLUNAS
        tree.heading("client", text="Dono (Usuário)")
        tree.column("client", width=120, anchor=tk.CENTER)
        tree.heading("plate", text="Placa (Chave Única)")
        tree.column("plate", width=100, anchor=tk.CENTER)
        tree.heading("model", text="Marca/Modelo")
        tree.column("model", width=180)  # Ajustado largura
        tree.heading("year", text="Ano")  # NOVO
        tree.column("year", width=60, anchor=tk.CENTER)  # NOVO
        tree.heading("color", text="Cor")  # NOVO
        tree.column("color", width=100, anchor=tk.CENTER)  # NOVO
        tree.heading("engine", text="Motor (L)")  # NOVO
        tree.column("engine", width=100, anchor=tk.CENTER)  # NOVO
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.refresh_cars_tree(tree)

        # Formulário de Cadastro
        form = ttk.Frame(frame, padding=10)
        form.pack(pady=10)

        # PLACA E USERNAME (Chave de busca para FK)
        fields = ["Dono (usuário)", "Placa", "Marca", "Modelo", "Ano", "Cor", "Motor (L)"]
        entries = {}

        # Ajuste: Configuração de cor do Entry
        entry_style = {'background': '#4A5360', 'foreground': TEXT_COLOR, 'insertbackground': PRIMARY_COLOR}

        for i, field in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(form, text=field + ":").grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)
            # BUG FIX: Usando tk.Entry e aplicando o estilo diretamente
            e = tk.Entry(form, width=20, **entry_style)
            e.grid(row=row, column=col + 1, padx=10, pady=5)
            entries[field.lower().replace(" ", "_").replace("(", "").replace(")", "")] = e

        def add_car():
            vals = {k: v.get().strip() for k, v in entries.items()}
            # Validação: Usuário e Placa são críticos
            if not all([vals['dono_usuario'], vals['placa']]):
                messagebox.showwarning("Atenção", "Usuário do Dono e Placa são obrigatórios para o cadastro.")
                return

            c = self.conn.cursor()
            try:
                # 1. Busca o client_id usando o username
                c.execute("SELECT id FROM users WHERE username=?", (vals['dono_usuario'],))
                client_row = c.fetchone()
                if not client_row:
                    messagebox.showerror("Erro", "Cliente (usuário) não encontrado. Cadastre o cliente primeiro.")
                    return
                client_id = client_row[0]  # Este é o ID (a Chave Estrangeira)

                # 2. Insere o carro usando o client_id (Chave Estrangeira)
                c.execute(
                    "INSERT INTO cars(client_id, license_plate, brand, model, year, color, engine) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (client_id, vals['placa'], vals['marca'], vals['modelo'], vals['ano'] or None, vals['cor'],
                     vals['motor_l']))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Carro cadastrado com sucesso e atrelado ao cliente.")
                self.refresh_cars_tree(tree)
                for entry in entries.values(): entry.delete(0, tk.END)
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Placa já cadastrada.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")

        ttk.Button(frame, text="Cadastrar Carro", style='Primary.TButton', command=add_car).pack(pady=10)
        ttk.Button(frame, text="Fechar", command=win.destroy).pack()

        self.setup_modal_window(win, f"Cadastro de Carros - {PROJECT_NAME}")

    def refresh_cars_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        # Consulta que agora inclui todos os campos relevantes
        c.execute('''
                  SELECT c.license_plate,
                         c.brand,
                         c.model,
                         c.year,
                         c.color,
                         c.engine,
                         u.username
                  FROM cars c
                           LEFT JOIN users u ON c.client_id = u.id
                  ORDER BY c.brand, c.model
                  ''')
        for row in c.fetchall():
            plate, brand, model, year, color, engine, username = row
            # Insere todos os dados nas colunas correspondentes
            tree.insert("", tk.END, values=(username, plate, f"{brand} {model}", year, color, engine))

    # 8) Tela de Cadastro de Motos (NOVA)
    def build_motorcycle_screen(self):
        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20);
        frame.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Cadastro de Motos", style='Title.TLabel').pack(pady=10, anchor=tk.W)
        ttk.Label(frame, text="A Placa é a chave única da moto e está atrelada ao ID numérico do cliente.",
                  font=("Inter", 10)).pack(pady=5, anchor=tk.W)  # Informação para o usuário

        # Treeview para exibir motos
        tree = ttk.Treeview(frame, columns=("client", "plate", "model", "year", "cc"), show="headings")  # NOVAS COLUNAS
        tree.heading("client", text="Dono (Usuário)")
        tree.column("client", width=120, anchor=tk.CENTER)
        tree.heading("plate", text="Placa (Chave Única)")
        tree.column("plate", width=100, anchor=tk.CENTER)
        tree.heading("model", text="Marca/Modelo")
        tree.column("model", width=150)
        tree.heading("year", text="Ano")  # NOVO
        tree.column("year", width=80, anchor=tk.CENTER)  # NOVO
        tree.heading("cc", text="Cilindrada (CC)")
        tree.column("cc", width=100, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.refresh_motorcycles_tree(tree)

        # Formulário de Cadastro
        form = ttk.Frame(frame, padding=10)
        form.pack(pady=10)

        fields = ["Dono (usuário)", "Placa", "Marca", "Modelo", "Ano", "Cilindrada (CC)"]
        entries = {}

        # Ajuste: Configuração de cor do Entry
        entry_style = {'background': '#4A5360', 'foreground': TEXT_COLOR, 'insertbackground': PRIMARY_COLOR}

        for i, field in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(form, text=field + ":").grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)
            # BUG FIX: Usando tk.Entry e aplicando o estilo diretamente
            e = tk.Entry(form, width=20, **entry_style)
            e.grid(row=row, column=col + 1, padx=10, pady=5)
            entries[field.lower().replace(" ", "_").replace("(", "").replace(")", "")] = e

        def add_motorcycle():
            vals = {k: v.get().strip() for k, v in entries.items()}
            # Validação: Usuário e Placa são críticos
            if not all([vals['dono_usuario'], vals['placa']]):
                messagebox.showwarning("Atenção", "Usuário do Dono e Placa são obrigatórios para o cadastro.")
                return

            c = self.conn.cursor()
            try:
                # 1. Busca o client_id usando o username
                c.execute("SELECT id FROM users WHERE username=?", (vals['dono_usuario'],))
                client_row = c.fetchone()
                if not client_row:
                    messagebox.showerror("Erro", "Cliente (usuário) não encontrado. Cadastre o cliente primeiro.")
                    return
                client_id = client_row[0]  # Este é o ID (a Chave Estrangeira)
                engine_cc = int(vals['cilindrada_cc']) if vals.get('cilindrada_cc') else None

                # 2. Insere a moto usando o client_id (Chave Estrangeira)
                c.execute(
                    "INSERT INTO motorcycles(client_id, license_plate, brand, model, year, engine_cc) VALUES (?, ?, ?, ?, ?, ?)",
                    (client_id, vals['placa'], vals['marca'], vals['modelo'], vals['ano'] or None, engine_cc))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Moto cadastrada com sucesso e atrelada ao cliente.")
                self.refresh_motorcycles_tree(tree)
                for entry in entries.values(): entry.delete(0, tk.END)
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Placa já cadastrada.")
            except ValueError:
                messagebox.showerror("Erro", "Cilindrada deve ser um número inteiro.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")

        ttk.Button(frame, text="Cadastrar Moto", style='Primary.TButton', command=add_motorcycle).pack(pady=10)
        ttk.Button(frame, text="Fechar", command=win.destroy).pack()

        self.setup_modal_window(win, f"Cadastro de Motos - {PROJECT_NAME}")

    def refresh_motorcycles_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        # Consulta que agora inclui todos os campos relevantes
        c.execute('''
                  SELECT m.license_plate,
                         m.brand,
                         m.model,
                         m.year,
                         m.engine_cc,
                         u.username
                  FROM motorcycles m
                           LEFT JOIN users u ON m.client_id = u.id
                  ORDER BY m.brand, m.model
                  ''')
        for row in c.fetchall():
            plate, brand, model, year, cc, username = row
            # Insere todos os dados nas colunas correspondentes
            tree.insert("", tk.END, values=(username, plate, f"{brand} {model}", year, cc))

    # 9) Tela de Gerenciamento de Usuários (agora é a 5)
    def build_user_management(self):
        if not self.user or self.user["role"] != "admin":
            messagebox.showwarning("Acesso", "Apenas administradores podem acessar o gerenciamento de usuários.")
            return
        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20);
        frame.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Gestão de Usuários (Apenas Admin)", style='Subtitle.TLabel').pack(pady=10, anchor=tk.W)

        tree = ttk.Treeview(frame, columns=("username", "email", "phone", "role"), show="headings")
        tree.heading("username", text="Usuário")
        tree.heading("email", text="Email")
        tree.heading("phone", text="Telefone")
        tree.heading("role", text="Função")
        tree.column("username", width=120, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_users_tree(tree)

        def remove_user():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Info", "Selecione um usuário.")
                return
            item = tree.item(sel[0])
            username = item["values"][0]

            if self.user and username == self.user["username"]:
                messagebox.showwarning("Aviso", "Você não pode remover a si mesmo.")
                return

            # Usando custom modal (messagebox.askyesno) para evitar o uso de tk.confirm()
            if messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o usuário {username}?"):
                c = self.conn.cursor()
                c.execute("DELETE FROM users WHERE username=?", (username,))
                self.conn.commit()
                self.refresh_users_tree(tree)
                messagebox.showinfo("OK", "Usuário removido.")

        ttk.Button(frame, text="Remover Usuário Selecionado", command=remove_user).pack(pady=10)
        ttk.Button(frame, text="Fechar", command=win.destroy).pack()

        self.setup_modal_window(win, f"Gerenciamento de Usuários - {PROJECT_NAME}")

    def refresh_users_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute("SELECT username,email,phone,role FROM users")
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3]), text=row[0])

    # ATENÇÃO: A função build_os_tools_screen foi removida para simplificar o fluxo.

    # 10) Tela de Serviços (Ordens - agora é a 6) - FLUXO CARRINHO
    def build_services_screen(self):
        # Limpa o carrinho temporário toda vez que a tela principal de serviços é aberta
        self.os_cart = {}

        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20);
        frame.pack(fill=tk.BOTH, expand=True)  # Aumentar padding

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Ordem de Serviço (Ponto de Venda)", style='Subtitle.TLabel').pack(pady=10,
                                                                                                 anchor=tk.W)  # Aumentar pady

        # --- Estrutura de Duas Colunas ---
        main_content = ttk.Frame(frame);
        main_content.pack(fill=tk.BOTH, expand=True)
        left_frame = ttk.Frame(main_content, padding=10);
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        right_frame = ttk.Frame(main_content, padding=10);
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        entry_style = {'background': '#4A5360', 'foreground': TEXT_COLOR, 'insertbackground': PRIMARY_COLOR}

        # ----------------------------------------------------
        # --- COLUNA DA ESQUERDA: DADOS DA OS E CARRINHO ---
        # ----------------------------------------------------

        # --- 1. Dados Principais da OS ---
        os_data_frame = ttk.LabelFrame(left_frame, text="1. Dados da OS e Cliente", padding=10)
        os_data_frame.pack(fill=tk.X, pady=10)

        form_grid = ttk.Frame(os_data_frame)
        form_grid.pack(fill=tk.X)

        ttk.Label(form_grid, text="Cliente (usuário):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        client_e = tk.Entry(form_grid, **entry_style);
        client_e.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(form_grid, text="Placa do Veículo:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        plate_e = tk.Entry(form_grid, **entry_style);
        plate_e.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(form_grid, text="Vendedor (Atendente):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        seller_name = self.user['fullname'] if self.user else "Convidado"
        ttk.Label(form_grid, text=seller_name, font=('Inter', 10, 'bold'), foreground=PRIMARY_COLOR).grid(row=1,
                                                                                                          column=1,
                                                                                                          padx=5,
                                                                                                          pady=5,
                                                                                                          sticky=tk.W)

        ttk.Label(form_grid, text="Mão de Obra (R$):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        mo_e = tk.Entry(form_grid, **entry_style);
        mo_e.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        mo_e.insert(0, "0.00")

        ttk.Label(form_grid, text="Descrição:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        desc_e = tk.Entry(form_grid, width=40, **entry_style);
        desc_e.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)

        # --- 2. Carrinho (Treeview de Itens da OS) ---
        ttk.Label(left_frame, text="2. Peças para Ordem de Serviço:", font=('Inter', 11, 'bold')).pack(pady=10,
                                                                                                       anchor=tk.W)

        cart_tree = ttk.Treeview(left_frame, columns=("qty", "unit_price", "subtotal"), show="headings")
        cart_tree.heading("qty", text="Qtd")
        cart_tree.column("qty", width=80, anchor=tk.CENTER)
        cart_tree.heading("unit_price", text="Preço Unitário")
        cart_tree.column("unit_price", width=120, anchor=tk.E)
        cart_tree.heading("subtotal", text="Subtotal")
        cart_tree.column("subtotal", width=120, anchor=tk.E)
        cart_tree.pack(fill=tk.BOTH, expand=True)

        # --- Footer do Carrinho (Total) ---
        footer_frame = ttk.Frame(left_frame);
        footer_frame.pack(fill=tk.X, pady=10)
        ttk.Label(footer_frame, text="Total das Peças:", font=('Inter', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        total_items_lbl = ttk.Label(footer_frame, text=format_currency(0.0), font=('Inter', 11, 'bold'),
                                    foreground=PRIMARY_COLOR)
        total_items_lbl.pack(side=tk.LEFT, padx=5)

        # --- Botão de Remoção ---
        def remove_from_cart():
            sel = cart_tree.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione um item no carrinho para remover.")
                return

            # O texto (text) do item da Treeview armazena o SKU/Nome da Peça
            part_id = cart_tree.item(sel[0], 'text')

            # Remove do dicionário e da Treeview
            if part_id in self.os_cart:
                del self.os_cart[part_id]
            cart_tree.delete(sel[0])
            update_cart_summary()

        ttk.Button(footer_frame, text="Remover Item Selecionado", command=remove_from_cart).pack(side=tk.RIGHT, padx=5)

        def update_cart_summary():
            """Recalcula e atualiza o Treeview do carrinho e o total das peças."""
            # Limpa o Treeview primeiro
            for item in cart_tree.get_children():
                cart_tree.delete(item)

            total = 0.0

            for part_id, data in self.os_cart.items():
                subtotal = data['qty'] * data['price']
                total += subtotal

                # O text é o ID da peça para fácil manipulação interna
                cart_tree.insert("", tk.END, text=part_id,
                                 values=(data['qty'], format_currency(data['price']), format_currency(subtotal)))

            total_items_lbl.config(text=format_currency(total))

            # Retorna o total das peças para a função de abertura da OS
            return total

        # --- 3. Botão de Abertura da OS ---
        def open_service_order():
            cl_user = client_e.get().strip()
            plate = plate_e.get().strip()
            desc = desc_e.get().strip()

            try:
                mo_price = float(mo_e.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Valor de Mão de Obra inválido.")
                return

            if not self.os_cart and mo_price == 0.0:
                messagebox.showwarning("Atenção", "A OS está vazia. Adicione peças ou o valor da Mão de Obra.")
                return

            client_id, error = self.check_vehicle_and_client(cl_user, plate)
            if error:
                messagebox.showerror("Erro de Cadastro", error)
                return

            date = datetime.date.today().isoformat()

            try:
                c = self.conn.cursor()

                # 1. Abre a OS no Banco
                c.execute(
                    "INSERT INTO services(client_id, vehicle_plate, description, labor_price, final_total, date, status, seller_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (client_id, plate, desc, mo_price, 0.0, date, "Aberto", seller_name))
                self.conn.commit()
                new_service_id = c.lastrowid

                # 2. Insere todos os itens do carrinho (peças)
                for part_id, data in self.os_cart.items():
                    c.execute(
                        "INSERT INTO service_parts (service_id, part_id, qty_used, price_unit) VALUES (?, ?, ?, ?)",
                        (new_service_id, part_id, data['qty'], data['price']))
                self.conn.commit()

                messagebox.showinfo("Sucesso",
                                    f"Ordem de Serviço #OS-{new_service_id} criada e peças registradas. Total (aprox.): {format_currency(mo_price + update_cart_summary())}")

                win.destroy()  # Fecha a janela após sucesso
                self.build_dashboard()  # Atualiza o Dashboard ou abre a tela de OS principal

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir OS: {str(e)}")

        ttk.Button(left_frame, text=f"Abrir Ordem de Serviço ({seller_name})", style='Primary.TButton',
                   command=open_service_order).pack(pady=15, fill=tk.X)

        # O botão "Registrar Uso de Ferramentas (Interno)" foi removido.
        ttk.Button(left_frame, text="Fechar Janela", command=win.destroy).pack(pady=5, fill=tk.X)

        # ----------------------------------------------------
        # --- COLUNA DA DIREITA: CATÁLOGO DE PEÇAS ---
        # ----------------------------------------------------

        ttk.Label(right_frame, text="3. Catálogo de Peças (Adicionar ao Carrinho)", style='Subtitle.TLabel').pack(
            pady=10, anchor=tk.W)

        # Treeview do Catálogo
        catalog_tree = ttk.Treeview(right_frame, columns=("sku", "qty", "price"), show="headings")
        catalog_tree.heading("sku", text="SKU")
        catalog_tree.column("sku", width=100, anchor=tk.CENTER)
        catalog_tree.heading("qty", text="Qtd Estoque")
        catalog_tree.column("qty", width=100, anchor=tk.CENTER)
        catalog_tree.heading("price", text="Preço Unitário")
        catalog_tree.column("price", width=120, anchor=tk.E)
        catalog_tree.pack(fill=tk.BOTH, expand=True)

        def refresh_catalog_tree(tree):
            for r in tree.get_children(): tree.delete(r)
            c = self.conn.cursor()
            c.execute("SELECT id, name, sku, qty, price FROM parts ORDER BY name")
            for id, name, sku, qty, price in c.fetchall():
                # text guarda o ID da peça
                tree.insert("", tk.END, text=id, values=(sku, qty, format_currency(price)))

        refresh_catalog_tree(catalog_tree)

        # --- Formulário de Adição ao Carrinho ---
        add_form = ttk.Frame(right_frame, padding=10);
        add_form.pack(fill=tk.X, pady=10)

        ttk.Label(add_form, text="Qtd a Adicionar:").grid(row=0, column=0, padx=5)
        add_qty_e = tk.Entry(add_form, width=10, **entry_style);
        add_qty_e.grid(row=0, column=1, padx=5)

        def add_item_to_os():
            sel = catalog_tree.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione uma peça no catálogo à direita.")
                return

            item = catalog_tree.item(sel[0])
            part_id = int(item['text'])  # ID real da peça no banco
            part_sku = item['values'][0]  # SKU
            qty_available = int(item['values'][1])
            part_price_str = item['values'][2].replace('R$ ', '').replace('.', '').replace(',', '.')  # Preço formatado
            part_price = float(part_price_str)

            try:
                qty_to_add = int(add_qty_e.get().strip())
                if qty_to_add <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida (deve ser um número inteiro > 0).")
                return

            # Lógica de "carrinho" (não checa estoque aqui, a baixa é no Faturamento)

            # Busca o nome da peça no carrinho para fácil remoção
            c = self.conn.cursor()
            c.execute("SELECT name FROM parts WHERE id=?", (part_id,))
            name = c.fetchone()[0]

            if part_id in self.os_cart:
                # Se já existe, aumenta a quantidade
                self.os_cart[part_id]['qty'] += qty_to_add
            else:
                # Se não existe, adiciona
                self.os_cart[part_id] = {'name': name, 'sku': part_sku, 'qty': qty_to_add, 'price': part_price}

            add_qty_e.delete(0, tk.END)
            add_qty_e.insert(0, "1")

            update_cart_summary()

        ttk.Button(add_form, text="Adicionar ao Carrinho", style='Primary.TButton', command=add_item_to_os).grid(row=0,
                                                                                                                 column=2,
                                                                                                                 padx=10)

        add_qty_e.insert(0, "1")  # Valor inicial 1

        self.setup_modal_window(win, f"Serviços - Abertura de OS - {PROJECT_NAME}")

    def check_vehicle_and_client(self, username, plate):
        c = self.conn.cursor()
        c.execute("SELECT id FROM users WHERE username=?", (username,))
        user_row = c.fetchone()
        if not user_row:
            return None, "Cliente (usuário) não encontrado."
        client_id = user_row[0]

        # Verifica se a placa pertence a um carro OU moto
        c.execute(
            "SELECT client_id FROM cars WHERE license_plate=? UNION SELECT client_id FROM motorcycles WHERE license_plate=?",
            (plate, plate))
        vehicle_row = c.fetchone()
        if not vehicle_row:
            return None, "Veículo com a placa informada não está cadastrado."

        if vehicle_row[0] != client_id:
            return None, "O veículo não pertence ao cliente (usuário) informado."

        return client_id, None

    def refresh_services_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute('''
                  SELECT s.id, u.username, s.vehicle_plate, s.labor_price, s.final_total, s.date, s.status
                  FROM services s
                           LEFT JOIN users u ON s.client_id = u.id
                  ORDER BY s.date DESC
                  ''')
        for row in c.fetchall():
            # ID, Username, Placa, Labor_Price, Final_Total, Date, Status
            tree.insert("", tk.END,
                        values=(row[1], row[2], format_currency(row[3]), format_currency(row[4]), row[5], row[6]),
                        text=str(row[0]))

    # --- NOVO FLUXO PARA ATUALIZAR ESTOQUE E GERAR FATURA ---
    def update_stock_and_invoice(self, service_id, is_paid):
        c = self.conn.cursor()

        # 1. CALCULA O TOTAL DA OS (Mão de Obra + Peças)
        c.execute("SELECT labor_price FROM services WHERE id=?", (service_id,))
        mo_price = c.fetchone()[0] or 0.0

        c.execute("SELECT part_id, qty_used, price_unit FROM service_parts WHERE service_id=?", (service_id,))
        parts_used = c.fetchall()

        parts_total = sum(qty * price for _, qty, price in parts_used)
        final_total = mo_price + parts_total

        # 2. VALIDA E DÁ BAIXA NO ESTOQUE
        # Verifica se há estoque suficiente antes de fazer qualquer baixa
        for part_id, qty_used, _ in parts_used:
            c.execute("SELECT qty FROM parts WHERE id=?", (part_id,))
            qty_available = c.fetchone()
            if not qty_available or qty_used > qty_available[0]:
                c.execute("SELECT sku FROM parts WHERE id=?", (part_id,))
                sku = c.fetchone()[0]
                return False, f"Estoque insuficiente para a peça SKU {sku}. Necessário: {qty_used}, Disponível: {qty_available[0] if qty_available else 0}"

        try:
            # Baixa no estoque
            for part_id, qty_used, _ in parts_used:
                c.execute("UPDATE parts SET qty = qty - ? WHERE id=?", (qty_used, part_id))

            # 3. ATUALIZA O TOTAL DA OS E STATUS PARA FECHADO
            c.execute("UPDATE services SET final_total = ?, status = 'Fechado' WHERE id=?", (final_total, service_id))

            # 4. GERA A FATURA
            date = datetime.date.today().isoformat()
            c.execute("INSERT INTO invoices(service_id, total, date, paid) VALUES (?, ?, ?, ?)",
                      (service_id, final_total, date, 1 if is_paid else 0))

            self.conn.commit()
            return True, final_total

        except Exception as e:
            self.conn.rollback()
            return False, f"Erro ao processar estoque/fatura: {str(e)}"

    # 11) Tela de Faturamento / Invoices (agora é a 7)
    def build_invoices_screen(self):
        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20);
        frame.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Registro de Faturas", style='Subtitle.TLabel').pack(pady=10, anchor=tk.W)

        # Treeview para mostrar SERVIÇOS ABERTOS prontos para faturamento
        ttk.Label(frame, text="Serviços Abertos Prontos para Faturar:", font=("Inter", 10, 'bold')).pack(pady=5,
                                                                                                         anchor=tk.W)

        # Tabela de Serviços Abertos
        open_services_tree = ttk.Treeview(frame, columns=("client", "plate", "date", "mo_price"), show="headings")
        open_services_tree.heading("client", text="Cliente (Usuário)")
        open_services_tree.column("client", width=100, anchor=tk.CENTER)
        open_services_tree.heading("plate", text="Placa")
        open_services_tree.column("plate", width=100, anchor=tk.CENTER)
        open_services_tree.heading("date", text="Data Abertura")
        open_services_tree.column("date", width=100, anchor=tk.CENTER)
        open_services_tree.heading("mo_price", text="M.O. (R$)")
        open_services_tree.column("mo_price", width=100, anchor=tk.E)
        open_services_tree.pack(fill=tk.X, pady=5, padx=5)

        def refresh_open_services_tree(tree):
            for r in tree.get_children(): tree.delete(r)
            c = self.conn.cursor()
            # Mostra serviços que estão abertos E AINDA NÃO FORAM FATURADOS
            c.execute('''
                      SELECT s.id, u.username, s.vehicle_plate, s.labor_price, s.date
                      FROM services s
                               JOIN users u ON s.client_id = u.id
                               LEFT JOIN invoices i ON s.id = i.service_id
                      WHERE s.status = 'Aberto'
                        AND i.service_id IS NULL
                      ORDER BY s.date DESC
                      ''')
            for row in c.fetchall():
                # o campo labor_price é o preço inicial da mão de obra
                tree.insert("", tk.END, values=(row[1], row[2], row[4], format_currency(row[3])), text=str(row[0]))

        refresh_open_services_tree(open_services_tree)

        # FORMULÁRIO DE GERAÇÃO DE FATURA
        form = ttk.Frame(frame);
        form.pack(pady=15)

        paid_var = tk.IntVar()
        ttk.Checkbutton(form, text="Pagamento Recebido (Marcar como Pago)", variable=paid_var).pack(pady=5)

        def generate_invoice():
            sel = open_services_tree.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione um Serviço na lista para gerar a fatura.")
                return

            service_id = open_services_tree.item(sel[0], "text")
            is_paid = paid_var.get()

            success, result = self.update_stock_and_invoice(service_id, is_paid)

            if success:
                final_total = result
                messagebox.showinfo("Sucesso",
                                    f"Fatura para OS #{service_id} gerada.\nTotal (M.O. + Peças): {format_currency(final_total)}\nEstoque atualizado com sucesso.")
                refresh_open_services_tree(open_services_tree)  # Remove da lista de abertos
                self.refresh_invoices_tree(invoices_tree)  # Adiciona na lista de faturas

                # Atualiza a tabela na tela de Serviços
                # Verifica se a janela de Serviços ainda está aberta para atualizar o treeview
                try:
                    services_window = next(w for w in self.root.winfo_children() if
                                           isinstance(w, tk.Toplevel) and w.title().startswith(
                                               f"Serviços - Abertura de OS"))
                    services_tree = services_window.winfo_children()[0].winfo_children()[1]
                    self.refresh_services_tree(services_tree)
                except StopIteration:
                    pass  # Janela de Serviços não está aberta

                self.build_dashboard()  # Atualiza o dashboard com novo estoque
            else:
                messagebox.showerror("Erro de Faturamento", f"Falha ao gerar fatura ou atualizar estoque:\n{result}")

        ttk.Button(form, text="Gerar Fatura e Dar Baixa no Estoque", style='Primary.TButton',
                   command=generate_invoice).pack(pady=10)

        # Tabela de Faturas Geradas
        ttk.Label(frame, text="Faturas Geradas:", font=("Inter", 10, 'bold')).pack(pady=5, anchor=tk.W)
        invoices_tree = ttk.Treeview(frame, columns=("service", "total", "date", "paid"), show="headings")
        invoices_tree.heading("service", text="Serviço ID")
        invoices_tree.column("service", width=100, anchor=tk.CENTER)
        invoices_tree.heading("total", text="Total")
        invoices_tree.column("total", width=100, anchor=tk.E)
        invoices_tree.heading("date", text="Data")
        invoices_tree.column("date", width=100, anchor=tk.CENTER)
        invoices_tree.heading("paid", text="Pago")
        invoices_tree.column("paid", width=80, anchor=tk.CENTER)
        invoices_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.refresh_invoices_tree(invoices_tree)

        ttk.Button(frame, text="Fechar Janela", command=win.destroy).pack(pady=5)

        self.setup_modal_window(win, f"Faturamento - {PROJECT_NAME}")

    def refresh_invoices_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute("SELECT id, service_id, total, date, paid FROM invoices ORDER BY date DESC")
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[1], format_currency(row[2]), row[3], "Sim" if row[4] else "Não"),
                        text=str(row[0]))

    # 12) Relatórios (simples) (agora é a 8)
    def build_reports_screen(self):
        win = tk.Toplevel(self.root)

        frame = ttk.Frame(win, padding=20);
        frame.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(frame)  # INSERIR LOGO

        ttk.Label(frame, text="Relatórios Rápidos", style='Subtitle.TLabel').pack(pady=10, anchor=tk.W)

        # Text widget com fundo dark
        rpt = tk.Text(frame, height=18, bg='#3C4855', fg='#FFFFFF', insertbackground=PRIMARY_COLOR)
        rpt.pack(fill=tk.BOTH, expand=True)

        # Gerar relatório com dados resumo
        c = self.conn.cursor()
        c.execute(
            "SELECT COUNT(*), SUM(final_total) FROM services WHERE status='Fechado'")  # Soma apenas serviços fechados (faturados)
        services_cnt, services_sum = c.fetchone()
        services_sum = services_sum or 0.0
        c.execute("SELECT COUNT(*), SUM(total) FROM invoices")
        inv_cnt, inv_sum = c.fetchone()
        inv_sum = inv_sum or 0.0
        report_text = f"""
RELATÓRIO DE GESTÃO - {PROJECT_NAME}
------------------------------------------------------
Data de geração: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}
------------------------------------------------------

1. VISÃO GERAL DE SERVIÇOS
Total de serviços fechados/faturados: {services_cnt}
Receita de M.O. e Peças Vendidas (Serviços Fechados): {format_currency(services_sum)}

2. VISÃO GERAL DE FATURAMENTO
Total de faturas geradas: {inv_cnt}
Receita faturada (Total das Faturas): {format_currency(inv_sum)}

3. OBSERVAÇÕES E ALERTAS
- Verificar peças com estoque baixo no Dashboard.
- Conferir ferramentas emprestadas/indisponíveis.
"""
        rpt.insert("1.0", report_text)
        ttk.Button(frame, text="Fechar", command=win.destroy).pack(pady=10)

        self.setup_modal_window(win, f"Relatórios - {PROJECT_NAME}")

    # 13) Fluxograma (REMOVIDA, era a 7)

    # 14) Wireframe (REMOVIDA, era a 8)

    # 15) Sobre / Contato (agora é a 9)
    def build_about_screen(self):
        win = tk.Toplevel(self.root)

        f = ttk.Frame(win, padding=20);
        f.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(f)  # INSERIR LOGO

        ttk.Label(f, text=PROJECT_NAME, style='Subtitle.TLabel').pack(pady=10)

        # --- NOVAS INFORMAÇÕES DE CONTATO ---
        ttk.Label(f,
                  text="Sistema de gestão focado em performance e mecânica automotiva\n\"De zero a cem em confiança\"",
                  justify=tk.CENTER).pack(pady=10)

        ttk.Label(f, text="☎️ Telefone: (11) 3456 7890", justify=tk.CENTER).pack(pady=5)
        ttk.Label(f, text="📧 E-mail: mcmarcelinhojogaador@gmail.com", justify=tk.CENTER).pack(pady=5)
        ttk.Label(f, text="🌐 Website: www.memtunning.com.br", justify=tk.CENTER).pack(pady=5)
        ttk.Label(f, text="📍 Endereço: Avenida Guarapiranga Jose Benedito 110", justify=tk.CENTER).pack(pady=5)

        ttk.Button(f, text="Fechar", command=win.destroy).pack(pady=15)

        self.setup_modal_window(win, f"Sobre / Contato - {PROJECT_NAME}")

    # 16) Configurações (agora é a 10)
    def build_settings_screen(self):
        win = tk.Toplevel(self.root)

        f = ttk.Frame(win, padding=20);
        f.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(f)  # INSERIR LOGO

        ttk.Label(f, text="Configurações Gerais", style='Subtitle.TLabel').pack(pady=10, anchor=tk.W)
        ttk.Label(f, text="Alterar logo (substituir arquivo logo.png):").pack(anchor=tk.W, pady=5)

        def change_logo():
            p = filedialog.askopenfilename(filetypes=[("PNG/JPG", "*.png;*.jpg;*.jpeg")])
            if p:
                try:
                    newpath = LOGO_PATH
                    with open(p, "rb") as src, open(newpath, "wb") as dst:
                        dst.write(src.read())
                    messagebox.showinfo("OK", "Logo atualizada. Reinicie a aplicação para ver mudanças.")
                except Exception as e:
                    messagebox.showerror("Erro", str(e))

        ttk.Button(f, text="Selecionar nova logo", command=change_logo).pack(pady=10)
        ttk.Button(f, text="Fechar", command=win.destroy).pack(pady=15)

        self.setup_modal_window(win, f"Configurações - {PROJECT_NAME}")

    # 17) Tela de Ajuda (agora é a 11)
    def build_help_screen(self):
        win = tk.Toplevel(self.root)

        f = ttk.Frame(win, padding=20);
        f.pack(fill=tk.BOTH, expand=True)

        self.insert_header_logo(f)  # INSERIR LOGO

        help_txt = f"""
MANUAL RÁPIDO - {PROJECT_NAME}
----------------------------------------
**1. Login e Acesso**
- **Usuário Admin:** Use 'admin' / 'admin123' para ter acesso a todos os módulos (incluindo Gestão de Usuários).
- **Clientes:** Devem ser registrados primeiro na tela 'Registrar Cliente' ou no módulo (5. Gestão de Usuários).

**2. Cadastros Principais (Itens 1, 2, 3, 4)**
- Antes de abrir uma OS, certifique-se de que os itens abaixo estão cadastrados:
    - **Clientes:** (item 3) Incluindo o **Usuário** (chave de login/busca).
    - **Veículos:** (itens 3 e 4) **Carros** e **Motos** devem ser atrelados ao Usuário e ter uma **Placa** única.
    - **Peças e Ferramentas:** (itens 1 e 2) Para controle de estoque e uso.

**3. Ordem de Serviço (OS) - Item 6**
- A tela de Serviços agora funciona como um **Ponto de Venda/Carrinho**.
- **Para Abrir uma OS:**
    1. Preencha o **Cliente (usuário)** e a **Placa do Veículo** (o sistema valida se a placa pertence ao cliente).
    2. Insira o valor da **Mão de Obra (M.O.)**.
    3. Na seção **Catálogo de Peças** (lado direito), selecione as peças e a quantidade e clique em "Adicionar ao Carrinho".
    4. O "Carrinho" (lado esquerdo) lista as peças.
    5. Clique em **"Abrir Ordem de Serviço"**.

**4. Faturamento e Estoque - Item 7**
- O Faturamento é o único local que **fecha a OS** e **dá baixa no estoque**.
- **Para Faturar:**
    1. Acesse o módulo **7. Faturamento**.
    2. Selecione uma OS na lista de "Serviços Abertos".
    3. O sistema irá calcular o **Total Final** (M.O. + Total das Peças da OS).
    4. Clique em **"Gerar Fatura e Dar Baixa no Estoque"**.
    5. **Atenção:** Se o estoque for insuficiente para a OS, a fatura será bloqueada com um alerta.

**Dica de Visual:**
- Para que o logo apareça, certifique-se de ter o arquivo **`logo.png`** com fundo escuro na pasta do projeto.
"""
        ttk.Label(f, text=help_txt, justify=tk.LEFT, font=("Inter", 10), foreground='#FFFFFF').pack(pady=10,
                                                                                                    anchor=tk.W)
        ttk.Button(f, text="Fechar", command=win.destroy).pack(pady=10)

        self.setup_modal_window(win, f"Ajuda - {PROJECT_NAME}")

    def logout(self):
        self.user = None
        messagebox.showinfo("Logout", "Você saiu da sessão.")
        self.build_welcome_screen()

    def clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()


# ---------- execução ----------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = MM_Tunning_App(root)
    root.mainloop()
