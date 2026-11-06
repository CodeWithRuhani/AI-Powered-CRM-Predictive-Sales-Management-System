from datetime import datetime,timedelta
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Lead,Interaction,SalesRepresentative,LeadPrediction,FollowUp
from app.schemas import LeadCreate,LeadUpdate,RepCreate,InteractionCreate,ChatInput,STATUSES,KINDS
from app.repositories import LeadRepository,CRMManager
from app.ml_model import LeadScoringModel
from app.ollama import OllamaClient
from app.services import FollowUpRecommender
router=APIRouter();ml=LeadScoringModel().load();ollama=OllamaClient();followup=FollowUpRecommender()
def out(x):
    return {'id':x.id,'name':x.name,'company':x.company,'email':x.email,'phone':x.phone,'industry':x.industry,
    'interested_service':x.interested_service,'lead_source':x.lead_source,'budget':x.budget,'lead_status':x.lead_status,
    'assigned_to':x.assigned_to,'assigned_rep':x.representative.name if x.representative else None,'created_at':x.created_at.isoformat()}
@router.post('/leads',status_code=201)
def create_lead(p:LeadCreate,db:Session=Depends(get_db)):
    try:return out(CRMManager(db).create_lead(p.model_dump()))
    except ValueError as e:raise HTTPException(422,str(e))
@router.get('/leads')
def list_leads(search:str|None=None,status:str|None=None,industry:str|None=None,db:Session=Depends(get_db)):
    if status and status not in STATUSES:raise HTTPException(422,'Invalid lead status')
    return [out(x) for x in LeadRepository(db).list(search,status,industry)]
@router.get('/leads/{id}')
def get_lead(id:int,db:Session=Depends(get_db)):
    x=LeadRepository(db).get(id)
    if not x:raise HTTPException(404,'Lead not found')
    return out(x)
@router.put('/leads/{id}')
def update_lead(id:int,p:LeadUpdate,db:Session=Depends(get_db)):
    x=db.get(Lead,id)
    if not x:raise HTTPException(404,'Lead not found')
    data=p.model_dump(exclude_unset=True)
    if data.get('lead_status') and data['lead_status'] not in STATUSES:raise HTTPException(422,'Invalid lead status')
    if data.get('assigned_to') and not db.get(SalesRepresentative,data['assigned_to']):raise HTTPException(422,'Representative not found')
    for k,v in data.items():setattr(x,k,str(v) if k=='email' and v else v)
    db.commit();return out(LeadRepository(db).get(id))
@router.delete('/leads/{id}')
def delete_lead(id:int,db:Session=Depends(get_db)):
    x=db.get(Lead,id)
    if not x:raise HTTPException(404,'Lead not found')
    db.delete(x);db.commit();return {'message':f'Lead {id} deleted'}
@router.post('/leads/{id}/score')
def score_lead(id:int,db:Session=Depends(get_db)):
    x=db.get(Lead,id)
    if not x:raise HTTPException(404,'Lead not found')
    items=LeadRepository(db).history(id);last=max((i.interaction_date for i in items),default=x.created_at)
    features={'industry':x.industry,'lead_source':x.lead_source,'budget':x.budget,'engagement_count':len(items),
    'days_since_last_contact':max(0,(datetime.utcnow()-last).days),'service_interest':x.interested_service}
    result=ml.predict(features);explanation=f"{len(items)} recorded interactions; budget signal {x.budget:,.0f}; source {x.lead_source}; last contact {features['days_since_last_contact']} days ago."
    row=LeadPrediction(lead_id=id,lead_score=result['lead_score'],conversion_probability=result['conversion_probability'],lead_category=result['lead_category'],explanation=explanation)
    db.add(row);db.commit()
    return {**result,'prediction_id':row.id,'explanation':explanation,'model_note':'Trained on synthetic demo data; not a validated forecast.'}
@router.get('/leads/{id}/history')
def history(id:int,db:Session=Depends(get_db)):
    if not db.get(Lead,id):raise HTTPException(404,'Lead not found')
    ints=LeadRepository(db).history(id)
    preds=db.query(LeadPrediction).filter_by(lead_id=id).order_by(LeadPrediction.predicted_at.desc()).all()
    fs=db.query(FollowUp).filter_by(lead_id=id).order_by(FollowUp.followup_date.desc()).all()
    return {'interactions':[{'id':i.id,'type':i.interaction_type,'notes':i.interaction_notes,'date':i.interaction_date.isoformat()} for i in ints],
    'predictions':[{'score':p.lead_score,'probability':p.conversion_probability,'category':p.lead_category} for p in preds],
    'followups':[{'id':f.id,'date':f.followup_date.isoformat(),'action':f.recommended_action,'status':f.followup_status} for f in fs]}
