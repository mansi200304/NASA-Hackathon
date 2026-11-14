import sys, h5py
f = h5py.File(sys.argv[1], "r")
M = f["science/LSAR/GUNW/metadata/"]
def s(x):
    v = x[()]
    return v.decode() if isinstance(v, bytes) else v
P = M["processingInformation/"]
for p in ["parameters/geocoding/azimuthIonosphericCorrectionApplied","parameters/geocoding/rangeIonosphericCorrectionApplied",
          "parameters/geocoding/hydrostaticTroposphericCorrectionApplied","parameters/geocoding/wetTroposphericCorrectionApplied",
          "algorithms/ionosphereEstimation/ionosphereAlgorithm","algorithms/ionosphereEstimation/ionosphereFilling",
          "algorithms/ionosphereEstimation/ionosphereFiltering","algorithms/ionosphereEstimation/unwrappingErrorCorrection",
          "algorithms/unwrapping/unwrappingAlgorithm","algorithms/unwrapping/costMode","algorithms/interferogramFormation/flatteningMethod",
          "algorithms/interferogramFormation/multilooking","algorithms/softwareVersion",
          "parameters/unwrappedInterferogram/frequencyA/numberOfRangeLooks","parameters/unwrappedInterferogram/frequencyA/numberOfAzimuthLooks",
          "parameters/unwrappedInterferogram/frequencyA/topographicFlatteningApplied","parameters/unwrappedInterferogram/frequencyA/ellipsoidalFlatteningApplied"]:
    print(p.split("/",1)[-1], "=", s(P[p]))
print("temporalBaseline (days):", s(M["orbit/temporalBaseline"]))
for t in ("reference","secondary"):
    print(t, "start", s(P[f"parameters/{t}/frequencyA/zeroDopplerStartTime"]))
ident = f["science/LSAR/identification"]
for k in ident: 
    try: print("id.", k, "=", s(ident[k]))
    except Exception as e: pass
