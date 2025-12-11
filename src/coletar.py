#!/usr/bin/env python3
"""
Módulo de coleta automática de notas do Adalove usando Playwright.

O script detecta e usa o navegador já instalado no sistema (Chrome, Edge, Firefox),
abre uma janela visível para que você faça login manualmente (suporta 2FA/SSO),
aguarda a navegação até a aba de notas, e exporta o HTML renderizado.
"""

import os
import sys
import subprocess
import platform

# Instalação automática de dependências
def install_dependencies():
    """Instala Playwright e Rich automaticamente (sem baixar navegadores extras)."""
    packages = {
        'playwright': 'playwright',
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
        print(f"📦 Instalando dependências: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q'] + missing)
        print("✅ Dependências instaladas! Reiniciando...\n")
        os.execv(sys.executable, [sys.executable] + sys.argv)

install_dependencies()

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box
import pyfiglet
import time
import json
import shutil
import tempfile

# Configuração do Console Rich
console = Console()

# Configurações
ADALOVE_URL = "https://adalove.inteli.edu.br/academic-life"
OUTPUT_FILE = "Adalove.html"
TIMEOUT_LOGIN = 300000  # 5 minutos para fazer login
TIMEOUT_NAVEGACAO = 60000  # 1 minuto para navegação normal


def print_header():
    """Imprime o cabeçalho em ASCII Art."""
    ascii_banner = pyfiglet.figlet_format("COLETOR ADALOVE", font="slant")
    console.print(f"[bold cyan]{ascii_banner}[/]")
    console.print("[bold white on blue]  Automação de Coleta de Notas - Inteli  [/]", justify="center")
    console.print()


def obter_user_data_dir(navegador_name):
    """
    Retorna o diretório de dados do usuário do navegador para usar perfis reais.
    Isso permite abrir o navegador com a tela de seleção de perfil.
    """
    sistema = platform.system().lower()
    
    user_data_dirs = {
        'chrome': {
            'windows': os.path.expandvars(r'%LocalAppData%\Google\Chrome\User Data'),
            'darwin': os.path.expanduser('~/Library/Application Support/Google/Chrome'),
            'linux': os.path.expanduser('~/.config/google-chrome'),
        },
        'edge': {
            'windows': os.path.expandvars(r'%LocalAppData%\Microsoft\Edge\User Data'),
            'darwin': os.path.expanduser('~/Library/Application Support/Microsoft Edge'),
            'linux': os.path.expanduser('~/.config/microsoft-edge'),
        },
        'brave': {
            'windows': os.path.expandvars(r'%LocalAppData%\BraveSoftware\Brave-Browser\User Data'),
            'darwin': os.path.expanduser('~/Library/Application Support/BraveSoftware/Brave-Browser'),
            'linux': os.path.expanduser('~/.config/BraveSoftware/Brave-Browser'),
        },
    }
    
    if sistema == 'darwin':
        sistema_key = 'darwin'
    elif sistema == 'windows':
        sistema_key = 'windows'
    else:
        sistema_key = 'linux'
    
    if navegador_name in user_data_dirs:
        path = user_data_dirs[navegador_name].get(sistema_key)
        if path and os.path.exists(path):
            return path
    
    return None


def encontrar_perfil_inteli(user_data_dir):
    """
    Procura o perfil do Chrome/Edge/Brave que está vinculado ao domínio inteli.edu.br.
    Retorna o nome do diretório do perfil (ex: 'Profile 1', 'Default') ou None.
    """
    if not user_data_dir or not os.path.exists(user_data_dir):
        return None
    
    console.print("[dim]🔍 Procurando perfil vinculado ao Inteli...[/]")
    
    # Lista de possíveis pastas de perfil
    perfis_possiveis = ['Default'] + [f'Profile {i}' for i in range(1, 20)]
    
    for perfil in perfis_possiveis:
        perfil_path = os.path.join(user_data_dir, perfil)
        
        if not os.path.exists(perfil_path):
            continue
        
        # Verifica o arquivo Preferences que contém info da conta
        prefs_file = os.path.join(perfil_path, 'Preferences')
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # Procura por email do Inteli nas preferências
                account_info = prefs.get('account_info', [])
                for account in account_info:
                    email = account.get('email', '')
                    if 'inteli.edu.br' in email.lower():
                        console.print(f"   [green]✓[/] Encontrado perfil: [cyan]{email}[/]")
                        return perfil
                
                # Também verifica em signin
                signin = prefs.get('signin', {})
                allowed_account = signin.get('allowed_first_run_account', '')
                if 'inteli.edu.br' in allowed_account.lower():
                    console.print(f"   [green]✓[/] Encontrado perfil: [cyan]{allowed_account}[/]")
                    return perfil
                    
            except (json.JSONDecodeError, IOError):
                continue
        
        # Verifica também o arquivo "Secure Preferences" como fallback
        secure_prefs_file = os.path.join(perfil_path, 'Secure Preferences')
        if os.path.exists(secure_prefs_file):
            try:
                with open(secure_prefs_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'inteli.edu.br' in content.lower():
                        console.print(f"   [green]✓[/] Perfil Inteli encontrado: [cyan]{perfil}[/]")
                        return perfil
            except IOError:
                continue
    
    console.print("   [yellow]⚠[/] Nenhum perfil do Inteli encontrado automaticamente")
    return None


def copiar_perfil_para_temp(user_data_dir, perfil_nome):
    """
    Copia os arquivos essenciais do perfil (cookies, login data) para um diretório temporário.
    Isso permite usar o perfil sem conflito com o Chrome em execução.
    Retorna o caminho do diretório temporário.
    """
    perfil_original = os.path.join(user_data_dir, perfil_nome)
    
    if not os.path.exists(perfil_original):
        return None
    
    # Cria diretório temporário
    temp_base = os.path.join(tempfile.gettempdir(), 'adalove_chrome_profile')
    temp_user_data = os.path.join(temp_base, 'User Data')
    temp_perfil = os.path.join(temp_user_data, perfil_nome)
    
    # Limpa diretório anterior se existir
    if os.path.exists(temp_base):
        try:
            shutil.rmtree(temp_base)
        except:
            pass
    
    os.makedirs(temp_perfil, exist_ok=True)
    
    console.print("[dim]📋 Copiando dados de sessão do perfil...[/]")
    
    # Arquivos essenciais para manter a sessão/login
    arquivos_essenciais = [
        'Cookies',
        'Login Data',
        'Web Data',
        'Preferences',
        'Secure Preferences',
        'Network',
        'Local Storage',
        'Session Storage',
        'IndexedDB',
    ]
    
    # Copia também o arquivo Local State do diretório raiz
    local_state = os.path.join(user_data_dir, 'Local State')
    if os.path.exists(local_state):
        try:
            shutil.copy2(local_state, os.path.join(temp_user_data, 'Local State'))
        except:
            pass
    
    for arquivo in arquivos_essenciais:
        origem = os.path.join(perfil_original, arquivo)
        destino = os.path.join(temp_perfil, arquivo)
        
        try:
            if os.path.isdir(origem):
                if os.path.exists(destino):
                    shutil.rmtree(destino)
                shutil.copytree(origem, destino)
            elif os.path.isfile(origem):
                shutil.copy2(origem, destino)
        except Exception:
            continue
    
    console.print(f"   [green]✓[/] Perfil copiado para temp")
    return temp_user_data


def detectar_navegador():
    """
    Detecta qual navegador está instalado no sistema.
    Retorna dict com informações do navegador ou None.
    
    Prioridade: Chrome > Brave > Edge > Firefox
    """
    sistema = platform.system().lower()
    
    navegadores = {
        'chrome': {
            'channel': 'chrome',
            'paths': {
                'linux': [
                    '/usr/bin/google-chrome',
                    '/usr/bin/google-chrome-stable',
                    '/snap/bin/chromium',
                    '/usr/bin/chromium',
                    '/usr/bin/chromium-browser',
                ],
                'darwin': [
                    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                ],
                'windows': [
                    os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
                    os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
                    os.path.expandvars(r'%LocalAppData%\Google\Chrome\Application\chrome.exe'),
                ],
            }
        },
        'brave': {
            'channel': 'chrome',
            'executable_path': True,
            'paths': {
                'linux': [
                    '/usr/bin/brave-browser',
                    '/usr/bin/brave',
                    '/snap/bin/brave',
                    '/opt/brave.com/brave/brave-browser',
                ],
                'darwin': [
                    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
                ],
                'windows': [
                    os.path.expandvars(r'%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe'),
                    os.path.expandvars(r'%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe'),
                    os.path.expandvars(r'%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe'),
                ],
            }
        },
        'edge': {
            'channel': 'msedge',
            'paths': {
                'linux': [
                    '/usr/bin/microsoft-edge',
                    '/usr/bin/microsoft-edge-stable',
                ],
                'darwin': [
                    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
                ],
                'windows': [
                    os.path.expandvars(r'%ProgramFiles%\Microsoft\Edge\Application\msedge.exe'),
                    os.path.expandvars(r'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe'),
                ],
            }
        },
        'firefox': {
            'channel': None,
            'type': 'firefox',
            'paths': {
                'linux': [
                    '/usr/bin/firefox',
                    '/snap/bin/firefox',
                ],
                'darwin': [
                    '/Applications/Firefox.app/Contents/MacOS/firefox',
                ],
                'windows': [
                    os.path.expandvars(r'%ProgramFiles%\Mozilla Firefox\firefox.exe'),
                    os.path.expandvars(r'%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe'),
                ],
            }
        },
    }
    
    # Normaliza o nome do sistema
    if sistema == 'darwin':
        sistema_key = 'darwin'
    elif sistema == 'windows':
        sistema_key = 'windows'
    else:
        sistema_key = 'linux'
    
    # Procura navegadores instalados
    for nome, config in navegadores.items():
        paths = config['paths'].get(sistema_key, [])
        for path in paths:
            if os.path.exists(path):
                console.print(f"[green]✓[/] Navegador detectado: [bold cyan]{nome.capitalize()}[/]")
                return {
                    'name': nome,
                    'channel': config.get('channel'),
                    'type': config.get('type', 'chromium'),
                    'path': path,
                    'executable_path': config.get('executable_path', False)
                }
    
    return None


def print_instrucoes():
    """Imprime instruções para o usuário em um painel estilizado."""
    instrucoes = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    instrucoes.add_column("Passo", style="bold cyan", width=5)
    instrucoes.add_column("Descrição")
    
    instrucoes.add_row("1.", "Seu navegador será aberto automaticamente")
    instrucoes.add_row("2.", "Faça login normalmente (suporta 2FA/SSO)")
    instrucoes.add_row("3.", "Navegue até a página do seu [bold]MÓDULO[/]")
    instrucoes.add_row("4.", "O script detectará a aba 'Notas' automaticamente")
    instrucoes.add_row("5.", "O HTML será salvo e o cálculo iniciará")
    
    console.print(Panel(instrucoes, title="📋 Instruções", border_style="blue"))
    console.print()


def coletar_notas(output_dir=None):
    """
    Abre o navegador e coleta as notas do Adalove.
    
    Args:
        output_dir: Diretório onde salvar o HTML. Se None, usa o diretório do script.
    
    Returns:
        bool: True se a coleta foi bem-sucedida, False caso contrário.
    """
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header()
    
    # Detecta navegador instalado
    navegador = detectar_navegador()
    
    if not navegador:
        console.print(Panel(
            "[bold red]Nenhum navegador compatível encontrado![/]\n\n"
            "Instale um dos seguintes:\n"
            "• Google Chrome\n"
            "• Brave Browser\n"
            "• Microsoft Edge\n"
            "• Mozilla Firefox",
            title="❌ Erro", border_style="red"
        ))
        
        from rich.prompt import Confirm
        if Confirm.ask("\n[yellow]Deseja baixar o Chromium (~150MB)?[/]", default=False):
            try:
                console.print("\n[dim]📦 Baixando Chromium...[/]")
                subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
                console.print("[green]✓[/] Chromium instalado!")
                navegador = {'name': 'chromium', 'channel': None, 'type': 'chromium', 'path': None, 'executable_path': False}
            except Exception as e:
                console.print(f"[red]✗[/] Erro ao instalar Chromium: {e}")
                return False
        else:
            return False
    
    print_instrucoes()
    
    with sync_playwright() as p:
        console.print("[bold]🚀 Abrindo navegador...[/]")
        
        # Tenta usar o perfil real do usuário
        user_data_dir = obter_user_data_dir(navegador['name'])
        
        # Tenta encontrar o perfil vinculado ao Inteli
        perfil_inteli = None
        temp_user_data = None
        if user_data_dir:
            perfil_inteli = encontrar_perfil_inteli(user_data_dir)
            if perfil_inteli:
                temp_user_data = copiar_perfil_para_temp(user_data_dir, perfil_inteli)
        
        browser = None
        
        try:
            # Escolhe o tipo de navegador
            if navegador['type'] == 'firefox':
                browser = p.firefox.launch(
                    headless=False,
                    args=['--start-maximized'] if platform.system() != 'Darwin' else []
                )
                context = browser.new_context(viewport=None, locale='pt-BR')
                page = context.new_page()
            else:
                # Para Chrome, Edge, Brave
                chromium_args = ['--start-maximized'] if platform.system() != 'Darwin' else []
                
                if temp_user_data and perfil_inteli:
                    console.print(f"[dim]👤 Usando sessão do perfil: {perfil_inteli}[/]")
                    chromium_args.append(f'--profile-directory={perfil_inteli}')
                    
                    launch_options = {
                        'headless': False,
                        'args': chromium_args,
                        'viewport': None,
                        'locale': 'pt-BR',
                        'ignore_https_errors': True,
                    }
                    
                    if navegador.get('executable_path') and navegador['path']:
                        launch_options['executable_path'] = navegador['path']
                    elif navegador['channel']:
                        launch_options['channel'] = navegador['channel']
                    
                    context = p.chromium.launch_persistent_context(temp_user_data, **launch_options)
                    page = context.pages[0] if context.pages else context.new_page()
                    
                else:
                    console.print("[dim]📂 Abrindo navegador (será necessário fazer login)[/]")
                    if navegador.get('executable_path') and navegador['path']:
                        browser = p.chromium.launch(
                            headless=False,
                            executable_path=navegador['path'],
                            args=chromium_args
                        )
                    else:
                        launch_options = {'headless': False, 'args': chromium_args}
                        if navegador['channel']:
                            launch_options['channel'] = navegador['channel']
                        browser = p.chromium.launch(**launch_options)
                    
                    context = browser.new_context(viewport=None, locale='pt-BR')
                    page = context.new_page()
                    
        except Exception as e:
            console.print(f"[yellow]⚠[/] Erro ao abrir {navegador['name']}: {e}")
            
            from rich.prompt import Confirm
            if Confirm.ask("\n[yellow]Deseja baixar o Chromium como alternativa?[/]", default=False):
                try:
                    console.print("\n[dim]📦 Baixando Chromium...[/]")
                    subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
                    browser = p.chromium.launch(
                        headless=False,
                        args=['--start-maximized'] if platform.system() != 'Darwin' else []
                    )
                    context = browser.new_context(viewport=None, locale='pt-BR')
                    page = context.new_page()
                    console.print("[green]✓[/] Chromium funcionando!")
                except Exception as e2:
                    console.print(f"[red]✗[/] Falha ao iniciar navegador: {e2}")
                    return False
            else:
                console.print("[red]Operação cancelada.[/]")
                return False
        
        # Maximiza a janela no Windows
        if platform.system() == 'Windows':
            try:
                page.set_viewport_size({'width': 1920, 'height': 1080})
                page.evaluate('() => { window.moveTo(0, 0); window.resizeTo(screen.availWidth, screen.availHeight); }')
            except:
                pass
        
        # Navega para o Adalove
        console.print(f"\n[bold]🌐 Acessando Adalove...[/]")
        page.goto(ADALOVE_URL)
        
        console.print(Panel(
            "[bold]Aguardando login...[/]\n\n"
            "Faça login e navegue até a página do módulo desejado.\n"
            "O script continuará automaticamente quando detectar a página.",
            title="⏳ Aguardando", border_style="yellow"
        ))
        
        # Função para fechar popup de faltas
        def fechar_popup_faltas(pg):
            """Fecha o popup de faltas que pode bloquear a interface."""
            try:
                close_selectors = [
                    'button[aria-label="close"]',
                    'button[aria-label="Close"]',
                    'button[aria-label="fechar"]',
                    '.MuiDialog-root button:has(svg)',
                    '.MuiModal-root button:has(svg)',
                    '[role="dialog"] button:has(svg path[fill="#2D253F"])',
                    'button:has(svg path[d*="M36.4808 4.68875"])',
                    '.MuiIconButton-root:has(svg path[d*="36.4808"])',
                ]
                
                for selector in close_selectors:
                    try:
                        close_btn = pg.locator(selector).first
                        if close_btn.is_visible(timeout=500):
                            close_btn.click()
                            console.print("   [dim]🔔 Popup fechado automaticamente[/]")
                            time.sleep(0.5)
                            return True
                    except:
                        continue
                return False
            except:
                return False
        
        # Função para encontrar a página com a aba de notas
        def encontrar_pagina_notas(ctx, timeout_ms):
            """Procura em todas as páginas/abas do contexto pela aba de Notas."""
            import time as _time
            inicio = _time.time()
            timeout_sec = timeout_ms / 1000
            
            while (_time.time() - inicio) < timeout_sec:
                for pg in ctx.pages:
                    try:
                        fechar_popup_faltas(pg)
                        notas_element = pg.locator('button:has-text("Notas"), [role="tab"]:has-text("Notas"), .MuiTab-root:has-text("Notas")').first
                        if notas_element.is_visible(timeout=500):
                            return pg
                    except:
                        continue
                _time.sleep(1)
            return None
        
        try:
            page = encontrar_pagina_notas(context, TIMEOUT_LOGIN)
            if page:
                console.print("\n[green]✓[/] Página do módulo detectada!")
            else:
                raise PlaywrightTimeout("Timeout ao procurar página de notas")
            
        except PlaywrightTimeout:
            console.print(Panel(
                "[bold red]Timeout![/]\n\n"
                "Não foi possível detectar a página do módulo.\n"
                "Certifique-se de navegar até a página do módulo após o login.",
                title="❌ Erro", border_style="red"
            ))
            if browser:
                browser.close()
            else:
                context.close()
            return False
        
        time.sleep(2)
        fechar_popup_faltas(page)
        
        # Clica na aba "Notas"
        console.print("[bold]📊 Clicando na aba 'Notas'...[/]")
        try:
            fechar_popup_faltas(page)
            
            notas_tab = page.locator('button:has-text("Notas"), [role="tab"]:has-text("Notas")').first
            notas_tab.click()
            
            time.sleep(1)
            fechar_popup_faltas(page)
            
            console.print("[dim]⏳ Aguardando tabela de notas carregar...[/]")
            page.wait_for_selector('tr.styled-tr', timeout=TIMEOUT_NAVEGACAO)
            time.sleep(2)
            
            console.print("[green]✓[/] Tabela de notas carregada!")
            
        except PlaywrightTimeout:
            console.print("[yellow]⚠[/] Não foi possível clicar automaticamente na aba 'Notas'.")
            console.print("   Por favor, clique manualmente na aba 'Notas'...")
            
            try:
                page.wait_for_selector('tr.styled-tr', timeout=TIMEOUT_NAVEGACAO)
                console.print("[green]✓[/] Tabela de notas detectada!")
                time.sleep(2)
            except PlaywrightTimeout:
                console.print(Panel(
                    "[bold red]Tabela de notas não encontrada.[/]\n\n"
                    "Certifique-se de clicar na aba 'Notas' manualmente.",
                    title="❌ Erro", border_style="red"
                ))
                if browser:
                    browser.close()
                else:
                    context.close()
                return False
        
        # Extrai o HTML da página
        console.print("\n[bold]📄 Extraindo HTML da página...[/]")
        html_content = page.content()
        
        # Salva o HTML
        if output_dir:
            output_path = os.path.join(output_dir, OUTPUT_FILE)
        else:
            # Salva no diretório raiz do projeto (um nível acima de src/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(os.path.dirname(script_dir), OUTPUT_FILE)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        console.print(f"[green]✓[/] HTML salvo em: [cyan]{output_path}[/]")
        
        # Fecha o navegador
        console.print("\n[dim]🔒 Fechando navegador...[/]")
        if browser:
            browser.close()
        else:
            context.close()
        
        return True


if __name__ == "__main__":
    try:
        sucesso = coletar_notas()
        if not sucesso:
            console.print("\n[red]Não foi possível coletar as notas.[/]")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário.[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Erro inesperado: {e}[/]")
        sys.exit(1)
