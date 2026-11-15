"""Collect the NISAR results the website shows into ONE small file, data/processed/nisar_summary.json, and copy the comparison figure next to it.
Reads nisar_vs_sentinel1.json (compare_nisar_s1.py), nisar_confirm.json (nisar_when.py) and cache/nisar_noise_test.json (nisar_noise_test.py),
so every number on the page traces back to a script. Re-run those three first if the NISAR data change.
Usage: python export_nisar.py"""
import json, os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = f"{ROOT}/data/processed"
cmp_ = json.load(open(f"{P}/nisar_vs_sentinel1.json"))
conf = json.load(open(f"{P}/nisar_confirm.json"))
noise = json.load(open(f"{P}/cache/nisar_noise_test.json"))["variants"]
b, a = noise["iono only"], noise["+hydro+wet"]
wx, eloy = json.load(open(f"{P}/stack_willcox_128D.json")), json.load(open(f"{P}/stack_eloy_77A.json"))


def area(slug, name):
    r = conf["per_area"][slug]
    return dict(name=name, s1_rate_cm_yr=round(r["rate_cm_yr_s1"], 2), years=r["years_for_90pct_chance_of_3sigma"], date=r["confirm_by_if_no_gaps"], chance_at_one_year=r["power_at_1yr"])


out = dict(
    pattern=dict(r=cmp_["test_B_rate_pattern"]["r"], n_blocks=cmp_["test_B_rate_pattern"]["n_blocks"], r_without_bad_date=cmp_["test_B_without_sep15"]["r"]),
    weather_fix=dict(residual_before_mm=b["resid_mm"], residual_after_mm=a["resid_mm"], jump_before_mm=b["jump_sd_mm"], jump_after_mm=a["jump_sd_mm"],
                     percent=round((b["resid_mm"] - a["resid_mm"]) / b["resid_mm"] * 100)),
    sinking=dict(nisar_cm_yr=cmp_["sinking_blocks"]["nisar_minus_rest"], s1_cm_yr=cmp_["sinking_blocks"]["s1_minus_rest"], n_blocks=cmp_["sinking_blocks"]["n_blocks"]),
    playa=dict(net_cm=cmp_["playa_nisar_net_change_cm"], years=cmp_["playa_nisar_years"], s1_trend_cm_yr=cmp_["playa_s1_trend_cm_yr"], s1_last3y_cm_yr=cmp_["playa_s1_last3y_cm_yr"]),
    overlap=dict(r=cmp_["test_A_overlap_change"]["r"]),
    confirm=dict(willcox=area("willcox", "Willcox basin"), eloy=area("eloy", "Eloy"), k_sigma=conf["k_sigma"], power=conf["power"]),
    record=dict(willcox=dict(start=wx["dates"][0], end=wx["dates"][-1], dates=len(wx["dates"]), track=wx["track"]),
                eloy=dict(start=eloy["dates"][0], end=eloy["dates"][-1], dates=len(eloy["dates"]), track=eloy["track"])),
    figure="nisar_vs_sentinel1_willcox.png",
    release="NASA NISAR L2 GUNW, Provisional release (production CRID P05023)",
)
json.dump(out, open(f"{P}/nisar_summary.json", "w"), indent=1)
shutil.copyfile(f"{ROOT}/docs/nisar_vs_sentinel1_willcox.png", f"{P}/nisar_vs_sentinel1_willcox.png")
print(json.dumps(out, indent=1))
