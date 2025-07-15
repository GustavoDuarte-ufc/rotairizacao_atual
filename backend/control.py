from backend.model import *
import logging
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#GET das tabelas
def get_costumers():
    with Session() as session:
        custumer = session.query(Costumers).all()
        logger.info(f"{len(custumer)} clientes recuperados\n")
        for c in custumer:
            print(f"ID: {c.id}, Nome: {c.name}, Email: {c.email}, Endereco: {c.address}, Latitude: {c.latitude}, Longitude: {c.longitude}, Situacao: {c.active}, Data_cadastro: {c.created_at}")
    return custumer

def get_depots():
    with Session() as session:
        depots = session.query(Depots).all()
        logger.info(f'Depositos recuperados\n')
        for d in depots:
            print(f"ID: {d.id}, Nome: {d.name}, Endereco: {d.address}, Latitude: {d.latitude}, Longitude: {d.longitude}, Situacao: {d.active}, Data_cadastro: {d.created_at}")
    return depots

def get_vehicles():
    with Session() as session:
        vehicles = session.query(Vehicles).options(joinedload(Vehicles.depot)).all()
        for v in vehicles:
            print(f'ID: {v.id}, Modelo: {v.model}, Situacao: {v.active}')
        logger.info(f"{len(vehicles)} veículos recuperados")
        return vehicles
    
def get_planning():
    with Session() as session:
        planning = session.query(Planning)\
            .options(
                joinedload(Planning.depot),
                joinedload(Planning.orders),
                joinedload(Planning.routes)
            ).all()
        for p in planning:
            print(f"[DEBUG] Planning ID {p.id} | Depósito: {p.depot.name if p.depot else 'N/A'}")
        return planning
    
def get_order():
    with Session() as session:
        orders = session.query(Orders).all()
        logger.info(f"[INFO] {len(orders)} pedidos recuperados")
        for o in orders:
            print(f"ID: {o.id}, Status: {o.status.name}, Cliente: {o.customer.name if o.customer else 'N/A'}, "
                  f"Demanda: {o.demand}, Criado em: {o.created_at}, "
                  f"Planning ID: {o.planning_id}, Route ID: {o.route_id}, Posição: {o.sequence_position}")
        return orders

def get_routes():
    with Session() as session:
        routes = session.query(Routes)\
            .options(joinedload(Routes.vehicle), joinedload(Routes.planning))\
            .all()
        for r in routes:
            print(f"ID: {r.id}, Veículo: {r.vehicle.plate if r.vehicle else 'N/A'}, "
                  f"Planejamento: {r.planning.id if r.planning else 'N/A'}, Status: {r.status}, "
                  f"Descrição: {r.description}")
        return routes

#ADD das tabelas
def add_costumers(name: str, email: str, address: str, latitude: float, longitude: float):
    with Session() as session:
        repetidos = session.query(Costumers).filter(Costumers.email != email).first()
        if repetidos:
            customer = Costumers(name=name, email=email, address=address, latitude=latitude, longitude=longitude)
            session.add(customer)
            session.commit()
            logger.info(f"Cliente criado: id={customer.id}, name='{customer.name}'")
            return customer
        else:
            logger.info('Email ja existente')

def add_depots(name: str, address: str, latitude: float, longitude: float):
    with Session() as session:
        repetidos = session.query(Depots).filter(Depots.name != name and Depots.latitude != latitude and Depots.longitude != longitude).first()
        if repetidos:
            depots = Depots(name=name, address=address, latitude=latitude, longitude=longitude)
            session.add(depots)
            session.commit()
            logger.info(f"Deposito criado: id={depots.id}, name='{depots.name}'")
            return depots
        else:
            logger.info('Deposito ja existente')

