import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import reports
from backend import audit_ledger as ledger
from backend.auth import SECRET_KEY, ALGORITHM, get_current_user
from backend.models import User as UserModel

logger = logging.getLogger("warehouse")

router = APIRouter()


@router.get("/audit/verify")
def verify_audit_ledger_integrity(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Verifies SHA-256 hash-chain integrity of the tamper-evident Trust Ledger.
    """
    res = ledger.verify_chain(db)
    from sqlalchemy import func
    from backend.models import AuditLedger
    total = db.query(func.count(AuditLedger.id)).scalar() or 0
    
    return {
        "valid": res["valid"],
        "checked_entries": res["checked"],
        "records_checked": res["checked"],
        "broken_at_entry": res["broken_at"],
        "broken_at_record": res["broken_at"],
        "total_entries": total,
        "total_records": total,
        "message": f"Audit ledger integrity verified across {res['checked']} records." if res["valid"] else f"Audit ledger integrity failure detected at record #{res['broken_at']}!",
        "integrity_status": "INTACT" if res["valid"] else "COMPROMISED"
    }


@router.get("/reports/export")
def export_report(
    request: Request,
    warehouse_id: str = "all", 
    time_range: str = "month", 
    format: str = "pdf",
    report_type: str = "stock_movement",
    db: Session = Depends(get_db)
):
    if format not in ("pdf", "csv", "xlsx"):
        raise HTTPException(400, "Invalid format. Must be pdf, csv, or xlsx.")
    if time_range not in ("day", "week", "month"):
        raise HTTPException(400, "Invalid time_range. Must be day, week, or month.")
    if report_type not in ("stock_movement", "executive", "operations", "inventory", "robots", "forecast", "anomaly", "replenishment", "simulation"):
        raise HTTPException(400, f"Invalid report_type: {report_type}")
        
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required. Send: Authorization: Bearer <token>")

    resolved_token = auth_header.split(" ")[1].strip()

    try:
        payload = jwt.decode(resolved_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        raise credentials_exception
        
    # Enforce RBAC for exports: restricted to Admin, Manager, and Auditor
    if user.role not in ("admin", "manager", "auditor"):
        raise HTTPException(status_code=403, detail="Unauthorized access: Report exporting is restricted.")

    try:
        if format == "csv":
            file_data = reports.generate_csv_report(warehouse_id, time_range, report_type)
            filename = f"{report_type}_report_{warehouse_id}_{time_range}_{datetime.now().strftime('%Y%m%d')}.csv"
            return StreamingResponse(
                file_data, 
                media_type="text/csv", 
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
        elif format == "xlsx":
            file_data = reports.generate_excel_report(warehouse_id, time_range, report_type)
            filename = f"{report_type}_report_{warehouse_id}_{time_range}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            return StreamingResponse(
                file_data, 
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
        else: # pdf
            file_data = reports.generate_pdf_report(warehouse_id, time_range, report_type)
            filename = f"{report_type}_report_{warehouse_id}_{time_range}_{datetime.now().strftime('%Y%m%d')}.pdf"
            return StreamingResponse(
                file_data, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
    except Exception as e:
        logger.error("Report export failed: %s", e, exc_info=True)
        raise HTTPException(500, "Failed to generate report: An error occurred during file compilation.")
