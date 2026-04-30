import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Page config
st.set_page_config(page_title="Big M Visualizer", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #ececec; }
    [data-testid="stMetricValue"] { color: #007bff !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #333333 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Big M Method — Interactive Visualizer")

# --- Sidebar: All Parameters ---
st.sidebar.header("🛠️ Model Parameters")
st.sidebar.subheader("📦 Product 2 (Big M applied)")
M_val = st.sidebar.slider("Big M value (M)", 100, 20000, 10000, 100)
fixed_cost_2 = st.sidebar.slider("Fixed Cost ($)", 0, 3000, 1000)
var_cost_2 = st.sidebar.slider("Variable Cost ($/unit)", 1, 20, 6)
n_limit_2 = st.sidebar.slider("Production Limit (n_max)", 500, 2000, 1000)

st.sidebar.divider()
st.sidebar.subheader("🌐 Overall Target & Other Products")
total_target = st.sidebar.number_input("Total Production Required", value=2100)
c1_unit_cost = st.sidebar.slider("Product 1 Unit Cost ($/unit)", 1.0, 10.0, 2.0)
c3_unit_cost = st.sidebar.slider("Product 3 Unit Cost ($/unit)", 1.0, 15.0, 7.0)

# Validation
min_required_M = var_cost_2 * n_limit_2 + fixed_cost_2
if M_val < min_required_M:
    st.sidebar.warning(f"⚠️ M is too small! Minimum required: ${min_required_M}")
else:
    st.sidebar.success("✅ M value is sufficient.")

# --- Optimization Function ---
def run_optimization(p1_cost, p2_var, p2_fix, p3_cost, n_max_2, total_n, M):
    model = pyo.ConcreteModel()
    model.C = pyo.Var(range(1,4))
    model.n = pyo.Var(range(1,4), within=pyo.Integers, bounds=(0, total_n))
    model.b = pyo.Var(within=pyo.Binary)

    model.obj = pyo.Objective(expr=pyo.summation(model.C), sense=pyo.minimize)
    model.total = pyo.Constraint(expr=pyo.summation(model.n) == total_n)
    model.C1 = pyo.Constraint(expr=model.C[1] == p1_cost * model.n[1])
    model.C2_b0_lb = pyo.Constraint(expr=-model.b * M <= model.C[2])
    model.C2_b0_ub = pyo.Constraint(expr=model.C[2] <= model.b * M)
    model.C2_b1_lb = pyo.Constraint(expr=-(1-model.b) * M <= model.C[2] - (p2_var * model.n[2] + p2_fix))
    model.C2_b1_ub = pyo.Constraint(expr=model.C[2] - (p2_var * model.n[2] + p2_fix) <= (1-model.b) * M)
    model.C2n = pyo.Constraint(expr=model.n[2] <= model.b * n_max_2)
    model.C3 = pyo.Constraint(expr=model.C[3] == p3_cost * model.n[3])

    try:
        opt = SolverFactory('cbc')
        results = opt.solve(model, tee=False)
        if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):
            return model, 'CBC'
    except Exception as e:
        st.error(f"Solver error: {e}")
    return None, None

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📝 Problem Setup", "📊 Concept Visualizer", "🧮 Optimization & Sensitivity"])

# ---- Tab 1: Problem Setup ----
with tab1:
    st.subheader("🎯 Business Scenario")
    st.markdown(f"""
    You are a production manager. Minimize the total cost to produce **{total_target} units** across 3 products.
    *   **Product 1**: ${c1_unit_cost} / unit (stable production line)
    *   **Product 3**: ${c3_unit_cost} / unit (high-cost line)
    *   **Product 2**: Fixed cost ${fixed_cost_2} + Variable cost ${var_cost_2} / unit
        *   *(Big M applied — this line can be turned ON or OFF)*
        *   *(Max production: {n_limit_2} units)*
    """)

    st.divider()
    st.subheader("📐 Mathematical Formulation")
    formula = r"""
    \begin{aligned}
    & \text{Minimize} & & \sum_{i=1}^{3} C_i \\
    & \text{Subject to} & & \sum_{i=1}^{3} n_i = N_{total} \\
    & & & C_1 = p_1 n_1, \quad C_3 = p_3 n_3 \\
    & & & n_2 \le b \cdot n_{max} \\
    & & & -b M \le C_2 \le b M \\
    & & & -(1-b) M \le C_2 - (p_2 n_2 + F_2) \le (1-b) M \\
    & & & n_i \in \mathbb{Z}_{\ge 0}, \quad b \in \{0, 1\}
    \end{aligned}
    """
    st.latex(formula)
    st.markdown(f"""
    **Current Parameter Values:**
    * $N_{{total}} = {total_target}, \\quad n_{{max}} = {n_limit_2}$
    * $p_1 = {c1_unit_cost}, \\quad p_2 = {var_cost_2}, \\quad p_3 = {c3_unit_cost}$
    * $F_2 = {fixed_cost_2}, \\quad M = {M_val}$
    """)

# ---- Tab 2: Concept Visualizer ----
with tab2:
    st.subheader("1. Comparing Constraint 'Open' vs 'Closed' by Binary Switch")
    st.markdown("See how the Big M method opens and closes the feasible region depending on the value of $b$.")

    def create_big_m_plot(b_val):
        n_plot = np.linspace(0, n_limit_2, 100)
        target_cost = var_cost_2 * n_plot + fixed_cost_2
        fig = go.Figure()
        if b_val == 1:
            fig.add_trace(go.Scatter(
                x=[0, n_limit_2, n_limit_2, 0], y=[-M_val, -M_val, M_val, M_val],
                fill='toself', fillcolor='rgba(0,191,255,0.25)',
                line=dict(color='rgba(0,191,255,0.6)', width=2, dash='dash'),
                name='Feasible Region (Big M)'))
            fig.add_trace(go.Scatter(
                x=n_plot, y=target_cost, mode='lines',
                name='Active Cost Formula', line=dict(color='#00ff00', width=4)))
        else:
            fig.add_trace(go.Scatter(
                x=[0, 20, 20, 0], y=[-400, -400, 400, 400],
                fill='toself', fillcolor='rgba(255,50,50,0.4)',
                line=dict(color='rgba(255,50,50,0.8)', width=2),
                name='Locked to Zero'))
            fig.add_trace(go.Scatter(
                x=[0], y=[0], mode='markers',
                name='Forced Solution (0,0)', marker=dict(color='#ff0000', size=15)))
        fig.update_layout(
            title=dict(text=f"<b>b = {b_val} — {'ON (Active)' if b_val==1 else 'OFF (Inactive)'}</b>", font=dict(size=18)),
            xaxis_title="Production Volume (n2)", yaxis_title="Cost (C2)",
            template="none", height=480,
            yaxis=dict(range=[-1000, max(M_val, min_required_M) + 1000])
        )
        return fig

    col_l, col_r = st.columns(2)
    with col_l:
        st.error("🔌 **b = 0 (OFF)**: Constraint is CLOSED")
        st.plotly_chart(create_big_m_plot(0), width='stretch')
        st.markdown("The red region forces $C_2$ to be **locked at exactly 0**.")
    with col_r:
        st.success("💡 **b = 1 (ON)**: Constraint is OPEN")
        st.plotly_chart(create_big_m_plot(1), width='stretch')
        st.markdown("The vast blue region (Big M) effectively removes the constraint, allowing the cost formula to apply freely.")

    st.markdown(r"""
    ### 📝 Big M Formulation — How Logical Constraints Are Encoded
    | Purpose | Big M Formulation | When b=0 (OFF) | When b=1 (ON) |
    | :--- | :--- | :--- | :--- |
    | **Lock cost to zero** | $-b M \le C_2 \le b M$ | 🔒 **Fixed at 0** | 🔓 **No restriction** |
    | **Activate cost formula** | $-(1-b) M \le C_2 - (\text{formula}) \le (1-b) M$ | 🔓 **No restriction** | 🎯 **Formula applied** |
    | **Allow / prohibit production** | $n_2 \le b \cdot n_{max}$ | 🚫 **Production blocked** | ✅ **Production allowed** |
    """)

# ---- Tab 3: Optimization & Sensitivity ----
with tab3:
    st.subheader("2. Optimization & Sensitivity Analysis")

    if 'optimized' not in st.session_state:
        st.session_state.optimized = False

    if st.button("Run Optimization 🚀"):
        st.session_state.optimized = True

    if st.session_state.optimized:
        st.divider()
        st.subheader("🔎 Sensitivity Analysis")
        st.markdown("Adjust **Product 1's unit cost** and observe in real time **when Product 2's line switches ON**.")

        sens_p1 = st.slider("Product 1 Unit Cost ($/unit)", 0.0, 15.0, float(c1_unit_cost), 0.1)

        model, solver_name = run_optimization(sens_p1, var_cost_2, fixed_cost_2, c3_unit_cost, n_limit_2, total_target, M_val)

        if model:
            b_on = pyo.value(model.b) > 0.5
            c1, c2, c3 = st.columns(3)
            c1.metric("Minimum Total Cost", f"${pyo.value(model.obj):,.0f}")
            c2.metric("Product 2 Line", "✅ Active (ON)" if b_on else "🚫 Idle (OFF)")
            c3.metric("Solver", solver_name.upper())

            if b_on:
                st.success(f"💡 Product 1 at ${sens_p1}/unit is expensive enough that activating Product 2's line (fixed cost: ${fixed_cost_2}) reduces the total cost.")
            else:
                st.info(f"💡 Product 1 at ${sens_p1}/unit is cheap enough that keeping Product 2's line idle (fixed cost: ${fixed_cost_2}) is the better choice.")

            n_vals = [pyo.value(model.n[i]) for i in range(1,4)]
            fig = go.Figure(data=[go.Bar(
                x=['Product 1', 'Product 2', 'Product 3'], y=n_vals,
                marker_color=['#636EFA', '#00CC96' if b_on else '#AB63FA', '#EF553B']
            )])
            fig.update_layout(
                title=f"Optimal Production Mix — Product 1 at ${sens_p1}/unit",
                yaxis_title="Production Volume (units)", template="none", height=400
            )
            st.plotly_chart(fig, width='stretch')

            total_n = sum(n_vals)
            total_c = pyo.value(model.obj)
            st.table({
                "Product": ["Product 1", "Product 2", "Product 3", "**Total**"],
                "Volume (n)": [*n_vals, total_n],
                "Cost (C)": [*[f"${pyo.value(model.C[i]):,.0f}" for i in range(1,4)], f"**${total_c:,.0f}**"]
            })
        else:
            st.error("No feasible solution found. Please review your parameter settings.")

st.divider()
