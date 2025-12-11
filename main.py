#!/usr/bin/env python3
"""
Calculadora de Prova Inteli
===========================

Script principal que orquestra a coleta automática de notas do Adalove
e calcula a nota necessária na prova para atingir a média 7.0.

Uso:
    python main.py          # Coleta automática + cálculo
    python main.py --manual # Apenas cálculo (requer Adalove.html)
"""

import os
import sys
import subprocess
import argparse

# Garante que o diretório src está no path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def install_base_dependencies():
    """Instala dependências base (Rich e pyfiglet) para o menu."""
    packages = {'rich': 'rich', 'pyfiglet': 'pyfiglet'}
    missing = []
    
    for module, package in packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"📦 Instalando dependências: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q'] + missing)
        print("✅ Dependências instaladas! Reiniciando...\n")
        os.execv(sys.executable, [sys.executable] + sys.argv)


install_base_dependencies()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from rich.table import Table
import pyfiglet

console = Console()


def print_banner():
    """Imprime o banner principal."""
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_banner = pyfiglet.figlet_format("INTELI NOTAS", font="slant")
    console.print(f"[bold cyan]{ascii_banner}[/]")
    console.print("[bold white on blue]  Calculadora de Nota de Prova - Inteli  [/]", justify="center")
    console.print()


def print_menu():
    """Exibe o menu de opções."""
    menu = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    menu.add_column("Opção", style="bold cyan", width=5)
    menu.add_column("Descrição")
    
    menu.add_row("1", "🤖 [bold]Coleta Automática[/] - Abre o navegador e extrai as notas")
    menu.add_row("2", "📊 [bold]Apenas Calcular[/] - Usa o arquivo Adalove.html existente")
    menu.add_row("3", "❌ [bold]Sair[/]")
    
    console.print(Panel(menu, title="📋 Menu Principal", border_style="blue"))


def executar_coleta():
    """Executa o módulo de coleta."""
    try:
        from src.coletar import coletar_notas
        return coletar_notas(output_dir=script_dir)
    except ImportError:
        # Fallback se a importação falhar
        coletar_path = os.path.join(src_dir, 'coletar.py')
        result = subprocess.run([sys.executable, coletar_path], cwd=script_dir)
        return result.returncode == 0


def executar_calculo():
    """Executa o módulo de cálculo."""
    try:
        from src.calcular import calcular_notas
        html_path = os.path.join(script_dir, 'Adalove.html')
        return calcular_notas(file_path=html_path)
    except ImportError:
        # Fallback se a importação falhar
        calcular_path = os.path.join(src_dir, 'calcular.py')
        html_path = os.path.join(script_dir, 'Adalove.html')
        result = subprocess.run([sys.executable, calcular_path, html_path], cwd=script_dir)
        return result.returncode == 0


def modo_automatico():
    """Executa coleta + cálculo automaticamente."""
    sucesso = executar_coleta()
    
    if sucesso:
        console.print()
        console.rule("[bold]Iniciando Cálculo[/]")
        console.print()
        executar_calculo()
    else:
        console.print(Panel(
            "[bold red]Não foi possível coletar as notas.[/]\n\n"
            "Tente novamente ou use a opção 'Apenas Calcular' com um arquivo HTML salvo manualmente.",
            title="❌ Erro", border_style="red"
        ))


def modo_manual():
    """Executa apenas o cálculo com arquivo existente."""
    html_path = os.path.join(script_dir, 'Adalove.html')
    
    if not os.path.exists(html_path):
        console.print(Panel(
            f"[bold red]Arquivo não encontrado![/]\n\n"
            f"O arquivo [yellow]Adalove.html[/] não existe.\n\n"
            "[bold]Como obter o arquivo:[/]\n"
            "1. Acesse o Adalove no navegador\n"
            "2. Navegue até a aba de Notas do módulo\n"
            "3. Clique com botão direito → 'Salvar como...'\n"
            f"4. Salve como [cyan]Adalove.html[/] em:\n   [dim]{script_dir}[/]",
            title="📄 Arquivo Ausente", border_style="yellow"
        ))
        return
    
    executar_calculo()


def main():
    """Função principal com menu interativo."""
    parser = argparse.ArgumentParser(description='Calculadora de Prova Inteli')
    parser.add_argument('--manual', '-m', action='store_true', 
                       help='Modo manual: apenas calcula com arquivo existente')
    parser.add_argument('--auto', '-a', action='store_true',
                       help='Modo automático: coleta e calcula sem menu')
    
    args = parser.parse_args()
    
    # Modos diretos via argumentos
    if args.manual:
        print_banner()
        modo_manual()
        return
    
    if args.auto:
        modo_automatico()
        return
    
    # Menu interativo
    while True:
        print_banner()
        print_menu()
        console.print()
        
        escolha = Prompt.ask(
            "[bold]Escolha uma opção[/]",
            choices=["1", "2", "3"],
            default="1"
        )
        
        if escolha == "1":
            modo_automatico()
            console.print()
            Prompt.ask("[dim]Pressione ENTER para voltar ao menu[/]")
            
        elif escolha == "2":
            modo_manual()
            console.print()
            Prompt.ask("[dim]Pressione ENTER para voltar ao menu[/]")
            
        elif escolha == "3":
            console.print("\n[bold cyan]Até mais! 👋[/]\n")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operação cancelada.[/]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {e}[/]\n")
        sys.exit(1)
