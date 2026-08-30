import io
import os
import pandas as pd
from datetime import datetime, date, timedelta
from sqlalchemy import text
from backend.database import engine

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "Smart Warehouse Platform — Inventory Analytics Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer (all pages)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 36, page_text)
        self.drawString(54, 36, "Automated System Report — Cloud Warehouse Platform")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 8.5 * inch - 54, 48)

        self.restoreState()


from typing import Dict, Any

def get_report_data_by_type(report_type: str, warehouse_id: str, time_range: str) -> Dict[str, Any]:
    today = date.today()
    if time_range == "day":
        start_date = today - timedelta(days=1)
    elif time_range == "week":
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today - timedelta(days=30)

    params = {"start_date": start_date}
    wh_filter = ""
    if warehouse_id and warehouse_id != "all" and warehouse_id != "all_warehouses":
        wh_filter = " AND warehouse_id = :wh"
        params["wh"] = warehouse_id

    # Fallback to stock movements if unknown
    if report_type == "stock_movement":
        query = f"""
        SELECT m.date, m.warehouse_id, w.name as warehouse_name, m.item_id, i.name as item_name, i.category,
               m.stock_in, m.stock_out, m.closing_stock, m.entered_by
        FROM stock_movements m
        JOIN warehouses w ON m.warehouse_id = w.id
        JOIN items i ON m.item_id = i.id
        WHERE m.date >= :start_date {wh_filter.replace('warehouse_id', 'm.warehouse_id')}
        ORDER BY m.date DESC, m.id DESC
        """
        df = pd.read_sql(text(query), engine, params=params)
        return {"data": df, "title": "Stock Movement Ledger", "headers": ["Date", "Warehouse", "Item", "In (+)", "Out (-)", "Closing", "User"]}

    elif report_type == "executive":
        # Consolidated summary of orders, inventory, robots
        orders_q = f"SELECT status, COUNT(*) as count FROM orders WHERE created_at >= :start_date {wh_filter} GROUP BY status"
        df_orders = pd.read_sql(text(orders_q), engine, params=params)
        
        inv_q = f"SELECT SUM(on_hand) as total_on_hand, SUM(available) as total_available FROM inventory WHERE 1=1 {wh_filter}"
        df_inv = pd.read_sql(text(inv_q), engine, params=params)
        
        robots_q = f"SELECT COUNT(*) as count, AVG(utilization_percent) as avg_util FROM robots WHERE 1=1 {wh_filter}"
        df_robots = pd.read_sql(text(robots_q), engine, params=params)
        
        completed = df_orders[df_orders["status"] == "COMPLETED"]["count"].sum() if not df_orders.empty else 0
        pending = df_orders[df_orders["status"] == "PENDING"]["count"].sum() if not df_orders.empty else 0
        total_on_hand = df_inv["total_on_hand"].iloc[0] if not df_inv.empty else 0
        total_available = df_inv["total_available"].iloc[0] if not df_inv.empty else 0
        total_robots = df_robots["count"].iloc[0] if not df_robots.empty else 0
        avg_robot_util = df_robots["avg_util"].iloc[0] if not df_robots.empty else 0
        
        df_summary = pd.DataFrame([
            {"Metric": "Orders Completed", "Value": str(int(completed or 0)), "Unit": "orders"},
            {"Metric": "Orders Pending", "Value": str(int(pending or 0)), "Unit": "orders"},
            {"Metric": "Inventory On Hand", "Value": str(int(total_on_hand or 0)), "Unit": "units"},
            {"Metric": "Inventory Available", "Value": str(int(total_available or 0)), "Unit": "units"},
            {"Metric": "Robot Fleet Size", "Value": str(int(total_robots or 0)), "Unit": "robots"},
            {"Metric": "Avg Robot Fleet Utilization", "Value": f"{round(avg_robot_util or 0, 1)}%", "Unit": "percent"}
        ])
        return {"data": df_summary, "title": "Executive Warehouse Performance Summary", "headers": ["Metric", "Value", "Unit"]}

    elif report_type == "operations":
        # Order and task performance details
        tasks_q = f"SELECT status, task_type, COUNT(*) as count FROM tasks WHERE created_at >= :start_date {wh_filter} GROUP BY status, task_type"
        df_tasks = pd.read_sql(text(tasks_q), engine, params=params)
        if df_tasks.empty:
            df_tasks = pd.DataFrame(columns=["status", "task_type", "count"])
        return {"data": df_tasks, "title": "Operational Task Throughput Report", "headers": ["Status", "Task Type", "Count"]}

    elif report_type == "inventory":
        # SKU availability, stockouts, and abc classes
        inv_q = f"""
        SELECT i.item_id, it.name as item_name, i.warehouse_id, i.on_hand, i.available, i.reserved, COALESCE(abc.abc_class, 'C') as abc_class
        FROM inventory i
        JOIN items it ON i.item_id = it.id
        LEFT JOIN abc_classifications abc ON i.item_id = abc.item_id AND abc.source = 'wms'
        WHERE 1=1 {wh_filter.replace('warehouse_id', 'i.warehouse_id')}
        ORDER BY i.available ASC
        """
        df_inv = pd.read_sql(text(inv_q), engine, params=params)
        return {"data": df_inv, "title": "Inventory Stock Status & ABC Report", "headers": ["Item ID", "Item Name", "Warehouse ID", "On Hand", "Available", "Reserved", "ABC Class"]}

    elif report_type == "robots":
        # Fleet performance
        robots_q = f"""
        SELECT robot_code, name, status, utilization_percent, total_tasks_completed, total_distance, battery_level
        FROM robots
        WHERE 1=1 {wh_filter}
        ORDER BY total_tasks_completed DESC
        """
        df_robots = pd.read_sql(text(robots_q), engine, params=params)
        return {"data": df_robots, "title": "Robot Fleet Utilization & Performance Report", "headers": ["Robot Code", "Name", "Status", "Utilization (%)", "Tasks Completed", "Distance (cells)", "Battery (%)"]}

    elif report_type == "forecast":
        # Forecast Horizon and errors
        forecast_q = """
        SELECT r.forecast_date, r.entity as family, r.predicted_value, r.actual_value, r.error_value, r.wape_pct
        FROM forecast_results r
        JOIN forecast_runs f ON r.run_id = f.run_id
        WHERE r.forecast_date >= :start_date
        ORDER BY r.forecast_date DESC
        """
        df_fc = pd.read_sql(text(forecast_q), engine, params={"start_date": start_date})
        return {"data": df_fc, "title": "Forecast Predictions & Error Report", "headers": ["Forecast Date", "Family", "Predicted", "Actual", "Error", "WAPE (%)"]}

    elif report_type == "anomaly":
        # Flagged anomalies and exposure
        anom_q = f"""
        SELECT date, item_id, item_name, discrepancy_quantity, estimated_exposure, severity, likely_cause
        FROM shrinkage_flags
        WHERE date >= :start_date {wh_filter}
        ORDER BY date DESC
        """
        df_anom = pd.read_sql(text(anom_q), engine, params=params)
        return {"data": df_anom, "title": "Inventory Discrepancy & Shrinkage Report", "headers": ["Date", "Item ID", "Item Name", "Discrepancy", "Exposure (INR)", "Severity", "Likely Cause"]}

    elif report_type == "replenishment":
        # Recommended replenishments
        recs_q = f"""
        SELECT item_id, warehouse_id, abc_class, current_stock, safety_stock, reorder_point, recommended_qty, urgency
        FROM replenishment_recommendations
        WHERE 1=1 {wh_filter}
        ORDER BY recommended_qty DESC
        """
        df_recs = pd.read_sql(text(recs_q), engine, params=params)
        return {"data": df_recs, "title": "Replenishment Recommendations Report", "headers": ["Item ID", "Warehouse ID", "ABC Class", "Current Stock", "Safety Stock", "Reorder Point", "Recommended Qty", "Urgency"]}

    elif report_type == "simulation":
        # Simulation metrics
        sim_q = f"""
        SELECT created_at, warehouse_id, scenario_type, tick_count, total_orders, completed_orders, avg_waiting_time
        FROM digital_twin_simulations
        WHERE created_at >= :start_date {wh_filter}
        ORDER BY created_at DESC
        """
        df_sim = pd.read_sql(text(sim_q), engine, params=params)
        return {"data": df_sim, "title": "Digital Twin Simulation Metrics Report", "headers": ["Created At", "Warehouse ID", "Scenario Type", "Ticks", "Total Orders", "Completed", "Avg Waiting (ticks)"]}

    return {"data": pd.DataFrame(), "title": "Unknown Report Profile", "headers": []}


