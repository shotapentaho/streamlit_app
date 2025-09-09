
import math
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, ConfigDict

from sklearn.ensemble import IsolationForest
from agent_models import ChartSpec


class DataContext(BaseModel):
    """
    Holds the active dataframe and a lightweight profile dict.
    Pydantic v2 needs arbitrary_types_allowed to accept pandas.DataFrame.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    df: pd.DataFrame = Field(repr=False)
    profile: Dict[str, Any]


# ---------------- Profiling ----------------
def build_profile(df: pd.DataFrame) -> Dict[str, Any]:
    schema = []
    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        non_null = series.notna().sum()
        nulls = int(series.isna().sum())
        unique = int(series.nunique())
        entry = {
            "name": col,
            "dtype": dtype,
            "non_null": int(non_null),
            "nulls": nulls,
            "unique": unique,
        }
        if np.issubdtype(series.dtype, np.number):
            entry.update({
                "mean": float(series.mean()) if non_null else None,
                "std": float(series.std()) if non_null else None,
                "min": float(series.min()) if non_null else None,
                "max": float(series.max()) if non_null else None,
            })
        schema.append(entry)

    return {
        "row_count": len(df),
                                                                                                                                                                                                                           1,11          Top
