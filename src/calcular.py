#!/usr/bin/env python3
"""
Módulo de cálculo de notas do Adalove.

Analisa o HTML exportado do portal e calcula a nota necessária na prova
para atingir a média 7.0.
"""

import os
import sys
import subprocess

# Instalação automática de dependências
def install_dependencies():
    """Instala dependências automaticamente se não estiverem presentes."""
    packages = {
        'bs4': 'beautifulsoup4',
        'rich': 'rich',
        'pyfiglet': 'pyfiglet'
    }
    
    missing = []
    for module, package in packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Instalando dependências: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q'] + missing)
        print("Dependências instaladas! Reiniciando...\n")
        os.execv(sys.executable, [sys.executable] + sys.argv)

install_dependencies()

from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, FloatPrompt
from rich import box
import pyfiglet

# Configuração do Console
console = Console()


def print_header():
    """Imprime o cabeçalho em ASCII Art."""
    ascii_banner = pyfiglet.figlet_format("CALCULADORA PROVA", font="slant")
    console.print(f"[bold cyan]{ascii_banner}[/]")
    console.print("[bold white on blue]  Sistema de Cálculo de Notas - Inteli  [/]", justify="center")
    console.print("\n")


def parse_float(text):
    """Converte texto para float lidando com vírgulas e erros."""
    try:
        return float(text.replace(',', '.'))
    except ValueError:
        return None


def get_style_nota(nota):
    """Retorna a cor baseada na nota."""
    if nota is None:
        return "dim white"
    if nota >= 7.0:
        return "bold green"
    elif nota >= 5.0:
        return "bold yellow"
    else:
        return "bold red"


