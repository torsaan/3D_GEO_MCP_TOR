from app import mcp
import geopandas as gpd
from shapely.geometry import base
import subprocess
import yaml
from datetime import datetime

@mcp.tool
def export_to_geopackage(features: dict, output_path: str) -> str:
    """
    Exports multiple layers to a single GeoPackage file.
    
    :param features: A dict where key is layer_name (e.g., 'Bygning')
                     and value is a list of [geometry, attributes] tuples.
    :param output_path: Filepath for the .gpkg file.
    :return: Success message.
    """
    # Load config to get CRS and quality rules
    with open('config/pipeline_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    crs = config['processing']['coordinate_system']
    quality_rules = config['export']
    
    for layer_name, data in features.items():
        geometries = [item[0] for item in data]
        attributes = [item[1] for item in data]
        
        gdf = gpd.GeoDataFrame(attributes, geometry=geometries, crs=crs)
        
        # Add FKB-compliant metadata
        gdf = _add_fkb_metadata(gdf, quality_rules)
        
        gdf.to_file(output_path, layer=layer_name, driver='GPKG')
        
    return f"Successfully exported {len(features)} layers to {output_path}"

def _add_fkb_metadata(gdf, quality_rules):
    """Helper to add the mandatory FKB quality attributes."""
    
    gdf['DATAFANGSTDATO'] = datetime.now().strftime('%Y%m%d')
    gdf['REGISTRERINGSVERSJON'] = '2022-01-01' # For FKB 5.0
    
    # Add ..KVALITET attributes
    gdf['DATAFANGSTMETODE'] = quality_rules['datafangstmetode']
    gdf['NØYAKTIGHET'] = quality_rules['accuracy_class'] # This should be more complex
    gdf['SYNBARHET'] = quality_rules['synbarhet']
    # ... etc. for H-NØYAKTIGHET
    
    return gdf

@mcp.tool
def convert_gpkg_to_sosi(gpkg_path: str, sosi_path: str) -> str:
    """
    Converts a GeoPackage to SOSI format using ogr2ogr.
    Requires GDAL with the FYBA (SOSI) driver installed.
    
    :param gpkg_path: Path to the input .gpkg file.
    :param sosi_path: Path for the output .sos file.
    :return: Success or error message.
    """
    cmd = [
        'ogr2ogr',
        '-f', 'SOSI',
        sosi_path,
        gpkg_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return f"Successfully converted {gpkg_path} to {sosi_path}"
    except subprocess.CalledProcessError as e:
        error_msg = f"SOSI conversion failed. Make sure GDAL and the SOSI driver are installed.\nError: {e.stderr}"
        print(error_msg)
        return error_msg
    except FileNotFoundError:
        error_msg = "Error: 'ogr2ogr' command not found. Is GDAL installed and in your system's PATH?"
        print(error_msg)
        return error_msg
    
@mcp.tool
def export_to_sosi(objects: list[dict], filename: str, utms_zone: int = 33) -> str:
    """
    Exports FKB objects to SOSI file format.
    
    :param objects: List of dicts { 'geometry': Shapely geom, 'metadata': dict with FKB keys }.
    :param filename: Output file name (writes to it).
    :param utms_zone: UTM zone for KOORDSYS.
    :return: Path to written file.
    """
    today = datetime.date.today().strftime("%Y%m%d")
    with open(filename, 'w', encoding='utf-8') as f:
        # Header
        f.write(".HODE 0:\n")
        f.write("..TEGNSETT UTF-8\n")
        f.write(f"..KOORDSYS {utms_zone}\n")  # e.g., 23 for UTM33
        f.write("..VERT-DATUM NN2000\n")
        f.write("..SOSI-VERSJON 5.0\n")
        f.write("..OBJEKTKATALOG FKBVeg 5.0.1\n")  # Adjust as needed
        
        # Objects
        for idx, obj in enumerate(objects):
            geom = obj['geometry']
            meta = obj['metadata']
            if isinstance(geom, LineString):
                f.write(f".KURVE {idx+1}:\n")
            elif isinstance(geom, base.Point):
                f.write(f".PUNKT {idx+1}:\n")
            # Add more for Polygon, etc.
            
            f.write(f"..OBJTYPE {meta.get('OBJTYPE', 'Unknown')}\n")
            f.write(f"..DATAFANGSTDATO {today}\n")
            f.write(f"..REGISTRERINGSVERSJON 2022-01-01\n")
            f.write("..KVALITET\n")
            kvalitet = meta.get('KVALITET', {'DATAFANGSTMETODE': 'byg', 'NØYAKTIGHET': 10, 'SYNBARHET': 0, 'DATAFANGSTMETODEHØYDE': 'byg', 'H-NØYAKTIGHET': 10})
            for k, v in kvalitet.items():
                f.write(f"...{k} {v}\n")
            if 'HREF' in meta:
                f.write(f"..HREF {meta['HREF']}\n")
            if 'MEDIUM' in meta:
                f.write(f"..MEDIUM {meta['MEDIUM']}\n")
            
            # Geometry coords
            coords = geom.coords
            f.write("..NØH\n")
            for coord in coords:
                f.write(f"{int(coord[1])} {int(coord[0])} {int(coord[2] if len(coord) > 2 else 0)}\n")
    
    return filename