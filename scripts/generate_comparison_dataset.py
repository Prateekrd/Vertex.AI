#!/usr/bin/env python3
"""
Generate a distinct, benchmark comparison dataset (Dataset 2) for SIH 26099
AI-Driven Material Master Harmonization across CPSEs.

Focus:
- Different CPSE Mix: GAIL (Gas Authority of India), CIL (Coal India Limited),
  PGCIL (Power Grid Corporation), BPCL (Bharat Petroleum), BHEL (Bharat Heavy Electricals)
- New Industrial Categories & Materials:
  * Rotating Equipment & Motors (Induction Motors, Submersible Pumps)
  * Heavy Piping Flanges & Fittings (Weld Neck Flanges, Equal Tees)
  * High-Spec Protective Coatings & Industrial Paints (Epoxy Primer, Polyurethane Paint)
  * Thermal Insulation & Lagging (Rockwool Insulation Blankets, Ceramic Fiber)
  * High-Voltage Switchgear & Transformers (Current Transformers, Vacuum Circuit Breakers)
  * Heavy Fasteners & Lock Nuts (Nyloc Lock Nuts, High Tensile Studs)
  * Process Instrumentation & Valves (Globe Valves, Check Valves, Strainers)
- Tests: Cross-enterprise duplicate clusters, intra-plant variations, and unique items.

Schema:
source_cpse_id,source_material_id,description,unit,material_group,plant
"""

import csv
from pathlib import Path

