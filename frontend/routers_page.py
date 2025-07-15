# frontend/router_page.py

from nicegui import ui
from backend.control import get_routes, add_route, update_route, get_planning
from backend.model import RouteStatus  # Supondo que tenha um enum RouteStatus

_route_list_container = None

def route_list_ui():
    _route_list_container.clear()
    with _route_list_container:
        ui.label("Lista de Rotas").classes("text-h5")
        routes = get_routes()
        if routes:
            for r in routes:
                header = f"Rota #{r.id} - Veículo: {r.vehicle.plate if r.vehicle else 'N/A'} - Status: {r.status.value}"
                with ui.expansion(header):
                    ui.label(f"Planejamento: {r.planning.id if r.planning else 'N/A'}")
                    ui.label(f"Descrição: {r.description if hasattr(r, 'description') else 'Sem descrição'}")
                    ui.button("Editar", on_click=lambda r_obj=r: edit_route_dialog(r_obj)).props("flat dense")
        else:
            ui.label("Nenhuma rota encontrada.")

def add_route_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label("Adicionar Nova Rota").classes("text-h6")

        plannings = get_planning()
        planning_options = {p.id: f"Planning #{p.id}" for p in plannings}
        planning_in = ui.select(label="Planejamento", options=planning_options)

        vehicle_in = ui.input(label="Veículo (placa)")

        # Status (se existir enum, ajuste aqui)
        status_options = {s.name: s.value for s in RouteStatus} if 'RouteStatus' in globals() else {"active": "Ativa", "inactive": "Inativa"}
        status_in = ui.select(label="Status", options=status_options, value="active")

        description_in = ui.input(label="Descrição").props("textarea")

        def save():
            if not vehicle_in.value or not planning_in.value:
                ui.notify("Veículo e Planejamento são obrigatórios.", color="negative")
                return
            
            new_route = add_route(
                planning_id=planning_in.value,
                vehicle_plate=vehicle_in.value,
                status=status_in.value,
                description=description_in.value
            )
            if new_route:
                ui.notify("Rota adicionada com sucesso!", color="positive")
                refresh()
                dialog.close()
            else:
                ui.notify("Erro ao adicionar rota.", color="negative")

        with ui.card_actions().classes("w-full justify-end"):
            ui.button("Salvar", on_click=save, color="primary")
            ui.button("Cancelar", on_click=dialog.close, color="negative")

    dialog.open()

def edit_route_dialog(route_obj):
    with ui.dialog() as dialog, ui.card():
        ui.label("Editar Rota").classes("text-h6")

        plannings = get_planning()
        planning_options = {p.id: f"Planning #{p.id}" for p in plannings}
        planning_in = ui.select(label="Planejamento", options=planning_options, value=route_obj.planning_id)

        vehicle_in = ui.input(label="Veículo (placa)", value=route_obj.vehicle.plate if route_obj.vehicle else "")

        status_options = {s.name: s.value for s in RouteStatus} if 'RouteStatus' in globals() else {"active": "Ativa", "inactive": "Inativa"}
        status_in = ui.select(label="Status", options=status_options, value=route_obj.status.value if hasattr(route_obj.status, 'value') else route_obj.status)

        description_in = ui.input(label="Descrição").props("textarea").value = getattr(route_obj, 'description', '')

        def save():
            if not vehicle_in.value or not planning_in.value:
                ui.notify("Veículo e Planejamento são obrigatórios.", color="negative")
                return
            
            updated_route = update_route(
                route_id=route_obj.id,
                planning_id=planning_in.value,
                vehicle_plate=vehicle_in.value,
                status=status_in.value,
                description=description_in.value
            )
            if updated_route:
                ui.notify("Rota atualizada com sucesso!", color="positive")
                refresh()
                dialog.close()
            else:
                ui.notify("Erro ao atualizar rota.", color="negative")

        with ui.card_actions().classes("w-full justify-end"):
            ui.button("Salvar", on_click=save, color="primary")
            ui.button("Cancelar", on_click=dialog.close, color="negative")

    dialog.open()

def refresh():
    route_list_ui()

def router_page(container):
    global _route_list_container
    container.clear()
    with container:
        _route_list_container = ui.column().classes("w-full h-full p-4")
        route_list_ui()
        ui.button("Adicionar Rota", on_click=add_route_dialog).classes("mt-4")
