# 📦 Inventory API Integration Guide

**Objective:** Implement and integrate Return Risk Management & Policy Simulation (Prescriptive DSS) for the Inventory Manager role

---

## 📋 Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [System Architecture](#system-architecture)
3. [5-Phase Integration Plan](#5-phase-integration-plan)
4. [API Reference](#api-reference)
5. [Frontend Integration](#frontend-integration)
6. [Testing Plan](#testing-plan)
7. [Performance Considerations](#performance-considerations)

---

## 🔍 Current State Analysis

### What You Currently Have:

| Component | Current Status | Required Features | Status |
|-----------|---------------|-------------------|---------|
| **Risk Scoring Engine** | ✅ Implemented | Real-time risk calculation (0-100) | ✅ Complete |
| **Policy Simulation** | ✅ Implemented | What-if analysis with threshold τ | ✅ Complete |
| **Optimal Threshold Finder** | ✅ Implemented | Grid search for τ* maximizing profit | ✅ Complete |
| **Risk Distribution Analysis** | ✅ Implemented | Statistical overview of risk scores | ✅ Complete |
| **Interactive UI** | ⚠️ Basic | Slider, charts, KPI cards | 🔄 Needs Enhancement |
| **Policy Deployment** | ❌ Missing | Deploy τ to production system | ➕ To Add |
| **Backtest Simulator** | ❌ Missing | Historical data validation | ➕ To Add |

### Key Insights:

- ✅ **Core DSS engine complete** - Risk scoring and simulation algorithms implemented
- ✅ **FastAPI foundation solid** - Port 8002, CORS configured, Pydantic models ready
- 🔄 **Frontend needs development** - Interactive dashboard with real-time updates
- ➕ **Production features needed** - Policy deployment, backtesting, monitoring

---

## 🏗️ System Architecture

### DSS Model Type: **Prescriptive**

```
┌─────────────────────────────────────────────────────────────────┐
│                    INVENTORY MANAGER DSS                        │
│                  (Prescriptive - Simulation)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT                  PROCESS                  OUTPUT         │
│  ┌──────────┐          ┌──────────┐            ┌──────────┐   │
│  │ Order    │          │ Risk     │            │ Risk     │   │
│  │ Data     │──────────│ Scoring  │────────────│ Score    │   │
│  │          │          │ Engine   │            │ 0-100    │   │
│  └──────────┘          └──────────┘            └──────────┘   │
│                                                                 │
│  ┌──────────┐          ┌──────────┐            ┌──────────┐   │
│  │ Policy   │          │ What-if  │            │ Expected │   │
│  │ Params   │──────────│ Simulator│────────────│ Profit   │   │
│  │ (τ, cost)│          │          │            │          │   │
│  └──────────┘          └──────────┘            └──────────┘   │
│                                                                 │
│  ┌──────────┐          ┌──────────┐            ┌──────────┐   │
│  │ Grid     │          │ Threshold│            │ Optimal  │   │
│  │ Search   │──────────│ Optimizer│────────────│ τ*       │   │
│  │ Params   │          │          │            │          │   │
│  └──────────┘          └──────────┘            └──────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Risk Score Calculation Formula:

$$
RiskScore = 0.4 \times CustomerReturnRate + 0.3 \times ProductReturnRate + 0.2 \times QuantityRisk + 0.1 \times ValueRisk
$$

### Expected Profit Formulas:

**If Risk < τ (Allow order):**
$$
ExpectedProfit = (Revenue - Costs) - (RiskScore \times ReturnCost)
$$

**If Risk ≥ τ (Block/Restrict order):**
$$
ExpectedProfit = (Revenue - Costs) \times (1 - ConversionImpact)
$$

---

## 🚀 5-Phase Integration Plan

---

### **PHASE 1: Enhance Risk Scoring Engine** ⭐⭐⭐

**Duration:** 2-3 days  
**Goal:** Improve risk calculation accuracy and add customer/product history tracking

#### Current Implementation:
```python
# Risk components (weighted):
- Customer Return Rate: 40%
- Product Return Rate: 30%
- Quantity Anomaly: 20%
- Order Value Risk: 10%
```

#### Enhancements Required:

1. **Add Historical Return Tracking:**
   ```python
   def get_customer_return_history(customer_id: str, days: int = 90) -> Dict:
       """Get customer's return behavior over last N days"""
       df_all = get_transactions_df(exclude_cancelled=False)
       
       # Filter by date range
       cutoff_date = datetime.now() - timedelta(days=days)
       df_recent = df_all[df_all['InvoiceDate'] >= cutoff_date]
       
       # Calculate metrics
       customer_data = df_recent[df_recent['CustomerID'] == customer_id]
       total_orders = customer_data['InvoiceNo'].nunique()
       cancelled_orders = customer_data[
           customer_data['InvoiceNo'].str.startswith('C', na=False)
       ]['InvoiceNo'].nunique()
       
       return {
           "total_orders": total_orders,
           "returns": cancelled_orders,
           "return_rate": cancelled_orders / total_orders if total_orders > 0 else 0,
           "period_days": days
       }
   ```

2. **New Endpoint:** `POST /calculate-risk-score-detailed`

   **Request:**
   ```json
   {
     "customer_id": "17850",
     "stock_code": "85123A",
     "quantity": 6,
     "unit_price": 2.55,
     "country": "United Kingdom"
   }
   ```

   **Response:**
   ```json
   {
     "success": true,
     "customer_id": "17850",
     "stock_code": "85123A",
     "risk_score": 42.35,
     "risk_level": "Medium",
     "components": {
       "customer_risk": {
         "return_rate": 15.5,
         "total_orders": 45,
         "returns": 7,
         "weight": 0.4,
         "contribution": 16.94
       },
       "product_risk": {
         "return_rate": 12.3,
         "total_orders": 150,
         "returns": 18,
         "weight": 0.3,
         "contribution": 12.71
       },
       "quantity_risk": {
         "ordered_quantity": 6,
         "avg_quantity": 9.5,
         "deviation": -0.37,
         "weight": 0.2,
         "contribution": 8.45
       },
       "value_risk": {
         "order_value": 15.30,
         "avg_order_value": 18.50,
         "deviation": 0.17,
         "weight": 0.1,
         "contribution": 4.25
       }
     },
     "message": "Risk assessment completed with detailed breakdown"
   }
   ```

3. **Add Country Risk Factor:**
   ```python
   # High-risk countries based on return patterns
   COUNTRY_RISK_MULTIPLIER = {
       "United Kingdom": 1.0,    # Baseline
       "Germany": 1.15,          # 15% higher risk
       "France": 1.10,
       "EIRE": 1.20,
       "Spain": 1.12,
       # ... other countries
   }
   ```

#### Test Cases:
- [ ] Calculate risk for known high-risk customer
- [ ] Calculate risk for new customer (default values)
- [ ] Calculate risk for frequently returned product
- [ ] Verify risk score is clamped to 0-100
- [ ] Test with different time periods (30, 60, 90 days)

---

### **PHASE 2: Advanced Policy Simulation** ⭐⭐⭐

**Duration:** 3-4 days  
**Goal:** Implement multi-scenario simulation and comparison tools

#### Changes Required:

1. **Add Batch Simulation Endpoint:**

   **New Endpoint:** `POST /simulate-multiple-policies`

   **Request:**
   ```json
   {
     "scenarios": [
       {
         "name": "Lenient Policy",
         "threshold_tau": 30,
         "return_processing_cost": 10.0,
         "conversion_impact": 0.1
       },
       {
         "name": "Moderate Policy",
         "threshold_tau": 50,
         "return_processing_cost": 10.0,
         "conversion_impact": 0.2
       },
       {
         "name": "Strict Policy",
         "threshold_tau": 70,
         "return_processing_cost": 10.0,
         "conversion_impact": 0.35
       }
     ],
     "sample_size": 1000
   }
   ```

   **Response:**
   ```json
   {
     "success": true,
     "total_scenarios": 3,
     "best_scenario": "Moderate Policy",
     "comparison": [
       {
         "scenario_name": "Lenient Policy",
         "threshold_tau": 30,
         "total_expected_profit": 125430.50,
         "orders_blocked": 150,
         "orders_allowed": 850,
         "block_rate": 15.0,
         "avg_risk_blocked": 78.5,
         "avg_risk_allowed": 25.3,
         "profit_per_order": 125.43
       },
       {
         "scenario_name": "Moderate Policy",
         "threshold_tau": 50,
         "total_expected_profit": 138250.75,
         "orders_blocked": 320,
         "orders_allowed": 680,
         "block_rate": 32.0,
         "avg_risk_blocked": 65.2,
         "avg_risk_allowed": 28.7,
         "profit_per_order": 138.25
       },
       {
         "scenario_name": "Strict Policy",
         "threshold_tau": 70,
         "total_expected_profit": 118900.25,
         "orders_blocked": 580,
         "orders_allowed": 420,
         "block_rate": 58.0,
         "avg_risk_blocked": 52.8,
         "avg_risk_allowed": 32.1,
         "profit_per_order": 118.90
       }
     ],
     "recommendation": {
       "optimal_scenario": "Moderate Policy",
       "reason": "Balances profit maximization with acceptable conversion impact",
       "profit_vs_lenient": "+10.2%",
       "profit_vs_strict": "+16.3%"
     }
   }
   ```

2. **Add Time-based Simulation:**
   ```python
   @app.post("/simulate-over-time")
   async def simulate_over_time(
       threshold_tau: float,
       return_processing_cost: float = 10.0,
       conversion_impact: float = 0.2,
       months: int = 12
   ):
       """Simulate policy impact over time (monthly breakdown)"""
       # Implementation here
   ```

3. **Add Sensitivity Analysis:**
   ```python
   @app.post("/sensitivity-analysis")
   async def sensitivity_analysis(
       base_tau: float = 50,
       cost_range: List[float] = [5.0, 10.0, 15.0, 20.0],
       impact_range: List[float] = [0.1, 0.2, 0.3, 0.4]
   ):
       """Analyze how profit changes with different cost/impact parameters"""
       # Implementation here
   ```

#### Test Cases:
- [ ] Compare 3+ scenarios simultaneously
- [ ] Verify best scenario is correctly identified
- [ ] Test sensitivity to cost changes
- [ ] Test sensitivity to conversion impact changes
- [ ] Validate monthly breakdown totals

---

### **PHASE 3: Optimal Threshold Optimizer** ⭐⭐⭐

**Duration:** 2-3 days  
**Goal:** Enhance grid search with visualization data and constraints

#### Current Implementation:
```python
# Grid search: tau = [0, 5, 10, 15, ..., 100]
# 21 data points
```

#### Enhancements Required:

1. **Add Finer Grid Search:**
   ```python
   @app.post("/find-optimal-threshold-advanced")
   async def find_optimal_threshold_advanced(
       return_processing_cost: float = 10.0,
       conversion_impact: float = 0.2,
       sample_size: int = 1000,
       grid_step: int = 1,  # Finer granularity: 1, 2, 5
       constraints: Optional[Dict[str, float]] = None
   ):
       """
       Advanced optimization with constraints:
       - min_orders_allowed: minimum orders that must pass
       - max_block_rate: maximum % of orders to block
       - min_profit_per_order: minimum profit per order
       """
   ```

2. **Add Visualization Data:**

   **Enhanced Response:**
   ```json
   {
     "success": true,
     "optimal_tau": 52,
     "max_expected_profit": 142350.80,
     "orders_blocked_at_optimal": 340,
     "orders_allowed_at_optimal": 660,
     "simulation_results": [
       {"tau": 0, "expected_profit": 95000, ...},
       {"tau": 1, "expected_profit": 96500, ...},
       ...
       {"tau": 100, "expected_profit": 45000, ...}
     ],
     "chart_data": {
       "x_axis": [0, 1, 2, ..., 100],
       "profit_curve": [95000, 96500, ...],
       "blocked_orders_curve": [0, 10, 20, ...],
       "allowed_orders_curve": [1000, 990, 980, ...]
     },
     "optimization_metadata": {
       "total_evaluations": 101,
       "search_time_seconds": 2.35,
       "convergence": "global_maximum_found"
     },
     "constraint_satisfaction": {
       "min_orders_allowed_met": true,
       "max_block_rate_met": true,
       "min_profit_per_order_met": true
     }
   }
   ```

3. **Add Multiple Objective Optimization:**
   ```python
   @app.post("/pareto-optimization")
   async def pareto_optimization(
       objectives: List[str] = ["maximize_profit", "minimize_blocks"],
       return_processing_cost: float = 10.0,
       conversion_impact: float = 0.2
   ):
       """Find Pareto-optimal solutions balancing multiple objectives"""
       # Implementation here
   ```

#### Test Cases:
- [ ] Verify optimal τ maximizes profit
- [ ] Test with different grid steps (1, 2, 5)
- [ ] Validate constraint satisfaction
- [ ] Check chart data has correct dimensions
- [ ] Compare results with coarse vs fine grid

---

### **PHASE 4: Policy Deployment & Monitoring** ⭐⭐

**Duration:** 3-4 days  
**Goal:** Add production deployment capabilities and monitoring

#### New Features:

1. **Policy Deployment Endpoint:**

   **New Endpoint:** `POST /deploy-policy`

   **Request:**
   ```json
   {
     "threshold_tau": 52,
     "policy_name": "Q4 2025 Return Risk Policy",
     "effective_date": "2025-11-15",
     "return_processing_cost": 10.0,
     "conversion_impact": 0.2,
     "actions": {
       "high_risk": "block_cod_payment",
       "medium_risk": "require_prepayment",
       "low_risk": "allow_all_methods"
     },
     "auto_rollback_threshold": 0.15  // Rollback if profit drops >15%
   }
   ```

   **Response:**
   ```json
   {
     "success": true,
     "policy_id": "POL-20251104-001",
     "status": "deployed",
     "deployment_timestamp": "2025-11-04T10:30:00Z",
     "affected_orders_count": 0,  // Will start affecting new orders
     "policy_config": {
       "threshold_tau": 52,
       "policy_name": "Q4 2025 Return Risk Policy",
       "effective_date": "2025-11-15",
       "actions": {...}
     },
     "monitoring": {
       "dashboard_url": "http://localhost:8080/inventory/monitoring",
       "alert_webhook": "http://localhost:8080/api/alerts",
       "metrics_update_interval": "5_minutes"
     }
   }
   ```

2. **Policy Monitoring Endpoint:**

   **New Endpoint:** `GET /policy-status/{policy_id}`

   **Response:**
   ```json
   {
     "success": true,
     "policy_id": "POL-20251104-001",
     "status": "active",
     "uptime_hours": 48.5,
     "metrics": {
       "orders_processed": 1250,
       "orders_blocked": 412,
       "orders_allowed": 838,
       "block_rate": 32.96,
       "avg_risk_score": 45.2,
       "actual_profit": 135400.50,
       "expected_profit": 142350.80,
       "profit_variance": -4.88,  // %
       "return_incidents": 12,
       "false_positive_rate": 5.2
     },
     "alerts": [
       {
         "severity": "warning",
         "message": "Actual profit 4.88% below expected",
         "timestamp": "2025-11-06T08:15:00Z"
       }
     ],
     "auto_rollback_status": "monitoring"  // or "triggered"
   }
   ```

3. **Backtesting Endpoint:**

   **New Endpoint:** `POST /backtest-policy`

   **Request:**
   ```json
   {
     "threshold_tau": 52,
     "return_processing_cost": 10.0,
     "conversion_impact": 0.2,
     "historical_period": {
       "start_date": "2010-12-01",
       "end_date": "2011-12-31"
     }
   }
   ```

   **Response:**
   ```json
   {
     "success": true,
     "backtest_summary": {
       "total_orders": 25900,
       "orders_would_block": 8545,
       "orders_would_allow": 17355,
       "estimated_profit": 3850000.50,
       "actual_historical_profit": 3650000.00,
       "profit_improvement": "+5.48%",
       "estimated_returns_prevented": 245,
       "cost_savings": 24500.00
     },
     "monthly_breakdown": [
       {
         "month": "2010-12",
         "orders": 2100,
         "blocked": 690,
         "profit": 310000.50
       },
       ...
     ],
     "confidence_interval": {
       "lower_bound": 3750000,
       "upper_bound": 3950000,
       "confidence_level": 0.95
     }
   }
   ```

#### Test Cases:
- [ ] Deploy policy and verify storage
- [ ] Monitor active policy metrics
- [ ] Backtest on historical data
- [ ] Test auto-rollback trigger
- [ ] Validate profit calculations

---

### **PHASE 5: Interactive Dashboard UI** ⭐⭐⭐

**Duration:** 4-5 days  
**Goal:** Build interactive frontend matching the specification from inventory.md

#### Frontend Components:

1. **Main Screen Layout:**
   ```html
   <!-- inventory.html -->
   <div class="inventory-dashboard">
     <!-- Header Section -->
     <div class="header-section">
       <h1>📦 Return-Risk Gatekeeping - Policy Simulation</h1>
       <p class="subtitle">Prescriptive DSS: Optimize return risk threshold (τ) to maximize expected profit</p>
     </div>

     <!-- Input Parameters Section -->
     <div class="parameters-section">
       <div class="card">
         <h3>Simulation Parameters</h3>
         <div class="input-group">
           <label>Return Processing Cost ($):</label>
           <input type="number" id="returnCost" value="10.0" step="0.5" min="0">
         </div>
         <div class="input-group">
           <label>Conversion Rate Impact (0-1):</label>
           <input type="number" id="conversionImpact" value="0.2" step="0.05" min="0" max="1">
         </div>
       </div>
     </div>

     <!-- Threshold Slider Section -->
     <div class="slider-section">
       <div class="card">
         <h3>Risk Threshold (τ)</h3>
         <p>Adjust threshold to see real-time profit impact</p>
         <div class="slider-container">
           <input type="range" id="tauSlider" min="0" max="100" value="50" step="1">
           <div class="slider-value">
             <span id="tauValue">50</span>
             <span class="unit">/ 100</span>
           </div>
         </div>
         <p class="slider-hint">
           Orders with Risk Score ≥ <strong id="tauDisplay">50</strong> will be 
           <span class="highlight-blocked">blocked/restricted</span>
         </p>
       </div>
     </div>

     <!-- KPI Cards Section -->
     <div class="kpi-section">
       <div class="kpi-card profit">
         <h4>Expected Profit</h4>
         <div class="kpi-value" id="kpiProfit">$142,350</div>
         <div class="kpi-trend" id="kpiTrend">+5.2% vs baseline</div>
       </div>
       <div class="kpi-card blocked">
         <h4>Orders Blocked</h4>
         <div class="kpi-value" id="kpiBlocked">340</div>
         <div class="kpi-subtext">34% block rate</div>
       </div>
       <div class="kpi-card allowed">
         <h4>Orders Allowed</h4>
         <div class="kpi-value" id="kpiAllowed">660</div>
         <div class="kpi-subtext">66% pass rate</div>
       </div>
       <div class="kpi-card optimal">
         <h4>🎯 Optimal τ*</h4>
         <div class="kpi-value" id="kpiOptimal">52</div>
         <div class="kpi-subtext">System recommendation</div>
       </div>
     </div>

     <!-- Chart Section -->
     <div class="chart-section">
       <div class="card">
         <h3>Expected Profit vs. Threshold (τ)</h3>
         <canvas id="profitChart"></canvas>
       </div>
     </div>

     <!-- Action Buttons -->
     <div class="actions-section">
       <button class="btn btn-primary" id="deployBtn">
         🚀 Deploy Policy
       </button>
       <button class="btn btn-secondary" id="backtestBtn">
         📊 Run Backtest
       </button>
       <button class="btn btn-info" id="compareBtn">
         🔄 Compare Scenarios
       </button>
     </div>

     <!-- Results Table -->
     <div class="results-section">
       <div class="card">
         <h3>Simulation Results</h3>
         <table id="resultsTable">
           <thead>
             <tr>
               <th>Threshold (τ)</th>
               <th>Expected Profit</th>
               <th>Orders Blocked</th>
               <th>Block Rate</th>
               <th>Avg Risk (Blocked)</th>
               <th>Avg Risk (Allowed)</th>
             </tr>
           </thead>
           <tbody id="resultsBody">
             <!-- Populated via JavaScript -->
           </tbody>
         </table>
       </div>
     </div>
   </div>
   ```

2. **JavaScript Integration:**
   ```javascript
   // Real-time slider updates
   document.getElementById('tauSlider').addEventListener('input', async (e) => {
     const tau = e.target.value;
     document.getElementById('tauValue').textContent = tau;
     document.getElementById('tauDisplay').textContent = tau;
     
     // Call API to simulate
     await simulatePolicy(tau);
   });

   async function simulatePolicy(tau) {
     const returnCost = document.getElementById('returnCost').value;
     const conversionImpact = document.getElementById('conversionImpact').value;
     
     const response = await fetch('http://localhost:8002/simulate-policy', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({
         threshold_tau: parseFloat(tau),
         return_processing_cost: parseFloat(returnCost),
         conversion_impact: parseFloat(conversionImpact),
         sample_size: 1000
       })
     });
     
     const data = await response.json();
     updateDashboard(data);
   }

   function updateDashboard(data) {
     // Update KPIs
     document.getElementById('kpiProfit').textContent = 
       `$${data.total_expected_profit.toLocaleString()}`;
     document.getElementById('kpiBlocked').textContent = data.orders_blocked;
     document.getElementById('kpiAllowed').textContent = data.orders_allowed;
     
     // Update chart
     updateProfitChart(data);
   }
   ```

3. **Chart.js Visualization:**
   ```javascript
   let profitChart = null;

   async function initializeChart() {
     // Get optimal threshold data
     const response = await fetch('http://localhost:8002/find-optimal-threshold');
     const data = await response.json();
     
     const ctx = document.getElementById('profitChart').getContext('2d');
     profitChart = new Chart(ctx, {
       type: 'line',
       data: {
         labels: data.simulation_results.map(r => r.tau),
         datasets: [{
           label: 'Expected Profit ($)',
           data: data.simulation_results.map(r => r.expected_profit),
           borderColor: '#4CAF50',
           backgroundColor: 'rgba(76, 175, 80, 0.1)',
           tension: 0.4,
           pointRadius: 3,
           pointHoverRadius: 6
         }]
       },
       options: {
         responsive: true,
         plugins: {
           annotation: {
             annotations: {
               optimalLine: {
                 type: 'line',
                 xMin: data.optimal_tau,
                 xMax: data.optimal_tau,
                 borderColor: '#FF5722',
                 borderWidth: 2,
                 label: {
                   content: `Optimal τ* = ${data.optimal_tau}`,
                   enabled: true,
                   position: 'top'
                 }
               }
             }
           }
         },
         scales: {
           x: {
             title: {
               display: true,
               text: 'Risk Threshold (τ)'
             }
           },
           y: {
             title: {
               display: true,
               text: 'Expected Profit ($)'
             }
           }
         }
       }
     });
   }
   ```

4. **Deploy Policy Modal:**
   ```javascript
   document.getElementById('deployBtn').addEventListener('click', () => {
     const tau = document.getElementById('tauSlider').value;
     
     const modal = `
       <div class="modal">
         <h3>Deploy Policy Confirmation</h3>
         <p>Are you sure you want to deploy this policy?</p>
         <ul>
           <li><strong>Threshold (τ):</strong> ${tau}</li>
           <li><strong>Effective Date:</strong> Immediately</li>
           <li><strong>Expected Impact:</strong> Will affect all new orders</li>
         </ul>
         <div class="modal-actions">
           <button class="btn btn-danger" onclick="confirmDeploy(${tau})">
             ✅ Confirm Deployment
           </button>
           <button class="btn btn-secondary" onclick="closeModal()">
             ❌ Cancel
           </button>
         </div>
       </div>
     `;
     
     showModal(modal);
   });

   async function confirmDeploy(tau) {
     const response = await fetch('http://localhost:8002/deploy-policy', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({
         threshold_tau: tau,
         policy_name: `Policy-${new Date().toISOString()}`,
         effective_date: new Date().toISOString(),
         return_processing_cost: parseFloat(document.getElementById('returnCost').value),
         conversion_impact: parseFloat(document.getElementById('conversionImpact').value),
         actions: {
           high_risk: "block_cod_payment",
           medium_risk: "require_prepayment",
           low_risk: "allow_all_methods"
         }
       })
     });
     
     const data = await response.json();
     
     if (data.success) {
       showNotification('✅ Policy deployed successfully!', 'success');
       closeModal();
     } else {
       showNotification('❌ Deployment failed', 'error');
     }
   }
   ```

#### Test Cases:
- [ ] Slider updates KPIs in real-time
- [ ] Chart displays profit curve correctly
- [ ] Optimal τ* is highlighted on chart
- [ ] Deploy button triggers confirmation modal
- [ ] Backtest opens results in new section
- [ ] Compare scenarios shows side-by-side comparison

---

## 📡 API Reference

### Base URL
```
http://localhost:8002
```

### Authentication
Currently no authentication required (development mode). In production, add JWT tokens.

---

### **1. Health Check**

**Endpoint:** `GET /health`

**Description:** Check if API is running

**Response:**
```json
{
  "status": "healthy",
  "service": "inventory",
  "version": "1.0.0",
  "port": 8002
}
```

---

### **2. Calculate Risk Score**

**Endpoint:** `POST /calculate-risk-score`

**Description:** Calculate return risk score for a single order

**Request Body:**
```json
{
  "customer_id": "17850",
  "stock_code": "85123A",
  "quantity": 6,
  "unit_price": 2.55,
  "country": "United Kingdom"
}
```

**Response:**
```json
{
  "success": true,
  "customer_id": "17850",
  "stock_code": "85123A",
  "risk_score": 42.35,
  "risk_level": "Medium",
  "message": "Risk assessment completed. Score: 42.35/100"
}
```

**Risk Levels:**
- **Low:** 0-33
- **Medium:** 33-67
- **High:** 67-100

---

### **3. Simulate Policy**

**Endpoint:** `POST /simulate-policy`

**Description:** Simulate policy with given threshold and parameters

**Request Body:**
```json
{
  "threshold_tau": 50,
  "return_processing_cost": 10.0,
  "conversion_impact": 0.2,
  "sample_size": 1000
}
```

**Response:**
```json
{
  "success": true,
  "threshold_tau": 50,
  "total_expected_profit": 138250.75,
  "orders_blocked": 320,
  "orders_allowed": 680,
  "avg_risk_blocked": 65.2,
  "avg_risk_allowed": 28.7,
  "recommendation": "Balanced policy - Moderate risk management"
}
```

---

### **4. Find Optimal Threshold**

**Endpoint:** `POST /find-optimal-threshold`

**Description:** Find threshold (τ*) that maximizes expected profit

**Query Parameters:**
- `return_processing_cost` (float, default: 10.0)
- `conversion_impact` (float, default: 0.2)
- `sample_size` (int, default: 1000)

**Response:**
```json
{
  "success": true,
  "optimal_tau": 52,
  "max_expected_profit": 142350.80,
  "orders_blocked_at_optimal": 340,
  "simulation_results": [
    {"tau": 0, "expected_profit": 95000, "orders_blocked": 0, "orders_allowed": 1000},
    {"tau": 5, "expected_profit": 98500, "orders_blocked": 50, "orders_allowed": 950},
    ...
    {"tau": 100, "expected_profit": 45000, "orders_blocked": 1000, "orders_allowed": 0}
  ]
}
```

---

### **5. Risk Distribution**

**Endpoint:** `GET /risk-distribution`

**Description:** Get statistical distribution of risk scores

**Query Parameters:**
- `sample_size` (int, default: 1000)

**Response:**
```json
{
  "success": true,
  "sample_size": 1000,
  "distribution": {
    "0-20": 180,
    "20-40": 320,
    "40-60": 280,
    "60-80": 170,
    "80-100": 50
  },
  "mean_risk": 42.35,
  "median_risk": 38.50,
  "std_risk": 22.15
}
```

---

## 🧪 Testing Plan

### **Unit Tests**

```python
# test_inventory_api.py
import pytest
from fastapi.testclient import TestClient
from inventory_api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_calculate_risk_score():
    request = {
        "customer_id": "17850",
        "stock_code": "85123A",
        "quantity": 6,
        "unit_price": 2.55,
        "country": "United Kingdom"
    }
    response = client.post("/calculate-risk-score", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert 0 <= data["risk_score"] <= 100
    assert data["risk_level"] in ["Low", "Medium", "High"]

def test_simulate_policy():
    request = {
        "threshold_tau": 50,
        "return_processing_cost": 10.0,
        "conversion_impact": 0.2,
        "sample_size": 100
    }
    response = client.post("/simulate-policy", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["orders_blocked"] + data["orders_allowed"] == 100

def test_find_optimal_threshold():
    response = client.post("/find-optimal-threshold?sample_size=100")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert 0 <= data["optimal_tau"] <= 100
    assert len(data["simulation_results"]) > 0

def test_risk_distribution():
    response = client.get("/risk-distribution?sample_size=100")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert sum(data["distribution"].values()) == 100
```

### **Integration Tests**

```python
# test_integration_inventory.py
def test_full_workflow():
    """Test complete workflow: risk -> simulate -> optimize -> deploy"""
    
    # Step 1: Calculate risk for sample order
    risk_response = client.post("/calculate-risk-score", json={
        "customer_id": "17850",
        "stock_code": "85123A",
        "quantity": 6,
        "unit_price": 2.55
    })
    risk_score = risk_response.json()["risk_score"]
    
    # Step 2: Simulate policy
    sim_response = client.post("/simulate-policy", json={
        "threshold_tau": 50,
        "return_processing_cost": 10.0,
        "conversion_impact": 0.2
    })
    profit_at_50 = sim_response.json()["total_expected_profit"]
    
    # Step 3: Find optimal
    opt_response = client.post("/find-optimal-threshold")
    optimal_tau = opt_response.json()["optimal_tau"]
    max_profit = opt_response.json()["max_expected_profit"]
    
    # Assertions
    assert max_profit >= profit_at_50  # Optimal should be >= any single point
    assert 0 <= optimal_tau <= 100
```

### **Performance Tests**

```python
# test_performance.py
import time

def test_risk_calculation_performance():
    """Risk calculation should complete in <100ms"""
    start = time.time()
    for _ in range(100):
        client.post("/calculate-risk-score", json={
            "customer_id": "17850",
            "stock_code": "85123A",
            "quantity": 6,
            "unit_price": 2.55
        })
    duration = time.time() - start
    avg_time = duration / 100
    assert avg_time < 0.1  # Less than 100ms per request

def test_optimization_performance():
    """Optimization should complete in <5 seconds"""
    start = time.time()
    client.post("/find-optimal-threshold?sample_size=1000")
    duration = time.time() - start
    assert duration < 5.0  # Less than 5 seconds
```

### **Test Checklist**

- [ ] All endpoints return 200 OK for valid requests
- [ ] Invalid requests return appropriate error codes (400, 404, 500)
- [ ] Risk scores are always between 0-100
- [ ] Policy simulation totals match sample size
- [ ] Optimal threshold is within 0-100 range
- [ ] Distribution buckets sum to sample size
- [ ] Performance meets requirements (<100ms risk, <5s optimization)
- [ ] CORS headers allow frontend access
- [ ] API documentation auto-generated at /docs

---

## ⚡ Performance Considerations

### **Current Bottlenecks:**

| Issue | Impact | Solution |
|-------|--------|----------|
| Risk calculation on every request | Slow for bulk orders | Cache recent calculations |
| Grid search (101 points) | 5+ seconds | Optimize with binary search or genetic algorithms |
| Large dataset loading | Memory intensive | Pagination, sampling strategies |
| No database indexing | Slow queries | Add indexes on CustomerID, InvoiceNo |

### **Optimization Strategies:**

1. **Caching Risk Scores:**
   ```python
   from functools import lru_cache
   from datetime import datetime, timedelta

   # Cache risk scores for 5 minutes
   @lru_cache(maxsize=1000)
   def get_cached_risk_score(customer_id: str, stock_code: str, 
                             cache_time: int) -> float:
       """Cache key includes time bucket to auto-expire"""
       return calculate_risk_score_internal(customer_id, stock_code)

   # Usage
   cache_bucket = int(datetime.now().timestamp() // 300)  # 5-min buckets
   risk = get_cached_risk_score(customer_id, stock_code, cache_bucket)
   ```

2. **Parallel Simulation:**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   import asyncio

   async def parallel_grid_search(tau_values, params):
       with ThreadPoolExecutor(max_workers=4) as executor:
           loop = asyncio.get_event_loop()
           futures = [
               loop.run_in_executor(executor, simulate_single_tau, tau, params)
               for tau in tau_values
           ]
           results = await asyncio.gather(*futures)
       return results
   ```

3. **Database Indexing:**
   ```javascript
   // MongoDB - Create compound indexes
   db.DSS.createIndex({ "CustomerID": 1, "InvoiceDate": -1 })
   db.DSS.createIndex({ "StockCode": 1, "InvoiceNo": 1 })
   db.DSS.createIndex({ "InvoiceNo": 1 })  // For cancelled detection
   ```

4. **Data Sampling Strategy:**
   ```python
   def intelligent_sampling(df, target_size=1000, stratify_by='RiskLevel'):
       """Stratified sampling to preserve risk distribution"""
       if len(df) <= target_size:
           return df
       
       # Calculate risk scores
       df['RiskLevel'] = pd.cut(df['RiskScore'], 
                                bins=[0, 33, 67, 100], 
                                labels=['Low', 'Medium', 'High'])
       
       # Stratified sample
       sample = df.groupby('RiskLevel', group_keys=False).apply(
           lambda x: x.sample(n=int(target_size * len(x) / len(df)))
       )
       return sample
   ```

5. **Response Compression:**
   ```python
   from fastapi.middleware.gzip import GZipMiddleware
   
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

### **Monitoring Metrics:**

```python
from prometheus_client import Counter, Histogram
import time

# Metrics
risk_calculations = Counter('inventory_risk_calculations_total', 
                           'Total risk score calculations')
simulation_duration = Histogram('inventory_simulation_duration_seconds',
                               'Time spent on policy simulation')

# Usage
@app.post("/calculate-risk-score")
async def calculate_risk_score(request: RiskScoreRequest):
    risk_calculations.inc()
    start_time = time.time()
    
    # ... calculation logic ...
    
    simulation_duration.observe(time.time() - start_time)
    return response
```

---

## 📚 Expected Outcomes

After completing all 5 phases, you'll have:

✅ **Advanced Risk Scoring** with detailed component breakdown  
✅ **Multi-Scenario Simulation** for policy comparison  
✅ **Optimized Threshold Finder** with visualization data  
✅ **Production Deployment** capabilities with monitoring  
✅ **Interactive Dashboard** with real-time updates  
✅ **Backtesting Framework** for historical validation  
✅ **Performance Optimization** with caching and indexing  
✅ **Comprehensive Testing** with unit, integration, and performance tests  
✅ **API Documentation** auto-generated at `/docs`  
✅ **Monitoring & Alerts** for deployed policies  

---

## 🎯 Quick Reference: File Changes

### **Files to Modify:**

| File | Changes | Priority |
|------|---------|----------|
| `python-apis/inventory_api.py` | Add all Phase 1-4 endpoints | ⭐⭐⭐ |
| `python-apis/db_utils.py` | Add return history tracking | ⭐⭐ |
| `src/main/resources/templates/dashboard/inventory.html` | Build Phase 5 UI | ⭐⭐⭐ |
| `python-apis/test_inventory.py` | Create comprehensive tests | ⭐⭐ |

### **New Endpoints to Add:**

| Endpoint | Method | Phase | Purpose |
|----------|--------|-------|---------|
| `/calculate-risk-score-detailed` | POST | 1 | Enhanced risk with breakdown |
| `/simulate-multiple-policies` | POST | 2 | Batch scenario comparison |
| `/simulate-over-time` | POST | 2 | Monthly breakdown |
| `/sensitivity-analysis` | POST | 2 | Parameter sensitivity |
| `/find-optimal-threshold-advanced` | POST | 3 | Constrained optimization |
| `/pareto-optimization` | POST | 3 | Multi-objective optimization |
| `/deploy-policy` | POST | 4 | Deploy to production |
| `/policy-status/{policy_id}` | GET | 4 | Monitor active policy |
| `/backtest-policy` | POST | 4 | Historical validation |

### **New Functions to Add:**

| Function | File | Purpose |
|----------|------|---------|
| `get_customer_return_history()` | db_utils.py | Track return patterns |
| `get_product_return_history()` | db_utils.py | Track product returns |
| `apply_country_risk_multiplier()` | inventory_api.py | Country-based adjustment |
| `batch_simulate()` | inventory_api.py | Parallel simulations |
| `calculate_profit_sensitivity()` | inventory_api.py | Sensitivity analysis |
| `deploy_policy_to_db()` | db_utils.py | Store policy config |
| `monitor_policy_metrics()` | inventory_api.py | Real-time monitoring |
| `run_backtest()` | inventory_api.py | Historical simulation |

---

## 💡 Pro Tips

1. **Start with Risk Scoring:** Get Phase 1 working perfectly before moving to simulation
2. **Test with Real Data:** Use actual customer/product IDs from your database
3. **Validate Formulas:** Compare expected profit calculations manually
4. **Use Postman:** Test all endpoints thoroughly before frontend integration
5. **Monitor Performance:** Track API response times from the start
6. **Cache Aggressively:** Risk scores and simulations are good caching candidates
7. **Document Assumptions:** Write down all cost/impact assumptions
8. **Version Policies:** Keep history of all deployed policies
9. **A/B Test:** Deploy new policies gradually with A/B testing
10. **Collect Feedback:** Monitor actual return rates vs. predictions

---

## 🔗 Integration with Other Services

### **Admin API (Port 8001):**
- Share user authentication/authorization
- Admin can view all deployed policies
- Admin approves policy deployments

### **Marketing API (Port 8003):**
- Cross-reference at-risk customers with high return risk
- Combine customer segments with risk profiles
- Targeted campaigns for high-risk customers

### **Sales API (Port 8004):**
- Real-time risk scoring during checkout
- Block/warn on high-risk orders
- Suggest alternative payment methods

### **API Gateway (Port 8080):**
```javascript
// Example: Gateway routes to Inventory API
app.post('/api/inventory/risk-score', async (req, res) => {
  const response = await fetch('http://localhost:8002/calculate-risk-score', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(req.body)
  });
  res.json(await response.json());
});
```

---

## 📞 Support & Troubleshooting

### **Common Issues:**

1. **"No transaction data found"**
   - Verify MongoDB connection in `db_utils.py`
   - Check collection name is "DSS"
   - Ensure database has data

2. **Risk scores always 50**
   - Customer/product not in database
   - Using default values for new entities
   - Check customer_id format matches database

3. **Optimization takes too long**
   - Reduce `sample_size` parameter
   - Use coarser grid (step=5 or step=10)
   - Enable caching

4. **CORS errors from frontend**
   - Verify CORS middleware is configured
   - Check allowed origins include frontend URL
   - Test with `curl` to isolate issue

5. **Incorrect profit calculations**
   - Verify cost assumptions (30% default)
   - Check return_processing_cost parameter
   - Validate conversion_impact is 0-1

### **Debug Mode:**

```python
# Add to inventory_api.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/calculate-risk-score")
async def calculate_risk_score(request: RiskScoreRequest):
    logger.debug(f"Request: {request}")
    # ... rest of code ...
    logger.debug(f"Risk score: {risk_score}")
    return response
```

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Performance tests meet requirements
- [ ] API documentation complete
- [ ] Frontend UI tested across browsers
- [ ] CORS configured correctly
- [ ] Database indexes created
- [ ] Caching implemented
- [ ] Monitoring/alerting set up
- [ ] Error handling comprehensive
- [ ] Security review completed
- [ ] Backup/rollback plan ready

---

**Last Updated:** November 4, 2025  
**Status:** Planning & Design Complete ✅ Ready for Implementation 🚀  
**API Port:** 8002  
**Role:** Inventory Manager  
**DSS Type:** Prescriptive (Simulation & Optimization)