DATASET_2_MATERIALS = [
    # ── 1. Motors & Rotating Equipment ─────────────────────────────────────
    {
        "category": "Electrical",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60101", "3-Phase Squirrel Cage Induction Motor 15kW 4-Pole 415V IE3", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81001", "Induction Motor 15 kW 4 Pole 415 Volt Foot Mounted IE3", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30501", "AC Induction Motor 15KW 4P 415V 50Hz B3 Frame", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92001", "MOTOR-AC-INDUCTION-15KW-4P-415V-IE3", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44101", "3-PH AC SQUIRREL CAGE INDUCTION MOTOR 15 KW 1450 RPM", "Plant_BHEL_Bhopal"),
        }
    },
    {
        "category": "Electrical",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60102", "Flameproof Induction Motor 7.5kW 2-Pole Zone 1 Gas Group IIA/IIB", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81002", "FLP Motor 7.5kW 2P 415V Flame Proof Ex-d", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30502", "Flameproof AC Motor 7.5 kW 2900 RPM Foot Mounted", "Plant_PGCIL_Agra"),
            "cpse_bpcl": ("BPCL-SAP-92002", "MOTOR-FLP-7.5KW-2POLE-EXD-ZONE1", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44102", "FLAMEPROOF SQUIRREL CAGE MOTOR 7.5KW 2P 415V", "Plant_BHEL_Haridwar"),
        }
    },

    # ── 2. Heavy Piping Flanges & Fittings ─────────────────────────────────
    {
        "category": "Fittings",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60103", "Weld Neck Flange 4 Inch Class 300 Sch 40 ASTM A105 WNRF", "Plant_GAIL_Dabhol"),
            "cpse_cil": ("CIL-MM-81003", "WNRF Flange 4\" 300# Sch-40 Forged CS A105", "Plant_CIL_Nagpur"),
            "cpse_pgcil": ("PGCIL-EQ-30503", "FLANGE-WNRF-4IN-300LB-SCH40-A105", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92003", "CS Forged Weld Neck Flange 100mm NB 300 LBS ASME B16.5", "Plant_BPCL_Bina"),
            "cpse_bhel": ("BHEL-IND-44103", "PIPE FLANGE WNRF 4 INCH 300 LB ASTM A105 SCH 40", "Plant_BHEL_Trichy"),
        }
    },
    {
        "category": "Fittings",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60104", "Equal Tee 3 Inch Sch 40 Butt Weld ASTM A234 WPB", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81004", "Pipe Fitting Equal Tee 3\" NB Schedule 40 BW CS", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30504", "TEE-EQUAL-3IN-SCH40-A234WPB-BW", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92004", "Carbon Steel Equal Tee 80mm NB Sch 40 A234 Gr WPB", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44104", "BUTT WELD EQUAL TEE 3 INCH SCH 40 ASTM A234 WPB", "Plant_BHEL_Haridwar"),
        }
    },
    {
        "category": "Fittings",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60105", "Blind Flange 6 Inch Class 150 Raised Face ASTM A105", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81005", "Blind Flange 6\" 150# RF Forged Carbon Steel", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30505", "BLIND-FLANGE-6IN-150LB-RF-A105", "Plant_PGCIL_Agra"),
            "cpse_bpcl": ("BPCL-SAP-92005", "Flange Blind 150mm NB 150 Lbs RF ASME B16.5 A105", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44105", "FORGED STEEL BLIND FLANGE 6 INCH 150 LB RF", "Plant_BHEL_Bhopal"),
        }
    },

    # ── 3. High-Spec Industrial Valves ─────────────────────────────────────
    {
        "category": "Valves",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60106", "Globe Valve 3 Inch Class 300 Flanged End ASTM A216 WCB", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81006", "Cast Steel Globe Valve 3\" 300# Flanged OS&Y A216 WCB", "Plant_CIL_Nagpur"),
            "cpse_pgcil": ("PGCIL-EQ-30506", "GLOBE-VALVE-CS-3IN-300#-FLANGED-WCB", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92006", "Valve Globe 80mm NB 300 LBS Flanged Body WCB", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44106", "GLOBE VALVE 3 INCH 300 LB WCB FLANGED OS AND Y", "Plant_BHEL_Trichy"),
        }
    },
    {
        "category": "Valves",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60107", "Dual Plate Check Valve 4 Inch Class 150 Wafer Type Body WCB", "Plant_GAIL_Dabhol"),
            "cpse_cil": ("CIL-MM-81007", "NRV Check Valve Dual Plate 4\" 150# Wafer A216 WCB", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30507", "VALVE-CHECK-DUAL-PLATE-4IN-150#-WAFER", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92007", "Non Return Valve Dual Plate 100mm NB 150# Wafer WCB", "Plant_BPCL_Bina"),
            "cpse_bhel": ("BHEL-IND-44107", "DUAL PLATE CHECK VALVE 4 INCH 150 LB WAFER TYPE", "Plant_BHEL_Haridwar"),
        }
    },

    # ── 4. High-Performance Paints & Industrial Coatings ───────────────────
    {
        "category": "Coatings",
        "unit": "l",
        "variants": {
            "cpse_gail": ("GAIL-M-60108", "Epoxy Zinc Rich Primer Two Pack Paint 20L Drum", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81008", "Two Pack Epoxy Zinc Rich Primer Paint Pail 20 Ltr", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30508", "PAINT-EPOXY-ZINC-RICH-PRIMER-20L", "Plant_PGCIL_Agra"),
            "cpse_bpcl": ("BPCL-SAP-92008", "Zinc Rich Epoxy Primer Coating 2-Component 20 Liter", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44108", "EPOXY ZINC RICH PRIMER PAINT 20 LITRES TWO PACK", "Plant_BHEL_Bhopal"),
        }
    },
    {
        "category": "Coatings",
        "unit": "l",
        "variants": {
            "cpse_gail": ("GAIL-M-60109", "Polyurethane Finish Enamel Paint Signal Red 20L", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81009", "PU Finish Enamel Paint Glossy Signal Red 20 Ltrs", "Plant_CIL_Nagpur"),
            "cpse_pgcil": ("PGCIL-EQ-30509", "PAINT-PU-ENAMEL-SIGNAL-RED-20LTR", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92009", "Aliphatic Polyurethane Topcoat Paint Red RAL 3001 20L", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44109", "POLYURETHANE ENAMEL PAINT SIGNAL RED 20 LTR", "Plant_BHEL_Trichy"),
        }
    },

    # ── 5. Thermal & Acoustic Insulation ───────────────────────────────────
    {
        "category": "Insulation",
        "unit": "m",
        "variants": {
            "cpse_gail": ("GAIL-M-60110", "Rockwool Insulation Mattress Density 100 kg/m3 50mm Thk Wire Mesh", "Plant_GAIL_Dabhol"),
            "cpse_cil": ("CIL-MM-81010", "Mineral Rockwool Blanket 50mm Thk 100 kg/m3 with GI Wire Mesh", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30510", "INSULATION-ROCKWOOL-MATTRESS-50MM-100D", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92010", "Bonded Mineral Wool Mattress LRB 50mm Thick IS 8183", "Plant_BPCL_Bina"),
            "cpse_bhel": ("BHEL-IND-44110", "ROCKWOOL INSULATION MATTRESS 50MM DENSITY 100 KG/M3", "Plant_BHEL_Haridwar"),
        }
    },
    {
        "category": "Insulation",
        "unit": "m",
        "variants": {
            "cpse_gail": ("GAIL-M-60111", "Ceramic Fiber Blanket 25mm Thk Density 128 kg/m3 1260C", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81011", "Ceramic Fiber Thermal Insulation Blanket 25mm 128kg/m3", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30511", "INSULATION-CERAMIC-FIBER-BLANKET-25MM", "Plant_PGCIL_Agra"),
            "cpse_bpcl": ("BPCL-SAP-92011", "High Temp Ceramic Fiber Blanket 25mm Thick 1260 Deg C", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44111", "CERAMIC FIBRE BLANKET 25MM DENSITY 128 KG/M3", "Plant_BHEL_Bhopal"),
        }
    },

    # ── 6. Lock Nuts & Specialized Fasteners ───────────────────────────────
    {
        "category": "Fasteners",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60112", "Nyloc Lock Nut M16 Grade 8 Zinc Plated DIN 985", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81012", "Hexagon Nylon Insert Lock Nut M16 Gr 8 DIN:985", "Plant_CIL_Nagpur"),
            "cpse_pgcil": ("PGCIL-EQ-30512", "NUT-NYLOC-LOCK-M16-GR8-DIN985", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92012", "Self Locking Nut M16 Nylon Ring Insert Grade 8", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44112", "NYLOC LOCK NUT M16 GRADE 8 ZINC PLATED", "Plant_BHEL_Trichy"),
        }
    },
    {
        "category": "Fasteners",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60113", "Nyloc Lock Nut M20 Grade 8 Zinc Plated DIN 985", "Plant_GAIL_Dabhol"),
            "cpse_cil": ("CIL-MM-81013", "Nylon Lock Nut M20 Grade 8 DIN 985", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30513", "NUT-LOCK-NYLOC-M20-GR-8", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92013", "Hex Self-Lock Nut M20 Nyloc Insert Grade 8", "Plant_BPCL_Bina"),
            "cpse_bhel": ("BHEL-IND-44113", "NYLOC LOCK NUT M20 GRADE 8 DIN 985", "Plant_BHEL_Haridwar"),
        }
    },
    {
        "category": "Fasteners",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60114", "High Tensile Hex Bolt M20 x 80mm Grade 10.9 IS 1364", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81014", "HT Hex Bolt M20x80 Gr 10.9 Half Thread IS:1364", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30514", "HEX-BOLT-M20X80-GRADE-10.9-HT", "Plant_PGCIL_Agra"),
            "cpse_bpcl": ("BPCL-SAP-92014", "Bolt Hex Head M20 x 80 Grade 10.9 Black Phosphate", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44114", "HEX HEAD BOLT M20 X 80 MM GRADE 10.9", "Plant_BHEL_Bhopal"),
        }
    },

    # ── 7. High-Voltage Power Cables & Switchgear ──────────────────────────
    {
        "category": "Electrical",
        "unit": "m",
        "variants": {
            "cpse_gail": ("GAIL-M-60115", "HT Power Cable 3 Core x 240 sq.mm 11kV XLPE Armoured Aluminum IS 7098", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81015", "11kV 3Cx240 SQ.MM XLPE ARMOURED AL POWER CABLE", "Plant_CIL_Nagpur"),
            "cpse_pgcil": ("PGCIL-EQ-30515", "CABLE-HT-11KV-3CX240-XLPE-AL-SWA", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92015", "Power Cable 11kV Grade 3C x 240 sq mm Aluminum Conductor IS:7098-2", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44115", "11 KV 3 CORE 240 SQ MM XLPE ARMOURED ALUMINIUM CABLE", "Plant_BHEL_Trichy"),
        }
    },
    {
        "category": "Electrical",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60116", "Vacuum Circuit Breaker VCB 11kV 1250A 25kA Indoor Panel", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81016", "11kV VCB Circuit Breaker 1250A 25kA Indoor Type", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30516", "SWITCHGEAR-VCB-11KV-1250A-25KA-INDOOR", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92016", "Vacuum Circuit Breaker 11kV Rating 1250 Amps 25kA Drawout", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44116", "INDOOR VCB 11KV 1250A 25KA CIRCUIT BREAKER PANEL", "Plant_BHEL_Haridwar"),
        }
    },

    # ── 8. Heavy Roller Bearings & Mechanical Seals ────────────────────────
    {
        "category": "Mechanical",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60117", "Spherical Roller Bearing 22216 EK/C3 Tapered Bore SKF", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81017", "Bearing Spherical Roller 22216-E1-K-C3 80x140x33mm", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30517", "BEARING-SPHERICAL-ROLLER-22216-EK-C3", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92017", "Roller Bearing Spherical 22216 EK C3 with Taper Bore", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44117", "SPHERICAL ROLLER BEARING 22216 EK C3 80X140X33", "Plant_BHEL_Bhopal"),
        }
    },
    {
        "category": "Mechanical",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60118", "Cartridge Mechanical Seal 45mm Balanced Single Seal Plan 11", "Plant_GAIL_Dabhol"),
            "cpse_cil": ("CIL-MM-81018", "Mechanical Seal Cartridge Type 45mm Shaft SiC/Carbon Viton", "Plant_CIL_Nagpur"),
            "cpse_pgcil": ("PGCIL-EQ-30518", "SEAL-MECHANICAL-CARTRIDGE-45MM-SIC-VITON", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92018", "Single Cartridge Mechanical Seal 45mm Dia API 682", "Plant_BPCL_Bina"),
            "cpse_bhel": ("BHEL-IND-44118", "CARTRIDGE MECHANICAL SEAL 45MM BALANCE TYPE", "Plant_BHEL_Haridwar"),
        }
    },

    # ── 9. Heavy Steel Sections & Piping ───────────────────────────────────
    {
        "category": "Steel",
        "unit": "m",
        "variants": {
            "cpse_gail": ("GAIL-M-60119", "Seamless Carbon Steel Pipe 4 Inch Sch 40 ASTM A106 Gr B", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81019", "CS Seamless Pipe 4\" NB Schedule 40 ASTM A106 Gr.B", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30519", "PIPE-CS-SMLS-4IN-SCH40-A106B", "Plant_PGCIL_Agra"),
            "cpse_bpcl": ("BPCL-SAP-92019", "Pipe Carbon Steel Seamless 100mm NB Sch 40 A106 Grade B", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44119", "CARBON STEEL SEAMLESS PIPE 4 INCH SCH 40 A106 GR B", "Plant_BHEL_Trichy"),
        }
    },
    {
        "category": "Steel",
        "unit": "kg",
        "variants": {
            "cpse_gail": ("GAIL-M-60120", "Mild Steel Chequered Plate 6mm Thk IS 2062 Tear Drop Pattern", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81020", "MS Chequered Plate 6mm IS:2062 E250 Tear Drop", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30520", "PLATE-CHEQUERED-MS-6MM-IS2062", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92020", "Chequered Steel Plate 6mm Thick Grade E250 IS 2062", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44120", "MILD STEEL CHEQUERED PLATE 6MM IS 2062", "Plant_BHEL_Bhopal"),
        }
    },
    {
        "category": "Steel",
        "unit": "m",
        "variants": {
            "cpse_gail": ("GAIL-M-60121", "Stainless Steel Pipe 50mm OD x 3mm WT SS304 Seamless", "Plant_GAIL_Dabhol"),
            "cpse_cil": ("CIL-MM-81021", "SS Pipe 50mm Dia x 3mm Wall Thickness SS304", "Plant_CIL_Nagpur"),
            "cpse_pgcil": ("PGCIL-EQ-30521", "PIPE-SS-50MM-3MM-WT-SS304-SMLS", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92021", "Seamless Stainless Steel Pipe 50mm OD Grade 304", "Plant_BPCL_Bina"),
            "cpse_bhel": ("BHEL-IND-44121", "SS 304 SEAMLESS PIPE 50MM OD X 3MM WT", "Plant_BHEL_Haridwar"),
        }
    },

    # ── 10. Heavy Safety PPE ───────────────────────────────────────────────
    {
        "category": "Safety",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60122", "Industrial Safety Helmet Yellow HDPE with Chin Strap IS 2925", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81022", "Safety Helmet Yellow Hard Hat Ratchet Suspension IS:2925", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30522", "HELMET-SAFETY-YELLOW-HDPE-IS2925", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92022", "Industrial Hard Hat Helmet Yellow High Impact HDPE EN397", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44122", "INDUSTRIAL SAFETY HELMET YELLOW IS 2925", "Plant_BHEL_Bhopal"),
        }
    },
    {
        "category": "Safety",
        "unit": "pair",
        "variants": {
            "cpse_gail": ("GAIL-M-60123", "Heavy Duty Nitrile Chemical Resistant Safety Gloves EN 374", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81023", "Chemical Resistant Green Nitrile Hand Gloves 13 Inch EN:374", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30523", "GLOVE-SAFETY-NITRILE-CHEMICAL-RESISTANT", "Plant_PGCIL_Agra"),
            "cpse_bpcl": ("BPCL-SAP-92023", "Safety Gloves Nitrile Chemical Protection Flocked Lined", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44123", "NITRILE CHEMICAL RESISTANT SAFETY GLOVES EN 374", "Plant_BHEL_Trichy"),
        }
    },
    {
        "category": "Safety",
        "unit": "pair",
        "variants": {
            "cpse_gail": ("GAIL-M-60124", "High Ankle Leather Safety Shoes Steel Toe Cap IS 15298 Size 10", "Plant_GAIL_Dabhol"),
            "cpse_cil": ("CIL-MM-81024", "Safety Boot High Ankle Leather Steel Toe Size 10 IS:15298", "Plant_CIL_Nagpur"),
            "cpse_pgcil": ("PGCIL-EQ-30524", "SAFETY-BOOT-HIGH-ANKLE-STEEL-TOE-SZ10", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92024", "Safety Shoe High Ankle Black Leather Steel Toe Size 10", "Plant_BPCL_Bina"),
            "cpse_bhel": ("BHEL-IND-44124", "HIGH ANKLE LEATHER SAFETY SHOES SIZE 10 IS 15298", "Plant_BHEL_Haridwar"),
        }
    },

    # ── 11. Heavy Industrial Lubricants & Adhesives ────────────────────────
    {
        "category": "Chemicals",
        "unit": "l",
        "variants": {
            "cpse_gail": ("GAIL-M-60125", "Industrial Gear Oil ISO VG 220 Drum 210L", "Plant_GAIL_Pata"),
            "cpse_cil": ("CIL-MM-81025", "Heavy Duty Industrial Enclosed Gear Oil ISO VG 220 210 Ltr", "Plant_CIL_Ranchi"),
            "cpse_pgcil": ("PGCIL-EQ-30525", "LUBE-OIL-GEAR-ISO-VG-220-210L", "Plant_PGCIL_Gurugram"),
            "cpse_bpcl": ("BPCL-SAP-92025", "MAK AMOCAM 220 Industrial Gear Oil Barrel 210 Liters", "Plant_BPCL_Mumbai"),
            "cpse_bhel": ("BHEL-IND-44125", "INDUSTRIAL GEAR LUBRICATING OIL ISO VG 220 210 LTR", "Plant_BHEL_Bhopal"),
        }
    },
    {
        "category": "Chemicals",
        "unit": "pc",
        "variants": {
            "cpse_gail": ("GAIL-M-60126", "RTV Silicone Gasket Maker Sealant Black 300ml Cartridge", "Plant_GAIL_Vijaipur"),
            "cpse_cil": ("CIL-MM-81026", "Silicone Adhesive Sealant Black High Temp 300ml Tube", "Plant_CIL_Dhanbad"),
            "cpse_pgcil": ("PGCIL-EQ-30526", "SEALANT-SILICONE-RTV-BLACK-300ML", "Plant_PGCIL_Manesar"),
            "cpse_bpcl": ("BPCL-SAP-92026", "RTV Black Silicone Sealant & Gasket Maker 300 ml Cartridge", "Plant_BPCL_Kochi"),
            "cpse_bhel": ("BHEL-IND-44126", "RTV SILICONE SEALANT ADHESIVE BLACK 300ML", "Plant_BHEL_Trichy"),
        }
    },
]


def generate_benchmark_records():
    rows = []
    cpse_order = ["cpse_gail", "cpse_cil", "cpse_pgcil", "cpse_bpcl", "cpse_bhel"]

    for cpse in cpse_order:
        for item in DATASET_2_MATERIALS:
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
    print(f"Dataset 2 successfully written: {output_path} ({len(rows)} records)")


if __name__ == "__main__":
    records = generate_benchmark_records()
    
    # Save as comparison upload in project root
    root_file = Path(r"e:\Projects\SIH 26\cpse_materials_comparison_upload.csv")
    write_csv(root_file, records)

    # Also save as sample in data/
    data_file = Path(r"e:\Projects\SIH 26\data\cpse_comparison_materials.csv")
    write_csv(data_file, records)
