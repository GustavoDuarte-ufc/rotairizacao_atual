from backend.control import *
from nicegui import ui
from osmnx import geocode

ui.state.show_disabled_customers = False

def cadastro_customer():
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
        ui.label("Adicionar Novo Cliente").classes("text-h6")
        name_in = ui.input(label="Nome")
        email_in = ui.input(label="E-mail")
        with ui.row().classes("items-center"):
            address_search = ui.input(label="Endereço")
            ui.button(icon="search", on_click=get_coords).classes("ml-2")
        lat_in = ui.input(label="Latitude")
        lon_in = ui.input(label="Longitude")

        def save():
            n, e, a = name_in.value.strip(), email_in.value.strip(), address_search.value.strip()
            try:
                lat, lon = float(lat_in.value), float(lon_in.value)
            except:
                ui.notify("Latitude/Longitude inválidas", color="negative")
                return
            if not (n and e and a):
                ui.notify("Preencha todos os campos.", color="negative")
                return
            add_costumers(n, e, a, lat, lon)
            refresh("Cliente adicionado!")
            dialog.close()
        with ui.card_actions().classes("w-full justify-end"):
            ui.button("Salvar", on_click=save, color="primary", icon="save")
            ui.button("Cancelar", on_click=dialog.close, color="negative", icon="close")
    dialog.open()

def customer_list():
    _cust_list.clear()
    with _cust_list:
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Clientes Cadastrados").classes("text-h6")
                ui.icon("people").classes("text-h6 ml-auto")
            with ui.row().classes("w-full justify-between"):
                ui.button("Adicionar", on_click=cadastro_customer,
                        color="primary", icon="add").classes("mb-4")
                sw = ui.switch("Mostrar desativados",
                            value=ui.state.show_disabled_customers)
        with ui.scroll_area():
            if customers := get_costumers():
                for customer in customers:
                    with ui.card().classes("w-full") as customer_spam, \
                            ui.row().classes("items-center justify-between w-full"):
                        with ui.row().classes("items-center gap-2"):
                            ui.button(icon="edit",
                                    color="primary").props("flat dense").tooltip("Editar")
                            if customer.active:
                                ui.button(icon="visibility_off",  # type: ignore
                                        color="dark").props("flat dense").tooltip("Desativar")
                            else:
                                ui.button(icon="visibility",
                                        color="positive").props("flat dense").tooltip("Ativar")
                        with ui.label(f"{customer.name}").classes("text-body1"), ui.tooltip():
                            ui.label(f"ID: {customer.id}").classes("body-text")
                            ui.label(f"Nome: {customer.name}").classes("body-text")
                            ui.label(f"Email: {customer.email}").classes("body-text")
                            ui.label(f"Endereço: {customer.address}").classes("body-text")
                            ui.label(f"Coords: ({customer.latitude}, {customer.longitude})").classes("body-text")
                        ui.badge("Ativo" if customer.active else "Inativo", 
                                 color="positive" if customer.active else "dark").classes("ml-auto")
                if not customer.active:
                    customer_spam.bind_visibility(sw, "value")
            else:
                ui.label("Nenhum cliente encontrado.")

def customer_page(container):
    global _cust_list, _cust_map
    container.clear()
    with container:
        _cust_list = ui.column().classes("w-1/3 h-full")
        customer_list()

def refresh(msg: str = "", color: str = "positive"):
    customer_list()
    if msg:
        ui.notify(msg, color=color)
