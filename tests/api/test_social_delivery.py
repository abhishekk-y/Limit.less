import httpx

API='/api/v1'

def test_provider_rejection_does_not_expire_app_login(test_client, register, monkeypatch):
 headers,_=register()
 test_client.post(API+'/social/connections/provider',headers=headers,json={'name':'publora','value':'test-key'})
 class Client:
  def __init__(self,**kwargs):pass
  async def __aenter__(self):return self
  async def __aexit__(self,*args):pass
  async def get(self,*args,**kwargs):return httpx.Response(401,request=httpx.Request('GET','https://api.publora.com'))
 monkeypatch.setattr('app.runtime.social_engine.httpx.AsyncClient',Client)
 assert test_client.get(API+'/social/channels',headers=headers).status_code==409
 assert test_client.get(API+'/auth/me',headers=headers).status_code==200

def test_draft_without_receipt_cannot_claim_provider_delivery(test_client, register):
 headers,_=register()
 draft=test_client.post(API+'/social/drafts',headers=headers,json={'title':'Draft','content':'A reviewed example draft.','kind':'post'}).json()
 response=test_client.post(API+f"/social/drafts/{draft['id']}/delivery",headers=headers)
 assert response.status_code==409
 assert test_client.get(API+'/social/drafts',headers=headers).json()[0]['published'] is False
