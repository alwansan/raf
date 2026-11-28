"""Independent RGBA endpoint basis and per-source-site sample controls.

All ten constant BC3 textures are authored diagnostics, not original content.
A missing site, incorrect calibration or absent pair cannot prove insensitivity.
"""
import numpy as np
from tools.gt_top_resource_closure import selected_array_causal as c

MASKS=(0,15,1,2,4,8,14,13,11,7)
CHANNELS=("red","green","blue","alpha")

def color(mask):
    c.need(type(mask) is int and mask in MASKS,"basis_mask")
    return tuple(float(bool(mask & (1<<i))) for i in range(4))

def output_diff(a,b):
    c.need(a.shape==b.shape and a.ndim==3 and a.shape[-1]==4 and
           np.isfinite(a).all() and np.isfinite(b).all(),"basis_output_schema")
    delta=np.abs(a-b)
    return dict(rgba=int(np.count_nonzero(np.max(delta,axis=-1)>1/255)),
                rgb=int(np.count_nonzero(np.max(delta[...,:3],axis=-1)>1/255)),
                alpha=int(np.count_nonzero(delta[...,3]>1/255)),
                exact_rgba=int(np.count_nonzero(np.max(delta,axis=-1)>0)))

def summarize(final,calibration,sites):
    c.need(set(final)==set(calibration)==set(MASKS) and 1<=len(sites)<=8,"basis_population")
    masks={m:c.near(calibration[m],c.CAL) for m in MASKS}
    counts={str(m):int(a.sum()) for m,a in masks.items()}
    site_rows=[];all_ok=all(v>0 for v in counts.values());active_sites=0
    for i,row in enumerate(sites):
        c.need(set(row)==set(MASKS),"basis_site_population")
        hits={};obs={}
        for m in MASKS:
            marker,value=row[m]
            cal=masks[m]
            c.need(marker.shape==value.shape==calibration[m].shape==final[m].shape and
                   np.isfinite(marker).all() and np.isfinite(value).all(),"basis_site_pixel_schema")
            hit=c.near(marker,c.HIT)&cal;miss=c.near(marker,c.MISS)&cal
            covered=hit|miss
            good=c.near(value,color(m))&hit
            missing_value=c.near(value,c.MISS)&miss
            n=int(hit.sum())
            verified=(int(covered.sum())==int(cal.sum()) and int(good.sum())==n and
                      int(missing_value.sum())==int(miss.sum()) and not (c.near(marker,c.HIT)&~cal).any())
            all_ok &= verified
            hits[m]=hit
            obs[str(m)]=dict(hit_pixels=n,miss_pixels=int(miss.sum()),calibrated=bool(verified),
                             expected_sample_pixels=int(good.sum()))
        observed=any(x.any() for x in hits.values())
        active_sites+=int(observed)
        pairs={}
        for k,name in enumerate(CHANNELS):
            pairs[name]=[int((hits[0]&hits[1<<k]).sum()),int((hits[15]&hits[15^(1<<k)]).sum())]
        site_rows.append(dict(index=i,observed=bool(observed),controls=obs,paired_hit_pixels=pairs))
    pair_rows={}
    for i,name in enumerate(CHANNELS):
        lo=(0,1<<i);hi=(15,15^(1<<i))
        pair_rows[name]=[dict(endpoint="low" if k==0 else "high",**output_diff(final[a],final[b]),
                         shared_hit_sites=sum(x["paired_hit_pixels"][name][k]>0 for x in site_rows))
                         for k,(a,b) in enumerate((lo,hi))]
    all_pairs=all(x["shared_hit_sites"]>0 for rows in pair_rows.values() for x in rows)
    return dict(calibration_pixels=counts,sites=site_rows,observed_sites=active_sites,
                all_calibration_controls_match=bool(all_ok),all_channel_pairs_have_shared_sample_hits=all_pairs,
                calibrated=bool(all_ok and active_sites>0 and all_pairs),pairs=pair_rows)

def classify(rows,expected_sites):
    c.need(type(expected_sites) is int and 1<=expected_sites<=8 and len(rows)==3
           and all(len(x["sites"])==expected_sites for x in rows),"basis_view_coverage")
    good=[x for x in rows if x["calibrated"]]
    responsive={name:sum(any(p["rgba"]>0 for p in x["pairs"][name]) for x in good) for name in CHANNELS}
    rgb={name:sum(any(p["rgb"]>0 for p in x["pairs"][name]) for x in good) for name in CHANNELS}
    coverage=[sum(x["sites"][i]["observed"] for x in good) for i in range(expected_sites)]
    verified=len(good)==3 and all(v>0 for v in coverage)
    return dict(status=("OBSERVED_RGBA_ENDPOINT_BASIS" if verified else "INCONCLUSIVE_RGBA_ENDPOINT_BASIS"),
                calibrated_views=len(good),source_sample_sites=expected_sites,site_observed_views=coverage,
                rgba_responsive_views=responsive,rgb_responsive_views=rgb,
                no_endpoint_response_in_test_views=verified and not any(responsive.values()),
                original_game_global_resources_verified=False,white_mesh_repair_verified=False,diagnostic_only=True)
