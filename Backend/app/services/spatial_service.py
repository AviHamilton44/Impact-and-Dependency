import zipfile
import io
import json
from fastkml import kml
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, Point
from typing import Dict, Any, Tuple, Optional

def parse_kml_geometry(content: bytes) -> Tuple[Optional[Dict[str, Any]], Tuple[float, float]]:
    """
    Parses KML content and returns (GeoJSON geometry, (lat, lng) centroid).
    """
    try:
        # Pass bytes directly to handle XML encoding declarations
        # In fastkml 1.0+, from_string is a classmethod returning the parsed instance.
        k = kml.KML.from_string(content)
        
        # Robust features retrieval (fastkml versions vary between list property and generator method)
        features = k.features
        if callable(features):
            features = list(features())
        else:
            features = list(features)
            
        if not features:
            print("No features found in KML")
            return None, (0.0, 0.0)
            
        # Recursive function to drill down into Document/Folder/Placemark
        def get_geometries(feat_list):
            geoms = []
            for f in feat_list:
                if hasattr(f, 'geometry') and f.geometry:
                    geoms.append(f.geometry)
                # Check for nested features (Folders, Documents)
                if hasattr(f, 'features'):
                    sub_feats = f.features
                    if callable(sub_feats):
                        sub_feats = sub_feats()
                    geoms.extend(get_geometries(list(sub_feats)))
            return geoms

        geometries = get_geometries(features)
        if not geometries:
            print("No geometries found in KML features")
            return None, (0.0, 0.0)

        # Take the first valid geometry (MVP simplification)
        g = geometries[0]
        s_geom = shape(g)
        centroid = s_geom.centroid
        
        return mapping(s_geom), (centroid.y, centroid.x)
    except Exception as e:
        print(f"KML parsing error: {e}")
        import traceback
        traceback.print_exc()
        return None, (0.0, 0.0)

def process_kmz_to_geojson(kmz_content: bytes) -> Tuple[Optional[Dict[str, Any]], Tuple[float, float]]:
    """
    Unzips KMZ and parses the primary doc.kml file.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(kmz_content)) as z:
            # Look for doc.kml or any .kml file
            kml_names = [name for name in z.namelist() if name.lower().endswith('.kml')]
            if not kml_names:
                print("No KML file found inside KMZ")
                return None, (0.0, 0.0)
            
            # Prioritize doc.kml if it exists
            kml_file = 'doc.kml' if 'doc.kml' in kml_names else kml_names[0]
            kml_content = z.read(kml_file)
            return parse_kml_geometry(kml_content)
    except Exception as e:
        print(f"KMZ processing error: {e}")
        import traceback
        traceback.print_exc()
        return None, (0.0, 0.0)
