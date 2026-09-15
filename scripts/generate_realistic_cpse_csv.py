#!/usr/bin/env python3
"""
Generate a realistic, comprehensive CPSE (Central Public Sector Enterprise)
material master dataset for SIH 26099 AI-Driven Standardization & Harmonization.

Includes realistic multi-CPSE industrial records across:
- ONGC (Oil and Natural Gas Corporation)
- BHEL (Bharat Heavy Electricals Limited)
- NTPC (National Thermal Power Corporation)
- SAIL (Steel Authority of India Limited)
- IOCL (Indian Oil Corporation Limited)

Features:
- Realistic ERP naming styles (verbose, abbreviated, compact hyphenated, noun-first inverted, spec-tagged)
- Standard industrial specifications (ASTM, ASME, IS, DIN, EN)
- Exact column schema matching project backend & frontend:
  source_cpse_id,source_material_id,description,unit,material_group,plant
"""

import csv
from pathlib import Path

# Canonical products with realistic cross-enterprise descriptions
CANONICAL_MATERIALS = [
    # ── 1. Pipes & Tubes (Steel / Metals) ──────────────────────────────────
    {
        "category": "Steel",
        "unit": "m",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10401", "PIPE SMLS CS ASTM A106 GR.B 2 INCH SCH 40", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21045", "Carbon Steel Seamless Pipe 2\" NB Sch-40 ASTM A106 Gr B", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40912", "CS Smls Pipe 2 Inch Sch 40 ASTM A106 Gr.B", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30118", "Pipe CS Seamless 50mm NB Schedule 40 A106 Grade B", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51203", "CS-PIPE-SMLS-2IN-SCH40-A106-GR-B", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Steel",
        "unit": "m",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10402", "Stainless Steel Pipe 10mm x 5m SS304 Seamless", "Plant_ONGC_MumbaiOffshore"),
            "cpse_bhel": ("BHEL-SAP-21046", "SS-Pipe-10mm-x-5m-SS304", "Plant_BHEL_Trichy"),
            "cpse_ntpc": ("NTPC-ERP-40913", "SS Pipe 10mm OD x 5m L Grade 304", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30119", "Pipe SS 304 10mm Dia x 5 Mtr", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51204", "STAINLESS STEEL PIPE 10MM X 5M", "Plant_IOCL_Mathura"),
        }
    },
    {
        "category": "Steel",
        "unit": "m",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10403", "SS Pipe 25mm x 6m SS316 Welded Sch 10S", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21047", "Stainless Steel Pipe 25mm x 6m Grade 316", "Plant_BHEL_Bhopal"),
            "cpse_ntpc": ("NTPC-ERP-40914", "SS-Pipe-25mm-x-6m-SS316", "Plant_NTPC_Ramagundam"),
            "cpse_sail": ("SAIL-MM-30120", "SS Pipe 25mm x 6m", "Plant_SAIL_Bokaro"),
            "cpse_iocl": ("IOCL-INV-51205", "PIPE-SS316-25MM-X-6MTR", "Plant_IOCL_Paradip"),
        }
    },
    {
        "category": "Metals",
        "unit": "m",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10404", "Copper Pipe 15mm x 6m Heavy Duty Class 1", "Plant_ONGC_Ankleshwar"),
            "cpse_bhel": ("BHEL-SAP-21048", "CU-Pipe-15mm-x-6m", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40915", "Copper Pipe 15mm x 6m", "Plant_NTPC_Korba"),
            "cpse_sail": ("SAIL-MM-30121", "CU Pipe 15mm Dia x 6 Mtr", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51206", "COPPER TUBE 15MM OD X 6M", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Steel",
        "unit": "m",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10405", "Alloy Steel Boiler Tube 50.8mm OD x 4.5mm WT SA213 T22", "Plant_ONGC_Uran"),
            "cpse_bhel": ("BHEL-SAP-21049", "TUBE AS SA213-T22 50.8OD X 4.5WT", "Plant_BHEL_Trichy"),
            "cpse_ntpc": ("NTPC-ERP-40916", "Boiler Tube Alloy Steel 50.8mm OD SA213 Gr T22", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30122", "AS Boiler Tube 50.8mm x 4.5mm SA213 T22", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51207", "TUBE-BOILER-AS-SA213T22-50.8X4.5", "Plant_IOCL_Mathura"),
        }
    },

    # ── 2. Plates & Structural Steel ───────────────────────────────────────
    {
        "category": "Steel",
        "unit": "kg",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10406", "CS-Plate-12mm", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21050", "Carbon Steel Plate 12mm IS 2062 E250 BR", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40917", "MS Plate 12mm Thk IS:2062 Grade E250", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30123", "IS 2062 E250 Mild Steel Plate 12mm", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51208", "PLATE-CS-12MM-IS2062-E250", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Steel",
        "unit": "kg",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10407", "Boiler Quality Steel Plate 25mm ASTM A516 Gr 70", "Plant_ONGC_Uran"),
            "cpse_bhel": ("BHEL-SAP-21051", "BQ Plate 25mm Thk ASTM A516 Grade 70", "Plant_BHEL_Bhopal"),
            "cpse_ntpc": ("NTPC-ERP-40918", "PLATE BQ 25MM ASTM A516 GR 70", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30124", "Carbon Steel Boiler Plate 25mm A516 Gr 70", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51209", "PLATE-BQ-25MM-A516GR70", "Plant_IOCL_Paradip"),
        }
    },
    {
        "category": "Metals",
        "unit": "kg",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10408", "Aluminum Sheet 2mm x 1m x 2m", "Plant_ONGC_MumbaiOffshore"),
            "cpse_bhel": ("BHEL-SAP-21052", "AL-Sheet-2mm-x-1m-x-2m", "Plant_BHEL_Hyderabad"),
            "cpse_ntpc": ("NTPC-ERP-40919", "AL Sheet 2mm x 1000mm x 2000mm Alloy 6061", "Plant_NTPC_Ramagundam"),
            "cpse_sail": ("SAIL-MM-30125", "Aluminum Alloy Sheet 2mm x 1m x 2m", "Plant_SAIL_Bokaro"),
            "cpse_iocl": ("IOCL-INV-51210", "SHEET-AL-2MM-1MX2M", "Plant_IOCL_Mathura"),
        }
    },
    {
        "category": "Steel",
        "unit": "kg",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10409", "Stainless Steel Sheet 2mm x 1.25m x 2.5m SS304 2B", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21053", "SS-Sheet-2mm-x-1.25m-x-2.5m-SS304", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40920", "SS Sheet 2mm Thk Grade 304 2B Finish", "Plant_NTPC_Korba"),
            "cpse_sail": ("SAIL-MM-30126", "Sheet SS 304 2mm x 1250mm x 2500mm", "Plant_SAIL_Durgapur"),
            "cpse_iocl": ("IOCL-INV-51211", "STAINLESS STEEL SHEET 2MM SS304", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Steel",
        "unit": "m",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10410", "TMT Rebar 16mm Fe 500D IS 1786 12m Length", "Plant_ONGC_Ankleshwar"),
            "cpse_bhel": ("BHEL-SAP-21054", "TMT Bar 16mm Dia Fe-500D", "Plant_BHEL_Bhopal"),
            "cpse_ntpc": ("NTPC-ERP-40921", "Steel Reinforcement Bar 16mm Fe 500D", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30127", "SAIL TMT 16mm Fe 500D Bar", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51212", "REBAR-TMT-16MM-FE500D", "Plant_IOCL_Mathura"),
        }
    },

    # ── 3. Fasteners ───────────────────────────────────────────────────────
    {
        "category": "Fasteners",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10411", "Hex Bolt M10x50 Gr 8.8", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21055", "Hex-Bolt-M10x50-Gr-8.8", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40922", "Hex Bolt M10 x 50mm Grade 8.8 IS 1364", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30128", "Bolt Hex Head M10x50 Gr 8.8 HT Zinc Plated", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51213", "HEX-BOLT-M10X50-GRADE-8.8", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Fasteners",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10412", "Hex Bolt M12x60 Gr 10.9", "Plant_ONGC_MumbaiOffshore"),
            "cpse_bhel": ("BHEL-SAP-21056", "Hex Bolt M12x60 Grade 10.9", "Plant_BHEL_Trichy"),
            "cpse_ntpc": ("NTPC-ERP-40923", "Hex-Bolt-M12x60-Gr-10.9", "Plant_NTPC_Ramagundam"),
            "cpse_sail": ("SAIL-MM-30129", "HT Hex Bolt M12 x 60 Grade 10.9 IS 1364", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51214", "BOLT-HEX-M12X60-GR10.9", "Plant_IOCL_Paradip"),
        }
    },
    {
        "category": "Fasteners",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10413", "Stud Bolt 3/4\" x 110mm ASTM A193 B7 with 2 Nuts A194 2H", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21057", "Stud Bolt 3/4in x 110mm Gr B7 w/ 2H Nuts", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40924", "STUD-BOLT-3/4X110-A193-B7-2H", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30130", "Alloy Steel Stud Bolt 3/4\" x 110mm B7/2H", "Plant_SAIL_Bokaro"),
            "cpse_iocl": ("IOCL-INV-51215", "STUD BOLT WITH NUTS 3/4 INCH X 110MM ASTM A193 B7", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Fasteners",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10414", "Hex Nut M10", "Plant_ONGC_Ankleshwar"),
            "cpse_bhel": ("BHEL-SAP-21058", "Hex Nut M10 Grade 8 IS 1364", "Plant_BHEL_Hyderabad"),
            "cpse_ntpc": ("NTPC-ERP-40925", "Hex-Nut-M10-Gr-8", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30131", "Nut Hex M10 Grade 8 Zinc Coated", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51216", "HEX NUT M10 IS1364", "Plant_IOCL_Mathura"),
        }
    },
    {
        "category": "Fasteners",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10415", "Spring Washer M10", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21059", "Spring-Washer-M10", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40926", "Spring Washer M10 Spring Steel IS 3063", "Plant_NTPC_Korba"),
            "cpse_sail": ("SAIL-MM-30132", "Washer Spring M10 DIN 127 Type B", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51217", "WASHER-SPRING-M10", "Plant_IOCL_Panipat"),
        }
    },

    # ── 4. Electrical & Switchgear ─────────────────────────────────────────
    {
        "category": "Electrical",
        "unit": "m",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10416", "Copper Cable 2.5mm2 3-core", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21060", "CU-Cable-2.5mm2-3-core", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40927", "CU Cable 2.5mm2 3-core Armoured 1.1kV", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30133", "Cable Cu XLPE 3 Core 2.5 sq mm Armored IS 7098", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51218", "CABLE-CU-2.5SQMM-3C-ARMOURED-1100V", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Electrical",
        "unit": "m",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10417", "XLPE ARMOURED CU CABLE 3.5 CORE X 120 SQMM 1.1KV", "Plant_ONGC_MumbaiOffshore"),
            "cpse_bhel": ("BHEL-SAP-21061", "Power Cable Cu XLPE/SWA/PVC 3.5C x 120 sq.mm", "Plant_BHEL_Bhopal"),
            "cpse_ntpc": ("NTPC-ERP-40928", "1.1KV 3.5Cx120 SQ.MM ARMORED COPPER POWER CABLE", "Plant_NTPC_Ramagundam"),
            "cpse_sail": ("SAIL-MM-30134", "Copper Armoured Cable 3.5C x 120mm2 IS 7098-1", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51219", "CABLE-XLPE-CU-3.5CX120-1.1KV", "Plant_IOCL_Paradip"),
        }
    },
    {
        "category": "Electrical",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10418", "MCB 32A 3-pole C-curve", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21062", "Miniature Circuit Breaker MCB 32A 3P C-Curve 10kA", "Plant_BHEL_Trichy"),
            "cpse_ntpc": ("NTPC-ERP-40929", "MCB 32A TP C-Curve 10kA IS/IEC 60898", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30135", "Circuit Breaker MCB 32A 3 Pole C-Curve", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51220", "MCB-32A-3P-C-CURVE-10KA", "Plant_IOCL_Mathura"),
        }
    },
    {
        "category": "Electrical",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10419", "Molded Case Circuit Breaker MCCB 250A 4 Pole 36kA", "Plant_ONGC_Uran"),
            "cpse_bhel": ("BHEL-SAP-21063", "MCCB 250A 4P 36kA Thermal Magnetic", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40930", "Circuit Breaker MCCB 250A 4-Pole 36kA Ics=Icu", "Plant_NTPC_Korba"),
            "cpse_sail": ("SAIL-MM-30136", "MCCB 250 Amp 4 Pole 36 kA Breaking Capacity", "Plant_SAIL_Durgapur"),
            "cpse_iocl": ("IOCL-INV-51221", "MCCB-250A-4POLE-36KA", "Plant_IOCL_Panipat"),
        }
    },

    # ── 5. Mechanical Spares & Seals ───────────────────────────────────────
    {
        "category": "Mechanical",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10420", "Ball Bearing 6205 25x52x15", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21064", "Deep Groove Ball Bearing 6205-2RS SKF", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40931", "Bearing Ball 6205-2RS1/C3 25x52x15mm", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30137", "Ball Bearing 6205 2RS C3", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51222", "BEARING-BALL-6205-2RS-C3", "Plant_IOCL_Mathura"),
        }
    },
    {
        "category": "Mechanical",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10421", "DEEP GROOVE BALL BEARING 6308 2RS C3 SKF", "Plant_ONGC_MumbaiOffshore"),
            "cpse_bhel": ("BHEL-SAP-21065", "Ball Bearing 6308-2RS1/C3 40x90x23mm", "Plant_BHEL_Bhopal"),
            "cpse_ntpc": ("NTPC-ERP-40932", "BRG BALL 6308-2RS-C3", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30138", "Deep Groove Ball Bearing 6308 2RS", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51223", "BEARING-6308-2RS-C3-40X90X23", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Mechanical",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10422", "O-Ring NBR 50mm ID", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21066", "Nitrile Rubber O-Ring 50mm ID x 3.5mm C/S", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40933", "O-Ring NBR 70 Shore 50x3.5mm", "Plant_NTPC_Ramagundam"),
            "cpse_sail": ("SAIL-MM-30139", "Seal O-Ring Nitrile 50mm ID", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51224", "O-RING-NBR-50MM-ID-3.5MM-CS", "Plant_IOCL_Paradip"),
        }
    },
    {
        "category": "Mechanical",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10423", "SWG Gasket 3\" Class 300 SS316L Flexible Graphite", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21067", "SPIRAL WOUND GASKET 3 INCH 300 LB SS316 GRAFOIL", "Plant_BHEL_Trichy"),
            "cpse_ntpc": ("NTPC-ERP-40934", "GASKET-SWG-3IN-300#-SS316-GRAPHITE", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30140", "Spiral Wound Gasket 3\" 300# ASME B16.20 SS316/Graphite", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51225", "Gasket Spiral Wound 3 Inch 300 Lbs SS 316 Filler Graphite", "Plant_IOCL_Panipat"),
        }
    },

    # ── 6. Industrial Valves & Pipe Fittings ───────────────────────────────
    {
        "category": "Valves",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10424", "Gate Valve 2 Inch Class 150 Flanged ASTM A216 WCB", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21068", "Cast Steel Gate Valve 2\" 150# Flanged WCB", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40935", "GATE-VALVE-CS-2IN-150#-FLANGED-A216WCB", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30141", "Valve Gate Cast Steel 50mm NB 150# Flanged End", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51226", "GATE VALVE 2 INCH 150 LB WCB FLANGED", "Plant_IOCL_Mathura"),
        }
    },
    {
        "category": "Valves",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10425", "Ball Valve 1 Inch 3-Piece SS316 800# Screwed NPT", "Plant_ONGC_Uran"),
            "cpse_bhel": ("BHEL-SAP-21069", "Stainless Steel Ball Valve 1\" 3-PC Full Bore SS316", "Plant_BHEL_Bhopal"),
            "cpse_ntpc": ("NTPC-ERP-40936", "BALL-VALVE-1IN-3PC-SS316-800#", "Plant_NTPC_Korba"),
            "cpse_sail": ("SAIL-MM-30142", "Valve Ball SS 316 25mm NB 3-Piece Screwed", "Plant_SAIL_Bokaro"),
            "cpse_iocl": ("IOCL-INV-51227", "SS316 BALL VALVE 1 INCH 800 LBS NPT", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Fittings",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10426", "Forged CS 90 Deg Elbow 2 Inch Sch 40 ASTM A105 BW", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21070", "Elbow 90 Deg 2\" NB Butt Weld Sch-40 A105", "Plant_BHEL_Trichy"),
            "cpse_ntpc": ("NTPC-ERP-40937", "CS Pipe Fitting Elbow 90D 2in Sch 40 ASTM A105", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30143", "ELBOW-90DEG-2IN-SCH40-A105-BW", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51228", "PIPE FITTING CS ELBOW 90 DEG 2 INCH SCH 40", "Plant_IOCL_Paradip"),
        }
    },

    # ── 7. Safety PPE ──────────────────────────────────────────────────────
    {
        "category": "Safety",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10427", "Safety Helmet White EN397", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21071", "Industrial Safety Helmet White HDPE IS 2925", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40938", "SAFETY-HELMET-WHITE-IS2925-EN397", "Plant_NTPC_Ramagundam"),
            "cpse_sail": ("SAIL-MM-30144", "Helmet Industrial Safety White Ratchet Type IS:2925", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51229", "SAFETY HELMET WHITE HDPE EN 397", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Safety",
        "unit": "pair",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10428", "Safety Gloves Cut-resistant EN388", "Plant_ONGC_MumbaiOffshore"),
            "cpse_bhel": ("BHEL-SAP-21072", "Cut Resistant Safety Hand Gloves Level 5 EN 388", "Plant_BHEL_Hyderabad"),
            "cpse_ntpc": ("NTPC-ERP-40939", "GLOVE-SAFETY-CUT-RESISTANT-EN388-L5", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30145", "Hand Gloves Cut Resistant Level 5 Nitrile Coated", "Plant_SAIL_Durgapur"),
            "cpse_iocl": ("IOCL-INV-51230", "SAFETY GLOVES CUT RESISTANT LEVEL 5", "Plant_IOCL_Mathura"),
        }
    },
    {
        "category": "Safety",
        "unit": "pair",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10429", "Leather Safety Shoes Steel Toe Cap IS 15298 Size 9", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21073", "Safety Shoes Steel Toe S3 IS:15298 Size 9", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40940", "SAFETY-SHOES-STEEL-TOE-SIZE-9-IS15298", "Plant_NTPC_Vindhyachal"),
            "cpse_sail": ("SAIL-MM-30146", "Industrial Safety Shoe Leather with Steel Toe Size 9", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51231", "SAFETY BOOT LEATHER STEEL TOE SIZE 9", "Plant_IOCL_Panipat"),
        }
    },

    # ── 8. Chemicals, Lubricants & Consumables ─────────────────────────────
    {
        "category": "Chemicals",
        "unit": "l",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10430", "Lubricating Oil ISO VG 68 20L", "Plant_ONGC_Ankleshwar"),
            "cpse_bhel": ("BHEL-SAP-21074", "Industrial Hydraulic Oil ISO VG 68 Pail 20L", "Plant_BHEL_Bhopal"),
            "cpse_ntpc": ("NTPC-ERP-40941", "LUBE-OIL-ISO-VG-68-20LTR", "Plant_NTPC_Korba"),
            "cpse_sail": ("SAIL-MM-30147", "Hydraulic Lubricating Oil Grade ISO VG 68", "Plant_SAIL_Rourkela"),
            "cpse_iocl": ("IOCL-INV-51232", "SERVO SYSTEM 68 HYDRAULIC OIL 20 LTR", "Plant_IOCL_Mathura"),
        }
    },
    {
        "category": "Chemicals",
        "unit": "pc",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10431", "Threadlocker Blue 50ml", "Plant_ONGC_Hazira"),
            "cpse_bhel": ("BHEL-SAP-21075", "Anaerobic Threadlocker Medium Strength Blue 50ml", "Plant_BHEL_Haridwar"),
            "cpse_ntpc": ("NTPC-ERP-40942", "Threadlocker Adhesive Blue 50ml Bottle Loctite 243", "Plant_NTPC_Dadri"),
            "cpse_sail": ("SAIL-MM-30148", "THREADLOCKER-BLUE-50ML-LOCTITE-243", "Plant_SAIL_Bhilai"),
            "cpse_iocl": ("IOCL-INV-51233", "SEALANT THREADLOCKER BLUE 50ML MEDIUM STRENGTH", "Plant_IOCL_Panipat"),
        }
    },
    {
        "category": "Chemicals",
        "unit": "kg",
        "variants": {
            "cpse_ongc": ("ONGC-MM-10432", "High Temperature Lithium Grease NLGI 2 18kg", "Plant_ONGC_MumbaiOffshore"),
            "cpse_bhel": ("BHEL-SAP-21076", "Industrial Bearing Grease Lithium Base NLGI-2 Pail 18kg", "Plant_BHEL_Trichy"),
            "cpse_ntpc": ("NTPC-ERP-40943", "LITHIUM-GREASE-NLGI-2-18KG-PAIL", "Plant_NTPC_Ramagundam"),
            "cpse_sail": ("SAIL-MM-30149", "Grease Multi Purpose Lithium Complex EP-2 18kg", "Plant_SAIL_Bokaro"),
            "cpse_iocl": ("IOCL-INV-51234", "SERVO GEM EP 2 LITHIUM GREASE 18 KG", "Plant_IOCL_Paradip"),
        }
    },
]


def generate_records():
    rows = []
    # Collect all records grouped by CPSE so it mimics real multi-enterprise consolidation
    cpse_order = ["cpse_ongc", "cpse_bhel", "cpse_ntpc", "cpse_sail", "cpse_iocl"]

    for cpse in cpse_order:
        for item in CANONICAL_MATERIALS:
            mat_id, desc, plant = item["variants"][cpse]
            rows.append({
                "source_cpse_id": cpse,
                "source_material_id": mat_id,
                "description": desc,
                "unit": item["unit"],
                "material_group": item["category"],
                "plant": plant,
            })
    return rows


def write_csv(output_path: Path, rows: list):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["source_cpse_id", "source_material_id", "description", "unit", "material_group", "plant"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Successfully generated {len(rows)} records at: {output_path}")


if __name__ == "__main__":
    records = generate_records()
    
    # Write to root project folder for instant upload
    root_csv = Path(r"e:\Projects\SIH 26\cpse_materials_realistic_upload.csv")
    write_csv(root_csv, records)

    # Also write to data/ as cpse_master_materials.csv
    data_csv = Path(r"e:\Projects\SIH 26\data\cpse_master_materials.csv")
    write_csv(data_csv, records)
