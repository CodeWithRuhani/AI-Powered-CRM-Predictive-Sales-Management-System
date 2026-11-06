from datetime import datetime
from sqlalchemy import String,Integer,Float,DateTime,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database import Base
class SalesRepresentative(Base):
    __tablename__='sales_representatives'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120))
    email:Mapped[str]=mapped_column(String(255),unique=True)
    role:Mapped[str]=mapped_column(String(80),default='Sales Representative')
    leads:Mapped[list['Lead']]=relationship(back_populates='representative')
class Lead(Base):
    __tablename__='leads'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120),index=True)
    company:Mapped[str]=mapped_column(String(160),index=True)
    email:Mapped[str|None]=mapped_column(String(255),nullable=True)
    phone:Mapped[str|None]=mapped_column(String(40),nullable=True)
    industry:Mapped[str]=mapped_column(String(100))
    interested_service:Mapped[str]=mapped_column(String(160))
    lead_source:Mapped[str]=mapped_column(String(80),default='Website')
    budget:Mapped[float]=mapped_column(Float,default=0)
    lead_status:Mapped[str]=mapped_column(String(30),default='New',index=True)
    assigned_to:Mapped[int|None]=mapped_column(ForeignKey('sales_representatives.id',ondelete='SET NULL'),nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    representative:Mapped['SalesRepresentative|None']=relationship(back_populates='leads')
    interactions:Mapped[list['Interaction']]=relationship(back_populates='lead',cascade='all, delete-orphan')
    predictions:Mapped[list['LeadPrediction']]=relationship(back_populates='lead',cascade='all, delete-orphan')
    followups:Mapped[list['FollowUp']]=relationship(back_populates='lead',cascade='all, delete-orphan')
class Interaction(Base):
    __tablename__='interactions'
    id:Mapped[int]=mapped_column(primary_key=True)
    lead_id:Mapped[int]=mapped_column(ForeignKey('leads.id',ondelete='CASCADE'),index=True)
    interaction_type:Mapped[str]=mapped_column(String(30))
    interaction_notes:Mapped[str]=mapped_column(Text)
    interaction_date:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    lead:Mapped[Lead]=relationship(back_populates='interactions')
class LeadPrediction(Base):
    __tablename__='lead_predictions'
    id:Mapped[int]=mapped_column(primary_key=True)
    lead_id:Mapped[int]=mapped_column(ForeignKey('leads.id',ondelete='CASCADE'),index=True)
    lead_score:Mapped[int]=mapped_column(Integer)
    conversion_probability:Mapped[float]=mapped_column(Float)
    lead_category:Mapped[str]=mapped_column(String(10))
    explanation:Mapped[str]=mapped_column(Text)
    predicted_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    lead:Mapped[Lead]=relationship(back_populates='predictions')
class FollowUp(Base):
    __tablename__='follow_ups'
    id:Mapped[int]=mapped_column(primary_key=True)
    lead_id:Mapped[int]=mapped_column(ForeignKey('leads.id',ondelete='CASCADE'),index=True)
    assigned_employee:Mapped[int|None]=mapped_column(ForeignKey('sales_representatives.id',ondelete='SET NULL'),nullable=True)
    followup_date:Mapped[datetime]=mapped_column(DateTime)
    recommended_action:Mapped[str]=mapped_column(Text)
    followup_status:Mapped[str]=mapped_column(String(20),default='Pending')
    lead:Mapped[Lead]=relationship(back_populates='followups')
