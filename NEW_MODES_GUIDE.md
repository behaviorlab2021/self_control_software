# Guide: Adding VARIABLE RATIO (5) & VARIABLE WARNING (6) Modes

New modes:
- **Mode 5 = VARIABLE RATIO** (identical to Mode 2 / SCHEDULE TRAINING)
- **Mode 6 = VARIABLE WARNING** (identical to Mode 4 / RANDOM WARNING)

---

## 1. DATABASE (SQL)

### 1a. queries/create_all.sql — Insert new modes (line 125)

```sql
-- BEFORE:
('RANDOM WARNING', 4);

-- AFTER:
('RANDOM WARNING', 4),
('VARIABLE RATIO', 5),
('VARIABLE WARNING', 6);
```

### 1b. queries/create_all.sql — check_round function (lines 359-494)

In ALL the CASE/WHEN blocks, add the new modes alongside their pairs:

| Where you see | Change to |
|---|---|
| `session_info.mode_id = 4` | `session_info.mode_id IN (4, 6)` |
| `session_info.mode_id = 2` | `session_info.mode_id IN (2, 5)` |

Mode 1 and mode 3 stay as they are.

This applies to these CASE blocks:
- `outcome_valid` (~line 360)
- `green_pecks_valid` (~line 396)
- `red_pecks_valid` (~line 416)
- `feedback_period_valid` (~line 432)
- `pecks_until_warning_valid` (~line 465)
- `quarter_valid` (~line 479)

### 1c. queries/checks.sql — Same pattern

Apply the same `IN (4, 6)` and `IN (2, 5)` changes to all CASE/WHEN blocks in this file.

### 1d. queries/CREATE OR REPLACE FUNCTION check_round(r.sql — Same pattern

Apply the same `IN (4, 6)` and `IN (2, 5)` changes to all CASE/WHEN blocks.

### 1e. Add modes to existing database

Run on the target database:
```sql
INSERT INTO experiment_modes (mode_name, mode_id) VALUES
('VARIABLE RATIO', 5),
('VARIABLE WARNING', 6);
```

---

## 2. PYTHON — Launcher (tk_support/launcher.py)

### 2a. Mode helper methods (lines 233-243)

Add two new methods:

```python
def is_variable_ratio_mode(self):
    return self.mode_id.get() == "VARIABLE RATIO"

def is_variable_warning_mode(self):
    return self.mode_id.get() == "VARIABLE WARNING"
```

### 2b. Mode checks in show_inputs (lines 148-187)

Everywhere the launcher checks modes to show/hide UI fields, include the new modes:

| Current check | Change to |
|---|---|
| `not self.is_basic_training_mode()` | `not self.is_basic_training_mode()` (no change needed - new modes should show reinforcement ratio) |
| `not self.is_schedule_training_mode()` | `not self.is_schedule_training_mode() and not self.is_variable_ratio_mode()` |

This affects the visibility of warning-related fields (lines 171, 182+):
- Warning Alarm Volume
- Warning Display Volume
- Warning Hits
- Punishment Periodicity
- etc.

VARIABLE RATIO (5) should hide warning fields (same as SCHEDULE TRAINING).
VARIABLE WARNING (6) should show warning fields (same as RANDOM WARNING).

No other changes needed — the modes dropdown is populated from the database automatically.

---

## 3. PYTHON — Experiment Layout (components/layout/experiment_layout.py)

### 3a. Line 85 — Hopper training check
```python
# No change needed — only checks mode_id == 1
```

### 3b. Line 162 — free_round()
```python
# BEFORE:
if self.session_data["mode_id"] == 4:

# AFTER:
if self.session_data["mode_id"] in (4, 6):
```

### 3c. Line 167 — randomize_array()
```python
# BEFORE:
if self.session_data["mode_id"] == 4:

# AFTER:
if self.session_data["mode_id"] in (4, 6):
```

### 3d. Line 279 — check_if_warning_signal_training()
```python
# No change needed — only checks mode_id == 3
```

### 3e. Line 397 — turn_on_screen()
```python
# No change needed — only checks mode_id == 1
```

---

## 4. PYTHON — R Reports (r_scripts/make_and_send.py)

### 4a. Line 69 — RMD file selection

Currently selects R script by mode_id: `mode_<id>_session_results.Rmd`

Option A (recommended): Map new modes to existing R scripts:
```python
# BEFORE:
rmd_path = os.path.normpath(os.path.join(script_dir, "mode_" + str(mode_id) + "_session_results.Rmd"))

# AFTER:
rmd_mode_map = {5: 2, 6: 4}  # VARIABLE RATIO -> use mode_2, VARIABLE WARNING -> use mode_4
rmd_mode_id = rmd_mode_map.get(mode_id, mode_id)
rmd_path = os.path.normpath(os.path.join(script_dir, "mode_" + str(rmd_mode_id) + "_session_results.Rmd"))
```

Option B: Copy and rename R scripts:
- Copy `mode_2_session_results.Rmd` -> `mode_5_session_results.Rmd`
- Copy `mode_4_session_results.Rmd` -> `mode_6_session_results.Rmd`

---

## Summary of changes

| File | What to change |
|---|---|
| `queries/create_all.sql` | Add modes 5,6 to INSERT + update all CASE/WHEN blocks |
| `queries/checks.sql` | Update all CASE/WHEN blocks (= 4 -> IN (4,6), = 2 -> IN (2,5)) |
| `queries/CREATE OR REPLACE FUNCTION check_round(r.sql` | Same CASE/WHEN updates |
| `self_control/tk_support/launcher.py` | Add helper methods + update field visibility checks |
| `self_control/components/layout/experiment_layout.py` | Lines 162, 167: add mode 6 alongside mode 4 |
| `self_control/r_scripts/make_and_send.py` | Map mode 5->2, 6->4 for R scripts |
| Database (runtime) | `INSERT INTO experiment_modes` for modes 5, 6 |
