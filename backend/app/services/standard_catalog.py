"""UNSPSC-style reference catalog for standard code mapping."""
from __future__ import annotations

import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings


# Standard code catalog (~200 entries, common industrial categories)
STANDARD_CODES: List[Dict[str, Any]] = [
    {"code": "10101501", "label": "Steel Plates", "level": 3, "description": "Hot-rolled steel plates, structural grade"},
    {"code": "10101502", "label": "Steel Sheets", "level": 3, "description": "Cold-rolled steel sheets, stainless or carbon"},
    {"code": "10101503", "label": "Steel Pipes", "level": 3, "description": "Seamless and welded steel pipes, various schedules"},
    {"code": "10101504", "label": "Steel Tubes", "level": 3, "description": "Precision tubes for instrumentation and hydraulics"},
    {"code": "10151501", "label": "Stainless Steel Bars", "level": 3, "description": "Round, square, flat stainless steel bars"},
    {"code": "10151502", "label": "Stainless Steel Angles", "level": 3, "description": "Equal and unequal angle sections"},
    {"code": "10151503", "label": "Stainless Steel Channels", "level": 3, "description": "Channel sections for structural use"},
    {"code": "10152001", "label": "Aluminum Sheets", "level": 3, "description": "Aluminum sheet and plate materials"},
    {"code": "10152002", "label": "Aluminum Rods", "level": 3, "description": "Aluminum round rods and profiles"},
    {"code": "11101501", "label": "Copper Wire", "level": 3, "description": "Bare copper wire, various gauges"},
    {"code": "11101502", "label": "Copper Cables", "level": 3, "description": "Electrical copper cables, multi-core"},
    {"code": "11151501", "label": "Electrical Connectors", "level": 3, "description": "Power and signal connectors"},
    {"code": "11151502", "label": "Circuit Breakers", "level": 3, "description": "AC/DC circuit breakers, molded case"},
    {"code": "11152001", "label": "Transformers", "level": 3, "description": "Power and distribution transformers"},
    {"code": "11152002", "label": "Switchgear", "level": 3, "description": "Medium voltage switchgear assemblies"},
    {"code": "12101501", "label": "Bolts, Hex", "level": 3, "description": "Hexagon head bolts, grade 8.8 and 10.9"},
    {"code": "12101502", "label": "Bolts, Stud", "level": 3, "description": "Double-end stud bolts"},
    {"code": "12101503", "label": "Nuts", "level": 3, "description": "Hex nuts, lock nuts, wing nuts"},
    {"code": "12101504", "label": "Washers", "level": 3, "description": "Flat, spring, lock washers"},
    {"code": "12101505", "label": "Screws", "level": 3, "description": "Machine screws, self-tapping screws"},
    {"code": "12101506", "label": "Rivets", "level": 3, "description": "Blind rivets, solid rivets"},
    {"code": "12151501", "label": "Bearings", "level": 3, "description": "Ball bearings, roller bearings"},
    {"code": "12151502", "label": "Shafts", "level": 3, "description": "Precision shafts, drive shafts"},
    {"code": "12152001", "label": "Gears", "level": 3, "description": "Spur, helical, bevel gears"},
    {"code": "12152002", "label": "Couplings", "level": 3, "description": "Flexible and rigid shaft couplings"},
    {"code": "12152003", "label": "Springs", "level": 3, "description": "Compression, tension, torsion springs"},
    {"code": "13101501", "label": "Hydraulic Pumps", "level": 3, "description": "Gear, vane, piston hydraulic pumps"},
    {"code": "13101502", "label": "Hydraulic Valves", "level": 3, "description": "Directional, pressure, flow control valves"},
    {"code": "13101503", "label": "Hydraulic Cylinders", "level": 3, "description": "Single and double acting cylinders"},
    {"code": "13151501", "label": "Pneumatic Valves", "level": 3, "description": "Solenoid, directional, flow control valves"},
    {"code": "13151502", "label": "Air Compressors", "level": 3, "description": "Reciprocating and rotary compressors"},
    {"code": "13152001", "label": "Fittings, Hydraulic", "level": 3, "description": "Hoses, fittings, quick couplings"},
    {"code": "14101501", "label": "Bearings, Pillow Block", "level": 3, "description": "Pillow block bearings, mounted"},
    {"code": "14101502", "label": "Bearings, Flanged", "level": 3, "description": "Flanged bearings, insert types"},
    {"code": "14151501", "label": "Seals, Mechanical", "level": 3, "description": "Mechanical seals for pumps and mixers"},
    {"code": "14151502", "label": "Seals, O-Ring", "level": 3, "description": "Standard O-ring seals, NBR, Viton, PTFE"},
    {"code": "14151503", "label": "Gaskets", "level": 3, "description": "Gaskets for flanges, spiral wound"},
    {"code": "15101501", "label": "Screws, Wood", "level": 3, "description": "Wood screws, various head types"},
    {"code": "15101502", "label": "Bolts, Anchor", "level": 3, "description": "Anchor bolts, chemical and mechanical"},
    {"code": "15151501", "label": "Brass Fittings", "level": 3, "description": "Brass compression and solder fittings"},
    {"code": "15151502", "label": "Brass Valves", "level": 3, "description": "Brass gate, globe, ball valves"},
    {"code": "15151503", "label": "Copper Fittings", "level": 3, "description": "Copper solder and compression fittings"},
    {"code": "15151504", "label": "Copper Pipes", "level": 3, "description": "Copper tubes for plumbing and HVAC"},
    {"code": "15201501", "label": "PVC Pipes", "level": 3, "description": "PVC pipes for drainage and electrical"},
    {"code": "15201502", "label": "PVC Fittings", "level": 3, "description": "PVC elbows, tees, couplings"},
    {"code": "15201503", "label": "PTFE Sheets", "level": 3, "description": "PTFE sheets and tapes for gaskets"},
    {"code": "16101501", "label": "Safety Helmets", "level": 3, "description": "Industrial safety helmets, EN397"},
    {"code": "16101502", "label": "Safety Glasses", "level": 3, "description": "Impact-resistant safety goggles"},
    {"code": "16101503", "label": "Safety Gloves", "level": 3, "description": "Cut, chemical, heat resistant gloves"},
    {"code": "16101504", "label": "Safety Boots", "level": 3, "description": "Steel toe safety boots"},
    {"code": "16101505", "label": "Ear Plugs", "level": 3, "description": "Foam and silicone ear plugs"},
    {"code": "16151501", "label": "Face Shields", "level": 3, "description": "Full face shields for welding and grinding"},
    {"code": "16151502", "label": "Respirators", "level": 3, "description": "FFP2/FFP3 disposable respirators"},
    {"code": "16201501", "label": "Fire Extinguishers", "level": 3, "description": "CO2, powder, water extinguishers"},
    {"code": "16201502", "label": "Fire Blankets", "level": 3, "description": "Fire blankets for small fires"},
    {"code": "16251501", "label": "First Aid Kits", "level": 3, "description": "Industrial first aid kits, Class A/B"},
    {"code": "16251502", "label": "Safety Showers", "level": 3, "description": "Eyewash and safety showers"},
    {"code": "17101501", "label": "Lubricating Oil", "level": 3, "description": "Industrial lubricating oils, ISO grades"},
    {"code": "17101502", "label": "Grease", "level": 3, "description": "Lithium and calcium based greases"},
    {"code": "17101503", "label": "Hydraulic Fluid", "level": 3, "description": "Hydraulic oils, fire resistant"},
    {"code": "17151501", "label": "Coolant", "level": 3, "description": "Metal cutting coolants, water soluble"},
    {"code": "17151502", "label": "Cleaning Solvents", "level": 3, "description": "Industrial cleaning solvents"},
    {"code": "17151503", "label": "Anti-Rust Oil", "level": 3, "description": "Corrosion prevention oils"},
    {"code": "17201501", "label": "Adhesives", "level": 3, "description": "Industrial adhesives and sealants"},
    {"code": "17201502", "label": "Epoxy Resin", "level": 3, "description": "Epoxy resin systems for bonding"},
    {"code": "17201503", "label": "Threadlocker", "level": 3, "description": "Anaerobic threadlocker compounds"},
    {"code": "18101501", "label": "Paint, Epoxy", "level": 3, "description": "Epoxy coating paints"},
    {"code": "18101502", "label": "Paint, Anti-Corrosive", "level": 3, "description": "Zinc-rich anti-corrosive paints"},
    {"code": "18101503", "label": "Primer", "level": 3, "description": "Surface primers for metal and wood"},
    {"code": "19101501", "label": "Valves, Gate", "level": 3, "description": "Gate valves, flanged or threaded"},
    {"code": "19101502", "label": "Valves, Globe", "level": 3, "description": "Globe valves, stainless or cast iron"},
    {"code": "19101503", "label": "Valves, Ball", "level": 3, "description": "Ball valves, pneumatic or manual"},
    {"code": "19151501", "label": "Pumps, Centrifugal", "level": 3, "description": "Centrifugal pumps, single/multi-stage"},
    {"code": "19151502", "label": "Pumps, Diaphragm", "level": 3, "description": "Diaphragm pumps, chemical duty"},
    {"code": "19152001", "label": "Pump Seals", "level": 3, "description": "Mechanical seals for centrifugal pumps"},
    {"code": "20101501", "label": "Motors, Electric", "level": 3, "description": "Industrial electric motors, 3-phase"},
    {"code": "20101502", "label": "Generators", "level": 3, "description": "Diesel and electric generators"},
    {"code": "20151501", "label": "Compressors", "level": 3, "description": "Reciprocating and rotary compressors"},
    {"code": "20151502", "label": "Fans, Industrial", "level": 3, "description": "Axial and centrifugal fans"},
    {"code": "20151503", "label": "Blowers", "level": 3, "description": "Industrial blowers, high volume"},
    {"code": "21101501", "label": "Filters, Air", "level": 3, "description": "Pneumatic and compressed air filters"},
    {"code": "21101502", "label": "Filters, Oil", "level": 3, "description": "Hydraulic and lubrication oil filters"},
    {"code": "21101503", "label": "Filters, Fuel", "level": 3, "description": "Fuel line filters"},
    {"code": "21151501", "label": "Sensors, Temperature", "level": 3, "description": "Thermocouples, RTD sensors"},
    {"code": "21151502", "label": "Sensors, Pressure", "level": 3, "description": "Pressure transmitters, gauges"},
    {"code": "21152001", "label": "Controllers", "level": 3, "description": "PLC modules, PID controllers"},
    {"code": "21152002", "label": "HMI Panels", "level": 3, "description": "Human machine interface panels"},
    {"code": "22101501", "label": "Wrenches", "level": 3, "description": "Spanner wrenches, socket sets"},
    {"code": "22101502", "label": "Screwdrivers", "level": 3, "description": "Flat and Phillips screwdrivers"},
    {"code": "22101503", "label": "Pliers", "level": 3, "description": "Combination, needle-nose, locking pliers"},
    {"code": "22151501", "label": "Drills", "level": 3, "description": "Electric and manual drills"},
    {"code": "22151502", "label": "Cutters", "level": 3, "description": "Hacksaws, bolt cutters, pipe cutters"},
    {"code": "22151503", "label": "Measuring Tools", "level": 3, "description": "Calipers, micrometers, gauges"},
    {"code": "23101501", "label": "Welding Rods", "level": 3, "description": "MIG, TIG, stick welding rods"},
    {"code": "23101502", "label": "Welding Machines", "level": 3, "description": "Welding power supplies, MIG/TIG"},
    {"code": "23101503", "label": "Welding Helmets", "level": 3, "description": "Auto-darkening welding helmets"},
    {"code": "24101501", "label": "Hand Trucks", "level": 3, "description": "Platform hand trucks, pallet jacks"},
    {"code": "24101502", "label": "Lifting Equipment", "level": 3, "description": "Chain hoists, winches, slings"},
    {"code": "24151501", "label": "Storage Racks", "level": 3, "description": "Warehouse storage racks and shelving"},
    {"code": "24151502", "label": "Workbenches", "level": 3, "description": "Industrial workbenches with vice"},
    {"code": "24201501", "label": "Locks", "level": 3, "description": "Industrial padlocks and cabinet locks"},
    {"code": "24201502", "label": "Keys", "level": 3, "description": "Key blanks and cylinder keys"},
    {"code": "25101501", "label": "Fasteners, Nuts", "level": 3, "description": "Hex nuts, cap nuts, flange nuts"},
    {"code": "25101502", "label": "Fasteners, Bolts", "level": 3, "description": "Hex bolts, carriage bolts, lag bolts"},
    {"code": "25101503", "label": "Fasteners, Washers", "level": 3, "description": "Spring, lock, and flat washers"},
    {"code": "25151501", "label": "Electrical Tape", "level": 3, "description": "PVC and fabric electrical tape"},
    {"code": "25151502", "label": "Wire Lugs", "level": 3, "description": "Crimp wire lugs and terminals"},
    {"code": "25151503", "label": "Cable Ties", "level": 3, "description": "Nylon cable ties, various sizes"},
    {"code": "25201501", "label": "Fluids, Cutting", "level": 3, "description": "Metal cutting fluids and coolants"},
    {"code": "25201502", "label": "Rust Inhibitor", "level": 3, "description": "Rust inhibiting compounds"},
    {"code": "26101501", "label": "Bearings, Ceramic", "level": 3, "description": "Ceramic hybrid bearings"},
    {"code": "26101502", "label": "Bearings, Tapered", "level": 3, "description": "Tapered roller bearings"},
    {"code": "26101503", "label": "Bearings, Spherical", "level": 3, "description": "Spherical roller bearings"},
    {"code": "27101501", "label": "Hoses, Hydraulic", "level": 3, "description": "Hydraulic hoses and hose assemblies"},
    {"code": "27101502", "label": "Hoses, Air", "level": 3, "description": "Compressed air hoses"},
    {"code": "27101503", "label": "Hoses, Fuel", "level": 3, "description": "Fuel injection hoses"},
    {"code": "28101501", "label": "Belts, V", "level": 3, "description": "V-belts for power transmission"},
    {"code": "28101502", "label": "Chains, Roller", "level": 3, "description": "Roller chains for conveyors"},
    {"code": "28101503", "label": "Sprockets", "level": 3, "description": "Sprockets for roller chains"},
    {"code": "29101501", "label": "Shaft Couplings", "level": 3, "description": "Flexible and rigid shaft couplings"},
    {"code": "29101502", "label": "Universal Joints", "level": 3, "description": "Universal joints and Cardan couplings"},
    {"code": "29101503", "label": "Clutches", "level": 3, "description": "Friction and electromagnetic clutches"},
    {"code": "30101501", "label": "Pneumatic Cylinders", "level": 3, "description": "Pneumatic linear cylinders"},
    {"code": "30151501", "label": "Valves, Solenoid", "level": 3, "description": "Solenoid operated directional valves"},
    {"code": "30151502", "label": "Regulators", "level": 3, "description": "Pressure and flow regulators"},
    {"code": "31101501", "label": "Filters, HEPA", "level": 3, "description": "HEPA filters for cleanrooms"},
    {"code": "31101502", "label": "Filters, Bag", "level": 3, "description": "Bag filters for dust collection"},
    {"code": "31151501", "label": "Valves, Check", "level": 3, "description": "Check valves, swing and lift types"},
    {"code": "31151502", "label": "Valves, Safety", "level": 3, "description": "Safety relief valves"},
    {"code": "32101501", "label": "Compressors, Screw", "level": 3, "description": "Screw compressors"},
    {"code": "32101502", "label": "Compressors, Scroll", "level": 3, "description": "Scroll compressors for HVAC"},
    {"code": "32101503", "label": "Compressors, Rotary", "level": 3, "description": "Rotary vane compressors"},
    {"code": "33101501", "label": "Turbines", "level": 3, "description": "Steam and gas turbines"},
    {"code": "33101502", "label": "Generators, Steam", "level": 3, "description": "Steam turbines and generators"},
    {"code": "33151501", "label": "Heat Exchangers", "level": 3, "description": "Shell and tube heat exchangers"},
    {"code": "33151502", "label": "Coolers, Air", "level": 3, "description": "Air cooled heat exchangers"},
    {"code": "33201501", "label": "Boilers", "level": 3, "description": "Industrial steam boilers"},
    {"code": "33201502", "label": "Boiler Accessories", "level": 3, "description": "Feed pumps, valves, gauges for boilers"},
    {"code": "34101501", "label": "Pumps, Submersible", "level": 3, "description": "Submersible pumps"},
    {"code": "34101502", "label": "Pumps, Booster", "level": 3, "description": "Booster pumps for water supply"},
    {"code": "34101503", "label": "Pumps, Chemical", "level": 3, "description": "Chemical dosing and metering pumps"},
    {"code": "34151501", "label": "Mixers, Industrial", "level": 3, "description": "Industrial mixing and blending equipment"},
    {"code": "34151502", "label": "Agitators", "level": 3, "description": "Tank agitators for liquids"},
    {"code": "35101501", "label": "Compressors, Screw, Industrial", "level": 3, "description": "Industrial screw compressors"},
    {"code": "35101502", "label": "Compressors, Reciprocating", "level": 3, "description": "Reciprocating compressors"},
    {"code": "36101501", "label": "Tanks, Storage", "level": 3, "description": "Storage tanks, steel and fiberglass"},
    {"code": "36101502", "label": "Vessels, Pressure", "level": 3, "description": "Pressure vessels"},
    {"code": "36151501", "label": "Containers, ISO", "level": 3, "description": "ISO shipping containers"},
    {"code": "36151502", "label": "Pallets, Wood", "level": 3, "description": "Standard wood pallets"},
    {"code": "36201501", "label": "Cranes", "level": 3, "description": "Overhead and gantry cranes"},
    {"code": "36201502", "label": "Hoists", "level": 3, "description": "Electric wire rope hoists"},
    {"code": "37101501", "label": "Conveyors", "level": 3, "description": "Belt and roller conveyors"},
    {"code": "37101502", "label": "Roller Systems", "level": 3, "description": "Gravity and powered roller systems"},
    {"code": "37151501", "label": "Chains, Conveyor", "level": 3, "description": "Conveyor chain assemblies"},
    {"code": "37151502", "label": "Sprockets, Conveyor", "level": 3, "description": "Conveyor sprockets and gears"},
    {"code": "38101501", "label": "Gearboxes", "level": 3, "description": "Industrial gearboxes and reducers"},
    {"code": "38101502", "label": "Gear Motors", "level": 3, "description": "Geared motor assemblies"},
    {"code": "38151501", "label": "Bearings, Linear", "level": 3, "description": "Linear guides and bearings"},
    {"code": "38151502", "label": "Ball Screws", "level": 3, "description": "Ball screws for precision motion"},
    {"code": "39101501", "label": "Cables, Power", "level": 3, "description": "Power cables, armored and non-armored"},
    {"code": "39101502", "label": "Cables, Control", "level": 3, "description": "Control cables, instrumentation"},
    {"code": "39151501", "label": "Busbars", "level": 3, "description": "Copper and aluminum busbars"},
    {"code": "39151502", "label": "Enclosures", "level": 3, "description": "Electrical enclosures, IP rated"},
    {"code": "40101501", "label": "Pumps, Diaphragm, Chemical", "level": 3, "description": "Chemical injection pumps"},
    {"code": "40101502", "label": "Valves, Diaphragm", "level": 3, "description": "Diaphragm valves for chemicals"},
    {"code": "40101503", "label": "Valves, Pinch", "level": 3, "description": "Pinch valves for slurries"},
    {"code": "40151501", "label": "Compressors, Turbo", "level": 3, "description": "Turbo compressors for high flow"},
    {"code": "40151502", "label": "Expanders", "level": 3, "description": "Turbo expanders for gas systems"},
    {"code": "41101501", "label": "Compressors, Centrifugal", "level": 3, "description": "Centrifugal compressors"},
    {"code": "41101502", "label": "Compressors, Axial", "level": 3, "description": "Axial compressors"},
    {"code": "41151501", "label": "Turbines, Steam", "level": 3, "description": "Steam turbines"},
    {"code": "41151502", "label": "Turbines, Gas", "level": 3, "description": "Gas turbines"},
    {"code": "41201501", "label": "Boilers, Electric", "level": 3, "description": "Electric steam boilers"},
    {"code": "41201502", "label": "Boilers, Gas", "level": 3, "description": "Gas fired boilers"},
    {"code": "42101501", "label": "Pumps, Jet", "level": 3, "description": "Jet pumps for wells"},
    {"code": "42101502", "label": "Pumps, Sump", "level": 3, "description": "Sump pumps for drainage"},
    {"code": "42101503", "label": "Pumps, Submersible, Sewage", "level": 3, "description": "Sewage submersible pumps"},
    {"code": "42151501", "label": "Mixers, Static", "level": 3, "description": "Static mixing elements"},
    {"code": "42151502", "label": "Mixers, Planetary", "level": 3, "description": "Planetary mixers for viscous fluids"},
    {"code": "42201501", "label": "Filters, Baghouse", "level": 3, "description": "Baghouse dust collectors"},
    {"code": "42201502", "label": "Cyclones", "level": 3, "description": "Cyclone separators"},
    {"code": "42251501", "label": "Valves, Check, Swing", "level": 3, "description": "Swing check valves"},
    {"code": "42251502", "label": "Valves, Non-Return", "level": 3, "description": "Non-return and lift check valves"},
    {"code": "42301501", "label": "Compressors, Rotary Screw", "level": 3, "description": "Rotary screw compressors, industrial"},
    {"code": "42301502", "label": "Compressors, Scroll, HVAC", "level": 3, "description": "Scroll compressors for HVAC systems"},
    {"code": "42351501", "label": "Generators, Portable", "level": 3, "description": "Portable diesel generators"},
    {"code": "42351502", "label": "Generators, Industrial", "level": 3, "description": "Industrial diesel generators"},
    {"code": "42401501", "label": "Transformers, Distribution", "level": 3, "description": "Distribution transformers"},
    {"code": "42401502", "label": "Transformers, Power", "level": 3, "description": "Power transformers, oil-filled"},
    {"code": "42401503", "label": "Transformers, Instrument", "level": 3, "description": "Instrument transformers for metering"},
    {"code": "42451501", "label": "Motors, DC", "level": 3, "description": "DC motors for industrial use"},
    {"code": "42451502", "label": "Motors, Servo", "level": 3, "description": "Servo motors for precision control"},
    {"code": "42451503", "label": "Motors, Stepper", "level": 3, "description": "Stepper motors for automation"},
]


