# Calculadora de Prova Inteli

Script Python para calcular a nota necessária na prova do módulo para atingir a média. Aplicável para qualquer curso/módulo do Inteli.

## Descrição

Este script analisa o arquivo HTML exportado do portal Adalove e calcula automaticamente:

-   A nota necessária na prova para atingir a média 7.0
-   Simulação com notas pendentes
-   Visualização completa do boletim atual

## Features

-   **Coleta automática** via automação de navegador (Playwright)
-   **Interface no terminal** com cores e tabelas formatadas
-   **Parsing automático** do HTML do Adalove
-   **Cálculo ponderado** das notas por peso de cada atividade
-   **Simulação de notas** para atividades ainda não lançadas
-   **Meta automática** para média 7.0 (padrão Inteli)
-   **Instalação automática** de dependências
-   **Compatível** com Windows, Linux e macOS

## Como Usar

### Opção 1: Coleta Automática (Recomendado)

O script `coletar_notas.py` usa automação de navegador para extrair os dados diretamente do Adalove:

```bash
python coletar_notas.py
```

**Como funciona:**

1. O script detecta automaticamente o navegador instalado (Chrome, Brave, Edge ou Firefox)
2. Seu navegador abre na página do Adalove
3. Você faz login normalmente (suporta 2FA/SSO do Google/Microsoft)
4. Navegue até a página do módulo desejado
5. O script detecta e clica na aba "Notas" automaticamente
6. O HTML é extraído e o cálculo inicia automaticamente

> **Por que usar automação?** O Adalove é uma Single Page Application (SPA) em React, onde o conteúdo é gerado dinamicamente via JavaScript. Por isso, simplesmente salvar o HTML pelo navegador nem sempre funciona corretamente.

**Navegadores suportados:**

-   Google Chrome
-   Brave Browser
-   Microsoft Edge
-   Mozilla Firefox

### Opção 2: Exportar HTML Manualmente

Se preferir não usar automação:

1. Acesse o portal Adalove
2. Navegue até a página de notas do seu módulo
3. Clique com o botão direito → "Salvar como..." → "Página web completa" ou "HTML"
4. Salve como `Adalove.html` na mesma pasta do script
5. Execute:

```bash
python notas.py

# Ou especificando o arquivo HTML
python notas.py caminho/para/seu/arquivo/Adalove.html
```

## Dependências

As dependências são instaladas automaticamente na primeira execução, mas você pode instalar manualmente:

```bash
# Para o script de cálculo
pip install beautifulsoup4 rich pyfiglet

# Para a coleta automática (usa seu navegador instalado, não precisa baixar nada extra)
pip install playwright
```

| Pacote           | Descrição                                                  |
| ---------------- | ---------------------------------------------------------- |
| `beautifulsoup4` | Parsing de HTML                                            |
| `rich`           | Interface rica no terminal (cores, tabelas, painéis)       |
| `pyfiglet`       | ASCII Art para o cabeçalho                                 |
| `playwright`     | Automação de navegador (usa Chrome/Edge/Firefox instalado) |

## Estrutura do Projeto

```
calculadora_prova_inteli/
├── notas.py           # Script principal de cálculo
├── coletar_notas.py   # Automação para coleta de dados
├── Adalove.html       # Arquivo HTML gerado (após coleta)
├── README.md
└── LICENSE
```

## Preview

O script exibe:

-   Banner em ASCII Art
-   Tabela com todas as atividades, pesos, notas e status
-   Painel colorido com o resultado:
    -   **Verde**: Você já atingiu a média!
    -   **Amarelo**: Nota necessária na prova
    -   **Vermelho**: Situação matematicamente complicada

## Requisitos

-   Python 3.6+
-   Conexão com internet (apenas para instalação automática de dependências)

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.
