from datetime import datetime,timedelta
from app.ollama import OllamaClient
class FollowUpRecommender:
    def __init__(self):self.ollama=OllamaClient()
    def recommend(self,lead,interactions):
        history='\n'.join(f'{x.interaction_type}: {x.interaction_notes}' for x in interactions[:8]) or 'No interactions recorded.'
        prompt=f'As a B2B sales assistant, suggest one next action and a polite follow-up message. Do not invent facts. Lead: {lead.name}, {lead.company}, interested in {lead.interested_service}, status {lead.lead_status}. History: {history}.'
        try:return {'recommendation':self.ollama.generate(prompt),'provider':'ollama'}
        except Exception:
            action='Follow up within one business day to understand requirements, budget and decision timeline.'
            message=f'Hi {lead.name}, thank you for your interest in {lead.interested_service}. Would you be available for a brief call to discuss next steps?'
            return {'recommendation':f'Next action: {action}\n\nSuggested message: {message}','provider':'local_fallback'}
