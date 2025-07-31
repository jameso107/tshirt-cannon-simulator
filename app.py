import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Constants
air_density = 1.225
Cd = 0.5
g = 9.81
barrel_diameter_in = 2.75
barrel_length_in = 24
barrel_diameter_m = barrel_diameter_in * 0.0254
barrel_length_m = barrel_length_in * 0.0254
barrel_area = math.pi * (barrel_diameter_m / 2) ** 2

# Objects
objects = {
    "T-shirt": {"mass": 0.170, "diam": 0.07},
    "Stress Ball": {"mass": 0.040, "diam": 0.07}
}

TARGET_RANGE_FT = 200
TARGET_RANGE_M = TARGET_RANGE_FT * 0.3048

def muzzle_velocity_ideal(mass, pressure_psi):
    pressure_pa = pressure_psi * 6894.76
    work = pressure_pa * barrel_area * barrel_length_m
    return math.sqrt((2 * work) / mass)

def simulate_range(mass, diameter, v0, angle_deg):
    A = math.pi * (diameter / 2) ** 2
    k = 0.5 * air_density * Cd * A
    angle = math.radians(angle_deg)
    vx, vy = v0 * math.cos(angle), v0 * math.sin(angle)
    x, y = 0, 0
    dt = 0.01
    while y >= 0:
        speed = math.sqrt(vx**2 + vy**2)
        drag = k * speed**2
        ax = -(drag / mass) * (vx / speed)
        ay = -(drag / mass) * (vy / speed) - g
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
    return x

# Calibrate friction factor for T-shirt
ideal_v_tshirt = muzzle_velocity_ideal(objects["T-shirt"]["mass"], 100)
low, high = 0.01, 1.0
for _ in range(100):
    mid = (low + high) / 2
    if simulate_range(objects["T-shirt"]["mass"], objects["T-shirt"]["diam"], ideal_v_tshirt * mid, 45) > TARGET_RANGE_M:
        high = mid
    else:
        low = mid
friction_factor_tshirt = (low + high) / 2

def simulate_trajectory(mass, diameter, v0, angle_deg):
    A = math.pi * (diameter / 2) ** 2
    k = 0.5 * air_density * Cd * A
    angle = math.radians(angle_deg)
    vx, vy = v0 * math.cos(angle), v0 * math.sin(angle)
    x, y = 0, 0
    dt = 0.01
    xs, ys = [], []
    while y >= 0:
        xs.append(x)
        ys.append(y)
        speed = math.sqrt(vx**2 + vy**2)
        drag = k * speed**2
        ax = -(drag / mass) * (vx / speed)
        ay = -(drag / mass) * (vy / speed) - g
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
    return np.array(xs) * 3.281, np.array(ys) * 3.281  # in ft

# --- STREAMLIT APP ---
st.title("Projectile Launcher Simulation")
psi = st.slider("Pressure (PSI)", 40, 120, 100, step=5)
angle = st.slider("Launch Angle (°)", 10, 60, 45, step=1)
stress_friction_factor = st.slider("Stress Ball Friction Factor (relative)", 0.3, 1.0, 0.5, step=0.05)

fig = go.Figure()

# T-shirt trajectory
v_tshirt = muzzle_velocity_ideal(objects["T-shirt"]["mass"], psi) * friction_factor_tshirt
x_tshirt, y_tshirt = simulate_trajectory(objects["T-shirt"]["mass"], objects["T-shirt"]["diam"], v_tshirt, angle)
fig.add_trace(go.Scatter(x=x_tshirt, y=y_tshirt, mode='lines', name="T-shirt"))

# Stress Ball trajectory
v_stress = muzzle_velocity_ideal(objects["Stress Ball"]["mass"], psi) * stress_friction_factor
x_stress, y_stress = simulate_trajectory(objects["Stress Ball"]["mass"], objects["Stress Ball"]["diam"], v_stress, angle)
fig.add_trace(go.Scatter(x=x_stress, y=y_stress, mode='lines', name="Stress Ball"))

fig.update_layout(
    title=f"Flight Paths at {psi} PSI, {angle}°",
    xaxis_title="Horizontal Distance (ft)",
    yaxis_title="Height (ft)",
    template="plotly_dark",
    width=800,
    height=500
)

st.plotly_chart(fig)
