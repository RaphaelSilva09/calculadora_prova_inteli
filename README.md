# 🎓 Calculadora de Prova Inteli

Script Python para calcular a nota necessária na prova do módulo para atingir a média. Aplicável para qualquer curso/módulo do Inteli.

## 📋 Descrição

Este projeto analisa o arquivo HTML exportado do portal Adalove e calcula automaticamente:

-   📊 A nota necessária na prova para atingir a média 7.0
-   🎲 Simulação com notas pendentes
-   📋 Visualização completa do boletim atual

## ✨ Features

-   **🤖 Coleta automática** via automação de navegador (Playwright)
-   **👤 Detecção de perfil Inteli** - usa automaticamente o perfil do Chrome/Edge/Brave vinculado à conta @inteli.edu.br
-   **🔔 Fechamento automático de popups** - fecha automaticamente o popup de faltas que bloqueia a interface
-   **🖥️ Janela maximizada** - navegador abre maximizado no Windows
-   **🎨 Interface estilizada** no terminal com cores e tabelas formatadas (Rich + pyfiglet)
-   **📄 Parsing automático** do HTML do Adalove
-   **⚖️ Cálculo ponderado** das notas por peso de cada atividade
-   **🎲 Simulação flexível de notas** - 3 opções: nota padrão (7.0), nota customizada ou entrada manual
-   **🎯 Meta automática** para média 7.0 (padrão Inteli)
-   **📦 Instalação automática** de dependências
-   **🌐 Compatível** com Windows, Linux e macOS

## 🚀 Como Usar

### Método Principal: Menu Interativo

```bash
python main.py
```

O menu oferece 3 opções:

1. **🤖 Coleta Automática** - Abre o navegador e extrai as notas
2. **📊 Apenas Calcular** - Usa o arquivo `Adalove.html` existente
3. **❌ Sair**

### Argumentos de Linha de Comando

```bash
# Modo automático (coleta + cálculo, sem menu)
python main.py --auto
python main.py -a

# Modo manual (apenas cálculo)
python main.py --manual
python main.py -m
```

### Como Funciona a Coleta Automática

1. O script detecta automaticamente o navegador instalado (Chrome, Brave, Edge ou Firefox)
2. **Detecta automaticamente o perfil vinculado ao Inteli** (busca email @inteli.edu.br nas configurações)
3. Copia o perfil para um diretório temporário (evita conflitos com o navegador aberto)
4. Seu navegador abre na página do Adalove já logado (ou você faz login normalmente)
5. Navegue até a página do módulo desejado
6. O script detecta e clica na aba "Notas" automaticamente
7. **Fecha automaticamente popups de faltas** que possam bloquear a interface
8. O HTML é extraído e o cálculo inicia automaticamente

> **Por que usar automação?** O Adalove é uma Single Page Application (SPA) em React, onde o conteúdo é gerado dinamicamente via JavaScript. Por isso, simplesmente salvar o HTML pelo navegador nem sempre funciona corretamente.

**Navegadores suportados:**

-   Google Chrome ✅
-   Brave Browser ✅
-   Microsoft Edge ✅
-   Mozilla Firefox ✅

### Opção Alternativa: Exportar HTML Manualmente

Se preferir não usar automação:

1. Acesse o portal Adalove
2. Navegue até a página de notas do seu módulo
3. Clique com o botão direito → "Salvar como..." → "Página web completa" ou "HTML"
4. Salve como `Adalove.html` na pasta do projeto
5. Execute: `python main.py --manual`

## 📦 Dependências

As dependências são instaladas automaticamente na primeira execução, mas você pode instalar manualmente:

```bash
pip install beautifulsoup4 rich pyfiglet playwright
```

| Pacote           | Descrição                                                  |
| ---------------- | ---------------------------------------------------------- |
| `beautifulsoup4` | Parsing de HTML                                            |
| `rich`           | Interface rica no terminal (cores, tabelas, painéis)       |
| `pyfiglet`       | ASCII Art para o cabeçalho                                 |
| `playwright`     | Automação de navegador (usa Chrome/Edge/Firefox instalado) |

## 📁 Estrutura do Projeto

```
calculadora_prova_inteli/
├── main.py              # 🚀 Script principal (ponto de entrada)
├── src/                 # 📂 Módulos auxiliares
│   ├── __init__.py
│   ├── coletar.py       # 🤖 Automação para coleta de dados
│   └── calcular.py      # 📊 Cálculo de notas
├── Adalove.html         # 📄 Arquivo HTML gerado (após coleta)
├── README.md
├── .gitignore
└── LICENSE
```

## 🖥️ Preview

O script exibe:

-   🎨 Banner em ASCII Art estilizado
-   📊 Tabela com todas as atividades, pesos, notas e status
-   📋 Painel colorido com o resultado:
    -   **🟢 Verde**: Você já atingiu a média!
    -   **🟡 Amarelo**: Nota necessária na prova
    -   **🔴 Vermelho**: Situação matematicamente complicada

## ⚙️ Requisitos

-   Python 3.6+
-   Navegador instalado (Chrome, Brave, Edge ou Firefox)
-   Conexão com internet (apenas para instalação automática de dependências)

## 📝 Changelog Recente

### v2.0.0 (Reestruturação)

-   ✨ **Novo script principal:** `main.py` com menu interativo
-   📂 **Reorganização:** Scripts auxiliares movidos para `src/`
-   🎨 **Interface unificada:** Estilo consistente com Rich em todos os scripts
-   👤 **Detecção automática de perfil:** Busca e usa o perfil vinculado ao @inteli.edu.br
-   🔔 **Fechamento automático de popup:** Fecha o popup de faltas que aparece para alguns usuários
-   🖥️ **Janela maximizada:** Navegador abre maximizado no Windows
-   🎲 **Simulação de notas aprimorada:** 3 opções (padrão 7.0, customizada ou manual)
-   🔗 **URL corrigida:** Acesso direto à página academic-life

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.
