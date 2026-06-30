from fastapi import APIRouter, HTTPException
from backend.database.connection import SessionLocal
from backend.database.models import CrimeIncident
from sqlalchemy import func
import collections

router = APIRouter(prefix="/api/network", tags=["Network Analysis"])

@router.get("/graph")
def get_network_graph():
    db = SessionLocal()
    try:
        # Fetch relationship between District and Crime Category
        district_crime_relations = db.query(
            CrimeIncident.district,
            CrimeIncident.crime_type,
            func.count(CrimeIncident.id).label("count")
        ).filter(
            CrimeIncident.district != None,
            CrimeIncident.crime_type != None
        ).group_by(
            CrimeIncident.district,
            CrimeIncident.crime_type
        ).all()

        # Fetch relationship between Repeat Offenders and Crime Category
        offender_crime_relations = db.query(
            CrimeIncident.repeat_offender,
            CrimeIncident.crime_type,
            func.count(CrimeIncident.id).label("count")
        ).filter(
            CrimeIncident.repeat_offender != None,
            CrimeIncident.crime_type != None
        ).group_by(
            CrimeIncident.repeat_offender,
            CrimeIncident.crime_type
        ).all()

        nodes = []
        edges = []
        node_ids = set()

        # Helper to add node safely
        def add_node(node_id, label, category, val=10):
            if node_id not in node_ids:
                nodes.append({
                    "id": node_id,
                    "label": label,
                    "category": category,
                    "value": val
                })
                node_ids.add(node_id)

        # Build connections from District to Crime Category
        for dist, crime, count in district_crime_relations:
            dist_id = f"district_{dist}"
            crime_id = f"crime_{crime}"
            
            # Base node sizing on count representation
            add_node(dist_id, dist, "District", val=20)
            add_node(crime_id, crime, "Crime Category", val=15)
            
            edges.append({
                "from": dist_id,
                "to": crime_id,
                "weight": count,
                "label": f"{count} cases"
            })

        # Build connections from Repeat Offender status to Crime Category
        for offender, crime, count in offender_crime_relations:
            if not offender:
                continue
            off_label = "Repeat Offenders" if offender.lower() in ["yes", "y", "true"] else "First-time Offenders"
            off_id = f"offender_{offender.lower()}"
            crime_id = f"crime_{crime}"
            
            add_node(off_id, off_label, "Offender Type", val=18)
            add_node(crime_id, crime, "Crime Category", val=15)
            
            edges.append({
                "from": off_id,
                "to": crime_id,
                "weight": count,
                "label": f"{count} cases"
            })

        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
