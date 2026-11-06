from sqlalchemy import or_
from sqlalchemy.orm import Session,joinedload
from app.models import Lead,Interaction,SalesRepresentative
class LeadRepository:
    def __init__(self,db:Session): self.db=db
    def create(self,**data):
        row=Lead(**data);self.db.add(row);self.db.commit();self.db.refresh(row);return row
    def get(self,id):
        return self.db.query(Lead).options(joinedload(Lead.representative)).filter(Lead.id==id).first()
    def list(self,search=None,status=None,industry=None):
        q=self.db.query(Lead).options(joinedload(Lead.representative))
        if search:
            s=f'%{search}%';q=q.filter(or_(Lead.name.ilike(s),Lead.company.ilike(s),Lead.email.ilike(s),Lead.interested_service.ilike(s)))
        if status:q=q.filter(Lead.lead_status==status)
        if industry:q=q.filter(Lead.industry==industry)
        return q.order_by(Lead.created_at.desc()).all()
    def history(self,id):
        return self.db.query(Interaction).filter_by(lead_id=id).order_by(Interaction.interaction_date.desc()).all()
class CRMManager:
    def __init__(self,db): self.db=db;self.repo=LeadRepository(db)
    def create_lead(self,data):
        if data.get('assigned_to') and not self.db.get(SalesRepresentative,data['assigned_to']):
            raise ValueError('Sales representative not found')
        return self.repo.create(**data)
    def record_interaction(self,data):
        if not self.db.get(Lead,data['lead_id']):raise ValueError('Lead not found')
        row=Interaction(**data);self.db.add(row);self.db.commit();self.db.refresh(row);return row
