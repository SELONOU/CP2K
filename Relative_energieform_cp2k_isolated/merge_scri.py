import pandas as pd

df1=pd.read_csv('rmse_mae_summary_2_digits_ML_vs_QM_MLMD.csv',sep=",")
df2=pd.read_csv('rmse_mae_summary_2_digits_CP2K_ML_QM.csv',sep=",")
df01 = pd.merge(df1, df2, on = 'filename')
df01.set_index('filename', inplace = True)
df01.to_csv('rmse_mae_summary_2_digits_ML_QM_MLMD_vs_QMMD.csv')
