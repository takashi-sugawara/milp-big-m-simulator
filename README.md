# 🚀 Big M Method — Interactive Visualizer

An interactive educational web application that visualizes how the **Big M method** works in Mixed-Integer Linear Programming (MILP).

🔗 **Live Demo**: *(add your Streamlit Community Cloud URL [here](https://milp-big-m-simulator-htdjoj9nzimwg3lgztfzzd.streamlit.app/))*

---

## 📌 What is the Big M Method?

In mathematical optimization, we often face **"either-or" constraints** — for example:
> *"If we run Product 2's production line, we pay a fixed cost of $1,000. If we don't, the cost is $0."*

Standard linear solvers cannot handle this kind of conditional logic directly. The **Big M method** transforms these logical constraints into a set of linear inequalities using:
- A **binary variable** $b \in \{0, 1\}$ acting as a logical switch
- A **sufficiently large constant** $M$ to "open" or "close" constraints

This app makes those mechanics tangible and interactive.

---

## 🎯 Features

| Tab | Content |
| :--- | :--- |
| **📝 Problem Setup** | Business scenario, full mathematical formulation |
| **📊 Concept Visualizer** | Side-by-side comparison of b=0 (OFF) vs b=1 (ON) |
| **🧮 Optimization & Sensitivity** | Live re-optimization with sensitivity analysis slider |

### Key Highlights
- **Big M validation**: Warns when M is too small to form valid constraints
- **Sensitivity Analysis**: Adjust Product 1's unit cost and watch Product 2's line switch ON/OFF in real time
- **All parameters in sidebar**: Change M, fixed cost, variable cost, production limits interactively

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web UI framework
- **[Pyomo](http://www.pyomo.org/)** — Mathematical optimization modeling
- **[CBC](https://github.com/coin-or/Cbc)** — Open-source MILP solver (COIN-OR)
- **[Plotly](https://plotly.com/)** — Interactive visualizations

---

## 🚀 Running Locally

```bash
# 1. Install CBC solver (macOS)
brew install cbc

# 2. Clone the repository
git clone https://github.com/your-username/big-m-visualizer.git
cd big-m-visualizer

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

---

## 📁 Project Structure

```
BigM_Simulator/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
├── packages.txt      # System-level dependencies (for Streamlit Cloud)
└── README.md         # This file
```

---

## 📐 Mathematical Formulation

$$
\begin{aligned}
& \text{Minimize} & & \sum_{i=1}^{3} C_i \\
& \text{Subject to} & & \sum_{i=1}^{3} n_i = N_{total} \\
& & & C_1 = p_1 n_1,\quad C_3 = p_3 n_3 \\
& & & n_2 \le b \cdot n_{max} \\
& & & -bM \le C_2 \le bM \\
& & & -(1-b)M \le C_2 - (p_2 n_2 + F_2) \le (1-b)M \\
& & & n_i \in \mathbb{Z}_{\ge 0},\quad b \in \{0,1\}
\end{aligned}
$$

---

## 📄 License

MIT License