def calcular_notas(file_path=None):
    """
    Calcula as notas e a nota necessária na prova.
    
    Args:
        file_path: Caminho para o arquivo HTML. Se None, usa 'Adalove.html'.
    
    Returns:
        bool: True se o cálculo foi bem-sucedido.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header()

    # Recebe o caminho do arquivo
    if file_path is None:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
        else:
            # Procura no diretório raiz do projeto (um nível acima de src/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(os.path.dirname(script_dir), 'Adalove.html')
    
    if not os.path.exists(file_path):
        console.print(Panel.fit(
            f"[bold red]ERRO FATAL:[/]\nArquivo [yellow]'{file_path}'[/] não encontrado.\n\n"
            "Salve a página do portal como HTML na mesma pasta deste script.",
            title="Arquivo Ausente", border_style="red"
        ))
        return False

    # Parsing
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    rows = soup.find_all('tr', class_='styled-tr')

    if not rows:
        console.print(Panel.fit(
            "[bold red]Nenhuma atividade encontrada![/]\n\n"
            "Verifique se o arquivo HTML está correto e contém a tabela de notas.",
            title="Erro de Parsing", border_style="red"
        ))
        return False

    soma_ponderada = 0.0
    peso_total = 0.0
    peso_prova = 0.0
    atividades_pendentes = []

    # Tabela Visual
    table = Table(title="📊 Boletim Atual", box=box.ROUNDED, show_lines=True)
    table.add_column("Atividade", style="cyan", no_wrap=False, max_width=50)
    table.add_column("Peso", justify="center", style="magenta")
    table.add_column("Nota", justify="center")
    table.add_column("Status", justify="center")

    for row in rows:
        nome_div = row.find('td', attrs={'data-label': 'Atividades'})
        raw_text = list(nome_div.stripped_strings)
        nome_atividade = " ".join(raw_text)

        peso_div = row.find('td', attrs={'data-label': 'Pontos'})
        peso = parse_float(list(peso_div.stripped_strings)[-1])

        notas_div = row.find('td', attrs={'data-label': 'Notas'})
        nota_text = list(notas_div.stripped_strings)[-1]
        nota = parse_float(nota_text)

        if peso is not None:
            peso_total += peso

        is_prova = "Prova" in nome_atividade and "Módulo" in nome_atividade

        if is_prova:
            peso_prova = peso
            table.add_row(f"[bold]{nome_atividade}[/]", str(peso), "-", "[bold blue]🎯 A CALCULAR[/]")
            continue

        status = ""
        nota_display = "-"
        
        if nota is not None:
            soma_ponderada += (nota * peso)
            nota_display = f"{nota:.1f}"
            status = "[green]✓ Lançada[/]"
        else:
            atividades_pendentes.append({'nome': nome_atividade, 'peso': peso})
            status = "[yellow]⏳ Pendente[/]"

        nome_truncado = nome_atividade[:47] + "..." if len(nome_atividade) > 50 else nome_atividade
        table.add_row(
            nome_truncado, 
            str(peso), 
            Text(nota_display, style=get_style_nota(nota)),
            status
        )

    console.print(table)
    console.print()
    
    # Resumo
    resumo = Table(box=box.SIMPLE, show_header=False)
    resumo.add_column("Label", style="bold")
    resumo.add_column("Valor", style="cyan")
    resumo.add_row("Peso Total do Módulo:", f"{peso_total}")
    resumo.add_row("Soma Ponderada Atual:", f"{soma_ponderada:.2f}")
    console.print(resumo)
    console.print()

    # Tratamento de atividades pendentes
    if atividades_pendentes:
        console.print(Panel(
            "[bold]Opções para notas pendentes:[/]\n\n"
            "• [cyan]ENTER[/] ou [cyan]7[/] → Preenche tudo com 7.0\n"
            "• [cyan]Outro número[/] (ex: 8.5) → Aplica essa nota em todas\n"
            "• [cyan]n[/] ou [cyan]não[/] → Inserir cada nota manualmente",
            title="🎲 Simulação de Notas", style="blue"
        ))
        
        resposta = Prompt.ask(
            "[bold]Digite:[/] [cyan]número[/] para nota padrão, [cyan]n[/] para manual, ou [cyan]ENTER[/] para 7.0",
            default="7"
        ).strip().lower()
        
        if resposta in ["n", "no", "não", "nao", "manual"]:
            console.print("\n[bold]Inserção manual de notas:[/]\n")
            for atv in atividades_pendentes:
                while True:
                    nota_input = FloatPrompt.ask(f"Nota para [cyan]{atv['nome'][:40]}...[/] (Peso {atv['peso']})")
                    if 0 <= nota_input <= 10:
                        soma_ponderada += (nota_input * atv['peso'])
                        console.print(f"[dim] → Registrado: {nota_input} × {atv['peso']} = {nota_input*atv['peso']:.2f}[/]")
                        break
                    console.print("[red]A nota deve ser entre 0 e 10.[/]")
                print()
        else:
            if resposta in ["", "y", "yes", "s", "sim"]:
                nota_padrao = 7.0
            else:
                try:
                    nota_padrao = float(resposta.replace(',', '.'))
                    if nota_padrao < 0 or nota_padrao > 10:
                        console.print("[yellow]Nota fora do intervalo 0-10. Usando 7.0[/]")
                        nota_padrao = 7.0
                except ValueError:
                    console.print("[yellow]Valor inválido. Usando 7.0[/]")
                    nota_padrao = 7.0
            
            console.print(f"\n[bold]Aplicando nota [cyan]{nota_padrao}[/] em todas as pendentes:[/]\n")
            for atv in atividades_pendentes:
                soma_ponderada += (nota_padrao * atv['peso'])
                console.print(f"[dim] → {atv['nome'][:40]}...: {nota_padrao} × {atv['peso']} = {nota_padrao*atv['peso']:.2f}[/]")
            console.print()

    # Cálculo Final
    MEDIA_ALVO = 7.0
    target_score = MEDIA_ALVO * peso_total
    pontos_restantes = target_score - soma_ponderada

    console.rule("[bold white]RESULTADO DA ANÁLISE[/]")
    print()

    if peso_prova == 0:
        console.print(Panel(
            "[bold red]Não foi possível identificar o peso da prova automaticamente.[/]\n\n"
            "Verifique se existe uma atividade 'Prova de Módulo' no boletim.",
            title="⚠️ Aviso", border_style="yellow"
        ))
        return False

    nota_necessaria = pontos_restantes / peso_prova

    if nota_necessaria <= 0:
        media_projetada = soma_ponderada / peso_total
        console.print(Panel(
            f"[bold green]APROVADO NA SIMULAÇÃO![/]\n\n"
            f"Sua média projetada: [bold]{media_projetada:.2f}[/]\n"
            f"Você já atingiu a pontuação para média {MEDIA_ALVO}!",
            border_style="green", title="🎉 SUCESSO 🎉", padding=(1, 5)
        ))
    
    elif nota_necessaria > 10:
        max_media = (soma_ponderada + (10 * peso_prova)) / peso_total
        console.print(Panel(
            f"[bold red]MATEMATICAMENTE COMPLICADO[/]\n\n"
            f"Você precisaria de [bold]{nota_necessaria:.2f}[/] na prova.\n"
            f"Média máxima possível (gabaritando): [bold]{max_media:.2f}[/]",
            border_style="red", title="💀 PERIGO 💀", padding=(1, 5)
        ))
    
    else:
        console.print(Panel(
            f"Para fechar com média [bold yellow]{MEDIA_ALVO}[/]:\n\n"
            f"Você precisa tirar [bold cyan]{nota_necessaria:.2f}[/] na Prova\n"
            f"(Peso da prova: {peso_prova})",
            border_style="yellow", title="🎯 META 🎯", padding=(1, 5)
        ))

    return True


if __name__ == "__main__":
    try:
        calcular_notas()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário.[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {e}[/]")
        sys.exit(1)