def add_vehicle(model: str, plate: str, capacity: int, cost_per_km: float, depot_id: int):
    with Session() as session:
        v = session.query(Vehicles).filter(Vehicles.plate != plate).first()
        if v:
            vehicle = Vehicles(model=model, plate=plate, capacity=capacity,
                               cost_per_km=cost_per_km, depot_id=depot_id)
            session.add(vehicle)
            session.commit()
            logger.info(f"Veículo criado: id={vehicle.id}, plate='{vehicle.plate}'")
            return vehicle
        else:
            logger.info('Veículo ja existente')

def add_planning(depot_id: int, deadline: Optional[datetime], status_str: str = "pending"):
    with Session() as session:
        try:
            planning = Planning(
                depot_id=depot_id,
                deadline=deadline,
                status=PlanningStatus[status_str],
                created_at=datetime.now(timezone.utc)
            )
            session.add(planning)
            session.commit()
            logger.info(f"Planning criado com id={planning.id}")
            return planning
        except KeyError:
            logger.error(f"Status '{status_str}' é inválido. Use: {[s.name for s in PlanningStatus]}")
        except Exception as e:
            logger.error(f"Erro ao adicionar planning: {e}")

def add_order(customer_id: int, demand: int = 1, planning_id: Optional[int] = None, route_id: Optional[int] = None, sequence_position: Optional[int] = None):
    with Session() as session:
        customer = session.query(Costumers).filter(Costumers.id == customer_id).first()
        if not customer:
            logger.error(f"Cliente id={customer_id} não encontrado para novo pedido")
            return None
        new_order = Orders(
            customer_id=customer_id,
            demand=demand,
            planning_id=planning_id,
            route_id=route_id,
            sequence_position=sequence_position,
            created_at=datetime.now(timezone.utc),
            status=OrderStatus.pending  # Assumindo OrderStatus importado e existente
        )
        session.add(new_order)
        session.commit()
        logger.info(f"Pedido criado com id={new_order.id} para cliente id={customer_id}")
        return new_order

def add_route(planning_id: int, vehicle_plate: str, status: str = "active", description: Optional[str] = None):
    with Session() as session:
        vehicle = session.query(Vehicles).filter(Vehicles.plate == vehicle_plate).first()
        planning = session.query(Planning).filter(Planning.id == planning_id).first()
        if not vehicle:
            print(f"Veículo com placa '{vehicle_plate}' não encontrado.")
            return None
        if not planning:
            print(f"Planejamento id={planning_id} não encontrado.")
            return None
        try:
            route_status = RouteStatus[status]
        except KeyError:
            print(f"Status '{status}' inválido para rota.")
            return None
        new_route = Routes(
            planning_id=planning.id,
            vehicle_id=vehicle.id,
            status=route_status,
            description=description
        )
        session.add(new_route)
        session.commit()
        print(f"Rota criada com id={new_route.id}")
        return new_route

#UPT das tabelas
def upd_customer(cust_id: int, new_name: str, new_email: str, new_address: str,
                    new_latitude: float, new_longitude: float):
    with Session() as session:
        cust = session.query(Costumers).filter(Costumers.id == cust_id).first()
        if cust:
            cust.name, cust.email = new_name, new_email
            cust.address, cust.latitude, cust.longitude = new_address, new_latitude, new_longitude
            session.commit()
            logger.info(f"Cliente id={cust_id} atualizado")
        else:
            logger.warning(f"Cliente id={cust_id} não encontrado para update")
        return cust

def upd_depots(dep_id: int, new_name: str, new_address: str,
                    new_latitude: float, new_longitude: float):
    with Session() as session:
        dep = session.query(Depots).filter(Depots.id == dep_id).first()
        if dep:
            dep.name = new_name
            dep.address, dep.latitude, dep.longitude = new_address, new_latitude, new_longitude
            session.commit()
            logger.info(f"Deposito id={dep_id} atualizado")
        else:
            logger.warning(f"Deposito id={dep_id} não encontrado para update")
        return dep

