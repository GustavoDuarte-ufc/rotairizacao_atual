from backend.control import *
from nicegui import ui
from osmnx import geocode

ui.state.show_disabled_depots = False

def cadastro_depots():
    def get_coords():
        if not address_search.value.strip():
            ui.notify("Preencha o endereço primeiro.", color="negative")
            return
        with ui.dialog() as wait_dialog:
            ui.label("Obtendo coordenadas...").classes("text-h6")
            wait_dialog.open()
        lat, lon = geocode(address_search.value)
        wait_dialog.close()  # close waiting dialog
        if lat and lon:
            lat_in.value = str(lat)
            lon_in.value = str(lon)
            ui.notify("Coordenadas obtidas com sucesso!", color="positive")
        else:
            ui.notify("Endereço inválido ou não encontrado", color="negative")

    with ui.dialog() as dialog, ui.card():
        ui.label("Adicionar Novo Deposito").classes("text-h6")
        name_in = ui.input(label="Nome")
        with ui.row().classes("items-center"):
            address_search = ui.input(label="Endereço")
            ui.button(icon="search", on_click=get_coords).classes("ml-2")
        lat_in = ui.input(label="Latitude")
        lon_in = ui.input(label="Longitude")

        def save():
            n, a = name_in.value.strip(), address_search.value.strip()
            try:
                lat, lon = float(lat_in.value), float(lon_in.value)
            except:
                ui.notify("Latitude/Longitude inválidas", color="negative")
                return
            if not (n and a):
                ui.notify("Preencha todos os campos.", color="negative")
                return
            add_depots(n, a, lat, lon)
            refresh("Deposito adicionado!")
            dialog.close()
        with ui.card_actions().classes("w-full justify-end"):
            ui.button("Salvar", on_click=save, color="primary", icon="save")
            ui.button("Cancelar", on_click=dialog.close, color="negative", icon="close")
    dialog.open()

def depost_list():
    _depots_list.clear()
    with _depots_list:
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Depots Cadastrados").classes("text-h6")
                ui.icon("depots").classes("text-h6 ml-auto")
            with ui.row().classes("w-full justify-between"):
                ui.button("Adicionar", on_click=cadastro_depots,
                        color="primary", icon="add").classes("mb-4")
                sw = ui.switch("Mostrar desativados",
                            value=ui.state.show_disabled_depots)
        with ui.scroll_area():
            if depots := get_depots():
                for depot in depots:
                    with ui.card().classes("w-full") as depots_spam, \
                            ui.row().classes("items-center justify-between w-full"):
                        with ui.row().classes("items-center gap-2"):
                            ui.button(icon="edit",
                                    color="primary").props("flat dense").tooltip("Editar")
                            if depot.active:
                                ui.button(icon="visibility_off",  # type: ignore
                                        color="dark").props("flat dense").tooltip("Desativar")
                            else:
                                ui.button(icon="visibility",
                                        color="positive").props("flat dense").tooltip("Ativar")
                        with ui.label(f"{depot.name}").classes("text-body1"), ui.tooltip():
                            ui.label(f"ID: {depot.id}").classes("body-text")
                            ui.label(f"Nome: {depot.name}").classes("body-text")
                            ui.label(f"Endereço: {depot.address}").classes("body-text")
                            ui.label(f"Coords: ({depot.latitude}, {depot.longitude})").classes("body-text")
                        ui.badge("Ativo" if depot.active else "Inativo", 
                                 color="positive" if depot.active else "dark").classes("ml-auto")
                if not depot.active:
                    depots_spam.bind_visibility(sw, "value")
            else:
                ui.label("Nenhum cliente encontrado.")

def depots_page(container):
    global _depots_list, _depots_map
    container.clear()
    with container:
        _depots_list = ui.column().classes("w-1/3 h-full")
        depost_list()

def refresh(msg: str = "", color: str = "positive"):
    depost_list()
    if msg:
        ui.notify(msg, color=color)
