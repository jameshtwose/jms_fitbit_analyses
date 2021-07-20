import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from typing import Callable, Dict, Union

def apply_scaling(df: pd.DataFrame, 
                  method: Union[Callable, str] = "MinMax", 
                  kwargs: Dict = {}):
    if method == "MinMax":
        scal_df = pd.DataFrame(MinMaxScaler(**kwargs).fit_transform(df), 
             index = df.index,
            columns = df.columns)
    elif method == "Standard":
        scal_df = pd.DataFrame(StandardScaler(**kwargs).fit_transform(df), 
             index = df.index,
            columns = df.columns)
    else:
        scal_df = pd.DataFrame(method(**kwargs).fit_transform(df), 
             index = df.index,
            columns = df.columns)
    return scal_df 