def generate_csv_report(warehouse_id: str, time_range: str, report_type: str = "stock_movement") -> io.BytesIO:
    """Generates CSV report."""
    res = get_report_data_by_type(report_type, warehouse_id, time_range)
    df = res["data"]
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output


def generate_excel_report(warehouse_id: str, time_range: str, report_type: str = "stock_movement") -> io.BytesIO:
    """Generates Excel report with an executive summary tab."""
    res = get_report_data_by_type(report_type, warehouse_id, time_range)
    df = res["data"]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=res["title"][:30])
        
        # Add summary tab
        summary_data = {
            "Analytics Indicator": [
                "Total records logged", 
                "Report type profile",
                "Warehouse filter",
                "Time window scope"
            ],
            "Value": [
                len(df),
                res["title"],
                warehouse_id,
                time_range
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, index=False, sheet_name="Executive Summary")
            
    output.seek(0)
    return output


def generate_pdf_report(warehouse_id: str, time_range: str, report_type: str = "stock_movement") -> io.BytesIO:
    """Generates PDF executive summary report using ReportLab."""
    res = get_report_data_by_type(report_type, warehouse_id, time_range)
    df = res["data"]
    output = io.BytesIO()
    
    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Corporate Colors
    PRIMARY = colors.HexColor("#0F172A")    # Deep Navy
    SECONDARY = colors.HexColor("#3B82F6")  # Blue Accent
    DARK_TEXT = colors.HexColor("#1E293B")  # Dark text
    MUTED_TEXT = colors.HexColor("#64748B") # Gray text
    CARD_BG = colors.HexColor("#F8FAFC")    # Light background card
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=SECONDARY,
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=DARK_TEXT,
        spaceAfter=6
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        textColor=colors.white
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=DARK_TEXT
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=DARK_TEXT
    )

    story = []

    # Title & Metadata Banner
    target_wh = "All Warehouses" if not warehouse_id or warehouse_id == "all" else warehouse_id
    story.append(Paragraph(res["title"], title_style))
    story.append(Paragraph(f"Interval: last {time_range} | Filtered by: {target_wh} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceAfter=12))

    # Executive Summary Card
    meta_data = [
        [
            Paragraph(f"<b>Total Records:</b> {len(df)}", table_cell_style),
            Paragraph(f"<b>Profile Class:</b> {report_type.upper()}", table_cell_style),
            Paragraph(f"<b>Reporting Status:</b> Operational", table_cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[2.3*inch, 2.5*inch, 2.2*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Records Table
    story.append(Paragraph("Report Records", h1_style))
    
    if df.empty:
        story.append(Paragraph("No records found for the selected parameters.", body_style))
    else:
        # Construct table headers dynamically
        headers_row = [Paragraph(h, table_header_style) for h in res["headers"]]
        table_data = [headers_row]
        
        # Construct table rows dynamically
        for _, row in df.iterrows():
            row_cells = []
            for col_idx, col_name in enumerate(df.columns):
                val = row[col_name]
                val_str = str(val) if val is not None else "—"
                
                # Highlight bold or format
                is_bold = col_idx == len(df.columns) - 1 or col_name in ("closing_stock", "available", "utilization_percent", "estimated_exposure")
                cell_style = table_cell_bold if is_bold else table_cell_style
                row_cells.append(Paragraph(val_str, cell_style))
            table_data.append(row_cells)
            
        # Calculate dynamic colWidths to fit page width (page width is 8.5 * inch - 108 margin = 504 pt)
        num_cols = len(res["headers"])
        col_width = (8.5 * inch - 108) / num_cols if num_cols > 0 else 100
        colWidths = [col_width] * num_cols
        
        t_feat = Table(table_data, colWidths=colWidths)
        t_feat.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY),
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, CARD_BG])
        ]))
        story.append(t_feat)

    doc.build(story, canvasmaker=NumberedCanvas)
    output.seek(0)
    return output