@router.post('/interactions',status_code=201)
def add_interaction(p:InteractionCreate,db:Session=Depends(get_db)):
    if p.interaction_type not in KINDS:raise HTTPException(422,'Type must be Call, Email, Meeting, Enquiry or Note')
    try:
        x=CRMManager(db).record_interaction(p.model_dump())
        return {'id':x.id,'lead_id':x.lead_id,'type':x.interaction_type,'notes':x.interaction_notes}
    except ValueError as e:raise HTTPException(404,str(e))
@router.post('/followups/recommend')
def recommend(lead_id:int,db:Session=Depends(get_db)):
    x=LeadRepository(db).get(lead_id)
    if not x:raise HTTPException(404,'Lead not found')
    result=followup.recommend(x,LeadRepository(db).history(lead_id))
    row=FollowUp(lead_id=lead_id,assigned_employee=x.assigned_to,followup_date=datetime.utcnow()+timedelta(days=1),recommended_action=result['recommendation'])
    db.add(row);db.commit();result['followup_id']=row.id;return result
@router.get('/followups/overdue')
def overdue(db:Session=Depends(get_db)):
    rows=db.query(FollowUp,Lead).join(Lead).filter(FollowUp.followup_status=='Pending',FollowUp.followup_date<datetime.utcnow()).order_by(FollowUp.followup_date.asc()).all()
    return [{'id':f.id,'lead_id':l.id,'lead_name':l.name,'due':f.followup_date.isoformat(),'action':f.recommended_action} for f,l in rows]
@router.get('/representatives')
def reps(db:Session=Depends(get_db)):
    return [{'id':x.id,'name':x.name,'email':x.email,'role':x.role} for x in db.query(SalesRepresentative).all()]
@router.post('/representatives',status_code=201)
def add_rep(p:RepCreate,db:Session=Depends(get_db)):
    x=SalesRepresentative(**p.model_dump());db.add(x)
    try:db.commit();db.refresh(x)
    except Exception:db.rollback();raise HTTPException(409,'Representative email already exists')
    return {'id':x.id,'name':x.name,'email':x.email,'role':x.role}
@router.get('/analytics')
def analytics(db:Session=Depends(get_db)):
    total=db.query(func.count(Lead.id)).scalar() or 0
    counts={k:v for k,v in db.query(Lead.lead_status,func.count(Lead.id)).group_by(Lead.lead_status).all()}
    cats={k:v for k,v in db.query(LeadPrediction.lead_category,func.count(func.distinct(LeadPrediction.lead_id))).group_by(LeadPrediction.lead_category).all()}
    trend_start=datetime.utcnow().date()-timedelta(days=29)
    trend_rows=db.query(func.date(Lead.created_at),func.count(Lead.id)).filter(
        Lead.created_at>=datetime.combine(trend_start,datetime.min.time())
    ).group_by(func.date(Lead.created_at)).all()
    trend_counts={str(day):count for day,count in trend_rows}
    lead_trend=[{'date':(trend_start+timedelta(days=day)).isoformat(),
                 'new_leads':trend_counts.get((trend_start+timedelta(days=day)).isoformat(),0)} for day in range(30)]
    converted=counts.get('Converted',0);performance=[]
    for rep in db.query(SalesRepresentative).all():
        n=db.query(func.count(Lead.id)).filter_by(assigned_to=rep.id).scalar() or 0
        w=db.query(func.count(Lead.id)).filter(Lead.assigned_to==rep.id,Lead.lead_status=='Converted').scalar() or 0
        performance.append({'name':rep.name,'leads':n,'converted':w})
    return {'total_leads':total,'new_leads':counts.get('New',0),'converted_leads':converted,'lost_leads':counts.get('Lost',0),
    'conversion_rate':round(converted/total*100,2) if total else 0,
    'statuses':{s:counts.get(s,0) for s in STATUSES},'categories':{s:cats.get(s,0) for s in ('Hot','Warm','Cold')},
    'representative_performance':performance,'lead_trend':lead_trend}
@router.get('/ml/metrics')
def metrics():return {'metrics':ml.metrics,'training_data':'Generated synthetic dataset','warning':'Held-out synthetic test metrics are not real-world validation.'}
@router.post('/chat')
def chat(p:ChatInput):return ollama.chat(p.message,p.profile,p.history)
@router.get('/health')
def health():return {'status':'ok','ollama_model':ollama.model,'ollama_url':ollama.url}
