"""Prototype académique reproductible. Exécuter : python pipeline.py"""
from pathlib import Path
import json
import sqlite3
import platform
import numpy as np
import pandas as pd
import sklearn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.inspection import permutation_importance
from sklearn.metrics import (roc_auc_score, average_precision_score, brier_score_loss,
    log_loss, precision_score, recall_score, f1_score, confusion_matrix,
    RocCurveDisplay, PrecisionRecallDisplay)

ROOT = Path(__file__).resolve().parent
SEED = 42
TARGET = 'default payment next month'

def load_data():
    df = pd.read_csv(ROOT / 'data/credit_clients.csv')
    if len(df) != 30000 or not df.ID.is_unique or not df[TARGET].isin([0, 1]).all():
        raise ValueError('Schéma UCI inattendu : vérifier la source et la cible.')
    return df

def prepare(df):
    # Codes non documentés : regroupement explicite, sans supprimer des clients.
    clean = df.copy()
    clean['EDUCATION'] = clean.EDUCATION.where(clean.EDUCATION.isin([1,2,3,4]), 4)
    clean['MARRIAGE'] = clean.MARRIAGE.where(clean.MARRIAGE.isin([1,2,3]), 3)
    # SEX conservé pour audit descriptif, exclu des prédicteurs ; pas une garantie d'équité.
    X = clean.drop(columns=['ID', TARGET, 'SEX'])
    return X, clean[TARGET]

def preprocessor(X):
    # États de paiement encodés comme catégories : 0/-2 ne sont pas des mois de retard.
    cat = ['EDUCATION','MARRIAGE','PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6']
    num = [c for c in X.columns if c not in cat]
    return ColumnTransformer([
        ('num', make_pipeline(SimpleImputer(strategy='median'), StandardScaler()), num),
        ('cat', make_pipeline(SimpleImputer(strategy='most_frequent'),
                              OneHotEncoder(handle_unknown='ignore', sparse_output=False)), cat)])

def metrics(y, p, threshold):
    pred = p >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return dict(roc_auc=roc_auc_score(y,p), average_precision=average_precision_score(y,p),
                brier=brier_score_loss(y,p), log_loss=log_loss(y,p),
                precision=precision_score(y,pred,zero_division=0),
                recall=recall_score(y,pred,zero_division=0), f1=f1_score(y,pred,zero_division=0),
                threshold=float(threshold), tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp))

