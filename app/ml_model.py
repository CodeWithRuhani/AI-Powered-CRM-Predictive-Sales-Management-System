from pathlib import Path
import joblib,numpy as np,pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from app.config import ROOT
FEATURES=['industry','lead_source','budget','engagement_count','days_since_last_contact','service_interest']
CAT=['industry','lead_source','service_interest'];NUM=['budget','engagement_count','days_since_last_contact']
MODEL_PATH=ROOT/'models'/'lead_conversion.joblib'
def synthetic_data(n=1200,seed=42):
    rng=np.random.default_rng(seed)
    d=pd.DataFrame({'industry':rng.choice(['Technology','Healthcare','Finance','Retail','Manufacturing','Education'],n),
    'lead_source':rng.choice(['Website','Referral','LinkedIn','Campaign','Cold Outreach'],n),
    'budget':rng.lognormal(10.2,.8,n).clip(500,250000),'engagement_count':rng.poisson(4,n).clip(0,25),
    'days_since_last_contact':rng.integers(0,61,n),
    'service_interest':rng.choice(['AI Automation','CRM','Analytics','Cloud','Custom Software'],n)})
    z=-2+d.engagement_count*.22+np.log1p(d.budget)*.22-d.days_since_last_contact*.035
    z+=d.lead_source.map({'Referral':.85,'LinkedIn':.35,'Website':.25,'Campaign':.05,'Cold Outreach':-.45})
    z+=d.industry.map({'Technology':.25,'Finance':.2,'Healthcare':.05,'Retail':-.05,'Manufacturing':.1,'Education':-.1})
    d['converted']=(rng.random(n)<1/(1+np.exp(-z))).astype(int)
    return d
class LeadScoringModel:
    def __init__(self):self.pipeline=None;self.metrics={}
    def train(self):
        d=synthetic_data();X=d[FEATURES];y=d.converted
        prep=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore'),CAT),('num',StandardScaler(),NUM)])
        self.pipeline=Pipeline([('prep',prep),('rf',RandomForestClassifier(n_estimators=160,max_depth=9,min_samples_leaf=3,class_weight='balanced',random_state=42,n_jobs=-1))])
        a,b,c,e=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
        self.pipeline.fit(a,c);pred=self.pipeline.predict(b);prob=self.pipeline.predict_proba(b)[:,1]
        self.metrics={'accuracy':round(accuracy_score(e,pred),3),'precision':round(precision_score(e,pred,zero_division=0),3),
        'recall':round(recall_score(e,pred,zero_division=0),3),'f1':round(f1_score(e,pred,zero_division=0),3),'roc_auc':round(roc_auc_score(e,prob),3)}
        MODEL_PATH.parent.mkdir(exist_ok=True);joblib.dump({'pipeline':self.pipeline,'metrics':self.metrics},MODEL_PATH)
    def load(self):
        if MODEL_PATH.exists():
            x=joblib.load(MODEL_PATH);self.pipeline=x['pipeline'];self.metrics=x['metrics']
        else:self.train()
        return self
    def predict(self,features):
        if self.pipeline is None:self.load()
        p=float(self.pipeline.predict_proba(pd.DataFrame([{k:features[k] for k in FEATURES}]))[0][1]);score=round(p*100)
        return {'lead_score':score,'conversion_probability':round(p,4),'lead_category':'Hot' if score>=70 else 'Warm' if score>=40 else 'Cold'}
