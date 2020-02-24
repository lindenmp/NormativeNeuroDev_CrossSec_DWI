#!/usr/bin/env python
# coding: utf-8

# # Preamble

# In[1]:


import os, sys, glob
import pandas as pd
import numpy as np
import scipy as sp
from scipy import stats
import scipy.io as sio
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype'] = 'none'


# In[2]:


sys.path.append('/Users/lindenmp/Dropbox/Work/ResProjects/NormativeNeuroDev_CrossSec_DWI/code/func/')
from proj_environment import set_proj_env
from func import mark_outliers, winsorize_outliers_signed


# In[3]:


train_test_str = 'squeakycleanExclude'
exclude_str = 't1Exclude'
parc_str = 'schaefer'
parc_scale = 200
extra_str = ''
# extra_str = '_nuis-netdens'
# extra_str = '_nuis-str'
parcel_names, parcel_loc, drop_parcels, num_parcels, yeo_idx, yeo_labels = set_proj_env(train_test_str = train_test_str, exclude_str = exclude_str,
                                                                            parc_str = parc_str, parc_scale = parc_scale, extra_str = extra_str)


# ### Setup output directory

# In[4]:


print(os.environ['MODELDIR_BASE'])
print(os.environ['MODELDIR'])
if not os.path.exists(os.environ['MODELDIR']): os.makedirs(os.environ['MODELDIR'])


# ### Data processing options

# In[5]:


wins_data = True
my_thresh = 3
norm_data = True


# ## Load data

# In[6]:


# Load data
df = pd.read_csv(os.path.join(os.environ['MODELDIR_BASE'], 'df_pheno.csv'))
df.set_index(['bblid', 'scanid'], inplace = True)
print(df.shape)


# In[7]:


# Load data
df_node = pd.read_csv(os.path.join(os.environ['MODELDIR_BASE'], 'df_node_base.csv'))
df_node.set_index(['bblid', 'scanid'], inplace = True)
print(df_node.shape)


# In[8]:


df_node.head()


# In[9]:


metrics = ('ct', 'vol', 'str', 'ac', 'mc')
dwi_metrics = ('str', 'ac', 'mc')
t1_metrics = ('ct', 'vol')


# ### Compute whole brain averages

# In[10]:


df_node_mean = pd.DataFrame(index = df_node.index, columns = metrics)
for metric in metrics:
    df_node_mean[metric] = df_node.filter(regex = metric, axis = 1).mean(axis = 1)


# # Plots

# In[11]:


# Labels
sns.set(style='white', context = 'talk', font_scale = 1)


# In[12]:


metric_x = 'ageAtScan1'
metric_y = 'mprage_antsCT_vol_TBV'
f = sns.jointplot(x = df[metric_x], y = df[metric_y], kind="reg")
f.annotate(sp.stats.pearsonr)
f.plot_joint(plt.scatter, c = "k", s = 5, linewidth = 2, marker = ".", alpha = 0.3)
f.ax_joint.collections[0].set_alpha(0)


# In[13]:


metric_x = 'ageAtScan1'
metric_y = 'str'
f = sns.jointplot(x = df[metric_x], y = df_node_mean[metric_y], kind="reg")
f.annotate(sp.stats.pearsonr)
f.plot_joint(plt.scatter, c = "k", s = 5, linewidth = 2, marker = ".", alpha = 0.3)
f.ax_joint.collections[0].set_alpha(0)


# In[14]:


metric_x = 'mprage_antsCT_vol_TBV'
# metric_x = 'network_density'
# metric_x = 'streamline_count'


# In[15]:


metric_y = 'str'
f = sns.jointplot(x = df[metric_x], y = df_node_mean[metric_y], kind="reg")
f.annotate(sp.stats.spearmanr)
f.plot_joint(plt.scatter, c = "k", s = 5, linewidth = 2, marker = ".", alpha = 0.3)
f.ax_joint.collections[0].set_alpha(0)


# In[16]:


metric_y = 'ac'
f = sns.jointplot(x = df[metric_x], y = df_node_mean[metric_y], kind="reg")
f.annotate(sp.stats.spearmanr)
f.plot_joint(plt.scatter, c = "k", s = 5, linewidth = 2, marker = ".", alpha = 0.3)
f.ax_joint.collections[0].set_alpha(0)


