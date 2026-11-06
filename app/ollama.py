import requests
from app.config import settings
class OllamaClient:
    def __init__(self):self.url=settings.OLLAMA_BASE_URL;self.model=settings.OLLAMA_MODEL
    def chat(self,message,profile,history=None):
        msgs=[{'role':'system','content':'You are a concise B2B CRM sales assistant. Explain CRM concepts, lead scoring and sales workflows. Never invent CRM records, prices or business facts. Conversion probability is only a synthetic-data demo estimate.'},
              {'role':'system','content':f"Current session profile: {profile.name}, {profile.company}, {profile.role}."}]
        for item in (history or [])[-8:]:
            if item.get('role') in ('user','assistant'):msgs.append({'role':item['role'],'content':str(item.get('content',''))[:4000]})
        msgs.append({'role':'user','content':message})
        try:
            r=requests.post(self.url+'/api/chat',json={'model':self.model,'messages':msgs,'stream':False},timeout=(settings.OLLAMA_CONNECT_TIMEOUT,settings.OLLAMA_TIMEOUT));r.raise_for_status()
            answer=r.json().get('message',{}).get('content','').strip()
            if answer:return {'reply':answer,'provider':'ollama','model':self.model}
        except requests.Timeout:
            return {'reply':f"Ollama did not respond within {settings.OLLAMA_TIMEOUT} seconds. The model may still be loading; please try again.",'provider':'ollama_timeout'}
        except requests.RequestException as e:
            return {'reply':f"Cannot connect to Ollama at {self.url}. Start Ollama and run `ollama pull {self.model}`. CRM APIs remain available. ({type(e).__name__})",'provider':'ollama_unavailable'}
        return {'reply':'The model returned an empty response. Please try again.','provider':'ollama_unavailable'}
    def generate(self,prompt):
        r=requests.post(self.url+'/api/generate',json={'model':self.model,'prompt':prompt,'stream':False},timeout=(settings.OLLAMA_CONNECT_TIMEOUT,settings.OLLAMA_TIMEOUT))
        r.raise_for_status();return r.json().get('response','').strip()
