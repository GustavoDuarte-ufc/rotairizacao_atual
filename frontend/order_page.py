"""
Gerenciamento de pedidos: cadastro, edição, lista e detalhes.
"""
from nicegui import ui
from backend.control import (
    get_order,
    add_order,
    update_order,
    get_costumers,
    get_planning,  # IMPORTAÇÃO ESSENCIAL ADICIONADA
)
from backend.model import OrderStatus
from datetime import datetime

_order_list_container = None  # type: ignore

def format_datetime_for_input(dt_obj: datetime | None) -> tuple[str | None, str | None]:
    """Converte datetime para strings de data (YYYY-MM-DD) e hora (HH:MM) para inputs."""
    if dt_obj:
        return dt_obj.strftime('%Y-%m-%d'), dt_obj.strftime('%H:%M')
    return None, None

def parse_datetime_from_input(date_str: str | None, time_str: str | None) -> datetime | None:
    """Converte strings de data e hora dos inputs para um objeto datetime."""
    if date_str and time_str:
        try:
            dt_str_formatted = date_str.replace('/', '-')
            dt = datetime.strptime(f"{dt_str_formatted} {time_str}", '%Y-%m-%d %H:%M')
            return dt
        except ValueError:
            ui.notify("Formato de data ou hora inválido.", color="negative")
            return None
    elif date_str and not time_str:  # Apenas data, assume meia-noite
        try:
            dt_str_formatted = date_str.replace('/', '-')
            dt = datetime.strptime(dt_str_formatted, '%Y-%m-%d')
            return dt
        except ValueError:
            ui.notify("Formato de data inválido.", color="negative")
            return None
    return None

def add_order_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label("Adicionar Novo Pedido").classes("text-h6")

        # Clientes ativos
        customers = get_costumers()
        customer_options = {c.id: c.name for c in customers if c.active}
        if not customer_options:
            ui.label("Nenhum cliente ativo encontrado. Crie e ative um cliente primeiro.")
            with ui.card_actions().classes("w-full justify-end"):
                ui.button("Fechar", on_click=dialog.close, color="negative")
            dialog.open()
            return
        customer_in = ui.select(label="Cliente", options=customer_options)

        # Demanda
        ui.label("Demanda")
        demand_in = ui.number(value=1, min=1, step=1)

        # Status
        status_options = {s.name: s.value for s in OrderStatus}
        status_in = ui.select(label="Status", options=status_options, value="pending")

        # Planejamento
        plannings = get_planning()
        planning_options = {p.id: f"Planning #{p.id} - {p.status.value}" for p in plannings}
        planning_in = ui.select(label="Planejamento (opcional)", options=planning_options).props('clearable')

        # Rotas (dinâmicas)
        route_in = ui.select(label="Rota (opcional)", options={}).props('clearable')

        def update_routes():
            selected_planning_id = planning_in.value
            if selected_planning_id:
                planning = next((p for p in plannings if p.id == selected_planning_id), None)
                if planning:
                    route_options = {r.id: f"Rota #{r.id} - Veículo {r.vehicle.plate}" for r in planning.routes}
                    route_in.options = route_options
                else:
                    route_in.options = {}
            else:
                route_in.options = {}

        planning_in.on("update:model-value", lambda _: update_routes())

        # Posição na rota
        seq_pos_in = ui.number(label="Posição na Rota", value=1, min=1).props('clearable')

        # Função salvar com prints para debug
        def save():
            print("===> Botão Salvar clicado")
            print(f"Cliente: {customer_in.value}")
            print(f"Demanda: {demand_in.value}")
            print(f"Status: {status_in.value}")
            print(f"Planning ID: {planning_in.value}")
            print(f"Route ID: {route_in.value}")
            print(f"Posição na Rota: {seq_pos_in.value}")

            if not customer_in.value:
                ui.notify("Cliente é obrigatório.", color="negative")
                return

            new_order = add_order(
                customer_id=customer_in.value,
                demand=demand_in.value,
                planning_id=planning_in.value,
                route_id=route_in.value,
                sequence_position=seq_pos_in.value,
            )
            if new_order:
                ui.notify("Pedido adicionado com sucesso!", color="positive")
                refresh()
                dialog.close()
            else:
                ui.notify("Erro ao adicionar pedido.", color="negative")

        with ui.card_actions().classes("w-full justify-end"):
            ui.button("Salvar", on_click=save, color="primary", icon="save")
            ui.button("Cancelar", on_click=dialog.close, color="negative", icon="close")

    dialog.open()