# In[17]:


metric_y = 'mc'
f = sns.jointplot(x = df[metric_x], y = df_node_mean[metric_y], kind="reg")
f.annotate(sp.stats.spearmanr)
f.plot_joint(plt.scatter, c = "k", s = 5, linewidth = 2, marker = ".", alpha = 0.3)
f.ax_joint.collections[0].set_alpha(0)


# In[18]:


for metric in dwi_metrics:
    x = df_node.filter(regex = metric, axis = 1).mean(axis = 1)
    outliers = mark_outliers(x, thresh = my_thresh)
    print(metric + ': ' + str(np.round((outliers.sum() / x.shape[0]) * 100,2)))


# A higher threshold than 3 probably makes sense but sticking with convention to avoid 'kick me' signs with reviewers.
# 
# Note, results are unaffected by setting my_thresh to 4,5, or 6

# ### Check frequency of outliers

# In[19]:


df_node_mask = pd.DataFrame(index = df_node.index, columns = df_node.columns)
for i, col in enumerate(df_node.columns):
    x = df_node.loc[:,col].copy()
    x_out = mark_outliers(x, thresh = my_thresh)
    df_node_mask.loc[:,col] = x_out

f, axes = plt.subplots(1,len(dwi_metrics))
f.set_figwidth(len(dwi_metrics)*5)
f.set_figheight(5)

for i, metric in enumerate(dwi_metrics):
    if df_node_mask.filter(regex = metric).sum().any():
        sns.distplot(df_node_mask.filter(regex = metric).sum()/df_node_mask.filter(regex = metric).shape[0]*100, ax = axes[i])


# ### Winsorize outliers

# In[20]:


my_str = '|'.join(dwi_metrics); print(my_str)


# In[21]:


if wins_data:
    for i, col in enumerate(df_node.filter(regex = my_str).columns):
        x = df_node.loc[:,col].copy()
        x_out = winsorize_outliers_signed(x, thresh = my_thresh)
        df_node.loc[:,col] = x_out
else:
    print('Skipping...')


# ## Normalize

# In[22]:


if np.any(df_node<0):
    print('WARNING: some regional values are <0.. box cox will fail')


# In[23]:


rank_r = np.zeros(df_node.filter(regex = my_str).shape[1])


# In[24]:


# normalise
if norm_data:
    for i, col in enumerate(df_node.filter(regex = my_str).columns):
        # normalize regional metric
        x = sp.stats.boxcox(df_node.loc[:,col])[0]
        # check if rank order is preserved
        rank_r[i] = sp.stats.spearmanr(df_node.loc[:,col],x)[0]
        # store normalized version
        df_node.loc[:,col] = x
else:
    print('Skipping...')


# In[25]:


np.sum(rank_r < .99)


# ### Check distributions

# In[26]:


f, axes = plt.subplots(2,len(dwi_metrics))
f.set_figwidth(len(dwi_metrics)*5)
f.set_figheight(10)

for i, metric in enumerate(dwi_metrics):
    kur = np.zeros((df_node.filter(regex = metric).shape[1]))
    skew = np.zeros((df_node.filter(regex = metric).shape[1]))
    for j, node in enumerate(df_node.filter(regex = metric).columns):
        d = sp.stats.zscore(df_node.filter(regex = metric).loc[:,node])
        kur[j] = sp.stats.kurtosistest(d)[0]
        skew[j] = sp.stats.skewtest(d)[0]
    
    sns.distplot(kur, ax = axes[0,i])
    axes[0,i].set_xlabel(metric+': kurtosis')
    sns.distplot(skew, ax = axes[1,i])
    axes[1,i].set_xlabel(metric+': skewness')


# In[27]:


my_str = os.environ['MODELDIR'].split('/')[-1]
my_str = my_str.split('_')[-1]
my_str


# In[28]:


if my_str == 'nuis-streamline' or my_str == 'nuis-netdens':
    df_node = df_node.filter(regex = 'squeakycleanExclude|str|ac|mc', axis = 1)
elif my_str == 'nuis-str':
    df_str = df_node.filter(regex = 'str', axis = 1).copy()
    df_node = df_node.filter(regex = 'squeakycleanExclude|ac|mc', axis = 1)
