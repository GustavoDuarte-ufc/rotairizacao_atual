from nicegui import ui
from backend.control import *

ui.state.show_disabled_vehicle = False

def cadastro_vehicle():
    with ui.dialog() as dialog, ui.card():
        ui.label("Adicionar Novo Veiculo").classes("text-h6")
        model_in = ui.input(label="Nome")
        plate_in = ui.input(label="Placa")
        capacity_in = ui.input(label="Capacidade")
        cost_per_km_in = ui.input(label="custo por Km")
        depot_options = {d.id: d.name for d in get_depots() if d.active}
        depot_in = ui.select(label="Depósito", options=depot_options)
        def save():
            try:
                cap = int(capacity_in.value); cost = float(cost_per_km_in.value)
            except:
                ui.notify("Capacidade/Custo inválidos", color="negative"); return
            if not (model_in.value.strip() and plate_in.value.strip() and depot_in.value):
                ui.notify("Preencha todos os campos.", color="negative"); return
            add_vehicle(model_in.value.strip(), plate_in.value.strip(), cap, cost, depot_in.value)
            refresh("Veículo adicionado!")
            dialog.close()
        with ui.card_actions().classes("w-full justify-end"):
            ui.button("Salvar", on_click=save, color="primary", icon="save")
            ui.button("Cancelar", on_click=dialog.close, color="negative", icon="close")

    dialog.open()

def vehicle_list():
    _vehi_list.clear()
    with _vehi_list:
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Veiculos Cadastrados").classes("text-h6")
                ui.icon("vehicle").classes("text-h6 ml-auto")
            with ui.row().classes("w-full justify-between"):
                ui.button("Adicionar", on_click=cadastro_vehicle,
                        color="primary", icon="add").classes("mb-4")
                sw = ui.switch("Mostrar desativados",
                            value=ui.state.show_disabled_vehicle)
        with ui.scroll_area():
            if vehicles := get_vehicles():
                for vehicler in vehicles:
                    with ui.card().classes("w-full") as vehicler_spam, \
                            ui.row().classes("items-center justify-between w-full"):
                        with ui.row().classes("items-center gap-2"):
                            ui.button(icon="edit",
                                    color="primary").props("flat dense").tooltip("Editar")
                            if vehicler.active:
                                ui.button(icon="visibility_off",  # type: ignore
                                        color="dark").props("flat dense").tooltip("Desativar")
                            else:
                                ui.button(icon="visibility",
                                        color="positive").props("flat dense").tooltip("Ativar")
                        with ui.label(f"{vehicler.model}").classes("text-body1"), ui.tooltip():
                            ui.label(f"ID: {vehicler.id}").classes("body-text")
                            ui.label(f"Modelo: {vehicler.model}").classes("body-text")
                            ui.label(f"Placa: {vehicler.plate}").classes("body-text")
                            ui.label(f"Capacidade: {vehicler.capacity}").classes("body-text")
                            ui.label(f"Custo por km: ({vehicler.cost_per_km}").classes("body-text")
                        ui.badge("Ativo" if vehicler.active else "Inativo", 
                                 color="positive" if vehicler.active else "dark").classes("ml-auto")
                if not vehicler.active:
                    vehicler_spam.bind_visibility(sw, "value")
            else:
                ui.label("Nenhum cliente encontrado.")

def vehicle_page(container):
    global _vehi_list, _vehi_map
    container.clear()
    with container:
        _vehi_list = ui.column().classes("w-1/3 h-full")
        vehicle_list()

def refresh(msg: str = "", color: str = "positive"):
    vehicle_list()
    if msg:
        ui.notify(msg, color=color)
