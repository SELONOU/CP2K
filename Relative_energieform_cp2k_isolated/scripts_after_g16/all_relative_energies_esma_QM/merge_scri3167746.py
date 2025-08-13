import pandas as pd

df1=pd.read_csv('mobley_3167746_nequip_450K_nvt.csv',sep=",")
df2=pd.read_csv('relative_energies_log_mobley_3167746.csv',sep=",")
df01 = pd.merge(df1, df2, on = 'frame_names')
df01.set_index('frame_names', inplace = True)
df01.to_csv('relative_energies_ML_QM_mobley_3167746.csv')