else:
    print('skipping...')


# In[29]:


df_node.shape


# ## Nuisance regression

# In[30]:


df_node_bak = df_node.copy()


# In[31]:


# labels of nuisance regressors
nuis = ['averageManualRating']
print(nuis)
df_nuis = df[nuis]
df_nuis = sm.add_constant(df_nuis)

my_str = '|'.join(t1_metrics); print(my_str)
cols = df_node.filter(regex = my_str, axis = 1).columns

mdl = sm.OLS(df_node.loc[:,cols].astype(float), df_nuis.astype(float)).fit()
y_pred = mdl.predict(df_nuis)
y_pred.columns = cols
df_node.loc[:,cols] = df_node.loc[:,cols] - y_pred


# In[32]:


if my_str == 'nuis-str':
    print('Running strength nuisance regression')
    for col in df_node.filter(regex = 'ac|mc', axis = 1).columns:
        nuis = ['mprage_antsCT_vol_TBV', 'dti64MeanRelRMS']
        df_nuis = df[nuis]
        df_nuis = sm.add_constant(df_nuis)

        col_nuis = 'str_' + col.split('_')[1]
        df_nuis.loc[:,'str'] = df_str.loc[:,col_nuis]

        mdl = sm.OLS(df_node.loc[:,col], df_nuis).fit()
        y_pred = mdl.predict(df_nuis)
        df_node.loc[:,col] = df_node.loc[:,col] - y_pred
else:
    if my_str == 'nuis-netdens':
        print('Running network density nuisance regression')
        nuis = ['mprage_antsCT_vol_TBV', 'dti64MeanRelRMS', 'network_density']
        df_nuis = df[nuis]
    else:
        print('Running standard nuisance regression')
        nuis = ['mprage_antsCT_vol_TBV', 'dti64MeanRelRMS']
        df_nuis = df[nuis]
    print(nuis)
    df_nuis = sm.add_constant(df_nuis)

    my_str = '|'.join(dwi_metrics); print(my_str)
    cols = df_node.filter(regex = my_str, axis = 1).columns

    mdl = sm.OLS(df_node.loc[:,cols], df_nuis).fit()
    y_pred = mdl.predict(df_nuis)
    y_pred.columns = cols
    df_node.loc[:,cols] = df_node.loc[:,cols] - y_pred


# In[33]:


r = np.zeros(df_node.shape[1])
for i, col in enumerate(df_node.columns):
    r[i] = sp.stats.spearmanr(df_node_bak[col],df_node[col])[0]
sns.distplot(r)


# In[34]:


f = sns.jointplot(x = df['ageAtScan1_Years'], y = df_node['str_0'], kind="reg")
f.annotate(sp.stats.spearmanr)
# f.annotate(sp.stats.pearsonr)
f.plot_joint(plt.scatter, c = "k", s = 5, linewidth = 2, marker = ".", alpha = 0.3)
f.ax_joint.collections[0].set_alpha(0)


# In[35]:


f = sns.jointplot(x = df['ageAtScan1_Years'], y = df_node['ac_0'], kind="reg")
f.annotate(sp.stats.spearmanr)
# f.annotate(sp.stats.pearsonr)
f.plot_joint(plt.scatter, c = "k", s = 5, linewidth = 2, marker = ".", alpha = 0.3)
f.ax_joint.collections[0].set_alpha(0)


# In[36]:


f = sns.jointplot(x = df['ageAtScan1_Years'], y = df_node['mc_0'], kind="reg")
f.annotate(sp.stats.spearmanr)
# f.annotate(sp.stats.pearsonr)
f.plot_joint(plt.scatter, c = "k", s = 5, linewidth = 2, marker = ".", alpha = 0.3)
f.ax_joint.collections[0].set_alpha(0)


# In[37]:


df_node.isna().any().any()


# ## Save out

# In[38]:


# Save out
df_node.to_csv(os.path.join(os.environ['MODELDIR'], 'df_node_clean.csv'))
# df_node.to_csv(os.path.join(os.environ['MODELDIR'], 'df_node_clean_my_thresh-'+str(my_thresh)+'.csv'))

