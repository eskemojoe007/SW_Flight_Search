# %% Import Base Packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys,os
sns.set()
import win32com.client
# end%%

# %% Try to get outlook item
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
outlook.GetDefaultFolder(6).Items.GetFirst().body

# end%%
