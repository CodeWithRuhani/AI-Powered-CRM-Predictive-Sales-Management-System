from datetime import datetime
from typing import Optional
from pydantic import BaseModel,EmailStr,Field
STATUSES={'New','Contacted','Interested','Negotiation','Converted','Lost'}
KINDS={'Call','Email','Meeting','Enquiry','Note'}
class LeadCreate(BaseModel):
    name:str=Field(min_length=1,max_length=120)
    company:str=Field(min_length=1,max_length=160)
    email:Optional[EmailStr]=None
    phone:Optional[str]=None
    industry:str
    interested_service:str
    lead_source:str='Website'
    budget:float=Field(default=0,ge=0)
    assigned_to:Optional[int]=None
class LeadUpdate(BaseModel):
    name:Optional[str]=None
    company:Optional[str]=None
    email:Optional[EmailStr]=None
    phone:Optional[str]=None
    industry:Optional[str]=None
    interested_service:Optional[str]=None
    lead_source:Optional[str]=None
    budget:Optional[float]=Field(default=None,ge=0)
    lead_status:Optional[str]=None
    assigned_to:Optional[int]=None
class RepCreate(BaseModel):
    name:str
    email:EmailStr
    role:str='Sales Representative'
class InteractionCreate(BaseModel):
    lead_id:int
    interaction_type:str
    interaction_notes:str=Field(min_length=2,max_length=5000)
class Profile(BaseModel):
    name:str=Field(default='Guest',min_length=1,max_length=120)
    email:Optional[EmailStr]=None
    company:str=Field(default='Guest',min_length=1,max_length=160)
    role:str=Field(default='Guest',min_length=1,max_length=80)
class ChatInput(BaseModel):
    message:str=Field(min_length=1,max_length=4000)
    profile:Profile
    history:list[dict]=[]
