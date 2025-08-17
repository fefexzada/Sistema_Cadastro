import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from banco import inicializar_banco, carregar_produtos, obter_vendas, adicionar_venda, remover_venda, calcular_total_pago, calcular_total_devido, adicionar_produto

# Inicializa banco de dados
inicializar_banco()

# Carrega produtos para usar no sistema
PRODUTOS_EXISTENTES = carregar_produtos()

# Definindo a aparência do Software
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppLoja(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controle de Vendas e Dívidas")
        self.geometry("1000x650")
        self.protocol("WM_DELETE_WINDOW", self.fechar_app)

        self.produto_em_edicao = None
        self.pagamento_var = tk.StringVar(value="Dinheiro")
        self.produtos_existentes = PRODUTOS_EXISTENTES.copy()

        self.create_widgets()
        self.style_treeview()
        self.ao_mudar_pagamento()
        self.atualizar_tabela()
        self.atualizar_total_label()

    def create_widgets(self):
        # Frame principal para entradas e botões
        frame_entradas_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_entradas_botoes.pack(pady=10, fill="x", padx=10)

        ctk.CTkLabel(frame_entradas_botoes, text="Nome do Produto:").pack(anchor="w")
        frame_produto_input = ctk.CTkFrame(frame_entradas_botoes, fg_color="transparent")
        frame_produto_input.pack(fill="x")

        self.entry_nome = ctk.CTkEntry(frame_produto_input, placeholder_text="Ex: Camiseta")
        self.entry_nome.pack(side="left", fill="x", expand=True, padx=(0, 5))  # Adicionado padding à direita
        self.entry_nome.bind("<KeyRelease>", self.buscar_sugestoes_produtos)

        self.combo_sugestoes = ctk.CTkComboBox(
            frame_produto_input, 
            values=[""], 
            state="readonly", 
            command=self.selecionar_sugestao_combobox,
            width=450  # Aumentada a largura fixa do combobox
        )
        self.combo_sugestoes.pack(side="left")
        self.combo_sugestoes.pack_forget()

        # Demais campos
        ctk.CTkLabel(frame_entradas_botoes, text="Quantidade:").pack(anchor="w", pady=(10, 0))
        self.entry_quantidade = ctk.CTkEntry(frame_entradas_botoes, placeholder_text="Ex: 2")
        self.entry_quantidade.pack(fill="x")

        ctk.CTkLabel(frame_entradas_botoes, text="Preço (R$):").pack(anchor="w", pady=(10, 0))
        self.entry_preco = ctk.CTkEntry(frame_entradas_botoes, placeholder_text="Ex: 49.90")
        self.entry_preco.pack(fill="x")

        ctk.CTkLabel(frame_entradas_botoes, text="Pagamento:").pack(anchor="w", pady=(10, 0))
        self.combo_pagamento = ctk.CTkComboBox(frame_entradas_botoes, variable=self.pagamento_var, 
                                             values=["Dinheiro", "Pix", "Não Pago", "Crédito", "Débito"], state="readonly")
        self.combo_pagamento.pack(fill="x")
        self.pagamento_var.trace("w", self.ao_mudar_pagamento)

        # Frame do devedor (aparece apenas quando pagamento é "Não Pago")
        self.frame_devedor = ctk.CTkFrame(frame_entradas_botoes, fg_color="transparent")
        ctk.CTkLabel(self.frame_devedor, text="Nome do Devedor:").pack(anchor="w")
        self.entry_devedor = ctk.CTkEntry(self.frame_devedor, placeholder_text="Nome de quem deve")
        self.entry_devedor.pack(fill="x")

        # Botões
        frame_botoes = ctk.CTkFrame(frame_entradas_botoes, fg_color="transparent")
        frame_botoes.pack(fill="x", pady=(10, 10))

        self.btn_salvar = ctk.CTkButton(frame_botoes, text="Salvar Produto", command=self.salvar)
        self.btn_salvar.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_deletar = ctk.CTkButton(frame_botoes, text="Deletar Selecionado", 
                                       command=self.deletar, fg_color="#D32F2F", hover_color="#B71C1C")
        self.btn_deletar.pack(side="left", padx=5, expand=True, fill="x")
        
        self.btn_limpar = ctk.CTkButton(frame_botoes, text="Limpar Campos", 
                                      command=self.limpar_campos, fg_color="#757575", hover_color="#616161")
        self.btn_limpar.pack(side="left", padx=5, expand=True, fill="x")

        # Labels de status e total
        self.label_status = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.label_status.pack(pady=5)
        
        self.total_label = ctk.CTkLabel(self, text="💰 Total do Dia (Pago): R$ 0.00", 
                                      font=("Arial", 14, "bold"), text_color=("blue", "cyan"))
        self.total_label.pack(pady=(0, 10))

        # Filtros
        frame_filtro = ctk.CTkFrame(self)
        frame_filtro.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(frame_filtro, text="Filtrar por Data:").pack(side="left", padx=(10,5))
        self.entry_data_filtro = ctk.CTkEntry(frame_filtro, placeholder_text="DD/MM/YYYY", width=120)
        self.entry_data_filtro.pack(side="left")

        ctk.CTkLabel(frame_filtro, text="Filtrar por Devedor:").pack(side="left", padx=(15, 5))
        self.entry_filtro_devedor = ctk.CTkEntry(frame_filtro, placeholder_text="Nome do devedor...")
        self.entry_filtro_devedor.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(frame_filtro, text="Filtrar", command=self.filtrar, width=80).pack(side="left")
        ctk.CTkButton(frame_filtro, text="Mostrar Todos", command=lambda: self.filtrar(limpar=True), width=120).pack(side="left", padx=5)

        # Tabela de vendas
        self.tabela = ttk.Treeview(self, columns=("ID", "Nome", "Qtd", "Preço", "Pagamento", "Status", "Devedor", "Data"), 
                                 show="headings", selectmode="browse")
        
        colunas = {
            "ID": (50, "center"), "Nome": (160, "w"), "Qtd": (60, "center"),
            "Preço": (80, "e"), "Pagamento": (100, "center"), "Status": (80, "center"),
            "Devedor": (120, "w"), "Data": (100, "center")
        }
        for col, (largura, alinhamento) in colunas.items():
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=largura, anchor=alinhamento)

        self.tabela.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tabela.bind("<<TreeviewSelect>>", self.selecionar_item)

    def style_treeview(self):
        # Configura o estilo da Treeview para combinar com o tema do CustomTkinter
        style = ttk.Style(self)
        bg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        header_bg = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"])

        style.theme_use("default")
        style.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0, rowheight=25)
        style.map('Treeview', background=[('selected', selected_color)])
        style.configure("Treeview.Heading", background=header_bg, foreground=text_color, font=("Arial", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"]))])

    def buscar_sugestoes_produtos(self, event):
        # Busca sugestões de produtos conforme o usuário digita.
        texto_digitado = self.entry_nome.get().strip().lower()

        if not texto_digitado:
            self.combo_sugestoes.pack_forget()
            return

        sugestoes_encontradas = [
            (nome, preco) for nome, preco in self.produtos_existentes.items()
            if texto_digitado in nome.lower()
        ]
        
        if sugestoes_encontradas:
            sugestoes = [f"{nome} (R$ {preco:.2f})" for nome, preco in sugestoes_encontradas]
            self.combo_sugestoes.configure(values=sugestoes)
            self.combo_sugestoes.pack(side="left", padx=(5,0))
        else:
            self.combo_sugestoes.pack_forget()

    def selecionar_sugestao_combobox(self, sugestao_selecionada):
        # Preenche os campos quando o usuário seleciona uma sugestão.
        if sugestao_selecionada and sugestao_selecionada != "":
            try:
                nome = sugestao_selecionada.split(" (R$ ")[0]
                preco_str = sugestao_selecionada.split(" (R$ ")[1].replace(")", "").strip()
                
                self.entry_nome.delete(0, tk.END)
                self.entry_nome.insert(0, nome)
                
                self.entry_preco.delete(0, tk.END)
                self.entry_preco.insert(0, preco_str)
                
                self.label_status.configure(text=f"Produto sugerido: {nome}", text_color="purple")
            except IndexError:
                self.label_status.configure(text="Erro ao processar sugestão.", text_color="red")
        
        self.combo_sugestoes.pack_forget()

    def salvar(self):
        # Salva ou atualiza uma venda no banco de dados
        try:
            nome = self.entry_nome.get().strip()
            quantidade = int(self.entry_quantidade.get())
            preco = float(self.entry_preco.get().replace(",", "."))
            pagamento = self.pagamento_var.get()
            devedor = self.entry_devedor.get().strip() if pagamento == "Não Pago" else ""
            status = "Deve" if pagamento == "Não Pago" else "Pago"

            if pagamento == "Não Pago" and not devedor:
                raise ValueError("Informe o nome do devedor.")
            if not nome:
                raise ValueError("Nome do produto não pode estar vazio.")

            # Verifica se o produto já existe no banco
            if nome not in self.produtos_existentes:
                try:
                    adicionar_produto(nome, preco)
                    self.produtos_existentes[nome] = preco
                except ValueError:
                    pass  # Produto já existe (caso raro de race condition)

            if self.produto_em_edicao:
                # Atualização de venda existente
                remover_venda(self.produto_em_edicao)
                adicionar_venda(nome, quantidade, pagamento, status, devedor)
                self.label_status.configure(text="✅ Produto atualizado!", text_color="green")
            else:
                # Nova venda
                adicionar_venda(nome, quantidade, pagamento, status, devedor)
                self.label_status.configure(text="✅ Produto cadastrado!", text_color="green")

            self.limpar_campos()
            self.atualizar_tabela()
            self.atualizar_total_label()
        except (ValueError, IndexError) as e:
            self.label_status.configure(text=f"⚠️ Erro: {str(e)}", text_color="red")

    def atualizar_tabela(self, data_filtro=None, devedor_filtro=None):
        # Atualiza a tabela com os dados do banco, aplicando filtros se fornecidos
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        vendas = obter_vendas(data_filtro, devedor_filtro)
        
        for row in reversed(vendas):
            row_list = [
                row['id'],
                row['nome'],
                row['quantidade'],
                f"R$ {row['preco']:.2f}",
                row['pagamento'],
                row['status'],
                row['devedor'],
                row['data']
            ]
            self.tabela.insert("", "end", values=row_list)

    def filtrar(self, limpar=False):
        # Aplica filtros na tabela de vendas.
        if limpar:
            self.entry_data_filtro.delete(0, tk.END)
            self.entry_filtro_devedor.delete(0, tk.END)
            data_filtro = None
            devedor_filtro = None
        else:
            data_filtro = self.entry_data_filtro.get().strip()
            devedor_filtro = self.entry_filtro_devedor.get().strip()

            if data_filtro and not self.validar_data(data_filtro):
                self.label_status.configure(text="⚠️ Data inválida! Use DD/MM/YYYY.", text_color="red")
                return

        self.atualizar_tabela(data_filtro, devedor_filtro)
        self.atualizar_total_label(data_filtro, devedor_filtro)
        
        status_text, status_color = "", "gray"
        if not data_filtro and not devedor_filtro:
            status_text = "📋 Exibindo todas as vendas."
        elif data_filtro and not devedor_filtro:
            status_text = f"📅 Exibindo vendas da data: {data_filtro}"
        elif not data_filtro and devedor_filtro:
            status_text = f"👤 Exibindo dívidas do devedor '{devedor_filtro}'"
        else:
            status_text = f"📅👤 Exibindo vendas de {data_filtro} para o devedor '{devedor_filtro}'"
        self.label_status.configure(text=status_text, text_color=status_color)

    def validar_data(self, data):
        # Valida o formato da data (DD/MM/YYYY)
        try:
            datetime.strptime(data, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def deletar(self):
        # Remove a venda selecionada
        item_selecionado = self.tabela.selection()
        if item_selecionado:
            id_venda = self.tabela.item(item_selecionado)["values"][0]
            if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar a venda com ID {id_venda}?"):
                remover_venda(id_venda)
                self.limpar_campos()
                self.atualizar_tabela()
                self.atualizar_total_label()
                self.label_status.configure(text="❌ Venda removida!", text_color="green")
        else:
            self.label_status.configure(text="⚠️ Selecione um item para deletar.", text_color="red")

    def limpar_campos(self):
        # Limpa todos os campos de entrada
        self.produto_em_edicao = None
        self.entry_nome.delete(0, tk.END)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)
        self.entry_devedor.delete(0, tk.END)
        self.pagamento_var.set("Dinheiro")
        self.btn_salvar.configure(text="Salvar Produto")
        self.label_status.configure(text="")
        if self.tabela.selection():
            self.tabela.selection_remove(self.tabela.selection())
        self.ao_mudar_pagamento()
        self.combo_sugestoes.pack_forget()

    # Ajuste na lógica da função, para se adequar ao banco de dados 
    def atualizar_total_label(self, data_filtro=None, devedor_filtro=None):
        # Atualiza o label que mostra os totais do dia por padrão
        if data_filtro is None and devedor_filtro is None:
            data_filtro = datetime.now().strftime("%d/%m/%Y")
        # Atualiza o label que mostra os totais
        total_pago = calcular_total_pago(data_filtro, devedor_filtro)
        total_devido = calcular_total_devido(data_filtro, devedor_filtro)
        
        if devedor_filtro:
            self.total_label.configure(
                text=f"💸 Total em Dívida para '{devedor_filtro}': R$ {total_devido:.2f}", 
                text_color="orange"
            )
        elif data_filtro:
            self.total_label.configure(
                text=f"💰 Total Pago em {data_filtro}: R$ {total_pago:.2f} | 💸 Devido: R$ {total_devido:.2f}", 
                text_color=("blue", "cyan")
            )
        else:
            self.total_label.configure(
                text=f"💰 Total Pago: R$ {total_pago:.2f} | 💸 Total Devido: R$ {total_devido:.2f}", 
                text_color=("blue", "cyan")
            )

    def selecionar_item(self, event):
        # Preenche os campos quando o usuário seleciona uma venda na tabela
        item_selecionado = self.tabela.selection()
        if item_selecionado:
            valores = self.tabela.item(item_selecionado)["values"]
            self.produto_em_edicao = valores[0]
            
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, valores[1])
            
            self.entry_quantidade.delete(0, tk.END)
            self.entry_quantidade.insert(0, valores[2])
            
            self.entry_preco.delete(0, tk.END)
            self.entry_preco.insert(0, str(valores[3]).replace('R$ ', ''))
            
            self.pagamento_var.set(valores[4])
            self.ao_mudar_pagamento() 
            
            if valores[4] == "Não Pago":
                self.entry_devedor.delete(0, tk.END)
                self.entry_devedor.insert(0, valores[6])
            
            self.btn_salvar.configure(text="Atualizar Venda")
            self.label_status.configure(text="Editando venda...", text_color="orange")

    def ao_mudar_pagamento(self, *args):
        # Mostra/oculta o campo de devedor conforme o tipo de pagamento.
        if self.pagamento_var.get() == "Não Pago":
            self.frame_devedor.pack(fill="x", padx=0, pady=(10, 0))
        else:
            self.frame_devedor.pack_forget()
            self.entry_devedor.delete(0, tk.END)

    def fechar_app(self):
        # Fecha a aplicação.
        self.destroy()

if __name__ == "__main__":
    app = AppLoja()
    app.mainloop()