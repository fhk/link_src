from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

base = importr("base")
tbart = importr("tbart")

pandas2ri.activate()

def solve(
        r_spatial_df_demand,
        r_spatial_df_candidates,
        p=1,
        metric=None):
    if metric is not None:
        r_assi_df = base.as_data_frame(
            tbart.allocations(
            r_spatial_df_demand,
            r_spatial_df_candidates,
            p=p,
            metric=metric)
        )
    else:
        r_assi_df = base.as_data_frame(
            tbart.allocations(
            r_spatial_df_demand,
            r_spatial_df_candidates,
            p=p)
        )

    return pandas2ri.ri2py(r_assi_df)

