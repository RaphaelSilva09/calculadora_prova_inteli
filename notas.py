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
from rich.progress import track
from rich import box
import pyfiglet
import time

# Configuração do Console
console = Console()

def print_header():
    """Imprime o cabeçalho em ASCII Art."""
    ascii_banner = pyfiglet.figlet_format("CALCULADORA PROVA INTELI?", font="slant")
    console.print(f"[bold cyan]{ascii_banner}[/]")
    console.print("[bold white on blue]  Sistema de Cálculo de Notas - Ciência da Computação  [/]", justify="center")
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

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header()

    # Recebe o caminho do arquivo via argumento ou usa o padrão
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'Adalove.html'
    
    if not os.path.exists(file_path):
        console.print(Panel.fit(
            f"[bold red]ERRO FATAL:[/]\nArquivo [yellow]'{file_path}'[/] não encontrado.\n\n"
            "Salve a página do portal como HTML na mesma pasta deste script.",
            title="Arquivo Ausente", border_style="red"
        ))
        return

    # Parsing com barra de carregamento fake (para estilo)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    rows = soup.find_all('tr', class_='styled-tr')

    soma_ponderada = 0.0
    peso_total = 0.0
    peso_prova = 0.0
    atividades_pendentes = []

    # Tabela Visual
    table = Table(title="Boletim Atual", box=box.ROUNDED, show_lines=True)
    table.add_column("Atividade", style="cyan", no_wrap=False)
    table.add_column("Peso", justify="center", style="magenta")
    table.add_column("Nota", justify="center")
    table.add_column("Status", justify="center")

    for row in rows:
        nome_div = row.find('td', attrs={'data-label': 'Atividades'})
        # Limpeza agressiva do nome para tirar ícones SVG e espaços
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
            table.add_row(f"[bold]{nome_atividade}[/]", str(peso), "-", "[bold blue]A CALCULAR[/]")
            continue

        status = ""
        nota_display = "-"
        
        if nota is not None:
            soma_ponderada += (nota * peso)
            nota_display = f"{nota:.1f}"
            status = "[green]✓ Lançada[/]"
        else:
            atividades_pendentes.append({'nome': nome_atividade, 'peso': peso})
            status = "[yellow]⚠ Pendente[/]"

        table.add_row(
            nome_atividade[:50] + ("..." if len(nome_atividade) > 50 else ""), 
            str(peso), 
            Text(nota_display, style=get_style_nota(nota)),
            status
        )

    console.print(table)
    console.print(f"\n[bold]Peso Total do Módulo:[/bold] {peso_total}")
    console.print(f"[bold]Soma Ponderada Atual:[/bold] {soma_ponderada:.2f}\n")

    # Input Visual
    if atividades_pendentes:
        console.print(Panel("Preencha as notas das atividades pendentes para simular:", style="blue"))
        
        # Pergunta se quer otimizar com nota média
        otimizar = Prompt.ask(
            "Deseja preencher todas as notas pendentes com [bold yellow]7.0[/]? [Y/n]",
            default="y"
        ).strip().lower()
        
        if otimizar in ["y", "yes", "s", "sim", ""]:
            for atv in atividades_pendentes:
                nota_input = 7.0
                soma_ponderada += (nota_input * atv['peso'])
                console.print(f"[dim] -> {atv['nome']}: {nota_input} * {atv['peso']} = {nota_input*atv['peso']:.2f}[/]")
            console.print()
        else:
            for atv in atividades_pendentes:
                while True:
                    nota_input = FloatPrompt.ask(f"Quanto você acha que tira em [cyan]{atv['nome']}[/] (Peso {atv['peso']})?")
                    if 0 <= nota_input <= 10:
                        soma_ponderada += (nota_input * atv['peso'])
                        # Atualiza tabela visualmente (opcional, aqui só somamos)
                        console.print(f"[dim] -> Registrado: {nota_input} * {atv['peso']} = {nota_input*atv['peso']:.2f}[/]")
                        break
                    console.print("[red]A nota deve ser entre 0 e 10.[/]")
                print()

    # Cálculo Final
    MEDIA_ALVO = 7.0 # Inteli padrão
    target_score = MEDIA_ALVO * peso_total
    pontos_restantes = target_score - soma_ponderada

    console.rule("[bold white]RESULTADO DA ANÁLISE[/]")
    print()

    if peso_prova == 0:
        console.print("[bold red]ERRO:[/bold] Não foi possível identificar o peso da prova automaticamente.")
        return

    nota_necessaria = pontos_restantes / peso_prova

    if nota_necessaria <= 0:
        # Passou
        panel_content = (
            f"[bold green]APROVADO NA SIMULAÇÃO![/]\n\n"
            f"Sua média projetada (sem prova): [bold]{(soma_ponderada/peso_total):.2f}[/]\n"
            f"Você já atingiu a pontuação necessária para a média {MEDIA_ALVO}."
        )
        console.print(Panel(panel_content, border_style="green", title="🎉 SUCESSO 🎉"))
    
    elif nota_necessaria > 10:
        # Reprovou matematicamente
        max_media = (soma_ponderada + (10 * peso_prova)) / peso_total
        panel_content = (
            f"[bold red]MATEMATICAMENTE COMPLICADO[/]\n\n"
            f"Você precisaria de [bold]{nota_necessaria:.2f}[/] na prova.\n"
            f"Sua média máxima possível (gabaritando a prova) é: [bold]{max_media:.2f}[/]"
        )
        console.print(Panel(panel_content, border_style="red", title="💀 PERIGO 💀"))
    
    else:
        # Cálculo Padrão
        panel_content = (
            f"Para fechar com média [bold yellow]{MEDIA_ALVO}[/]:\n\n"
            f"Você precisa tirar [bold cyan size=20]{nota_necessaria:.2f}[/] na Prova\n"
            f"(Peso da prova: {peso_prova})"
        )
        console.print(Panel(panel_content, border_style="yellow", title="🎯 META 🎯", padding=(1, 5)))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Operação cancelada pelo usuário.[/]")
        sys.exit