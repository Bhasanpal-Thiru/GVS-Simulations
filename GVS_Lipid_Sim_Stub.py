# GVS_Lipid_Sim_Stub.py
# Coarse-Grained Monte Carlo Stub: Membrane Yield EoS & General Anesthesia

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def generate_lipid_lattice(N_nodes=2000, z_target=6.0):
    """
    Generates a quasi-2D random geometric graph to simulate the 
    neuronal lipid bilayer. Target valency (z) for a stable 2D fluid is ~6.0.
    """
    print(f"Initializing quasi-2D lipid lattice with {N_nodes} nodes...")
    # Radius calculated to approximate the target coordination valency
    radius = np.sqrt(z_target / (np.pi * N_nodes))
    G = nx.random_geometric_graph(N_nodes, radius)
    
    # Prune isolated nodes to ensure a contiguous membrane
    G.remove_nodes_from(list(nx.isolates(G)))
    return G

def embed_anesthetic_defects(G, log_P, concentration, scaling_factor=1.5):
    """
    Simulates the Meyer-Overton Equation of State.
    Defect volume and lattice displacement scale strictly with log P.
    """
    G_defected = G.copy()
    
    # Number of topological defects scales with concentration and lipid solubility
    num_defects = int(concentration * log_P * scaling_factor)
    if num_defects > G_defected.number_of_nodes():
        num_defects = G_defected.number_of_nodes()
        
    nodes = list(G_defected.nodes())
    defect_targets = np.random.choice(nodes, num_defects, replace=False)
    
    for node in defect_targets:
        # Embedding the defect physically displaces neighboring lipid nodes,
        # simulated here by dropping elastodynamic causal links.
        neighbors = list(G_defected.neighbors(node))
        if neighbors:
            # High log P molecules break more local connections (higher displacement)
            break_fraction = min(1.0, (log_P / 5.0)) 
            edges_to_break = [(node, neighbor) for neighbor in neighbors[:int(len(neighbors) * break_fraction)]]
            G_defected.remove_edges_from(edges_to_break)
            
    return G_defected

# --- Simulation Parameters ---
# Empirical log P values (Oil:Gas partition proxy)
log_P_xenon = 1.9
log_P_isoflurane = 2.4

concentrations = np.linspace(0, 1500, 20)
valency_xenon = []
valency_isoflurane = []

# Generate the baseline biological substrate
G_membrane = generate_lipid_lattice(N_nodes=2000, z_target=6.0)
baseline_z = np.mean([d for n, d in G_membrane.degree()])
print(f"Baseline Membrane Valency (z): {baseline_z:.2f}")

print("Simulating topological defect embedding...")
for conc in concentrations:
    # Simulate Xenon embedding
    G_xe = embed_anesthetic_defects(G_membrane, log_P_xenon, conc)
    z_xe = np.mean([d for n, d in G_xe.degree()]) if G_xe.number_of_nodes() > 0 else 0
    valency_xenon.append(z_xe)
    
    # Simulate Isoflurane embedding
    G_iso = embed_anesthetic_defects(G_membrane, log_P_isoflurane, conc)
    z_iso = np.mean([d for n, d in G_iso.degree()]) if G_iso.number_of_nodes() > 0 else 0
    valency_isoflurane.append(z_iso)

# --- Plotting the Geometric Phase Transition ---
plt.figure(figsize=(10, 6))

# CORRECTED: Added 'rf' prefix to treat LaTeX slashes cleanly while using f-strings
plt.plot(concentrations, valency_xenon, 'b-o', label=rf'Xenon ($\log P = {log_P_xenon}$)', alpha=0.8)
plt.plot(concentrations, valency_isoflurane, 'r-s', label=rf'Isoflurane ($\log P = {log_P_isoflurane}$)', alpha=0.8)

# The critical valency threshold (shatter-point) where 
# macroscopic rigidity fails and ion channels uncouple.
z_crit = 3.5 

# CORRECTED: Added 'rf' prefix to handle \approx properly
plt.axhline(y=z_crit, color='k', linestyle='--', linewidth=2, label=rf'Critical Yield Limit ($z_{{crit}} \approx {z_crit}$)')

plt.title('General Anesthesia: Topological Defect Concentration vs. Membrane Valency', fontsize=14)
plt.xlabel('Anesthetic Concentration (Arbitrary Units)', fontsize=12)
plt.ylabel('Average Coordination Valency ($z$)', fontsize=12)
plt.axhspan(0, z_crit, color='gray', alpha=0.2, label='Anesthetic State (Lattice Shattered)')
plt.legend(loc='upper right', fontsize=11)
plt.grid(True, linestyle=':', alpha=0.6)

plt.savefig('GVS_Anesthesia_Yield.png', dpi=300, bbox_inches='tight')
print("Simulation complete. Plot saved as 'GVS_Anesthesia_Yield.png'.")