def upd_vehicle(vehicle_id: int, model: str, plate: str, capacity: int, cost_per_km: float, depot_id: int):
    with Session() as session:
        v = session.query(Vehicles).filter(Vehicles.id == vehicle_id).first()
        if v:
            v.model, v.plate = model, plate
            v.capacity, v.cost_per_km, v.depot_id = capacity, cost_per_km, depot_id
            session.commit()
            logger.info(f"Veículo id={vehicle_id} atualizado")
        return v

def update_planning(planning_id: int, depot_id: int, deadline: Optional[datetime], status_str: str):
    """
    Atualiza os campos de um planejamento existente.
    Retorna o planejamento atualizado ou None se não encontrado.
    """
    with Session() as session:
        planning = session.query(Planning).filter(Planning.id == planning_id).first()
        if planning:
            planning.depot_id = depot_id
            planning.deadline = deadline # Permite definir deadline como None
            try:
                planning.status = PlanningStatus[status_str]
            except KeyError:
                logger.error(f"Status inválido '{status_str}' para o planejamento id={planning_id}")
                return None
            session.commit()
            logger.info(f"Planejamento id={planning_id} atualizado")
        else:
            logger.warning(f"Planejamento id={planning_id} não encontrado para update")
        return planning

def update_order(order_id: int, demand: int, status_str: str,
                 planning_id: int | None = None,
                 route_id: int | None = None,
                 sequence_position: int | None = None):
    with Session() as session:
        order = session.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            return None

        order.demand = demand
        order.status = OrderStatus[status_str]
        order.planning_id = planning_id
        order.route_id = route_id
        order.sequence_position = sequence_position
        session.commit()
        return order
    
def update_route(route_id: int, planning_id: int, vehicle_plate: str, status: str = "active", description: Optional[str] = None):
    with Session() as session:
        route = session.query(Routes).filter(Routes.id == route_id).first()
        if not route:
            print(f"Rota id={route_id} não encontrada para atualização.")
            return None
        
        vehicle = session.query(Vehicles).filter(Vehicles.plate == vehicle_plate).first()
        planning = session.query(Planning).filter(Planning.id == planning_id).first()
        if not vehicle:
            print(f"Veículo com placa '{vehicle_plate}' não encontrado.")
            return None
        if not planning:
            print(f"Planejamento id={planning_id} não encontrado.")
            return None
        try:
            route_status = RouteStatus[status]
        except KeyError:
            print(f"Status '{status}' inválido para rota.")
            return None

        route.planning_id = planning.id
        route.vehicle_id = vehicle.id
        route.status = route_status
        route.description = description
        session.commit()
        print(f"Rota id={route.id} atualizada.")
        return route

#TOG das tabelas
def tog_customer_active(cust_id: int, active: bool):
    with Session() as session:
        cust = session.query(Costumers).filter(Costumers.id == cust_id).first()
        if cust:
            cust.active = active
            session.commit()
            logger.info(f"Cliente id={cust_id} set active={active}")
        else:
            logger.warning(f"Cliente id={cust_id} não encontrado para toggle")
        return cust
    
def tog_depots_active(dep_id: int, active: bool):
    with Session() as session:
        dep = session.query(Depots).filter(Depots.id == dep_id).first()
        if dep:
            dep.active = active
            session.commit()
            logger.info(f"Deposito id={dep_id} set active={active}")
        else:
            logger.warning(f"Deposito id={dep_id} não encontrado para toggle")
        return dep
    
def tog_vehicle_active(vehicle_id: int, active: bool):
    with Session() as session:
        v = session.query(Vehicles).filter(Vehicles.id == vehicle_id).first()
        if v:
            v.active = active
            session.commit()
            logger.info(f"Veículo id={vehicle_id} set active={active}")
        return v
    
def tog_order_active(order_id: int, active: bool):
    with Session() as session:
        order = session.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            logger.warning(f"Pedido id={order_id} não encontrado para toggle")
            return None
        order.active = active
        session.commit()
        logger.info(f"Pedido id={order_id} set active={active}")
        return order