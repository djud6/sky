# This data structure defines the input fields the frontend must display
# for a given Scope, Region,Category combination.

# ghg_inputs_data.py

GHG_INPUT_DEFINITIONS = {
    "Scope1": {
        "North America": {
            "Aviation": [
                { # Only Tier Available (Acts as Highest/Default)
                    "tier_level": "Basic Fuel Use (Regional Tier 1)",
                    "tier_id": "NA_eq_1",
                    "inputs": [
                        {"key": "fuel_use", "label": "Total Fuel Use (liters)", "type": "text", "required": True, "unit": "liters"},
                        {"key": "emission_factor", "label": "Emission Factor (mass/liter)", "type": "text", "required": True, "unit": "mass/liter"},
                    ],
                    "output_label": "Total Emissions"
                }
            ],
            "Marine": [
                # --- EXCLUDED EQUATIONS NOTE ---
                # Equations USA_eq_2 (PM10 Factor) and USA_eq_5 (Aggregation) 
                # are intentionally excluded from this tiered list because they 
                # calculate intermediate factors or perform summation, not the 
                # final CO2/GHG emissions that drive the input retrieval process.
                # -------------------------------
                { # 1. Highest Tier (Default): USA_eq_3 (Time-Series/AIS Activity)
                    "tier_level": "Highest Tier (Time-Series/AIS Activity)",
                    "tier_id": "USA_eq_3", 
                    "inputs": [
                        {"key": "P_p", "label": "Engine Power (kW/AIS Record)", "type": "text", "required": True, "unit": "kW"},
                        {"key": "A", "label": "Time Interval per Record (hours)", "type": "text", "required": True, "unit": "hours"},
                        {"key": "EF", "label": "Emission Factor (g/kWh)", "type": "text", "required": True, "unit": "g/kWh"},
                        {"key": "LLAF", "label": "Low Load Adjustment Factor", "type": "text", "required": False, "unit": ""}, 
                    ],
                    "output_label": "Propulsion Engine Emissions (grams)"
                },
                { # 2. Fallback 1: USA_eq_4 (Mode-Specific Activity)
                    "tier_level": "Fallback 1 (Mode-Specific Activity)",
                    "tier_id": "USA_eq_4",
                    "inputs": [
                        {"key": "P_p_i", "label": "Engine Power per Mode (dict/list)", "type": "text", "required": True, "unit": "kW"},
                        {"key": "A_i", "label": "Time in Operating Mode i (dict/list)", "type": "text", "required": True, "unit": "hours"},
                        {"key": "EF", "label": "Emission Factor (g/kWh)", "type": "text", "required": True, "unit": "g/kWh"},
                        {"key": "LLAF_i", "label": "LLAF for Mode i (dict/list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Propulsion Emissions for Mode i (grams)"
                },
                { # 3. Fallback 2: USA_eq_6 (Load Factor)
                    "tier_level": "Fallback 2 (Load Factor)",
                    "tier_id": "USA_eq_6",
                    "inputs": [
                        {"key": "P", "label": "Engine Power (kW)", "type": "text", "required": True, "unit": "kW"},
                        {"key": "LF", "label": "Load Factor (0-1)", "type": "text", "required": True, "unit": ""},
                        {"key": "A", "label": "Engine Operating Activity (hours)", "type": "text", "required": True, "unit": "hours"},
                        {"key": "EF", "label": "Emission Factor (g/kWh)", "type": "text", "required": True, "unit": "g/kWh"},
                    ],
                    "output_label": "Total Vessel Emissions (grams)"
                },
                { # 4. Fallback 3: USA_eq_1 (Basic Activity)
                    "tier_level": "Fallback 3 (Basic Activity)",
                    "tier_id": "USA_eq_1",
                    "inputs": [
                        {"key": "P", "label": "Engine Operating Power (kW)", "type": "text", "required": True, "unit": "kW"},
                        {"key": "A", "label": "Engine Operating Activity (hours)", "type": "text", "required": True, "unit": "hours"},
                        {"key": "EF", "label": "Emission Factor (g/kWh)", "type": "text", "required": True, "unit": "g/kWh"},
                        {"key": "LLAF", "label": "Low Load Adjustment Factor", "type": "text", "required": False, "unit": ""}, 
                    ],
                    "output_label": "Per Vessel Emissions (grams)"
                },
                { # 5. Lowest Fallback: MEX_eq_1 (Aggregated Fuel Quantity)
                    "tier_level": "Lowest Tier (Aggregated Fuel Quantity)",
                    "tier_id": "MEX_eq_1",
                    "inputs": [
                        {"key": "Q_ri", "label": "Residual Oil Consumed (tons)", "type": "text", "required": True, "unit": "tons"},
                        {"key": "EF_rp", "label": "Res. Oil Emission Factor (g/ton)", "type": "text", "required": True, "unit": "g/ton"},
                        {"key": "Q_di", "label": "Distillate Oil Consumed (tons)", "type": "text", "required": True, "unit": "tons"},
                        {"key": "EF_dp", "label": "Dist. Oil Emission Factor (g/ton)", "type": "text", "required": True, "unit": "g/ton"},
                    ],
                    "output_label": "Total Emissions of Pollutant p (grams)"
                }
            ],
            "Railroad": [
                { # 1. Highest Tier (Default): NA_eq_2 (Emissions from Allocated Fuel)
                    # Note: Since F_ci is calculated in NA_eq_1, the user must provide EITHER F_ci OR the inputs for NA_eq_1.
                    # We assume the FE will collect F_ci directly.
                    "tier_level": "Highest Tier (Emissions from Allocated Fuel)",
                    "tier_id": "NA_eq_2", 
                    "inputs": [
                        {"key": "F_ci", "label": "Allocated Fuel Consumption (liters/year)", "type": "text", "required": True, "unit": "liters/year"},
                        {"key": "EF_lp", "label": "Emission Factor (kg/liter)", "type": "text", "required": True, "unit": "kg/liter"},
                    ],
                    "output_label": "Estimated Annual Emissions (kg)"
                },
                { # 2. Lowest Fallback: NA_eq_1 (Fuel Consumption Allocation)
                    "tier_level": "Fallback 1 (Fuel Consumption Allocation)",
                    "tier_id": "NA_eq_1",
                    "inputs": [
                        {"key": "F_cn", "label": "National Fuel Consumption (liters)", "type": "text", "required": True, "unit": "liters"},
                        {"key": "TL_i", "label": "Track Length for Inventory Area (km)", "type": "text", "required": True, "unit": "km"},
                        {"key": "TL_n", "label": "National Railroad Track Length (km)", "type": "text", "required": True, "unit": "km"},
                    ],
                    "output_label": "Estimated Fuel Consumption for Area i (liters)"
                }
            ]# No Road data equations available for NA
        },
        "Europe": {
            "Aviation": [
                { # 1. Highest Tier (Default): EU_eq_2 (Method A - Tank Difference)
                    "tier_level": "Highest Tier (Method A - Tank Difference)",
                    "tier_id": "EU_eq_2", 
                    "inputs": [
                        {"key": "T_N", "label": "Fuel in tanks after current uplift (t)", "type": "text", "required": True, "unit": "tons"},
                        {"key": "T_N_1", "label": "Fuel in tanks after next uplift (t)", "type": "text", "required": True, "unit": "tons"},
                        {"key": "U_N_1", "label": "Fuel uplift for next flight (t)", "type": "text", "required": True, "unit": "tons"},
                    ],
                    "output_label": "Fuel Consumed for Current Flight (tons)"
                },
                { # 2. Fallback 1: EU_eq_3 (Method B - Tank Difference)
                    # Note: EU_eq_3 calls the Uniform equation Uni_eq_1, which is the same formula structure.
                    "tier_level": "Fallback 1 (Method B - Tank Difference)",
                    "tier_id": "EU_eq_3", 
                    "inputs": [
                        {"key": "R_N_1", "label": "Fuel remaining previous flight (t)", "type": "text", "required": True, "unit": "tons"},
                        {"key": "R_N", "label": "Fuel remaining current flight (t)", "type": "text", "required": True, "unit": "tons"},
                        {"key": "U_N", "label": "Fuel uplift for current flight (t)", "type": "text", "required": True, "unit": "tons"},
                        {"key": "EF", "label": "Emission Factor (t CO₂/t fuel)", "type": "text", "required": True, "unit": "t CO₂/t fuel"},
                    ],
                    "output_label": "Total CO₂ Emissions (tons)"
                },
                { # 3. Lowest Fallback: EU_eq_1 (Simplified Fuel Use)
                    "tier_level": "Lowest Tier (Simplified Fuel Use)",
                    "tier_id": "EU_eq_1", 
                    "inputs": [
                        {"key": "AD", "label": "Activity Data (Fuel Consumed, t)", "type": "text", "required": True, "unit": "tons"},
                        {"key": "EF", "label": "Emission Factor (t CO₂/t fuel)", "type": "text", "required": True, "unit": "t CO₂/t fuel"},
                    ],
                    "output_label": "Total CO₂ Emissions (tons)"
                }
            ],
            "Marine": [
                # --------------------------------------------------------------------------
                # EXCLUDED EQUATIONS NOTE for Tier Prioritization:
                # USA_eq_2 (PM10 Factor) and USA_eq_5 (Aggregation) are excluded from the 
                # primary CO2/GHG tiered list. 
                # Rationale: They calculate intermediate factors (USA_eq_2) or perform 
                # summation (USA_eq_5), rather than representing a distinct, data-gathering 
                # tier for final CO2/GHG emissions.
                # --------------------------------------------------------------------------
                { # 1. Highest Tier (Default): EU_eq_1 (CO2 Mass Balance)
                    "tier_level": "Highest Tier (MRV CO₂ Mass Balance)",
                    "tier_id": "EU_eq_1",
                    "inputs": [
                        {"key": "M_i", "label": "Total Fuel Mass by Type (dict)", "type": "text", "required": True, "unit": "tons"}, 
                        {"key": "M_iNC", "label": "Non-Combusted Fuel Mass (dict)", "type": "text", "required": True, "unit": "tons"}, 
                        {"key": "EF_CO2", "label": "CO₂ Emission Factors (dict)", "type": "text", "required": True, "unit": "kg CO₂/ton"}, 
                    ],
                    "output_label": "Total CO₂ Emissions (kg)"
                },
                { # 2. Fallback 1: EU_eq_2 (CH4 Emissions)
                    "tier_level": "Fallback 1 (MRV CH₄ Mass Balance)",
                    "tier_id": "EU_eq_2",
                    "inputs": [
                        {"key": "M_i", "label": "Total Fuel Mass by Type (dict)", "type": "text", "required": True, "unit": "tons"}, 
                        {"key": "M_iNC", "label": "Non-Combusted Fuel Mass (dict)", "type": "text", "required": True, "unit": "tons"}, 
                        {"key": "EF_CH4", "label": "CH₄ Emission Factors (dict)", "type": "text", "required": True, "unit": "kg CH₄/ton"}, 
                        {"key": "CH4_s", "label": "Supplementary CH₄ Emissions (kg)", "type": "text", "required": False, "unit": "kg"},
                    ],
                    "output_label": "Total CH₄ Emissions (kg)"
                },
                { # 3. Fallback 2: EU_eq_3 (N2O Emissions)
                    "tier_level": "Fallback 2 (MRV N₂O Mass Balance)",
                    "tier_id": "EU_eq_3",
                    "inputs": [
                        {"key": "M_i", "label": "Total Fuel Mass by Type (dict)", "type": "text", "required": True, "unit": "tons"}, 
                        {"key": "M_iNC", "label": "Non-Combusted Fuel Mass (dict)", "type": "text", "required": True, "unit": "tons"}, 
                        {"key": "EF_N2O", "label": "N₂O Emission Factors (dict)", "type": "text", "required": True, "unit": "kg N₂O/ton"}, 
                    ],
                    "output_label": "Total N₂O Emissions (kg)"
                },
                { # 4. Lowest Fallback: EU_eq_6 (Total GHG Aggregate)
                    "tier_level": "Lowest Tier (Total GHG Aggregate)",
                    "tier_id": "EU_eq_6",
                    "inputs": [
                        {"key": "CO2", "label": "CO₂ Emissions (kg)", "type": "text", "required": True, "unit": "kg"},
                        {"key": "CH4", "label": "CH₄ Emissions (kg)", "type": "text", "required": True, "unit": "kg"},
                        {"key": "N2O", "label": "N₂O Emissions (kg)", "type": "text", "required": True, "unit": "kg"},
                        {"key": "GWP_CH4", "label": "GWP of CH₄ (Default 28)", "type": "text", "required": False, "unit": ""},
                        {"key": "GWP_N2O", "label": "GWP of N₂O (Default 265)", "type": "text", "required": False, "unit": ""},
                    ],
                    "output_label": "Total GHG Emissions (kg CO₂e)"
                }
            ],
            "Railroad": [
                { # 1. Highest Tier (Default): EU_eq_4 (Locomotive Usage)
                    "tier_level": "Highest Tier (Locomotive Usage Methodology)",
                    "tier_id": "EU_eq_4",
                    "inputs": [
                        {"key": "N", "label": "Number of Locomotives (dict)", "type": "text", "required": True, "unit": ""}, 
                        {"key": "H", "label": "Operating Hours per Loco (dict)", "type": "text", "required": True, "unit": "hours"}, 
                        {"key": "P", "label": "Nominal Power Output (dict)", "type": "text", "required": True, "unit": "kW"}, 
                        {"key": "LF", "label": "Load Factor (dict, 0-1)", "type": "text", "required": True, "unit": ""}, 
                        {"key": "EF_i", "label": "Emission Factor (dict)", "type": "text", "required": True, "unit": "kg/kWh"}, 
                        {"key": "j_set", "label": "Locomotive Categories (list)", "type": "text", "required": True, "unit": ""},
                        {"key": "m_set", "label": "Fuel Types (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Emissions (kg or g)"
                },
                { # 2. Fallback 1: EU_eq_3 (Fuel Used by Locomotive Type)
                    "tier_level": "Fallback 1 (Fuel by Locomotive Type)",
                    "tier_id": "EU_eq_3",
                    "inputs": [
                        {"key": "FC", "label": "Fuel Consumption by (Loco Type, Fuel) (dict)", "type": "text", "required": True, "unit": "tonnes"}, 
                        {"key": "EF_i", "label": "Emission Factor (dict)", "type": "text", "required": True, "unit": "kg/tonne"}, 
                        {"key": "j_set", "label": "Locomotive Categories (list)", "type": "text", "required": True, "unit": ""},
                        {"key": "m_set", "label": "Fuel Types (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Emissions of Pollutant i (kg or g)"
                },
                { # 3. Lowest Fallback: EU_eq_1 (Fuel Base Methodology)
                    "tier_level": "Lowest Tier (Fuel Base Methodology)",
                    "tier_id": "EU_eq_1",
                    "inputs": [
                        {"key": "FC", "label": "Fuel Consumption by Type (dict)", "type": "text", "required": True, "unit": ""}, 
                        {"key": "EF_i", "label": "Emission Factor by Fuel Type (dict)", "type": "text", "required": True, "unit": ""}, 
                        {"key": "m_set", "label": "Set of Fuel Types (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Emissions of Pollutant i (kg or g)"
                }
            ],
            "Road": [
                { # Only Tier Available: Eu_eq_1 (Distance-Based Fuel Consumption)
                    "tier_level": "Single Tier (Distance-Based Fuel Consumption)",
                    "tier_id": "Eu_eq_1",
                    "inputs": [
                        {"key": "EF", "label": "Emission Factor (g)", "type": "text", "required": True, "unit": "g"},
                        {"key": "Fuel_Total", "label": "Total Fuel Consumed", "type": "text", "required": True, "unit": "mass/volume"},
                        {"key": "D_Total", "label": "Total Distance Traveled (km)", "type": "text", "required": True, "unit": "km"},
                    ],
                    "output_label": "Carbon Emissions (g CO₂/km)"
                }
            ]
        },
        #Next is Asia which only contains China's different fleet types
        "China": {
            "Aviation": [
                { # Only Tier Available (Acts as Default)
                    "tier_level": "Basic Fuel Consumption (Single Tier)",
                    "tier_id": "China_eq_1",
                    "inputs": [
                        {"key": "fuel_consumption", "label": "Fuel Consumption", "type": "text", "required": True, "unit": "unit of fuel"},
                        {"key": "emission_factor", "label": "Emission Factor", "type": "text", "required": True, "unit": "mass/unit of fuel"},
                    ],
                    "output_label": "Total Emissions"
                }
            ],
            "Marine": [
                { # 1. Highest Tier (Default): CHINA_eq_2 (Multiple Trips Aggregation)
                    "tier_level": "Highest Tier (Aggregated Trips)",
                    "tier_id": "CHINA_eq_2",
                    "inputs": [
                        {"key": "F_list", "label": "Fuel Consumptions (list)", "type": "text", "required": True, "unit": "liters or MJ"},
                        {"key": "EF_list", "label": "Emission Factors (list)", "type": "text", "required": True, "unit": "kg CO₂/unit"},
                    ],
                    "output_label": "Total Aggregated CO₂ Emissions (kg CO₂)"
                },
                { # 2. Lowest Tier (Fallback): CHINA_eq_1 (Single Trip Calculation)
                    "tier_level": "Lowest Tier (Single Trip)",
                    "tier_id": "CHINA_eq_1",
                    "inputs": [
                        {"key": "F", "label": "Fuel Consumption for Trip (liters or MJ)", "type": "text", "required": True, "unit": "liters or MJ"},
                        {"key": "EF", "label": "Emission Factor (kg CO₂/unit)", "type": "text", "required": True, "unit": "kg CO₂/unit"},
                    ],
                    "output_label": "CO₂ Emissions for Single Trip (kg CO₂)"
                }
            ],
            "Railroad": [
                { # Only Tier Available (Acts as Default): China_eq_1 (Locomotive Usage)
                    "tier_level": "Highest Tier (Locomotive Usage Methodology)",
                    "tier_id": "China_eq_1",
                    "inputs": [
                        # Inputs are complex dictionaries/lists required by the summation formula in Scope1View.py
                        {"key": "N", "label": "Number of Trains (dict)", "type": "text", "required": True, "unit": ""}, 
                        {"key": "H", "label": "Hours of Operation (dict)", "type": "text", "required": True, "unit": "hours"}, 
                        {"key": "P", "label": "Capacity (dict)", "type": "text", "required": True, "unit": "passenger/cargo"}, 
                        {"key": "LF", "label": "Load Factor (dict, 0-1)", "type": "text", "required": True, "unit": ""}, 
                        {"key": "EF", "label": "Emission Factor (dict)", "type": "text", "required": True, "unit": "kg/MJ or kg/fuel"}, 
                        {"key": "segments", "label": "Route Segments (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Estimated Emissions (kg or g)"
                }
            ],
            "Road": [
                # --------------------------------------------------------------------------
                # EXCLUDED EQUATIONS NOTE for Tier Prioritization:
                # The following China Road equations are EXCLUDED from this primary tiered list 
                # because they either calculate CO2 using specialized methods or are not standalone tiers:
                # 
                # 1. China_eq_6: Validation/Estimation placeholder (Not a final calculation tier)
                # 2. China_eq_7, China_eq_8, China_eq_9: Redundant Tier structures that duplicate 
                #    the calculation logic of the prioritized Tiers 1, 2, and 3 (China_eq_3, 4, 5).
                # --------------------------------------------------------------------------
                { # 1. Highest Tier (Default): China_eq_5 (Tier 3 - N2O/CH4)
                    "tier_level": "Highest Tier (Tier 3 - Distance/Warm-Up)",
                    "tier_id": "China_eq_5",
                    "inputs": [
                        # NOTE: These dictionaries must be indexed by sets A, B, C, and D.
                        {"key": "EF", "label": "Emission Factor (Dict: Indexed by A, B, C, D)", "type": "text", "required": True, "unit": "kg/TJ"},
                        {"key": "Distance", "label": "Stabilized Distance Traveled (Dict)", "type": "text", "required": True, "unit": "km"},
                        {"key": "Warm_Up", "label": "Warm-Up Emissions (Dict)", "type": "text", "required": True, "unit": "kg"},
                        {"key": "A_set", "label": "Fuel Types (list)", "type": "text", "required": True, "unit": ""},
                        {"key": "B_set", "label": "Vehicle Types (list)", "type": "text", "required": True, "unit": ""},
                        {"key": "C_set", "label": "Control Technologies (list)", "type": "text", "required": True, "unit": ""},
                        {"key": "D_set", "label": "Operating Conditions (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Estimated Emissions (kg)"
                },
                { # 2. Fallback 1: China_eq_4 (Tier 2 - N2O/CH4)
                    "tier_level": "Fallback 1 (Tier 2 - Fuel/Vehicle/Control)",
                    "tier_id": "China_eq_4",
                    "inputs": [
                        # Dictionaries must be indexed by sets A, B, and C.
                        {"key": "EF", "label": "Emission Factor (Dict: Indexed by A, B, C)", "type": "text", "required": True, "unit": "kg/TJ"},
                        {"key": "Fuel", "label": "Fuel Consumed (Dict: Indexed by A, B, C)", "type": "text", "required": True, "unit": "TJ"},
                        {"key": "A_set", "label": "Fuel Types (list)", "type": "text", "required": True, "unit": ""},
                        {"key": "B_set", "label": "Vehicle Types (list)", "type": "text", "required": True, "unit": ""},
                        {"key": "C_set", "label": "Control Technologies (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Estimated Emissions (kg)"
                },
                { # 3. Fallback 2: China_eq_1 (CO2 - Preservation Method)
                    "tier_level": "Fallback 2 (CO₂ Preservation Method - Vehicle Count)",
                    "tier_id": "China_eq_1",
                    "inputs": [
                        {"key": "P", "label": "Number of Vehicles", "type": "text", "required": True, "unit": ""},
                        {"key": "F_E", "label": "Fuel Efficiency (liters/km)", "type": "text", "required": True, "unit": "liters/km"},
                        {"key": "VKT", "label": "Velocity Kilometers Traveled (VKT)", "type": "text", "required": True, "unit": "km"},
                        {"key": "EF", "label": "Emission Factor (kg CO2/liter)", "type": "text", "required": True, "unit": "kg CO2/liter"},
                    ],
                    "output_label": "Total Emissions (mass)"
                },
                { # 4. Fallback 3: China_eq_2 (CO2 - Cycle Conversion/Passenger)
                    "tier_level": "Fallback 3 (CO₂ Passenger KM Method)",
                    "tier_id": "China_eq_2",
                    "inputs": [
                        {"key": "PKM", "label": "Passenger Kilometers (PKM)", "type": "text", "required": True, "unit": "km"},
                        {"key": "FE_PKM", "label": "Energy Consumption per PKM (MJ/PKM)", "type": "text", "required": True, "unit": "MJ/PKM"},
                        {"key": "EF", "label": "CO₂ Emission Factor (kg CO2/MJ)", "type": "text", "required": True, "unit": "kg CO2/MJ"},
                    ],
                    "output_label": "Total Emissions (mass)"
                },
                { # 5. Lowest Fallback: China_eq_3 (Tier 1 - N2O/CH4)
                    "tier_level": "Lowest Tier (Tier 1 - Basic Fuel Type)",
                    "tier_id": "China_eq_3",
                    "inputs": [
                        # Dictionaries must be indexed by set A only.
                        {"key": "EF", "label": "Emission Factor (Dict: Indexed by Fuel Type)", "type": "text", "required": True, "unit": "kg/TJ"},
                        {"key": "Fuel", "label": "Fuel Consumed (Dict: Indexed by Fuel Type)", "type": "text", "required": True, "unit": "TJ"},
                        {"key": "A_set", "label": "Fuel Types (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Estimated Emissions (kg)"
                }
            ]
        },
        "Africa": { 
            "Aviation": [
                { # 1. Highest Tier (Default): Africa_eq_2 (LTO/Cruise Split)
                    "tier_level": "Highest Tier (LTO/Cruise Phase Split)",
                    "tier_id": "Africa_eq_2",
                    "inputs": [
                        {"key": "fuel_LTO", "label": "Fuel Consumption - LTO Phase", "type": "text", "required": True, "unit": "unit of fuel"},
                        {"key": "EF_LTO", "label": "EF - LTO Phase", "type": "text", "required": True, "unit": "mass/unit of fuel"},
                        {"key": "fuel_cruise", "label": "Fuel Consumption - Cruise Phase", "type": "text", "required": True, "unit": "unit of fuel"},
                        {"key": "EF_cruise", "label": "EF - Cruise Phase", "type": "text", "required": True, "unit": "mass/unit of fuel"},
                    ],
                    "output_label": "Emissions by Phase (LTO, Cruise, Total)"
                },
                { # 2. Lowest Tier (Fallback): Africa_eq_1 (Basic Fuel-Based)
                    "tier_level": "Lowest Tier (Basic Fuel-Based Calculation)",
                    "tier_id": "Africa_eq_1",
                    "inputs": [
                        {"key": "fuel_consumption", "label": "Total Fuel Consumption", "type": "text", "required": True, "unit": "unit of fuel"},
                        {"key": "emission_factor", "label": "Emission Factor", "type": "text", "required": True, "unit": "mass/unit of fuel"},
                    ],
                    "output_label": "Total Emissions"
                }
            ],
            "Marine": [
                { # Only Tier Available (Acts as Default)
                    "tier_level": "Highest Tier (Aggregated Fuel/Mode)",
                    "tier_id": "Africa_eq_1",
                    "inputs": [
                        {"key": "Fuel_Consumed", "label": "Fuel Consumed (Dict: by Fuel/Mode)", "type": "text", "required": True, "unit": "tons or liters"}, 
                        {"key": "Emission_Factor", "label": "Emission Factor (Dict: by Fuel/Mode)", "type": "text", "required": True, "unit": "kg CO₂/unit"}, 
                    ],
                    "output_label": "Total CO₂ Emissions (kg CO₂)"
                }
            ],
            "Railroad": [
                { # 1. Highest Tier (Default): Africa_eq_3 (Tier 3 - Locomotive Usage)
                    "tier_level": "Highest Tier (Tier 3 - Locomotive Usage)",
                    "tier_id": "Africa_eq_3",
                    "inputs": [
                        {"key": "N", "label": "Number of Locomotives (dict)", "type": "text", "required": True, "unit": ""}, 
                        {"key": "H", "label": "Annual Hours of Use (dict)", "type": "text", "required": True, "unit": "hours"}, 
                        {"key": "P", "label": "Rated Power (dict)", "type": "text", "required": True, "unit": "kW"}, 
                        {"key": "LF", "label": "Load Factor (dict, 0-1)", "type": "text", "required": True, "unit": ""}, 
                        {"key": "EF", "label": "Emission Factor (dict)", "type": "text", "required": True, "unit": "kg/kWh"}, 
                        {"key": "i_set", "label": "Locomotive Types (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Estimated Emissions (kg)"
                },
                { # 2. Fallback 1: Africa_eq_2 (Tier 2 - Locomotive Type Fuel)
                    "tier_level": "Fallback 1 (Tier 2 - Locomotive Type Fuel)",
                    "tier_id": "Africa_eq_2",
                    "inputs": [
                        {"key": "Fuel", "label": "Fuel Consumed by Locomotive Type (dict)", "type": "text", "required": True, "unit": "TJ"}, 
                        {"key": "EF", "label": "Emission Factor (dict)", "type": "text", "required": True, "unit": "kg/TJ"}, 
                        {"key": "i_set", "label": "Locomotive Types (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Estimated Emissions (kg)"
                },
                { # 3. Lowest Tier (Fallback): Africa_eq_1 (Tier 1 - Basic Fuel Base)
                    "tier_level": "Lowest Tier (Tier 1 - Basic Fuel Base)",
                    "tier_id": "Africa_eq_1",
                    "inputs": [
                        {"key": "Fuel", "label": "Fuel Consumed by Fuel Type (dict)", "type": "text", "required": True, "unit": "TJ"}, 
                        {"key": "EF", "label": "Emission Factor (dict)", "type": "text", "required": True, "unit": "kg/TJ"}, 
                        {"key": "j_set", "label": "Fuel Types (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Estimated Emissions (kg)"
                }
            ],
            "Road": [
                { # 1. Highest Tier (Default): Africa_eq_1 (Primary CO2 from Fuel Sold)
                    "tier_level": "Highest Tier (Primary CO₂ from Fuel Sold)",
                    "tier_id": "Africa_eq_1",
                    "inputs": [
                        {"key": "Fuel_A", "label": "Fuel Sold (Dict: by type A)", "type": "text", "required": True, "unit": "TJ"}, 
                        {"key": "EF_A", "label": "Emission Factor (Dict: by type A)", "type": "text", "required": True, "unit": "kg/TJ"}, 
                        {"key": "A_Set", "label": "Set of Fuel Types (list)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total CO₂ Emissions (kg)"
                },
                { # 2. Lowest Tier (Fallback): Africa_eq_2 (CO2 from Urea Additives)
                    "tier_level": "Fallback 1 (CO₂ from Urea-Based Catalysts)",
                    "tier_id": "Africa_eq_2",
                    "inputs": [
                        {"key": "A", "label": "Urea-based Additive Consumed (Gg)", "type": "text", "required": True, "unit": "Gg"},
                        {"key": "P", "label": "Purity (Mass Fraction of Urea, 0-1)", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "CO₂ Emissions from Additive (Gg CO₂)"
                }
            ]
        }
    },
    "Scope2": {
        "Europe": {
            # --- CATEGORY 1: MARKET-BASED REPORTING ---
            "Market-Based": [ 
                { # 1. Highest Tier (Default): EU_eq_3 (Market-Based Aggregate)
                    "tier_level": "Highest Tier (Market-Based by Source)",
                    "tier_id": "EU_eq_3",
                    "inputs": [
                        {"key": "A_set", "label": "Set of Energy Sources (list)", "type": "text", "required": True, "unit": ""},
                        {"key": "EF", "label": "Emission Factor per Source (dict)", "type": "text", "required": True, "unit": "kg/MWh"},
                        {"key": "EC", "label": "Consumption per Source (dict)", "type": "text", "required": True, "unit": "MWh"},
                    ],
                    "output_label": "Total Scope 2 Emissions (Market-Based)"
                },
                { # 2. Lowest Fallback: EU_eq_1 (Location-Based Grid Mix)
                    "tier_level": "Lowest Tier (Location-Based Grid Mix)",
                    "tier_id": "EU_eq_1",
                    "inputs": [
                        {"key": "EC", "label": "Total Electricity Consumption (MWh)", "type": "text", "required": True, "unit": "MWh"},
                        {"key": "GAEF", "label": "Grid Average Emission Factor (kg/MWh)", "type": "text", "required": True, "unit": "kg/MWh"},
                    ],
                    "output_label": "Total Scope 2 Emissions (Location-Based)"
                },
            ],
            # --- CATEGORY 2: LOCATION-BASED REPORTING ---
            "Location-Based": [ 
                { # 1. Highest Tier (Default): EU_eq_1 (Location-Based Grid Mix)
                    "tier_level": "Highest Tier (Location-Based Grid Mix)",
                    "tier_id": "EU_eq_1",
                    "inputs": [
                        {"key": "EC", "label": "Total Electricity Consumption (MWh)", "type": "text", "required": True, "unit": "MWh"},
                        {"key": "GAEF", "label": "Grid Average Emission Factor (kg/MWh)", "type": "text", "required": True, "unit": "kg/MWh"},
                    ],
                    "output_label": "Total Scope 2 Emissions (Location-Based)"
                },
                { # 2. Fallback 1: EU_eq_2 (Regional Consumption Estimation)
                    "tier_level": "Fallback 1 (Regional Consumption Estimation)",
                    "tier_id": "EU_eq_2",
                    "inputs": [
                        {"key": "SF", "label": "Building Square Footage", "type": "text", "required": True, "unit": "Sq Ft"},
                        {"key": "kWh", "label": "kWh per Sq ft (Avg Consumption Rate)", "type": "text", "required": True, "unit": "kWh/Sq Ft"},
                        {"key": "Sq_ft", "label": "Scaling Factor", "type": "text", "required": True, "unit": ""},
                    ],
                    "output_label": "Total Electricity Consumption (MWh)"
                },
                { # 3. Lowest Fallback (Final): Uni_eq_6 (Generalized Estimation)
                    "tier_level": "Lowest Tier (Generalized MWh Calculation)",
                    "tier_id": "Uni_eq_6",
                    "inputs": [
                        {"key": "square_footage", "label": "Building Square Footage", "type": "text", "required": True, "unit": "Sq Ft"},
                        {"key": "kWh_per_sqft", "label": "kWh per Square foot (Rate)", "type": "text", "required": True, "unit": "kWh/Sq Ft"},
                    ],
                    "output_label": "Total Electricity Consumption (MWh)"
                },
            ]
        },
        "North America": {
            "Location-Based": [
                { # 1. Highest Tier (Default): NA_eq_2 (eGRID-Based Rate)
                    "tier_level": "Highest Tier (eGRID/Regional Emission Rate)",
                    "tier_id": "NA_eq_2",
                    "inputs": [
                        {"key": "electricity_usage", "label": "Electricity Consumed (MWh)", "type": "text", "required": True, "unit": "MWh"},
                        {"key": "EF", "label": "eGRID Emission Factor (lbs/MWh)", "type": "text", "required": True, "unit": "lbs/MWh"},
                    ],
                    "output_label": "Total Emissions (lbs)"
                },
                { # 2. Lowest Tier (Fallback): NA_eq_1 (Multi-Pollutant Factor)
                    "tier_level": "Lowest Tier (Multi-Pollutant Factor)",
                    "tier_id": "NA_eq_1",
                    "inputs": [
                        {"key": "electricity", "label": "Total Electricity Purchased", "type": "text", "required": True, "unit": "MWh/kWh"},
                        {"key": "EF", "label": "Emission Factors (dict: CO2, CH4, N2O)", "type": "text", "required": True, "unit": "lb/MWh or kg/kWh"},
                    ],
                    "output_label": "Emissions by Pollutant (dict)"
                },
            ]
        },
        "Asia": {
            # --- CATEGORY 1: MARKET-BASED REPORTING ---
            # This path prioritizes tracking specific contractual attributes.
            "Market-Based": [
                { # 1. Highest Tier (Default): Asia_eq_1 (Contract Source Factor)
                    "tier_level": "Highest Tier (Market-Based Factor)",
                    "tier_id": "Asia_eq_1",
                    "inputs": [
                        {"key": "kWh", "label": "Electricity Used (kWh)", "type": "text", "required": True, "unit": "kWh"},
                        {"key": "contract_source_EF", "label": "Contract Source Emissions Factor", "type": "text", "required": True, "unit": "kg/kWh"},
                    ],
                    "output_label": "Total Scope 2 Emissions (kg)"
                },
                { # 2. Lowest Tier (Fallback): Asia_eq_2 (Local Grid Factor)
                    # This serves as the Residual Mix fallback, using the Location-Based factor.
                    "tier_level": "Lowest Tier (Location-Based Grid Mix)",
                    "tier_id": "Asia_eq_2",
                    "inputs": [
                        {"key": "kWh", "label": "Electricity Used (kWh)", "type": "text", "required": True, "unit": "kWh"},
                        {"key": "local_grid_EF", "label": "Local Grid Emissions Factor", "type": "text", "required": True, "unit": "kg/kWh"},
                    ],
                    "output_label": "Total Scope 2 Emissions (kg)"
                },
            ],
            
            # --- CATEGORY 2: LOCATION-BASED REPORTING ---
            # This path focuses on the general grid average, with no further fallback available.
            "Location-Based": [
                { # 1. Only Tier (Default): Asia_eq_2 (Local Grid Factor)
                    "tier_level": "Highest Tier (Location-Based Grid Mix)",
                    "tier_id": "Asia_eq_2",
                    "inputs": [
                        {"key": "kWh", "label": "Electricity Used (kWh)", "type": "text", "required": True, "unit": "kWh"},
                        {"key": "local_grid_EF", "label": "Local Grid Emissions Factor", "type": "text", "required": True, "unit": "kg/kWh"},
                    ],
                    "output_label": "Total Scope 2 Emissions (kg)"
                }
                # Fallback is disabled as there are no simpler regional or estimation methods available.
            ]
        }   
    },
    # -------------------------------------------------------------------------
    # SCOPE 3: VALUE CHAIN EMISSIONS (Tiered by Data Quality)
    # -------------------------------------------------------------------------
    "Scope3": {
        "Europe": { # Region is locked to Europe (EU) for initial implementation
            "Purchased Goods": [
                { # 1. Highest Tier (Default): Supplier-specific Method
                    "tier_level": "Highest Tier (Supplier-Specific)",
                    "tier_id": "S3_PG_Supplier_eq_1",
                    "inputs": [
                        {"key": "quantity", "label": "Quantity Purchased (e.g., kg, units)", "type": "text", "required": True},
                        {"key": "emission_factor", "label": "Supplier EF (kg CO₂e/unit)", "type": "text", "required": True},
                        {"key": "supplier_reported_emissions", "label": "Supplier Reported Scope 1 & 2 Data", "type": "text", "required": False} 
                    ],
                    "output_label": "Total CO₂e Emissions (kg)"
                },
                { # 2. Fallback 1: Hybrid Method
                    "tier_level": "Fallback 1 (Hybrid Method)",
                    "tier_id": "S3_PG_Hybrid_eq_1",
                    "inputs": [
                        {"key": "supplier_scope_data", "label": "Supplier Scope 1 & 2 Data (from suppliers)", "type": "text", "required": False},
                        {"key": "activity_based_emissions", "label": "Activity Based Emissions (dict for materials/fuel)", "type": "text", "required": True},
                        {"key": "secondary_estimations", "label": "Secondary Data Estimations (dict for gaps)", "type": "text", "required": False},
                    ],
                    "output_label": "Total CO₂e Emissions (kg)"
                },
                { # 3. Fallback 2: Average-data Method
                    "tier_level": "Fallback 2 (Average-data Method)",
                    "tier_id": "S3_PG_Average_eq_1",
                    "inputs": [
                        {"key": "quantity_purchased", "label": "Quantity Purchased (e.g., kg, liters)", "type": "text", "required": True},
                        {"key": "average_emission_factor", "label": "Industry Average EF (kg CO₂e/unit)", "type": "text", "required": True},
                    ],
                    "output_label": "Total CO₂e Emissions (kg)"
                },
                { # 4. Lowest Fallback: Spend-based Method
                    "tier_level": "Lowest Tier (Spend-based Method)",
                    "tier_id": "S3_PG_Spend_eq_1",
                    "inputs": [
                        {"key": "amount_spent", "label": "Amount Spent ($)", "type": "text", "required": True},
                        {"key": "industry_emission_factor", "label": "Industry EF (kg CO₂e/$)", "type": "text", "required": True},
                    ],
                    "output_label": "Total CO₂e Emissions (kg)"
                },
            ],
            "Upstream Fuels": [
                { # 1. Highest Tier (Default): S3_UF_Supplier_eq_1
                    "tier_level": "Highest Tier (Supplier-specific)",
                    "tier_id": "S3_UF_Supplier_eq_1",
                    "inputs": [
                        {"key": "fuel_consumption", "label": "Fuel Consumed (unit)", "type": "text", "required": True},
                        {"key": "upstream_emissions_factor", "label": "Supplier Upstream EF (kg CO₂e/unit)", "type": "text", "required": True},
                    ],
                    "output_label": "Upstream CO₂e Emissions (kg)"
                },
                { # 2. Lowest Fallback: S3_UF_Average_eq_1
                    "tier_level": "Lowest Tier (Average-data)",
                    "tier_id": "S3_UF_Average_eq_1",
                    "inputs": [
                        {"key": "fuel_consumption", "label": "Fuel Consumed (unit)", "type": "text", "required": True},
                        {"key": "average_upstream_factor", "label": "Industry Average Upstream EF (kg CO₂e/unit)", "type": "text", "required": True},
                    ],
                    "output_label": "Upstream CO₂e Emissions (kg)"
                },
            ],
            "T&D Losses": [
                { # 1. Highest Tier (Default): S3_TD_Supplier_eq_1
                    "tier_level": "Highest Tier (Supplier-specific)",
                    "tier_id": "S3_TD_Supplier_eq_1",
                    "inputs": [
                        {"key": "electricity_consumed", "label": "Electricity Consumed (kWh/MWh)", "type": "text", "required": True},
                        {"key": "td_loss_rate", "label": "Supplier T&D Loss Rate (%)", "type": "text", "required": True},
                        {"key": "grid_ef", "label": "Grid Emission Factor (kg CO₂e/unit)", "type": "text", "required": True},
                    ],
                    "output_label": "T&D Loss CO₂e Emissions (kg)"
                },
                { # 2. Lowest Fallback: S3_TD_Average_eq_1
                    "tier_level": "Lowest Tier (Average-data)",
                    "tier_id": "S3_TD_Average_eq_1",
                    "inputs": [
                        {"key": "electricity_consumed", "label": "Electricity Consumed (kWh/MWh)", "type": "text", "required": True},
                        {"key": "avg_td_loss_rate", "label": "Average T&D Loss Rate (%)", "type": "text", "required": True},
                        {"key": "grid_ef", "label": "Grid Emission Factor (kg CO₂e/unit)", "type": "text", "required": True},
                    ],
                    "output_label": "T&D Loss CO₂e Emissions (kg)"
                },
            ],
            "Upstream Electricity": [
                { # 1. Highest Tier (Default): S3_UE_Supplier_eq_1
                    "tier_level": "Highest Tier (Supplier-specific)",
                    "tier_id": "S3_UE_Supplier_eq_1",
                    "inputs": [
                        {"key": "electricity_consumed", "label": "Electricity Consumed (kWh/MWh)", "type": "text", "required": True},
                        {"key": "upstream_ef", "label": "Supplier Upstream EF (kg CO₂e/kWh)", "type": "text", "required": True},
                    ],
                    "output_label": "Upstream CO₂e Emissions (kg)"
                },
                { # 2. Lowest Fallback: S3_UE_Average_eq_1
                "tier_level": "Lowest Tier (Average-data)",
                "tier_id": "S3_UE_Average_eq_1",
                "inputs": [
                        {"key": "electricity_consumed", "label": "Electricity Consumed (kWh/MWh)", "type": "text", "required": True},
                        {"key": "average_upstream_ef", "label": "Industry Average Upstream EF (kg CO₂e/kWh)", "type": "text", "required": True},
                    ],
                "output_label": "Upstream CO₂e Emissions (kg)"
                },
            ]
        }
    },
    "Scope4": {
        "Global": { # Region is Global as per documentation
            # CATEGORY 1: EVs Replacing Fossil Cars
            "EVs Replacing Fossil Cars": [
                { # Only Tier Available (Default): Differential Formula
                    "tier_level": "Primary Calculation",
                    "tier_id": "CalculateEVsReplacingDieselCars",
                    "inputs": [
                        {"key": "E_fuel", "label": "Fossil Fuel Emissions (kg CO₂e/km)", "type": "text", "required": True, "unit": "kg CO₂e/km"},
                        {"key": "E_EV", "label": "EV Emissions (Grid Mix) (kg CO₂e/km)", "type": "text", "required": True, "unit": "kg CO₂e/km"},
                        {"key": "D_travelled", "label": "Distance Travelled by EVs (km)", "type": "text", "required": True, "unit": "km"},
                    ],
                    "output_label": "Avoided Emissions (kg CO₂e)"
                }
            ],
            
            # CATEGORY 2: Sustainable Aviation Fuels (SAF)
            "SAF Replacing Jet Fuel": [
                { # Only Tier Available (Default): Differential Formula
                    "tier_level": "Primary Calculation",
                    "tier_id": "CalculateSAFReplacingJetFuel",
                    "inputs": [
                        {"key": "V_SAF", "label": "Volume of SAF used (liters)", "type": "text", "required": True, "unit": "liters"},
                        {"key": "E_jetfuel", "label": "Conventional Jet Fuel EF (kg CO₂e/liter)", "type": "text", "required": True, "unit": "kg CO₂e/liter"},
                        {"key": "E_SAF", "label": "SAF Emission Factor (kg CO₂e/liter)", "type": "text", "required": True, "unit": "kg CO₂e/liter"},
                    ],
                    "output_label": "Avoided Emissions (kg CO₂e)"
                }
            ],
            
            # CATEGORY 3: High-Speed Rail & Public Transit Shift
            "Rail Transit Shift": [
                { # Only Tier Available (Default): Differential Formula
                    "tier_level": "Primary Calculation",
                    "tier_id": "CalculateRailTransitShiftAvoidedEmissions",
                    "inputs": [
                        {"key": "E_car", "label": "Emissions per passenger-km for cars", "type": "text", "required": True, "unit": "kg CO₂e/pkm"},
                        {"key": "E_rail", "label": "Emissions per passenger-km for rail", "type": "text", "required": True, "unit": "kg CO₂e/pkm"},
                        {"key": "P_shifted", "label": "Number of passengers shifted", "type": "text", "required": True, "unit": "passengers"},
                    ],
                    "output_label": "Avoided Emissions (kg CO₂e)"
                }
            ],
            
            # CATEGORY 4: Green Hydrogen Replacing Fossil Fuels
            "Green Hydrogen Replacing Fossil Fuels": [
                { # Only Tier Available (Default): Differential Formula
                    "tier_level": "Primary Calculation",
                    "tier_id": "CalculateGreenHydrogenReplacingFossilFuels",
                    "inputs": [
                        {"key": "Hused", "label": "Total Hydrogen Consumed (kg)", "type": "text", "required": True, "unit": "kg"},
                        {"key": "Efossil", "label": "EF for Fossil Fuel Replaced (kg CO₂/kg)", "type": "text", "required": True, "unit": "kg CO₂/kg"},
                        {"key": "EH2", "label": "EF for Hydrogen (kg CO₂/kg H₂)", "type": "text", "required": True, "unit": "kg CO₂/kg H₂"},
                    ],
                    "output_label": "Avoided Emissions (kg CO₂e)"
                }
            ],
            
            # CATEGORY 5: Work-from-Home Emissions Reduction
            "Work-from-Home Emissions Reduction": [
                { # Only Tier Available (Default): Aggregation Formula
                    "tier_level": "Primary Calculation",
                    "tier_id": "CalculateWorkFromHomeAvoidedEmissions",
                    "inputs": [
                        {"key": "N_employees", "label": "Number of employees working remotely", "type": "text", "required": True, "unit": ""},
                        {"key": "E_commute", "label": "CO₂ emissions per employee commute (kg/day)", "type": "text", "required": True, "unit": "kg/day"},
                        {"key": "D_remote", "label": "Number of remote workdays per year", "type": "text", "required": True, "unit": "days"},
                    ],
                    "output_label": "Avoided Emissions (kg CO₂e)"
                }
            ],

            # CATEGORY 6: CO2 Capture and Sequestration
            "CO₂ Capture and Sequestration": [
                { # Only Tier Available (Default): Aggregation Formula
                    "tier_level": "Primary Calculation",
                    "tier_id": "CalculateCO2CaptureAndSequestration",
                    "inputs": [
                        {"key": "Ccaptured", "label": "Total CO₂ Captured (metric tons)", "type": "text", "required": True, "unit": "metric tons"},
                        {"key": "Sefficiency", "label": "Storage Efficiency Factor (%)", "type": "text", "required": True, "unit": "%"},
                    ],
                    "output_label": "Avoided Emissions (kg CO₂e)"
                }
            ],
            
            # NOTE: Other Scope 4 methods (Renewable Energy, Energy Efficiency, Process Heat Recovery, Recycling) 
            # should be added here once their calculation method names are confirmed from the backend views.
        }
    }    
}
