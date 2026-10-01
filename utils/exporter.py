import pandas as pd
import json
from typing import List
from models.analysis_model import AnalysisModel

def export_to_csv(records: List[AnalysisModel]) -> str:
    data = [r.to_dict() for r in records]
    df = pd.DataFrame(data)
    if "json_resultado" in df.columns:
        df["json_resultado"] = df["json_resultado"].apply(lambda x: json.dumps(x, ensure_ascii=False))
    if "objetos" in df.columns:
        df["objetos"] = df["objetos"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
    if "cores" in df.columns:
        df["cores"] = df["cores"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
    
    return df.to_csv(index=False, encoding="utf-8-sig")

def export_to_json(records: List[AnalysisModel]) -> str:
    data = [r.to_dict() for r in records]
    return json.dumps(data, indent=4, ensure_ascii=False)