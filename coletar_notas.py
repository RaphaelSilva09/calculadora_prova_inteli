#!/usr/bin/env python3
"""
Script de automação para coletar notas do Adalove usando Playwright.

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
    """Instala Playwright automaticamente (sem baixar navegadores extras)."""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        print("📦 Instalando Playwright...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'playwright'])
        print("✅ Playwright instalado! Reiniciando...\n")
        os.execv(sys.executable, [sys.executable] + sys.argv)

install_dependencies()

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

# Configurações
ADALOVE_URL = "https://adalove.inteli.edu.br"
OUTPUT_FILE = "Adalove.html"
TIMEOUT_LOGIN = 300000  # 5 minutos para fazer login
TIMEOUT_NAVEGACAO = 60000  # 1 minuto para navegação normal


def detectar_navegador():
    """
    Detecta qual navegador está instalado no sistema.
    Retorna tupla (browser_type, channel) para usar com Playwright.
    
    Prioridade: Chrome > Brave > Edge > Firefox
    Compatível com Windows, Linux e macOS.
    """
    sistema = platform.system().lower()
    
    # Caminhos comuns dos navegadores por sistema operacional
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
                'darwin': [  # macOS
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
            'channel': 'chrome',  # Brave é baseado em Chromium, usa channel chrome
            'executable_path': True,  # Indica que precisa passar o path do executável
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
            'channel': None,  # Firefox usa tipo diferente
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
                print(f"✅ Navegador detectado: {nome.capitalize()}")
                return {
                    'name': nome,
                    'channel': config.get('channel'),
                    'type': config.get('type', 'chromium'),
                    'path': path,
                    'executable_path': config.get('executable_path', False)
                }
    
    return None


def print_banner():
    """Imprime banner de início."""
    print("\n" + "=" * 60)
    print("   🤖 COLETOR AUTOMÁTICO DE NOTAS - ADALOVE")
    print("=" * 60 + "\n")


def print_instrucoes():
    """Imprime instruções para o usuário."""
    print("📋 INSTRUÇÕES:")
    print("   1. Seu navegador será aberto automaticamente")
    print("   2. Faça login normalmente (suporta 2FA/SSO)")
    print("   3. Navegue até a página do seu MÓDULO")
    print("   4. O script detectará a aba 'Notas' e clicará automaticamente")
    print("   5. O HTML será salvo e o cálculo iniciará")
    print("\n" + "-" * 60 + "\n")


def coletar_notas():
    """Abre o navegador e coleta as notas do Adalove."""
    
    print_banner()
    
    # Detecta navegador instalado
    navegador = detectar_navegador()
    
    if not navegador:
        print("❌ Nenhum navegador compatível encontrado!")
        print("   Instale um dos seguintes navegadores:")
        print("   - Google Chrome")
        print("   - Brave Browser")
        print("   - Microsoft Edge")
        print("   - Mozilla Firefox")
        
        # Pergunta se quer baixar Chromium como fallback
        resposta = input("\n🔄 Deseja baixar o Chromium (~150MB) para continuar? [s/N]: ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            try:
                print("\n📦 Baixando Chromium...")
                subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
                print("✅ Chromium instalado!")
                return {'name': 'chromium', 'channel': None, 'type': 'chromium', 'path': None, 'executable_path': False}
            except Exception as e:
                print(f"❌ Erro ao instalar Chromium: {e}")
                return None
        return None
    
    print_instrucoes()
    
    with sync_playwright() as p:
        print("🚀 Abrindo navegador...")
        
        try:
            # Escolhe o tipo de navegador
            if navegador['type'] == 'firefox':
                browser = p.firefox.launch(
                    headless=False,
                    args=['--start-maximized'] if platform.system() != 'Darwin' else []
                )
            elif navegador.get('executable_path') and navegador['path']:
                # Brave e outros que precisam do caminho do executável
                browser = p.chromium.launch(
                    headless=False,
                    executable_path=navegador['path'],
                    args=['--start-maximized'] if platform.system() != 'Darwin' else []
                )
            else:
                # Chrome, Edge ou Chromium baixado
                launch_options = {
                    'headless': False,
                    'args': ['--start-maximized'] if platform.system() != 'Darwin' else []
                }
                if navegador['channel']:
                    launch_options['channel'] = navegador['channel']
                browser = p.chromium.launch(**launch_options)
        except Exception as e:
            print(f"⚠️  Erro ao abrir {navegador['name']}: {e}")
            
            # Pergunta se quer baixar Chromium como fallback
            resposta = input("\n🔄 Deseja baixar o Chromium (~150MB) como alternativa? [s/N]: ").strip().lower()
            if resposta in ['s', 'sim', 'y', 'yes']:
                try:
                    print("\n📦 Baixando Chromium...")
                    subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
                    browser = p.chromium.launch(
                        headless=False,
                        args=['--start-maximized'] if platform.system() != 'Darwin' else []
                    )
                    print("✅ Chromium instalado e funcionando!")
                except Exception as e2:
                    print(f"❌ Falha ao iniciar navegador: {e2}")
                    return False
            else:
                print("❌ Operação cancelada.")
                return False
        
        context = browser.new_context(
            viewport=None,  # Usa tamanho da janela
            locale='pt-BR'
        )
        
        page = context.new_page()
        
        # Navega para o Adalove
        print(f"🌐 Acessando {ADALOVE_URL}...")
        page.goto(ADALOVE_URL)
        
        # Aguarda o usuário fazer login e chegar na página inicial
        print("\n⏳ Aguardando login...")
        print("   [Faça login e navegue até a página do módulo desejado]")
        print("   [O script continuará automaticamente quando detectar a página]\n")
        
        try:
            # Aguarda elemento que indica que está logado e na página de módulo
            page.wait_for_selector(
                'button:has-text("Notas"), [role="tab"]:has-text("Notas"), .MuiTab-root:has-text("Notas")',
                timeout=TIMEOUT_LOGIN
            )
            print("✅ Página do módulo detectada!")
            
        except PlaywrightTimeout:
            print("❌ Timeout: Não foi possível detectar a página do módulo.")
            print("   Certifique-se de navegar até a página do módulo após o login.")
            browser.close()
            return False
        
        # Pequena pausa para garantir carregamento completo
        time.sleep(2)
        
        # Clica na aba "Notas"
        print("📊 Clicando na aba 'Notas'...")
        try:
            notas_tab = page.locator('button:has-text("Notas"), [role="tab"]:has-text("Notas")').first
            notas_tab.click()
            
            print("⏳ Aguardando tabela de notas carregar...")
            page.wait_for_selector('tr.styled-tr', timeout=TIMEOUT_NAVEGACAO)
            time.sleep(2)
            
            print("✅ Tabela de notas carregada!")
            
        except PlaywrightTimeout:
            print("⚠️  Não foi possível clicar automaticamente na aba 'Notas'.")
            print("   Por favor, clique manualmente na aba 'Notas' e aguarde...")
            
            try:
                page.wait_for_selector('tr.styled-tr', timeout=TIMEOUT_NAVEGACAO)
                print("✅ Tabela de notas detectada!")
                time.sleep(2)
            except PlaywrightTimeout:
                print("❌ Timeout: Tabela de notas não encontrada.")
                browser.close()
                return False
        
        # Extrai o HTML da página
        print("\n📄 Extraindo HTML da página...")
        html_content = page.content()
        
        # Salva o HTML
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML salvo em: {output_path}")
        
        # Fecha o navegador
        print("\n🔒 Fechando navegador...")
        browser.close()
        
        return True


def executar_calculo():
    """Executa o script de cálculo de notas."""
    print("\n" + "=" * 60)
    print("   📊 INICIANDO CÁLCULO DE NOTAS")
    print("=" * 60 + "\n")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notas.py')
    subprocess.run([sys.executable, script_path])


def main():
    """Função principal."""
    try:
        sucesso = coletar_notas()
        
        if sucesso:
            executar_calculo()
        else:
            print("\n❌ Não foi possível coletar as notas.")
            print("   Tente novamente ou use o método manual (salvar HTML).")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

