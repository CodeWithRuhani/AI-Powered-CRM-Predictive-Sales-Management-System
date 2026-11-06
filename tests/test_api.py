from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health():assert client.get('/health').status_code==200
def test_metrics():assert 'roc_auc' in client.get('/ml/metrics').json()['metrics']
def test_analytics_includes_30_day_lead_trend():
    response=client.get('/analytics')
    assert response.status_code==200,response.text
    trend=response.json()['lead_trend']
    assert len(trend)==30
    assert all({'date','new_leads'}<=set(day) for day in trend)
    assert trend[0]['date']<trend[-1]['date']
def test_chat_accepts_email_only_and_guest_profiles(monkeypatch):
    from app import routes
    monkeypatch.setattr(routes.ollama,'chat',lambda message,profile,history:{'reply':'Hello!','provider':'test'})
    for profile in ({'email':'user@example.com'},{}):
        response=client.post('/chat',json={'message':'Hello','profile':profile})
        assert response.status_code==200,response.text
        assert response.json()['reply']=='Hello!'
def test_chat_timeout_uses_long_read_timeout_and_clear_error(monkeypatch):
    import requests
    from app import ollama as ollama_module
    from app.schemas import Profile
    client=ollama_module.OllamaClient()
    captured={}
    def timeout_request(*args,**kwargs):
        captured['timeout']=kwargs['timeout']
        raise requests.ReadTimeout()
    monkeypatch.setattr(ollama_module.requests,'post',timeout_request)
    result=client.chat('Hello',Profile())
    assert captured['timeout']==(ollama_module.settings.OLLAMA_CONNECT_TIMEOUT,ollama_module.settings.OLLAMA_TIMEOUT)
    assert result['provider']=='ollama_timeout'
    assert 'try again' in result['reply']
def test_lead_lifecycle():
    p={'name':'Demo Lead','company':'Example Ltd','email':'demo@example.com','phone':'+911234567890','industry':'Technology','interested_service':'AI Automation','lead_source':'Referral','budget':50000}
    r=client.post('/leads',json=p);assert r.status_code==201,r.text
    i=r.json()['id'];assert client.get(f'/leads/{i}').status_code==200
    assert client.post(f'/leads/{i}/score').status_code==200
    assert client.put(f'/leads/{i}',json={'lead_status':'Interested'}).status_code==200
    assert client.get(f'/leads/{i}/history').status_code==200
    assert client.delete(f'/leads/{i}').status_code==200
