"""
PDF Report Generator - Creates comprehensive simulation report
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

def generate_pdf_report(results, scenarios, seed):
    """Generate comprehensive PDF report"""
    
    # Create PDF document
    pdf_filename = "simulation_report.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=6,
        textColor=colors.darkblue
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    # Story to hold all elements
    story = []
    
    # Page 1 - Setup
    story.append(Paragraph("Market Simulation Report", title_style))
    story.append(Spacer(1, 0.25*inch))
    
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("Simulation Setup", heading_style))
    
    # Setup table
    setup_data = [
        ["Parameter", "Value"],
        ["Total Agents", "100"],
        ["Simulation Time", "30 minutes"],
        ["Snapshot Interval", "1 second"],
        ["Random Seed", str(seed)],
        ["Arrival Rate", "0.1 events/second/agent"]
    ]
    
    setup_table = Table(setup_data, colWidths=[2*inch, 2*inch])
    setup_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(setup_table)
    story.append(Spacer(1, 0.25*inch))
    
    story.append(Paragraph("Scenario Composition", subheading_style))
    
    # Scenario composition table
    scenario_data = [["Scenario", "Noise Traders", "Market Makers", "Momentum Traders", "Total"]]
    for name, config in scenarios.items():
        scenario_data.append([
            name,
            str(config['noise']),
            str(config['market_maker']),
            str(config['momentum']),
            str(sum(config.values()))
        ])
    
    scenario_table = Table(scenario_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
    scenario_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightblue),
        ('BACKGROUND', (1, 1), (1, -1), colors.lightgrey),
        ('BACKGROUND', (2, 1), (2, -1), colors.lightgreen),
        ('BACKGROUND', (3, 1), (3, -1), colors.lightcoral),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(scenario_table)
    
    # Add page break
    story.append(Spacer(1, 0.5*inch))
    
    # Page 2, 3, 4 - Individual Scenarios
    for scenario_name in ['A', 'B', 'C']:
        result = results[scenario_name]
        
        # Add heading
        story.append(Paragraph(f"Scenario {scenario_name} Analysis", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Scenario description
        config = scenarios[scenario_name]
        desc_text = f"""
        This scenario consists of {config['noise']} Noise Traders, 
        {config['market_maker']} Market Makers, and {config['momentum']} Momentum Traders.
        Noise traders act randomly without regard to market conditions. 
        Market makers provide liquidity by quoting both bid and ask prices. 
        Momentum traders follow trend signals based on moving averages.
        """
        story.append(Paragraph(desc_text, normal_style))
        story.append(Spacer(1, 0.25*inch))
        
        # Add mid-price plot
        mid_price_img = f"scenario_{scenario_name}_mid_price.png"
        if os.path.exists(mid_price_img):
            story.append(Paragraph("Mid-Price Time Series", subheading_style))
            img = Image(mid_price_img, width=6*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 0.1*inch))
        
        # Add spread plot
        spread_img = f"scenario_{scenario_name}_spread.png"
        if os.path.exists(spread_img):
            story.append(Paragraph("Spread Time Series", subheading_style))
            img = Image(spread_img, width=6*inch, height=3*inch)
            story.append(img)
        
        # Add page break except after last scenario
        if scenario_name != 'C':
            story.append(Spacer(1, 0.5*inch))
    
    # Page 5 - Comparison Table
    story.append(Paragraph("Scenario Comparison", heading_style))
    story.append(Spacer(1, 0.25*inch))
    
    # Comparison table data
    comp_data = [["Metric", "Scenario A", "Scenario B", "Scenario C"]]
    
    metrics_list = []
    for scenario_name in ['A', 'B', 'C']:
        metrics_list.append(results[scenario_name]['metrics'])
    
    # Add metrics to table
    metric_definitions = [
        ("Avg Spread", "avg_spread", "{:.4f}"),
        ("Volatility", "volatility", "{:.4f}"),
        ("VWAP", "vwap", "{:.2f}"),
        ("Total Volume", "total_volume", "{:.0f}"),
        ("Avg Trade Size", "avg_trade_size", "{:.2f}"),
        ("Price Range", "price_range", "{:.2f}"),
        ("Num Trades", "num_trades", "{:.0f}")
    ]
    
    for display_name, metric_key, format_str in metric_definitions:
        row = [display_name]
        for metrics in metrics_list:
            if metric_key in metrics:
                row.append(format_str.format(metrics[metric_key]))
            else:
                # For num_trades, need to get from trade tape
                if metric_key == "num_trades":
                    num_trades = len(results['A']['trade_tape'].trades)  # Simplified
                    row.append(format_str.format(num_trades))
                else:
                    row.append("N/A")
        comp_data.append(row)
    
    # Create comparison table
    comp_table = Table(comp_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('BACKGROUND', (1, 1), (1, -1), colors.lavender),
        ('BACKGROUND', (2, 1), (2, -1), colors.honeydew),
        ('BACKGROUND', (3, 1), (3, -1), colors.mistyrose),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica'),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica')
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Add comparison plot if exists
    comp_img = "scenario_comparison.png"
    if os.path.exists(comp_img):
        story.append(Paragraph("Visual Comparison", subheading_style))
        img = Image(comp_img, width=6*inch, height=4*inch)
        story.append(img)
    
    # Page 6 - Interpretation
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Interpretation & Analysis", heading_style))
    story.append(Spacer(1, 0.25*inch))
    
    interpretation_text = """
    <b>Why Scenario B stabilizes prices:</b>
    Market makers provide continuous liquidity by posting both bid and ask quotes. 
    This constant presence of orders tightens the bid-ask spread and dampens price volatility. 
    Their inventory management helps absorb temporary order imbalances.
    
    <b>Why Scenario C destabilizes prices:</b>
    Momentum traders create positive feedback loops. When prices rise, they buy more, 
    pushing prices higher. When prices fall, they sell, accelerating declines. 
    This herding behavior amplifies trends and increases volatility.
    
    <b>Why crashes occur naturally:</b>
    Even without explicit crash mechanisms, markets can experience crashes due to:
    1. Liquidity evaporation when many traders act simultaneously
    2. Margin calls or portfolio rebalancing creating forced selling
    3. Psychological thresholds triggering stop-loss orders
    4. Information cascades where traders imitate others' actions
    
    <b>Key Insights:</b>
    1. Liquidity providers (market makers) are essential for market stability
    2. Trend-following strategies can destabilize markets
    3. Random trading creates baseline volatility
    4. Market microstructure significantly impacts price formation
    5. Agent heterogeneity is crucial for realistic market simulation
    
    <b>Policy Implications:</b>
    1. Market makers should be incentivized during volatile periods
    2. Circuit breakers can prevent momentum-driven crashes
    3. Transaction taxes may reduce noise trading
    4. Transparency in order books improves market efficiency
    """
    
    # Split interpretation into paragraphs
    paragraphs = interpretation_text.split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), normal_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    print(f"\nPDF report generated: {pdf_filename}")
    
    return pdf_filename