def main():
    out = ROOT / 'outputs'
    out.mkdir(exist_ok=True)
    df = load_data()
    quality = pd.DataFrame({'variable':df.columns, 'missing':df.isna().sum().values,
                            'unique':df.nunique().values, 'min':df.min().values,
                            'max':df.max().values})
    quality.to_csv(out/'data_quality.csv',index=False)
    X,y = prepare(df)
    # 60 % train / 20 % validation / 20 % test, indices clients disjoints.
    trainval, test = train_test_split(df.index, test_size=.2, stratify=y, random_state=SEED)
    train, val = train_test_split(trainval, test_size=.25, stratify=y.loc[trainval], random_state=SEED)
    assert not (set(train)&set(val) or set(train)&set(test) or set(val)&set(test))
    split = pd.Series(index=df.index, dtype='object')
    split.loc[train], split.loc[val], split.loc[test] = 'train','validation','test'
    # Choix du modèle et du seuil uniquement sur validation.
    # Calibration par CV interne au train ; prétraitement réappris dans chaque pli.
    logistic = make_pipeline(preprocessor(X), LogisticRegression(max_iter=3000, C=1.0))
    forest = make_pipeline(preprocessor(X), RandomForestClassifier(
        n_estimators=160, max_depth=10, min_samples_leaf=30, random_state=SEED, n_jobs=2))
    candidates = {'dummy':DummyClassifier(strategy='prior'), 'logistic':logistic,
        'forest_calibrated':CalibratedClassifierCV(forest, method='sigmoid',
            cv=StratifiedKFold(3,shuffle=True,random_state=SEED))}
    rows=[]
    for name, model in candidates.items():
        print('Entraînement :', name, flush=True)
        model.fit(X.loc[train], y.loc[train])
        prob = model.predict_proba(X.loc[val])[:,1]
        rows.append({'model':name, **metrics(y.loc[val],prob,.5)})
    validation = pd.DataFrame(rows)
    validation.to_csv(out/'validation_metrics.csv',index=False)
    winner = validation.loc[validation.model!='dummy'].sort_values('log_loss').iloc[0].model
    model = candidates[winner]
    pv = model.predict_proba(X.loc[val])[:,1]
    thresholds = np.arange(.05,.81,.01)
    sweep = pd.DataFrame([metrics(y.loc[val],pv,t) for t in thresholds])
    sweep.to_csv(out/'validation_thresholds.csv',index=False)
    # Critère pédagogique : F1. Ne représente pas le coût économique bancaire.
    threshold = float(sweep.sort_values('f1',ascending=False).iloc[0].threshold)
    # Modèle figé : aucune remise à niveau ni réglage après consultation du test.
    pt = model.predict_proba(X.loc[test])[:,1]
    test_metrics = {'model':winner, **metrics(y.loc[test],pt,threshold)}
    pd.DataFrame([test_metrics]).to_csv(out/'test_metrics.csv',index=False)
    scored = df.loc[test,['ID','AGE','SEX','LIMIT_BAL']].copy()
    scored['actual_default']=y.loc[test]
    scored['predicted_probability']=pt
    scored['predicted_default']=(pt>=threshold).astype(int)
    scored['risk_band']=pd.cut(pt,[-.001,.1,.3,1],labels=['<10%','10-30%','>30%'])
    scored['error_type']=np.select([
        (scored.actual_default==0)&(scored.predicted_default==1),
        (scored.actual_default==1)&(scored.predicted_default==0)], ['false_positive','false_negative'],default='correct')
    scored.to_csv(out/'test_predictions.csv',index=False)
    pd.DataFrame({'ID':df.ID,'split':split}).to_csv(out/'split_membership.csv',index=False)
    # Importance calculée sur validation : perte d'AUC, association et non causalité.
    imp = permutation_importance(model,X.loc[val],y.loc[val],n_repeats=3,
                                  random_state=SEED,scoring='roc_auc',n_jobs=2)
    pd.DataFrame({'feature':X.columns,'importance':imp.importances_mean,
                  'std':imp.importances_std}).sort_values('importance',ascending=False).to_csv(out/'feature_importance.csv',index=False)
    frac,mean = calibration_curve(y.loc[test],pt,n_bins=10,strategy='quantile')
    pd.DataFrame({'mean_probability':mean,'observed_default_rate':frac}).to_csv(out/'calibration.csv',index=False)
    fig, axes=plt.subplots(1,3,figsize=(15,4))
    RocCurveDisplay.from_predictions(y.loc[test],pt,ax=axes[0])
    PrecisionRecallDisplay.from_predictions(y.loc[test],pt,ax=axes[1])
    axes[1].axhline(y.loc[test].mean(),ls='--',color='gray')
    axes[2].plot(mean,frac,'o-');axes[2].plot([0,1],[0,1],'--',color='gray')
    axes[2].set(xlabel='Probabilité prédite moyenne',ylabel='Taux de défaut observé',title='Calibration — test')
    fig.tight_layout();fig.savefig(out/'evaluation.png',dpi=160);plt.close(fig)
    with sqlite3.connect(out/'credit_risk.sqlite') as con:
        scored.to_sql('test_predictions',con,if_exists='replace',index=False)
    metadata={'seed':SEED,'train_size':len(train),'validation_size':len(val),'test_size':len(test),
        'selected_model':winner,'selection_metric':'validation log_loss',
        'threshold_criterion':'validation F1','python':platform.python_version(),
        'sklearn':sklearn.__version__,'pandas':pd.__version__,
        'dataset':'Yeh (2009), UCI, DOI:10.24432/C55S3H, CC BY 4.0'}
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(json.dumps(test_metrics,indent=2))
    return test_metrics

if __name__=='__main__':
    main()
