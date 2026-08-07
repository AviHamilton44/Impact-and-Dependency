from app.services.computation_service import calculate_tnfd_outputs

class MockSite:
    def __init__(self):
        self.geometry = {"type": "Polygon", "coordinates": [[[0,0], [0,1], [1,1], [1,0], [0,0]]]}
        self.site_id = "f7e52d43-debe-4c12-8718-5077d169beec"

class MockEncore:
    def __getattr__(self, name):
        return "VL"

class MockSonScore:
    def __init__(self, metrics=None):
        self.metrics = metrics

metrics_full = {
    "raw_metrics": {
        "Pillar1": {
            "Aridity Index": 0.8,
            "Vegetation Structure (NDVI)": 0.5,
            "Leaf Area Index (LAI)": 1.2,
            "Canopy Height Model (CHM)": 15.0,
            "Forest Landscape Integrity Index (FLII)": 0.9,
            "Trophic State Index": -0.2,
            "Algal Bloom Intensity": 0.1,
            "Water Clarity Index": 0.3,
            "Water Surface Dynamics": 0.4,
            "JRC Water Persistence": 0.6,
            "Shoreline Development Index": 0.5,
            "Riparian Complexity Index (RCI)": 0.4,
            "Habitat Health Index": 40.0,
            "Tree Cover Loss Rate": 0.05,
            "Riparian NDVI Temporal Trend": 0.1,
            "Global Human Modification": 0.2,
            "Human Disturbance Index": 0.3,
            "Light Pollution Index": 10.0,
            "KBA Overlap Area": 0.0,
            "Endemic Species Richness": 15.0,
            "Threatened Species Richness": 2.0,
            "Extinction-risk Index (CERI)": 0.05,
            "Flagship Habitat Index": 0.4,
            "Endemic Plant Richness": 5.0,
            "Threatened Plant Richness": 1.0,
            "STAR Threat Index": 0.0,
            "Ecosystem Integrity Index (EII)": 0.85,
            "Biodiversity Intactness Index (BII)": 0.75,
            "Natural Habitat Coverage": 0.8,
            "Natural Land Cover": 0.8,
            "CPLAND Connectivity": 0.8,
            "Potentially Disappeared Fraction (PDF)": 0.8
        }
    }
}

outputs_full = calculate_tnfd_outputs(MockSite(), MockEncore(), MockSonScore(metrics_full))
print("Full Site Confidence Pct:", outputs_full.get("data_quality", {}).get("confidence_pct"))
print("Full Site Confidence Label:", outputs_full.get("data_quality", {}).get("confidence"))
