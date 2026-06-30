from fastapi import APIRouter, HTTPException
from backend.database.connection import SessionLocal
from backend.database.models import CrimeIncident
from sqlalchemy import func

router = APIRouter(prefix="/api/network", tags=["Network Analysis"])

@router.get("/graph")
def get_network_graph():
    db = SessionLocal()
    try:
        # District ↔ Crime Type relationships
        district_crime = db.query(
            CrimeIncident.district,
            CrimeIncident.crime_type,
            func.count(CrimeIncident.id).label("count")
        ).filter(
            CrimeIncident.district != None,
            CrimeIncident.crime_type != None
        ).group_by(
            CrimeIncident.district,
            CrimeIncident.crime_type
        ).order_by(func.count(CrimeIncident.id).desc()).all()

        # District ↔ Offender Type relationships
        district_offender = db.query(
            CrimeIncident.district,
            CrimeIncident.repeat_offender,
            func.count(CrimeIncident.id).label("count")
        ).filter(
            CrimeIncident.district != None,
            CrimeIncident.repeat_offender != None
        ).group_by(
            CrimeIncident.district,
            CrimeIncident.repeat_offender
        ).all()

        # Crime Type ↔ Status relationships
        crime_status = db.query(
            CrimeIncident.crime_type,
            CrimeIncident.status,
            func.count(CrimeIncident.id).label("count")
        ).filter(
            CrimeIncident.crime_type != None,
            CrimeIncident.status != None
        ).group_by(
            CrimeIncident.crime_type,
            CrimeIncident.status
        ).all()

        # Build sankey source/target/value lists
        sankey_links = []
        label_set = []
        label_index = {}

        def get_label_idx(name):
            if name not in label_index:
                label_index[name] = len(label_set)
                label_set.append(name)
            return label_index[name]

        # District → Crime Type
        for dist, crime, count in district_crime[:80]:  # limit to top 80
            if dist and crime:
                sankey_links.append({
                    "source": get_label_idx(f"[District] {dist}"),
                    "target": get_label_idx(f"[Crime] {crime}"),
                    "value": int(count),
                    "layer": "district_crime"
                })

        # Crime Type → Status
        for crime, status, count in crime_status[:60]:
            if crime and status:
                sankey_links.append({
                    "source": get_label_idx(f"[Crime] {crime}"),
                    "target": get_label_idx(f"[Status] {status}"),
                    "value": int(count),
                    "layer": "crime_status"
                })

        # Crime Type heatmap data
        heatmap_data = {}
        for dist, crime, count in district_crime:
            if dist not in heatmap_data:
                heatmap_data[dist] = {}
            heatmap_data[dist][crime] = int(count)

        # Offender summary
        offender_summary = []
        for dist, offender, count in district_offender:
            if dist and offender:
                offender_summary.append({
                    "district": dist,
                    "offender_type": "Repeat" if str(offender).lower() in ["yes", "y", "true", "1"] else "First-time",
                    "count": int(count)
                })

        return {
            "sankey": {
                "labels": label_set,
                "links": sankey_links
            },
            "heatmap": heatmap_data,
            "offender_summary": offender_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
