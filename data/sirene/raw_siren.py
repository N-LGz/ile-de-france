import pandas as pd
import os
import numpy as np

"""
This stage loads the raw data from the French enterprise registry.
"""

def configure(context):
    context.config("data_path")
    context.config("siren_path", "sirene/StockUniteLegale_utf8.zip")

    context.stage("data.sirene.raw_siret")

def execute(context):
    relevant_siren = context.stage("data.sirene.raw_siret")["siren"].unique()
    df_siren = []

    with context.progress(label = "Reading SIREN ...") as progress:
        csv = pd.read_csv("%s/%s" % (context.config("data_path"), context.config("siren_path")), usecols = [
                "siren", "categorieJuridiqueUniteLegale"
            ],
            dtype = dict(siren = int, categorieJuridiqueUniteLegale = int),
            chunksize = 10240
        )

        for df_chunk in csv:
            progress.update(len(df_chunk))

            df_chunk = df_chunk[
                df_chunk["siren"].isin(relevant_siren)
            ]

            if len(df_chunk) > 0:
                df_siren.append(df_chunk)

    return pd.concat(df_siren)

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("siren_path"))):
        raise RuntimeError("SIRENE: SIREN data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("siren_path")))
