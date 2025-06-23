from backend.model import *
import logging
from datetime import datetime
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
        planning = session.query(Planning).all()
        for p in planning:
            print(f"ID: {p.id}, {p.deadline}, {p.created_at}")
        return planning

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

def add_planning(depot_id: int, deadline: datetime | None = None):
    """
    Adiciona um novo planejamento. O status inicial é 'pending'.
    Retorna a instância do planejamento criado.
    """
    with Session() as session:
        planning = Planning(depot_id=depot_id, deadline=deadline, status=PlanningStatus.pending) # type: ignore
        session.add(planning)
        session.commit()
        logger.info(f"Planejamento criado: id={planning.id} para depot id={depot_id}")
        return planning


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

def update_planning(planning_id: int, depot_id: int, deadline: datetime | None, status_str: str):
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