class StandardCodeCatalog:
    """Reference catalog for mapping harmonized clusters to UNSPSC codes."""

    def __init__(self):
        self._embeddings: Optional[np.ndarray] = None
        self._labels: List[str] = []
        self._codes: List[str] = []

    def _ensure_index(self) -> None:
        if self._embeddings is not None:
            return
        from app.services.embedding import get_embedding_service
        labels = [c["label"] for c in STANDARD_CODES]
        self._labels = labels
        self._codes = [c["code"] for c in STANDARD_CODES]
        es = get_embedding_service()
        self._embeddings = es.encode(labels, normalize=True)

    def find_closest(self, description: str, cluster_embedding: Optional[np.ndarray] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find closest standard codes for a description."""
        self._ensure_index()
        if cluster_embedding is not None:
            query = cluster_embedding.reshape(1, -1)
        else:
            from app.services.embedding import get_embedding_service
            query = get_embedding_service().encode([description], normalize=True)

        scores = self._embeddings.dot(query.T).T[0]
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {"code": self._codes[i], "label": self._labels[i], "score": float(scores[i])}
            for i in top_indices
        ]

    def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        for c in STANDARD_CODES:
            if c["code"] == code:
                return c
        return None

    def list_all(self) -> List[Dict[str, Any]]:
        return STANDARD_CODES.copy()


standard_code_catalog = StandardCodeCatalog()