def edit_order_dialog(order_obj):
    with ui.dialog() as dialog, ui.card():
        ui.label("Editar Pedido").classes("text-h6")

        customers = get_costumers()
        customer_options = {c.id: c.name for c in customers}
        customer_in = ui.select(label="Cliente", options=customer_options, value=order_obj.customer_id)

        ui.label("Demanda")
        demand_in = ui.number(value=order_obj.demand, min=1, step=1)

        status_options = {s.name: s.value for s in OrderStatus}
        status_in = ui.select(label="Status", options=status_options, value=order_obj.status.name)

        plannings = get_planning()
        planning_options = {p.id: f"ID {p.id} - {p.depot.name if p.depot else 'N/A'}" for p in plannings}
        planning_in = ui.select(label="Planejamento", options=planning_options, value=order_obj.planning_id)

        route_options = {}
        if order_obj.planning and order_obj.planning.routes:
            route_options = {r.id: f"Rota {r.id}" for r in order_obj.planning.routes}
        route_in = ui.select(label="Rota", options=route_options, value=order_obj.route_id)

        position_in = ui.input(label="Posição na Rota", value=str(order_obj.sequence_position or "")).props("type=number")

        def save():
            if not (customer_in.value and status_in.value):
                ui.notify("Cliente e Status são obrigatórios.", color="negative")
                return

            try:
                seq_pos = int(position_in.value) if position_in.value.strip() else None
            except ValueError:
                ui.notify("Posição deve ser um número inteiro.", color="negative")
                return

            updated_order = update_order(
                order_id=order_obj.id,
                demand=demand_in.value,
                status_str=status_in.value,
                planning_id=planning_in.value,
                route_id=route_in.value,
                sequence_position=seq_pos
            )

            if updated_order:
                ui.notify("Pedido atualizado com sucesso!", color="positive")
                refresh()
                dialog.close()
            else:
                ui.notify("Erro ao atualizar pedido.", color="negative")

        with ui.card_actions().classes("w-full justify-end"):
            ui.button("Salvar", on_click=save, color="primary", icon="save")
            ui.button("Cancelar", on_click=dialog.close, color="negative", icon="close")

    dialog.open()

def order_list_ui():
    _order_list_container.clear()
    with _order_list_container, ui.card().classes("w-full h-full overflow-auto"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label("Pedidos").classes("text-h5")
            ui.icon("assignment").classes("text-h4")
        ui.button("Adicionar Pedido", on_click=add_order_dialog,
                  color="primary", icon="add").classes("mb-4")

        orders = get_order()
        if orders:
            ui.separator()
            for o in orders:
                header_text = f"ID: {o.id} - Cliente: {o.customer.name if o.customer else 'N/A'} - Status: {o.status.value}"
                with ui.expansion(header_text, icon="assignment_ind").classes('w-full mb-2'):
                    with ui.card_section():
                        ui.label(f"Demanda: {o.demand}").classes("text-sm")
                        ui.label(f"Criado em: {o.created_at.strftime('%d/%m/%Y %H:%M') if o.created_at else 'N/A'}").classes("text-sm")
                        ui.label(f"Planning ID: {o.planning_id if o.planning_id else 'N/A'}").classes("text-sm")
                        ui.label(f"Route ID: {o.route_id if o.route_id else 'N/A'}").classes("text-sm")
                        ui.label(f"Posição na rota: {o.sequence_position if o.sequence_position else 'N/A'}").classes("text-sm")
                    ui.button(icon="edit", on_click=lambda o_obj=o: edit_order_dialog(o_obj), color="primary").props("flat dense").tooltip("Editar Pedido")
        else:
            ui.label("Nenhum pedido encontrado.")

def order_page(container):
    global _order_list_container
    container.clear()
    with container:
        _order_list_container = ui.column().classes("w-full h-full p-4")
        order_list_ui()

def refresh():
    order_list_ui()