from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, Float, Boolean, Enum, DateTime, Table, select
from sqlalchemy import create_engine, ForeignKey, insert
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import enum
from datetime import datetime, timezone, timedelta

# Create a SQLite engine for the database (router.db)
engine = create_engine("sqlite:///router.db")
# Create a base class for declarative models
Base = declarative_base()
# Create a session factory
Session = sessionmaker(bind=engine)

# Define costumers table
class Costumers(Base):
    __tablename__ = "costumers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    address = Column(UnicodeText)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    orders = relationship("Orders", back_populates="customer")

# Define depots table
class Depots(Base):
    __tablename__ = "depots"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    address = Column(UnicodeText)
    latitude = Column(Float, default=float("nan"))
    longitude = Column(Float, default=float("nan"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    vehicles = relationship("Vehicles", back_populates="depot")
    planning = relationship("Planning", back_populates="depot")

# Define vehicles table
class Vehicles(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True)
    model = Column(String(100))
    plate = Column(String(10), unique=True, index=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    cost_per_km = Column(Float, default=1.0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    depot_id = Column(Integer, ForeignKey("depots.id"), nullable=False)
    depot = relationship("Depots", back_populates="vehicles")
    routes = relationship("Routes", back_populates="vehicle")

# Define an Enum for Order Status
class OrderStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    delivered = "delivered"
    cancelled = "cancelled"

# Define orders table
class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    demand = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    customer_id = Column(Integer, ForeignKey("costumers.id"), nullable=False)
    customer = relationship("Costumers", back_populates="orders")
    planning_id = Column(Integer, ForeignKey("planning.id"))
    planning = relationship("Planning", back_populates="orders")
    route_id = Column(Integer, ForeignKey("routes.id"))  # Nova FK para rota
    sequence_position = Column(Integer)  # Posição na rota
    route = relationship("Routes", back_populates="orders")

# Define an Enum for Planning Status
class PlanningStatus(enum.Enum):
    pending = "pending"
    optimizing = "optimizing"
    ready = "ready"
    executed = "executed"
    cancelled = "cancelled"

# Define a table for planning
class Planning(Base):
    __tablename__ = "planning"
    id = Column(Integer, primary_key=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(Enum(PlanningStatus), default=PlanningStatus.pending, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    orders = relationship("Orders", back_populates="planning")
    depot_id = Column(Integer, ForeignKey("depots.id"), nullable=False)
    depot = relationship("Depots", back_populates="planning")
    routes = relationship("Routes", back_populates="planning")

# Define a table for routes
class Routes(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    distance = Column(Float, nullable=False, default=0.0)
    load = Column(Float, nullable=False, default=0.0)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    vehicle = relationship("Vehicles", back_populates="routes")
    planning_id = Column(Integer, ForeignKey("planning.id"), nullable=False)
    planning = relationship("Planning", back_populates="routes")
    orders = relationship(
        "Orders",
        back_populates="route",
        order_by="Orders.sequence_position"
    )

# Create all tables in the database if they don't exist
Base.metadata.create_all(engine)