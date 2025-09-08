import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar, DateEntry
import sqlite3
from datetime import datetime, timedelta
import calendar
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
import webbrowser
from PIL import Image, ImageTk

class SistemaGerenciamentoEstudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento - Estúdio Larissa Gouveia")
        self.root.geometry("1200x800")
        self.root.configure(bg='#FFF')
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Carregar e exibir logo
        self.carregar_logo()
        
        # Conexão com o banco de dados
        self.conn = sqlite3.connect('estudio.db')
        self.criar_tabelas()
        
        # Interface
        self.criar_interface()
        
        # Carregar dados iniciais
        self.carregar_clientes()
        self.carregar_servicos()
        self.carregar_agenda()
        
    def configurar_estilo(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar cores (rosa e branco)
        self.cor_principal = '#FFC0CB'  # Rosa claro
        self.cor_secundaria = '#FFB6C1'  # Rosa médio
        self.cor_destaque = '#FF69B4'   # Rosa forte
        self.cor_fundo = '#FFFFFF'       # Branco
        self.cor_texto = '#333333'       # Cinza escuro
        
        # Configurar estilos
        self.style.configure('TFrame', background=self.cor_fundo)
        self.style.configure('TLabel', background=self.cor_fundo, foreground=self.cor_texto)
        self.style.configure('TButton', background=self.cor_principal, foreground=self.cor_texto)
        self.style.configure('TNotebook', background=self.cor_fundo)
        self.style.configure('TNotebook.Tab', background=self.cor_secundaria, foreground=self.cor_texto)
        self.style.map('TNotebook.Tab', background=[('selected', self.cor_principal)])
        self.style.configure('Treeview', background=self.cor_fundo, fieldbackground=self.cor_fundo, foreground=self.cor_texto)
        self.style.configure('Treeview.Heading', background=self.cor_secundaria, foreground=self.cor_texto)
        self.style.configure('TCombobox', fieldbackground=self.cor_fundo, background=self.cor_fundo)
        self.style.configure('TEntry', fieldbackground=self.cor_fundo)
        
    def carregar_logo(self):
        try:
            # Criar um frame para a logo
            logo_frame = ttk.Frame(self.root)
            logo_frame.pack(pady=10)
            
            # Criar label com o nome do estúdio (substituindo a logo)
            logo_texto = "Larissa Gouveia\nBody piercing × Furo humanizado × Lobuloplastia"
            logo_label = ttk.Label(logo_frame, text=logo_texto, font=('Arial', 16, 'bold'), 
                                  foreground=self.cor_destaque, background=self.cor_fundo,
                                  justify='center')
            logo_label.pack()
            
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            # Fallback: usar texto se a imagem não carregar
            logo_frame = ttk.Frame(self.root)
            logo_frame.pack(pady=10)
            logo_label = ttk.Label(logo_frame, text="Estúdio Larissa Gouveia", 
                                  font=('Arial', 16, 'bold'), foreground=self.cor_destaque)
            logo_label.pack()
    
    def criar_tabelas(self):
        cursor = self.conn.cursor()
        
        # Tabela de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                email TEXT,
                data_nascimento TEXT,
                observacoes TEXT
            )
        ''')
        
        # Tabela de serviços
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                duracao INTEGER NOT NULL
            )
        ''')
        
        # Tabela de agendamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                servico_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                status TEXT DEFAULT 'Agendado',
                valor_pago REAL,
                observacoes TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                FOREIGN KEY (servico_id) REFERENCES servicos (id)
            )
        ''')
        
        # Inserir serviços padrão se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM servicos")
        if cursor.fetchone()[0] == 0:
            servicos_padrao = [
                ("Furo humanizado", "Perfuração de orelha com técnica humanizada", 50.0, 30),
                ("Body Piercing", "Aplicação de piercing corporal", 80.0, 45),
                ("Lobuloplastia sem corte", "Correção de lóbulo sem corte", 150.0, 60),
                ("Auriculoterapia chinesa", "Terapia de aurículo", 70.0, 50),
                ("Limpeza de pele", "Limpeza facial profunda", 90.0, 60)
            ]
            cursor.executemany("INSERT INTO servicos (nome, descricao, preco, duracao) VALUES (?, ?, ?, ?)", servicos_padrao)
        
        self.conn.commit()
    
    def criar_interface(self):
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba de Clientes
        self.frame_clientes = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_clientes, text='Clientes')
        self.criar_aba_clientes()
        
        # Aba de Serviços
        self.frame_servicos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_servicos, text='Serviços')
        self.criar_aba_servicos()
        
        # Aba de Agenda
        self.frame_agenda = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_agenda, text='Agenda')
        self.criar_aba_agenda()
        
        # Aba de Relatórios
        self.frame_relatorios = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_relatorios, text='Relatórios')
        self.criar_aba_relatorios()
        
        # Aba de Configurações
        self.frame_config = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_config, text='Configurações')
        self.criar_aba_configuracoes()
    
    def criar_aba_clientes(self):
        # Frame de cadastro
        frame_cadastro = ttk.LabelFrame(self.frame_clientes, text="Cadastro de Cliente")
        frame_cadastro.pack(fill='x', padx=10, pady=5)
        
        # Campos do formulário
        ttk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_nome = ttk.Entry(frame_cadastro, width=40)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        
        ttk.Label(frame_cadastro, text="Telefone:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_telefone = ttk.Entry(frame_cadastro, width=20)
        self.entry_telefone.grid(row=1, column=1, padx=5, pady=5)
        self.entry_telefone.bind('<KeyRelease>', self.formatar_telefone)
        
        ttk.Label(frame_cadastro, text="Email:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.entry_email = ttk.Entry(frame_cadastro, width=20)
        self.entry_email.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(frame_cadastro, text="Data Nasc.:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_data_nasc = ttk.Entry(frame_cadastro, width=15)
        self.entry_data_nasc.grid(row=2, column=1, padx=5, pady=5)
        self.entry_data_nasc.bind('<KeyRelease>', self.formatar_data)
        ttk.Button(frame_cadastro, text="📅", command=self.abrir_calendario_nascimento).grid(row=2, column=2, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame_cadastro, text="Observações:").grid(row=3, column=0, padx=5, pady=5, sticky='ne')
        self.text_observacoes = tk.Text(frame_cadastro, width=50, height=4)
        self.text_observacoes.grid(row=3, column=1, padx=5, pady=5, columnspan=3)
        
        # Botões
        frame_botoes = ttk.Frame(frame_cadastro)
        frame_botoes.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(frame_botoes, text="Adicionar", command=self.adicionar_cliente).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="Limpar", command=self.limpar_campos_cliente).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="Editar", command=self.editar_cliente).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="Excluir", command=self.excluir_cliente).pack(side='left', padx=5)
        
        # Lista de clientes
        frame_lista = ttk.LabelFrame(self.frame_clientes, text="Lista de Clientes")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('id', 'nome', 'telefone', 'email')
        self.tree_clientes = ttk.Treeview(frame_lista, columns=columns, show='headings')
        
        self.tree_clientes.heading('id', text='ID')
        self.tree_clientes.heading('nome', text='Nome')
        self.tree_clientes.heading('telefone', text='Telefone')
        self.tree_clientes.heading('email', text='Email')
        
        self.tree_clientes.column('id', width=50)
        self.tree_clientes.column('nome', width=200)
        self.tree_clientes.column('telefone', width=100)
        self.tree_clientes.column('email', width=150)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=scrollbar.set)
        
        self.tree_clientes.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree_clientes.bind('<<TreeviewSelect>>', self.preencher_campos_cliente)
    
    def criar_aba_servicos(self):
        # Frame de serviços
        frame_servicos = ttk.LabelFrame(self.frame_servicos, text="Serviços Oferecidos")
        frame_servicos.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame para edição de serviços
        frame_edicao = ttk.Frame(frame_servicos)
        frame_edicao.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_edicao, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_servico_nome = ttk.Entry(frame_edicao, width=30)
        self.entry_servico_nome.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_edicao, text="Descrição:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.entry_servico_desc = ttk.Entry(frame_edicao, width=30)
        self.entry_servico_desc.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_edicao, text="Preço R$:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_servico_preco = ttk.Entry(frame_edicao, width=15)
        self.entry_servico_preco.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_edicao, text="Duração (min):").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.entry_servico_duracao = ttk.Entry(frame_edicao, width=15)
        self.entry_servico_duracao.grid(row=1, column=3, padx=5, pady=5)
        
        frame_botoes_servico = ttk.Frame(frame_edicao)
        frame_botoes_servico.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(frame_botoes_servico, text="Adicionar Serviço", command=self.adicionar_servico).pack(side='left', padx=5)
        ttk.Button(frame_botoes_servico, text="Editar Serviço", command=self.editar_servico).pack(side='left', padx=5)
        ttk.Button(frame_botoes_servico, text="Excluir Serviço", command=self.excluir_servico).pack(side='left', padx=5)
        
        # Lista de serviços
        columns = ('id', 'nome', 'descricao', 'preco', 'duracao')
        self.tree_servicos = ttk.Treeview(frame_servicos, columns=columns, show='headings')
        
        self.tree_servicos.heading('id', text='ID')
        self.tree_servicos.heading('nome', text='Nome')
        self.tree_servicos.heading('descricao', text='Descrição')
        self.tree_servicos.heading('preco', text='Preço (R$)')
        self.tree_servicos.heading('duracao', text='Duração (min)')
        
        self.tree_servicos.column('id', width=50)
        self.tree_servicos.column('nome', width=150)
        self.tree_servicos.column('descricao', width=250)
        self.tree_servicos.column('preco', width=80)
        self.tree_servicos.column('duracao', width=100)
        
        scrollbar = ttk.Scrollbar(frame_servicos, orient='vertical', command=self.tree_servicos.yview)
        self.tree_servicos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_servicos.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        self.tree_servicos.bind('<<TreeviewSelect>>', self.preencher_campos_servico)
    
    def criar_aba_agenda(self):
        # Frame de controle de data
        frame_controle_data = ttk.Frame(self.frame_agenda)
        frame_controle_data.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(frame_controle_data, text="◀ Semana Anterior", command=self.semana_anterior).pack(side='left', padx=5)
        self.label_semana = ttk.Label(frame_controle_data, text="", font=('Arial', 10, 'bold'))
        self.label_semana.pack(side='left', padx=10)
        ttk.Button(frame_controle_data, text="Próxima Semana ▶", command=self.proxima_semana).pack(side='left', padx=5)
        ttk.Button(frame_controle_data, text="Hoje", command=self.hoje).pack(side='left', padx=5)
        
        # Frame de agendamento
        frame_agendamento = ttk.LabelFrame(self.frame_agenda, text="Novo Agendamento")
        frame_agendamento.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_agendamento, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.combo_cliente = ttk.Combobox(frame_agendamento, width=30, state='readonly')
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_agendamento, text="Serviços:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        
        # Frame para lista de serviços selecionados
        frame_servicos_selecionados = ttk.Frame(frame_agendamento)
        frame_servicos_selecionados.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky='we')
        
        self.lista_servicos_selecionados = tk.Listbox(frame_servicos_selecionados, height=4, width=40)
        scrollbar_servicos = ttk.Scrollbar(frame_servicos_selecionados, orient='vertical', command=self.lista_servicos_selecionados.yview)
        self.lista_servicos_selecionados.configure(yscrollcommand=scrollbar_servicos.set)
        
        self.lista_servicos_selecionados.pack(side='left', fill='both', expand=True)
        scrollbar_servicos.pack(side='right', fill='y')
        
        # Frame para botões de serviços
        frame_botoes_servicos = ttk.Frame(frame_agendamento)
        frame_botoes_servicos.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        self.combo_servico = ttk.Combobox(frame_botoes_servicos, width=20, state='readonly')
        self.combo_servico.pack(side='top', padx=5, pady=2)
        
        ttk.Button(frame_botoes_servicos, text="Adicionar Serviço", command=self.adicionar_servico_agendamento).pack(side='top', padx=5, pady=2)
        ttk.Button(frame_botoes_servicos, text="Remover Serviço", command=self.remover_servico_agendamento).pack(side='top', padx=5, pady=2)
        
        # Label para mostrar o valor total
        self.label_valor_total = ttk.Label(frame_agendamento, text="Valor Total: R$ 0,00", font=('Arial', 10, 'bold'))
        self.label_valor_total.grid(row=2, column=2, columnspan=2, padx=5, pady=5)
        
        ttk.Label(frame_agendamento, text="Data:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_data = DateEntry(frame_agendamento, width=15, background='darkblue', 
                                   foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.entry_data.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame_agendamento, text="Hora:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.combo_hora = ttk.Combobox(frame_agendamento, width=10, values=[f"{h:02d}:00" for h in range(8, 19)])
        self.combo_hora.grid(row=3, column=1, padx=5, pady=5)
        self.combo_hora.set("09:00")
        
        ttk.Button(frame_agendamento, text="Agendar", command=self.fazer_agendamento).grid(row=3, column=2, columnspan=2, pady=10)
        
        # Frame de agenda
        frame_calendario = ttk.LabelFrame(self.frame_agenda, text="Agenda")
        frame_calendario.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Criação do calendário semanal
        self.criar_calendario_semanal(frame_calendario)
    
    def criar_calendario_semanal(self, parent):
        # Limpar frame antes de recriar
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Definir a semana atual (corrigido para usar a data atual)
        hoje = datetime.now()
        if not hasattr(self, 'data_referencia'):
            self.data_referencia = hoje
        inicio_semana = self.data_referencia - timedelta(days=self.data_referencia.weekday())
        
        # Atualizar label da semana
        fim_semana = inicio_semana + timedelta(days=5)
        self.label_semana.config(text=f"Semana: {inicio_semana.strftime('%d/%m/%Y')} a {fim_semana.strftime('%d/%m/%Y')}")
        
        # Cabeçalho com dias da semana
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        for i, dia in enumerate(dias_semana):
            data_dia = inicio_semana + timedelta(days=i)
            label_text = f"{dia}\n{data_dia.strftime('%d/%m')}"
            label = ttk.Label(parent, text=label_text, anchor='center', background=self.cor_secundaria)
            label.grid(row=0, column=i+1, padx=2, pady=2, sticky='nsew')
        
        # Cria células para cada hora do dia
        horas = [f"{h:02d}:00" for h in range(8, 19)]
        for i, hora in enumerate(horas):
            label = ttk.Label(parent, text=hora, anchor='e')
            label.grid(row=i+1, column=0, padx=2, pady=2, sticky='e')
            
            for j in range(1, 7):  # 6 dias da semana (segunda a sábado)
                cell = tk.Frame(parent, relief='solid', borderwidth=1, width=150, height=40, bg='white')
                cell.grid(row=i+1, column=j, padx=2, pady=2, sticky='nsew')
                cell.grid_propagate(False)
                
                # Adicionar agendamentos existentes
                data_dia = inicio_semana + timedelta(days=j-1)
                self.adicionar_agendamentos_celula(cell, data_dia.strftime("%Y-%m-%d"), hora)
        
        # Configurar pesos das colunas
        for i in range(7):
            parent.columnconfigure(i, weight=1)
        
        for i in range(len(horas)+1):
            parent.rowconfigure(i, weight=1)
    
    def adicionar_agendamentos_celula(self, cell, data, hora):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.id, c.nome, s.nome, a.status, a.valor_pago, s.preco
            FROM agendamentos a
            JOIN clientes c ON a.cliente_id = c.id
            JOIN servicos s ON a.servico_id = s.id
            WHERE a.data = ? AND a.hora = ?
        ''', (data, hora))
        
        agendamentos = cursor.fetchall()
        
        if agendamentos:
            for agendamento in agendamentos:
                id_agendamento, cliente, servico, status, valor_pago, preco_original = agendamento
                
                # Cor de fundo baseada no status
                cor_fundo = 'lightgreen' if status == 'Concluído' else \
                           'lightyellow' if status == 'Agendado' else \
                           'lightcoral' if status == 'Cancelado' else 'white'
                
                # Texto com informações do agendamento
                texto = f"{cliente}\n{servico}"
                if valor_pago and valor_pago != preco_original:
                    texto += f"\nR$ {valor_pago:.2f} (desc.)"
                else:
                    texto += f"\nR$ {preco_original:.2f}"
                
                label = tk.Label(cell, text=texto, font=('Arial', 7), bg=cor_fundo, wraplength=140)
                label.pack(fill='both', expand=True)
                label.bind('<Button-1>', lambda e, id=id_agendamento: self.abrir_menu_agendamento(id))
    
    def abrir_menu_agendamento(self, id_agendamento):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Editar", command=lambda: self.editar_agendamento(id_agendamento))
        menu.add_command(label="Concluir", command=lambda: self.concluir_agendamento(id_agendamento))
        menu.add_command(label="Cancelar", command=lambda: self.cancelar_agendamento(id_agendamento))
        menu.add_command(label="Aplicar Desconto", command=lambda: self.aplicar_desconto(id_agendamento))
        menu.add_command(label="Excluir", command=lambda: self.excluir_agendamento(id_agendamento))
        menu.post(tk._default_root.winfo_pointerx(), tk._default_root.winfo_pointery())
    
    def aplicar_desconto(self, id_agendamento):
        # Buscar informações do agendamento
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.valor_pago, s.preco, c.nome, s.nome 
            FROM agendamentos a
            JOIN servicos s ON a.servico_id = s.id
            JOIN clientes c ON a.cliente_id = c.id
            WHERE a.id = ?
        ''', (id_agendamento,))
        
        agendamento = cursor.fetchone()
        if not agendamento:
            return
        
        valor_atual, preco_original, cliente, servico = agendamento
        if valor_atual is None:
            valor_atual = preco_original
        
        # Janela para aplicar desconto
        janela_desconto = tk.Toplevel(self.root)
        janela_desconto.title("Aplicar Desconto")
        janela_desconto.geometry("300x200")
        
        ttk.Label(janela_desconto, text=f"Cliente: {cliente}").pack(pady=5)
        ttk.Label(janela_desconto, text=f"Serviço: {servico}").pack(pady=5)
        ttk.Label(janela_desconto, text=f"Preço Original: R$ {preco_original:.2f}").pack(pady=5)
        
        ttk.Label(janela_desconto, text="Novo Valor:").pack(pady=5)
        entry_novo_valor = ttk.Entry(janela_desconto)
        entry_novo_valor.insert(0, f"{valor_atual:.2f}")
        entry_novo_valor.pack(pady=5)
        
        def confirmar_desconto():
            try:
                novo_valor = float(entry_novo_valor.get().replace(',', '.'))
                cursor.execute("UPDATE agendamentos SET valor_pago = ? WHERE id = ?", (novo_valor, id_agendamento))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Desconto aplicado com sucesso!")
                janela_desconto.destroy()
                self.carregar_agenda()
            except ValueError:
                messagebox.showerror("Erro", "Digite um valor válido!")
        
        ttk.Button(janela_desconto, text="Aplicar Desconto", command=confirmar_desconto).pack(pady=10)
    
    def editar_agendamento(self, id_agendamento):
        # Buscar informações do agendamento
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.data, a.hora, a.cliente_id, a.servico_id, a.observacoes
            FROM agendamentos a
            WHERE a.id = ?
        ''', (id_agendamento,))
        
        agendamento = cursor.fetchone()
        if not agendamento:
            return
        
        data, hora, cliente_id, servico_id, observacoes = agendamento
        
        # Janela de edição
        janela_edicao = tk.Toplevel(self.root)
        janela_edicao.title("Editar Agendamento")
        janela_edicao.geometry("400x300")
        
        ttk.Label(janela_edicao, text="Data:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        entry_data = DateEntry(janela_edicao, width=15, background='darkblue', 
                              foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        entry_data.set_date(datetime.strptime(data, "%Y-%m-%d"))
        entry_data.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(janela_edicao, text="Hora:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        combo_hora = ttk.Combobox(janela_edicao, width=10, values=[f"{h:02d}:00" for h in range(8, 19)])
        combo_hora.set(hora)
        combo_hora.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(janela_edicao, text="Observações:").grid(row=2, column=0, padx=5, pady=5, sticky='ne')
        text_observacoes = tk.Text(janela_edicao, width=30, height=5)
        text_observacoes.insert('1.0', observacoes or '')
        text_observacoes.grid(row=2, column=1, padx=5, pady=5)
        
        def confirmar_edicao():
            nova_data = entry_data.get_date().strftime("%Y-%m-%d")
            nova_hora = combo_hora.get()
            novas_observacoes = text_observacoes.get("1.0", "end-1c")
            
            cursor.execute('''
                UPDATE agendamentos 
                SET data = ?, hora = ?, observacoes = ?
                WHERE id = ?
            ''', (nova_data, nova_hora, novas_observacoes, id_agendamento))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Agendamento atualizado com sucesso!")
            janela_edicao.destroy()
            self.carregar_agenda()
        
        ttk.Button(janela_edicao, text="Salvar Alterações", command=confirmar_edicao).grid(row=3, column=0, columnspan=2, pady=10)
    
    def concluir_agendamento(self, id_agendamento):
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE agendamentos SET status = 'Concluído' WHERE id = ?", (id_agendamento,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Agendamento marcado como concluído!")
            self.carregar_agenda()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar agendamento: {str(e)}")
    
    def cancelar_agendamento(self, id_agendamento):
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE agendamentos SET status = 'Cancelado' WHERE id = ?", (id_agendamento,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Agendamento cancelado!")
            self.carregar_agenda()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cancelar agendamento: {str(e)}")
    
    def excluir_agendamento(self, id_agendamento):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este agendamento?"):
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM agendamentos WHERE id = ?", (id_agendamento,))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Agendamento excluído!")
                self.carregar_agenda()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir agendamento: {str(e)}")
    
    def criar_aba_relatorios(self):
        # Frame de filtros
        frame_filtros = ttk.LabelFrame(self.frame_relatorios, text="Filtros")
        frame_filtros.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_filtros, text="Período:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.combo_periodo = ttk.Combobox(frame_filtros, width=15, values=['Diário', 'Semanal', 'Mensal', 'Personalizado'])
        self.combo_periodo.grid(row=0, column=1, padx=5, pady=5)
        self.combo_periodo.set('Mensal')
        self.combo_periodo.bind('<<ComboboxSelected>>', self.ajustar_periodo)
        
        ttk.Label(frame_filtros, text="Data Início:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.entry_data_inicio = DateEntry(frame_filtros, width=12, background='darkblue', 
                                          foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.entry_data_inicio.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.entry_data_fim = DateEntry(frame_filtros, width=12, background='darkblue', 
                                       foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.entry_data_fim.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(frame_filtros, text="Gerar Relatório", command=self.gerar_relatorio).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(frame_filtros, text="Exportar PDF", command=self.exportar_pdf).grid(row=0, column=7, padx=5, pady=5)
        
        # Ajustar período inicial
        self.ajustar_periodo(None)
        
        # Frame de resultados
        frame_resultados = ttk.LabelFrame(self.frame_relatorios, text="Resultados")
        frame_resultados.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.text_relatorio = tk.Text(frame_resultados, height=20)
        scrollbar = ttk.Scrollbar(frame_resultados, orient='vertical', command=self.text_relatorio.yview)
        self.text_relatorio.configure(yscrollcommand=scrollbar.set)
        
        self.text_relatorio.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
    
    def criar_aba_configuracoes(self):
        # Frame de configurações do WhatsApp
        frame_whatsapp = ttk.LabelFrame(self.frame_config, text="Lembretes por WhatsApp")
        frame_whatsapp.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_whatsapp, text="Mensagem padrão para lembretes:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.text_mensagem_whatsapp = tk.Text(frame_whatsapp, width=60, height=4)
        self.text_mensagem_whatsapp.insert('1.0', "Olá! Lembramos que você tem um agendamento conosco no Estúdio Larissa Gouveia. Esperamos por você!")
        self.text_mensagem_whatsapp.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Label(frame_whatsapp, text="Enviar lembrete com antecedência:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.combo_antecedencia = ttk.Combobox(frame_whatsapp, width=15, values=['1 dia', '2 dias', '3 dias', '1 semana'])
        self.combo_antecedencia.set('1 dia')
        self.combo_antecedencia.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(frame_whatsapp, text="Enviar Lembretes Agora", command=self.enviar_lembretes_whatsapp).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Frame de backup
        frame_backup = ttk.LabelFrame(self.frame_config, text="Backup de Dados")
        frame_backup.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(frame_backup, text="Fazer Backup Agora", command=self.fazer_backup).pack(pady=10)
        ttk.Button(frame_backup, text="Restaurar Backup", command=self.restaurar_backup).pack(pady=10)
    
    def formatar_telefone(self, event):
        texto = self.entry_telefone.get().replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        
        if len(texto) <= 11:
            if len(texto) <= 2:
                texto_formatado = texto
            elif len(texto) <= 6:
                texto_formatado = f'({texto[:2]}) {texto[2:]}'
            elif len(texto) <= 10:
                texto_formatado = f'({texto[:2]}) {texto[2:6]}-{texto[6:]}'
            else:
                texto_formatado = f'({texto[:2]}) {texto[2:7]}-{texto[7:]}'
            
            # Remover bind temporariamente para evitar loop infinito
            self.entry_telefone.unbind('<KeyRelease>')
            self.entry_telefone.delete(0, 'end')
            self.entry_telefone.insert(0, texto_formatado)
            self.entry_telefone.bind('<KeyRelease>', self.formatar_telefone)
            
            # Posicionar cursor no final
            self.entry_telefone.icursor('end')
    
    def formatar_data(self, event):
        widget = event.widget
        texto = widget.get().replace('/', '').replace(':', '')
        
        if len(texto) <= 8:
            if len(texto) <= 2:
                texto_formatado = texto
            elif len(texto) <= 4:
                texto_formatado = f'{texto[:2]}/{texto[2:]}'
            else:
                texto_formatado = f'{texto[:2]}/{texto[2:4]}/{texto[4:8]}'
            
            # Remover bind temporariamente para evitar loop infinito
            widget.unbind('<KeyRelease>')
            widget.delete(0, 'end')
            widget.insert(0, texto_formatado)
            widget.bind('<KeyRelease>', self.formatar_data)
            
            # Posicionar cursor no final
            widget.icursor('end')
    
    def abrir_calendario_nascimento(self):
        def set_data():
            self.entry_data_nasc.delete(0, 'end')
            self.entry_data_nasc.insert(0, cal.selection_get().strftime('%d/%m/%Y'))
            top.destroy()
        
        top = tk.Toplevel(self.root)
        top.title("Selecionar Data de Nascimento")
        top.geometry("300x300")
        
        cal = Calendar(top, selectmode='day', year=datetime.now().year-20, month=datetime.now().month, day=datetime.now().day)
        cal.pack(pady=20)
        
        ttk.Button(top, text="Selecionar", command=set_data).pack(pady=10)
    
    def ajustar_periodo(self, event):
        periodo = self.combo_periodo.get()
        hoje = datetime.now()
        
        if periodo == 'Diário':
            self.entry_data_inicio.set_date(hoje)
            self.entry_data_fim.set_date(hoje)
        elif periodo == 'Semanal':
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            fim_semana = inicio_semana + timedelta(days=6)
            self.entry_data_inicio.set_date(inicio_semana)
            self.entry_data_fim.set_date(fim_semana)
        elif periodo == 'Mensal':
            primeiro_dia = hoje.replace(day=1)
            ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])
            self.entry_data_inicio.set_date(primeiro_dia)
            self.entry_data_fim.set_date(ultimo_dia)
    
    def semana_anterior(self):
        self.data_referencia = self.data_referencia - timedelta(weeks=1)
        self.carregar_agenda()
    
    def proxima_semana(self):
        self.data_referencia = self.data_referencia + timedelta(weeks=1)
        self.carregar_agenda()
    
    def hoje(self):
        self.data_referencia = datetime.now()
        self.carregar_agenda()
    
    def adicionar_servico_agendamento(self):
        servico_str = self.combo_servico.get()
        if servico_str:
            self.lista_servicos_selecionados.insert('end', servico_str)
            self.calcular_valor_total()
    
    def remover_servico_agendamento(self):
        selecionado = self.lista_servicos_selecionados.curselection()
        if selecionado:
            self.lista_servicos_selecionados.delete(selecionado[0])
            self.calcular_valor_total()
    
    def calcular_valor_total(self):
        total = 0.0
        for i in range(self.lista_servicos_selecionados.size()):
            servico_str = self.lista_servicos_selecionados.get(i)
            # Extrair o preço do serviço (assumindo que o preço está entre parênteses)
            match = re.search(r'R\$\s*([\d,]+)', servico_str)
            if match:
                preco_str = match.group(1).replace(',', '.')
                try:
                    total += float(preco_str)
                except ValueError:
                    pass
        
        self.label_valor_total.config(text=f"Valor Total: R$ {total:.2f}")
    
    def preencher_campos_servico(self, event):
        selection = self.tree_servicos.selection()
        if not selection:
            return
        
        item = self.tree_servicos.item(selection[0])
        servico_id = item['values'][0]
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,))
        servico = cursor.fetchone()
        
        if servico:
            self.entry_servico_nome.delete(0, 'end')
            self.entry_servico_nome.insert(0, servico[1])
            self.entry_servico_desc.delete(0, 'end')
            self.entry_servico_desc.insert(0, servico[2] if servico[2] else "")
            self.entry_servico_preco.delete(0, 'end')
            self.entry_servico_preco.insert(0, f"{servico[3]:.2f}")
            self.entry_servico_duracao.delete(0, 'end')
            self.entry_servico_duracao.insert(0, servico[4] if servico[4] else "")
    
    def adicionar_servico(self):
        nome = self.entry_servico_nome.get().strip()
        descricao = self.entry_servico_desc.get().strip()
        preco = self.entry_servico_preco.get().strip()
        duracao = self.entry_servico_duracao.get().strip()
        
        if not all([nome, preco, duracao]):
            messagebox.showerror("Erro", "Nome, preço e duração são obrigatórios!")
            return
        
        try:
            preco_val = float(preco.replace(',', '.'))
            duracao_val = int(duracao)
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO servicos (nome, descricao, preco, duracao) VALUES (?, ?, ?, ?)",
                (nome, descricao, preco_val, duracao_val)
            )
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Serviço cadastrado com sucesso!")
            self.carregar_servicos()
            self.limpar_campos_servico()
            
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número e duração um número inteiro!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar serviço: {str(e)}")
    
    def editar_servico(self):
        selection = self.tree_servicos.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um serviço para editar!")
            return
        
        item = self.tree_servicos.item(selection[0])
        servico_id = item['values'][0]
        
        nome = self.entry_servico_nome.get().strip()
        descricao = self.entry_servico_desc.get().strip()
        preco = self.entry_servico_preco.get().strip()
        duracao = self.entry_servico_duracao.get().strip()
        
        if not all([nome, preco, duracao]):
            messagebox.showerror("Erro", "Nome, preço e duração são obrigatórios!")
            return
        
        try:
            preco_val = float(preco.replace(',', '.'))
            duracao_val = int(duracao)
            
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE servicos SET nome=?, descricao=?, preco=?, duracao=? WHERE id=?",
                (nome, descricao, preco_val, duracao_val, servico_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Serviço atualizado com sucesso!")
            self.carregar_servicos()
            
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número e duração um número inteiro!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar serviço: {str(e)}")
    
    def excluir_servico(self):
        selection = self.tree_servicos.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um serviço para excluir!")
            return
        
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este serviço?"):
            return
        
        item = self.tree_servicos.item(selection[0])
        servico_id = item['values'][0]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM servicos WHERE id=?", (servico_id,))
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Serviço excluído com sucesso!")
            self.limpar_campos_servico()
            self.carregar_servicos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir serviço: {str(e)}")
    
    def limpar_campos_servico(self):
        self.entry_servico_nome.delete(0, 'end')
        self.entry_servico_desc.delete(0, 'end')
        self.entry_servico_preco.delete(0, 'end')
        self.entry_servico_duracao.delete(0, 'end')
    
    def carregar_clientes(self):
        # Limpar treeview
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        # Buscar clientes no banco
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, telefone, email FROM clientes ORDER BY nome")
        
        # Preencher treeview
        for row in cursor.fetchall():
            self.tree_clientes.insert('', 'end', values=row)
        
        # Atualizar combobox de clientes na aba de agendamentos
        cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
        clientes = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        self.combo_cliente['values'] = clientes
        if clientes:
            self.combo_cliente.current(0)
    
    def carregar_servicos(self):
        # Limpar treeview
        for item in self.tree_servicos.get_children():
            self.tree_servicos.delete(item)
        
        # Buscar serviços no banco
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, descricao, preco, duracao FROM servicos ORDER BY nome")
        
        # Preencher treeview
        for row in cursor.fetchall():
            self.tree_servicos.insert('', 'end', values=row)
        
        # Atualizar combobox de serviços na aba de agendamentos
        cursor.execute("SELECT id, nome, preco FROM servicos ORDER BY nome")
        servicos = [f"{row[0]} - {row[1]} (R$ {row[2]:.2f})" for row in cursor.fetchall()]
        self.combo_servico['values'] = servicos
        if servicos:
            self.combo_servico.current(0)
    
    def carregar_agenda(self):
        # Recriar o calendário semanal
        for widget in self.frame_agenda.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget['text'] == "Agenda":
                self.criar_calendario_semanal(widget)
                break
    
    def adicionar_cliente(self):
        nome = self.entry_nome.get().strip()
        telefone = self.entry_telefone.get().strip()
        email = self.entry_email.get().strip()
        data_nasc = self.entry_data_nasc.get().strip()
        observacoes = self.text_observacoes.get("1.0", "end-1c").strip()
        
        if not nome:
            messagebox.showerror("Erro", "O nome do cliente é obrigatório!")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nome, telefone, email, data_nascimento, observacoes) VALUES (?, ?, ?, ?, ?)",
                (nome, telefone, email, data_nasc, observacoes)
            )
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self.limpar_campos_cliente()
            self.carregar_clientes()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar cliente: {str(e)}")
    
    def editar_cliente(self):
        selection = self.tree_clientes.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar!")
            return
        
        item = self.tree_clientes.item(selection[0])
        cliente_id = item['values'][0]
        
        nome = self.entry_nome.get().strip()
        telefone = self.entry_telefone.get().strip()
        email = self.entry_email.get().strip()
        data_nasc = self.entry_data_nasc.get().strip()
        observacoes = self.text_observacoes.get("1.0", "end-1c").strip()
        
        if not nome:
            messagebox.showerror("Erro", "O nome do cliente é obrigatório!")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE clientes SET nome=?, telefone=?, email=?, data_nascimento=?, observacoes=? WHERE id=?",
                (nome, telefone, email, data_nasc, observacoes, cliente_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            self.carregar_clientes()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar cliente: {str(e)}")
    
    def excluir_cliente(self):
        selection = self.tree_clientes.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir!")
            return
        
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este cliente?"):
            return
        
        item = self.tree_clientes.item(selection[0])
        cliente_id = item['values'][0]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
            self.limpar_campos_cliente()
            self.carregar_clientes()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir cliente: {str(e)}")
    
    def limpar_campos_cliente(self):
        self.entry_nome.delete(0, 'end')
        self.entry_telefone.delete(0, 'end')
        self.entry_email.delete(0, 'end')
        self.entry_data_nasc.delete(0, 'end')
        self.text_observacoes.delete("1.0", 'end')
    
    def preencher_campos_cliente(self, event):
        selection = self.tree_clientes.selection()
        if not selection:
            return
        
        item = self.tree_clientes.item(selection[0])
        cliente_id = item['values'][0]
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()
        
        if cliente:
            self.entry_nome.delete(0, 'end')
            self.entry_nome.insert(0, cliente[1])
            self.entry_telefone.delete(0, 'end')
            self.entry_telefone.insert(0, cliente[2] if cliente[2] else "")
            self.entry_email.delete(0, 'end')
            self.entry_email.insert(0, cliente[3] if cliente[3] else "")
            self.entry_data_nasc.delete(0, 'end')
            self.entry_data_nasc.insert(0, cliente[4] if cliente[4] else "")
            self.text_observacoes.delete("1.0", 'end')
            self.text_observacoes.insert("1.0", cliente[5] if cliente[5] else "")
    
    def fazer_agendamento(self):
        cliente_str = self.combo_cliente.get()
        data = self.entry_data.get_date().strftime("%d/%m/%Y")
        hora = self.combo_hora.get().strip()
        
        servicos_selecionados = []
        for i in range(self.lista_servicos_selecionados.size()):
            servico_str = self.lista_servicos_selecionados.get(i)
            servicos_selecionados.append(servico_str)
        
        if not all([cliente_str, servicos_selecionados, data, hora]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        
        try:
            cliente_id = int(cliente_str.split(' - ')[0])
            
            # Converter data para formato do banco
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            data_db = data_obj.strftime("%Y-%m-%d")
            
            cursor = self.conn.cursor()
            
            # Inserir cada serviço selecionado
            for servico_str in servicos_selecionados:
                servico_id = int(servico_str.split(' - ')[0])
                cursor.execute(
                    "INSERT INTO agendamentos (cliente_id, servico_id, data, hora, status) VALUES (?, ?, ?, ?, ?)",
                    (cliente_id, servico_id, data_db, hora, 'Agendado')
                )
            
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Agendamento realizado com sucesso!")
            self.lista_servicos_selecionados.delete(0, 'end')
            self.label_valor_total.config(text="Valor Total: R$ 0,00")
            self.carregar_agenda()
            
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar agendamento: {str(e)}")
    
    def gerar_relatorio(self):
        data_inicio = self.entry_data_inicio.get_date()
        data_fim = self.entry_data_fim.get_date()
        
        try:
            # Converter datas para formato do banco
            data_inicio_db = data_inicio.strftime("%Y-%m-%d")
            data_fim_db = data_fim.strftime("%Y-%m-%d")
            
            cursor = self.conn.cursor()
            
            # Consulta para obter agendamentos no período (apenas concluídos)
            cursor.execute('''
                SELECT a.data, a.hora, c.nome as cliente, s.nome as servico, s.preco, a.valor_pago
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN servicos s ON a.servico_id = s.id
                WHERE a.data BETWEEN ? AND ? AND a.status = 'Concluído'
                ORDER BY a.data, a.hora
            ''', (data_inicio_db, data_fim_db))
            
            agendamentos = cursor.fetchall()
            
            # Calcular totais
            total_servicos = len(agendamentos)
            total_faturamento = sum(ag[5] if ag[5] is not None else ag[4] for ag in agendamentos)
            
            # Gerar relatório
            relatorio = f"RELATÓRIO DE SERVIÇOS CONCLUÍDOS\n"
            relatorio += f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n"
            relatorio += "=" * 60 + "\n\n"
            
            relatorio += f"Total de serviços realizados: {total_servicos}\n"
            relatorio += f"Faturamento total: R$ {total_faturamento:.2f}\n\n"
            
            relatorio += "Detalhamento por serviço:\n"
            relatorio += "-" * 60 + "\n"
            
            # Agrupar por serviço
            servicos_dict = {}
            for ag in agendamentos:
                servico = ag[3]
                if servico not in servicos_dict:
                    servicos_dict[servico] = {'quantidade': 0, 'faturamento': 0}
                servicos_dict[servico]['quantidade'] += 1
                valor = ag[5] if ag[5] is not None else ag[4]
                servicos_dict[servico]['faturamento'] += valor
            
            for servico, dados in servicos_dict.items():
                percentual = (dados['faturamento'] / total_faturamento * 100) if total_faturamento > 0 else 0
                relatorio += f"{servico}: {dados['quantidade']} serviços, R$ {dados['faturamento']:.2f} ({percentual:.1f}%)\n"
            
            relatorio += "\nAgendamentos detalhados:\n"
            relatorio += "-" * 60 + "\n"
            
            for ag in agendamentos:
                valor = ag[5] if ag[5] is not None else ag[4]
                relatorio += f"{ag[0]} {ag[1]} - {ag[2]} - {ag[3]} - R$ {valor:.2f}\n"
            
            self.text_relatorio.delete("1.0", "end")
            self.text_relatorio.insert("1.0", relatorio)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def exportar_pdf(self):
        try:
            # Solicitar local para salvar o arquivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Salvar relatório como PDF"
            )
            
            if not file_path:
                return  # Usuário cancelou
                
            # Criar documento PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Título
            titulo = Paragraph("Relatório de Serviços - Estúdio Larissa Gouveia", styles['Title'])
            elements.append(titulo)
            elements.append(Spacer(1, 12))
            
            # Período
            data_inicio = self.entry_data_inicio.get_date()
            data_fim = self.entry_data_fim.get_date()
            periodo = Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", styles['Normal'])
            elements.append(periodo)
            elements.append(Spacer(1, 12))
            
            # Dados para a tabela
            data_inicio_db = data_inicio.strftime("%Y-%m-%d")
            data_fim_db = data_fim.strftime("%Y-%m-%d")
            
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT a.data, a.hora, c.nome as cliente, s.nome as servico, s.preco, a.valor_pago
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN servicos s ON a.servico_id = s.id
                WHERE a.data BETWEEN ? AND ? AND a.status = 'Concluído'
                ORDER BY a.data, a.hora
            ''', (data_inicio_db, data_fim_db))
            
            agendamentos = cursor.fetchall()
            
            # Cabeçalho da tabela
            data = [['Data', 'Hora', 'Cliente', 'Serviço', 'Valor (R$)']]
            
            # Adicionar dados à tabela
            for ag in agendamentos:
                valor = ag[5] if ag[5] is not None else ag[4]
                data.append([ag[0], ag[1], ag[2], ag[3], f"{valor:.2f}"])
            
            # Calcular totais
            total_servicos = len(agendamentos)
            total_faturamento = sum(ag[5] if ag[5] is not None else ag[4] for ag in agendamentos)
            
            # Adicionar linha de totais
            data.append(['', '', '', 'TOTAL:', f"{total_faturamento:.2f}"])
            
            # Criar tabela
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 12))
            
            # Resumo
            resumo = Paragraph(f"Total de serviços: {total_servicos}<br/>Faturamento total: R$ {total_faturamento:.2f}", styles['Normal'])
            elements.append(resumo)
            
            # Gerar PDF
            doc.build(elements)
            
            messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso para:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar PDF: {str(e)}")
    
    def enviar_lembretes_whatsapp(self):
        try:
            # Determinar a data de referência para lembretes
            antecedencia = self.combo_antecedencia.get()
            if antecedencia == '1 dia':
                dias_antes = 1
            elif antecedencia == '2 dias':
                dias_antes = 2
            elif antecedencia == '3 dias':
                dias_antes = 3
            else:  # 1 semana
                dias_antes = 7
                
            data_referencia = (datetime.now() + timedelta(days=dias_antes)).strftime("%Y-%m-%d")
            
            # Buscar agendamentos para a data de referência
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT a.data, a.hora, c.nome, c.telefone, s.nome
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN servicos s ON a.servico_id = s.id
                WHERE a.data = ? AND a.status = 'Agendado' AND c.telefone IS NOT NULL
            ''', (data_referencia,))
            
            agendamentos = cursor.fetchall()
            
            if not agendamentos:
                messagebox.showinfo("Lembretes", "Nenhum agendamento encontrado para enviar lembretes.")
                return
            
            mensagem_padrao = self.text_mensagem_whatsapp.get("1.0", "end-1c").strip()
            
            for agendamento in agendamentos:
                data, hora, cliente, telefone, servico = agendamento
                telefone_limpo = telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
                
                # Personalizar mensagem
                mensagem = mensagem_padrao.replace("{cliente}", cliente)
                mensagem = mensagem.replace("{data}", datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y"))
                mensagem = mensagem.replace("{hora}", hora)
                mensagem = mensagem.replace("{servico}", servico)
                
                # Codificar mensagem para URL
                mensagem_codificada = mensagem.replace(' ', '%20').replace('\n', '%0A')
                
                # Criar link do WhatsApp
                link_whatsapp = f"https://web.whatsapp.com/send?phone=55{telefone_limpo}&text={mensagem_codificada}"
                
                # Abrir no navegador
                webbrowser.open(link_whatsapp)
            
            messagebox.showinfo("Lembretes", f"Links do WhatsApp gerados para {len(agendamentos)} clientes. \n\nOs links serão abertos no navegador. Certifique-se de estar logado no WhatsApp Web.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar lembretes: {str(e)}")
    
    def fazer_backup(self):
        try:
            # Solicitar local para salvar o backup
            file_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db")],
                title="Salvar backup como"
            )
            
            if not file_path:
                return  # Usuário cancelou
                
            # Fazer cópia do banco de dados
            import shutil
            shutil.copy2('estudio.db', file_path)
            
            messagebox.showinfo("Backup", f"Backup realizado com sucesso em:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fazer backup: {str(e)}")
    
    def restaurar_backup(self):
        try:
            # Solicitar arquivo de backup
            file_path = filedialog.askopenfilename(
                filetypes=[("Database files", "*.db")],
                title="Selecionar arquivo de backup"
            )
            
            if not file_path:
                return  # Usuário cancelou
                
            if not messagebox.askyesno("Confirmar", "Tem certeza que deseja restaurar o backup? Todos os dados atuais serão substituídos."):
                return
                
            # Fazer cópia do backup para o arquivo atual
            import shutil
            shutil.copy2(file_path, 'estudio.db')
            
            # Recarregar todos os dados
            self.carregar_clientes()
            self.carregar_servicos()
            self.carregar_agenda()
            
            messagebox.showinfo("Restauração", "Backup restaurado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar backup: {str(e)}")

def main():
    root = tk.Tk()
    app = SistemaGerenciamentoEstudio(root)
    root.mainloop()

if __name__ == "__main__":
    main()

  """
Sistema de Gerenciamento - Estúdio Larissa Gouveia
Copyright (C) 2024 Hilton Honorio Neto. Todos os direitos reservados.

Este software é disponibilizado apenas para fins educacionais.
É estritamente proibida a utilização comercial sem licença expressa.

Para licenciamento comercial: honoriohneto@gmail.com
"""
