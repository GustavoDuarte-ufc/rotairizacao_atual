from nicegui import ui
from frontend.customers_page import *
from frontend.depots_page import *
from frontend.planning_page import *
from frontend.vehicle_page import *
from frontend.order_page import *
from frontend.routers_page import *

def base_layout() -> ui.row:
    """
    Cria o layout base da aplicação:
    1. Header com botão de menu e título
    2. Container principal para renderizar o conteúdo de cada página
    3. Footer com informações de rodapé
    Retorna o container (ui.Row) onde o conteúdo específico deve ser inserido.
    """
    # Container principal que ocupa toda a área disponível
    main_container = ui.row().classes('w-full no-wrap')
    # main_container = ui.skeleton().classes('w-full h-full no-wrap')

    # Cabeçalho
    with ui.header().classes('bg-primary text-white'):
        # Botão de menu com opções de navegação
        with ui.button(icon='menu'):
            with ui.menu():
                with ui.menu_item(on_click=lambda: depots_page(main_container)):
                    with ui.row().classes('items-center no-wrap w-full justify-start gap-2'):
                        ui.icon('warehouse')
                        ui.label('Depósitos')
                with ui.menu_item(on_click=lambda: customer_page(main_container)):
                    with ui.row().classes('items-center no-wrap w-full justify-start gap-2'):
                        ui.icon('people')
                        ui.label('Clientes')
                with ui.menu_item(on_click=lambda: router_page(main_container)):
                    with ui.row().classes('items-center no-wrap w-full justify-start gap-2'):
                        ui.icon('people')
                        ui.label('Clientes')
                with ui.menu_item(on_click=lambda: vehicle_page(main_container)):
                    with ui.row().classes('items-center no-wrap w-full justify-start gap-2'):
                        ui.icon('local_shipping')
                        ui.label('Veículos')
                with ui.menu_item(on_click=lambda: order_page(main_container)):
                    with ui.row().classes('items-center no-wrap w-full justify-start gap-2'):
                        ui.icon('shopping_cart')
                        ui.label('Pedidos')
                with ui.menu_item(on_click=lambda: planning_page(main_container)):
                    with ui.row().classes('items-center no-wrap w-full justify-start gap-2'):
                        ui.icon('event_note')
                        ui.label('Planejamentos')
                ui.separator()
                with ui.menu_item(on_click=lambda: about(main_container)):
                    with ui.row().classes('items-center no-wrap w-full justify-start gap-2'):
                        ui.icon('info')
                        ui.label('Sobre')
                # # Exemplo de item de menu com texto e ícone (pode ser removido ou mantido para referência)
                # with ui.menu_item(on_click=lambda: ui.notify('Item "Teste" com ícone clicado!')):
                #     with ui.row().classes('items-center no-wrap w-full justify-between'):
                #         ui.label('Teste')
                #         ui.icon('settings')
        # Título da aplicação
        ui.label("Laboratório de Matemática Industrial (Roteirizador)") \
          .classes('text-h5 ml-5')
        ui.icon("route").classes('text-h5 ml-auto')


    # Footer
    with ui.footer().classes('bg-primary text-white flex items-center p-1'):
        ui.label("Lab. MI").classes('text-body2')
        ui.label("2025").classes('text-body2')
        ui.label("Desenvolvedores: Albert E. F. Muritiba(Docente), Gustavo Duarte(Discente)").classes('ml-auto text-body2')
        ui.label("Versão 1.0").classes('ml-auto text-body2')

    return main_container

@ui.page("/")
def index():
    """
    Página inicial:
    - Monta o layout base
    - Renderiza a página de gerenciamento de depósitos dentro do container
    """
    container = base_layout()
    # depot_page(container)
    # customer_page(container)
    customer_page(container)  # Exemplo: renderiza a página de veículos


def about(container: ui.row):
    """
    Página "Sobre":
    - Limpa o container principal
    - Exibe informações sobre a aplicação
    """
    container.clear()
    with container, ui.card().classes('w-full h-full'):
        ui.label("Sobre a aplicação").classes('text-h4')
        ui.label("Esta é uma aplicação de exemplo para o Laboratório de Matemática Industrial.").classes('text-body1')
        ui.label("Desenvolvedores: Equipe de Desenvolvimento").classes('text-body2')
        ui.label("Versão 1.0").classes('text-body2')
        ui.button("Voltar", on_click=lambda: ui.navigate.to("/")).classes('mt-4')
