# Sistema de Controle de Vendas e Dívidas

Um sistema completo para gerenciamento de vendas, controle de estoque e acompanhamento de dívidas, desenvolvido para um pequeno comércio.

## 📌 Visão Geral

Este projeto foi desenvolvido para automatizar e facilitar o controle de vendas em uma pequena loja, oferecendo:

- Cadastro de produtos
- Registro de vendas com diferentes formas de pagamento
- Controle de dívidas (vendas não pagas)
- Relatórios diários e filtros avançados
- Interface intuitiva e moderna

##  Funcionalidades Principais

###  Controle de Vendas
- Cadastro de vendas com detalhes do produto, quantidade e preço
- Diferentes formas de pagamento: Dinheiro, Pix, Crédito, Débito
- Registro de vendas não pagas (dívidas) com nome do devedor

###  Relatórios e Filtros
- Visualização do total pago e total devido por dia
- Filtros por data e por devedor
- Exibição de todas as vendas ou apenas dívidas específicas

###  Autocompletar Produtos
- Sistema de sugestão de produtos conforme digitação
- Cadastro automático de novos produtos

###  Interface Moderna
- Design dark mode com CustomTkinter
- Tabela organizada com todas as informações de vendas
- Feedback visual claro para ações do usuário

##  Tecnologias Utilizadas

- **Python** (Linguagem principal)
- **CustomTkinter** (Interface gráfica moderna)
- **SQLite** (Banco de dados embutido)
- **Datetime** (Controle de datas e horários)

## ⚙️ Como Executar

1. Certifique-se de ter Python 3.x instalado
2. Instale as dependências:
   ```
   pip install customtkinter
   ```
3. Execute o arquivo principal:
   ```
   python main.py
   ```

##  Estrutura do Projeto

- `main.py`: Arquivo principal com a interface gráfica
- `banco.py`: Módulo com todas as operações de banco de dados
- `README.md`: Este arquivo com documentação do projeto

##  Licença

Este projeto é open-source e está disponível para uso e modificação.

---

Desenvolvido para facilitar o gerenciamento diário de um pequeno comércio, tornando o controle de vendas e dívidas mais eficiente e organizado.
