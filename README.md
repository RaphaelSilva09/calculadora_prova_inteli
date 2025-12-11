# Calculadora de Prova Inteli

Script Python para calcular a nota necessária na prova do módulo para atingir a média. Aplicável para qualquer curso/módulo do Inteli.

## Descrição

Este script analisa o arquivo HTML exportado do portal Adalove e calcula automaticamente:
- A nota necessária na prova para atingir a média 7.0
- Simulação com notas pendentes
- Visualização completa do boletim atual

## Features

- **Interface no terminal** com cores e tabelas formatadas
- **Parsing automático** do HTML do Adalove
- **Cálculo ponderado** das notas por peso de cada atividade
- **Simulação de notas** para atividades ainda não lançadas
- **Meta automática** para média 7.0 (padrão Inteli)
- **Instalação automática** de dependências
- **Compatível** com Windows, Linux e macOS

## Como Usar

### 1. Exportar o HTML do Adalove

1. Acesse o portal Adalove
2. Navegue até a página de notas do seu módulo
3. Clique com o botão direito → "Salvar como..." → "Página web completa" ou "HTML"
4. Salve como `Adalove.html` na mesma pasta do script

### 2. Executar o Script

```bash
# Execução padrão (busca Adalove.html na mesma pasta)
python notas.py

# Ou especificando o arquivo HTML
python notas.py caminho/para/seu/arquivo/Adalove.html
```

## Dependências

As dependências são instaladas automaticamente na primeira execução, mas você pode instalar manualmente:

```bash
pip install beautifulsoup4 rich pyfiglet
```

| Pacote | Descrição |
|--------|-----------|
| `beautifulsoup4` | Parsing de HTML |
| `rich` | Interface rica no terminal (cores, tabelas, painéis) |
| `pyfiglet` | ASCII Art para o cabeçalho |

## Preview

O script exibe:
- Banner em ASCII Art
- Tabela com todas as atividades, pesos, notas e status
- Painel colorido com o resultado:
  - **Verde**: Você já atingiu a média!
  - **Amarelo**: Nota necessária na prova
  - **Vermelho**: Situação matematicamente complicada

## Requisitos

- Python 3.6+
- Conexão com internet (apenas para instalação automática de dependências)

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.
