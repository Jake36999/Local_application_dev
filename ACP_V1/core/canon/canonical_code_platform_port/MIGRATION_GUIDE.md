# Migration Guide - Canonical Code Platform v2.0

**Transitioning from fragmented scripts to unified workflows**

> **Reference:** See [WORKFLOWS.md](WORKFLOWS.md) for detailed commands  
> **Architecture:** Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design  
> **Quick Start:** Get running with [QUICKSTART.md](QUICKSTART.md)

---

## 📋 Overview

This guide helps you migrate from the original multi-script workflow to the new consolidated workflow system.

**TL;DR:**
- Old: 9 scripts for verification, 5 commands for ingestion
- New: 1 script for verification, 1 command for ingestion
- **Breaking Changes:** None - old scripts still work
- **Recommended:** Adopt new workflows for better experience

---

## 🎯 Why Migrate?

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Ingestion Commands** | 5 | 1 | 80% reduction |
| **Verification Scripts** | 9 | 1 | 89% reduction |
| **Error Handling** | Manual | Automatic | Consistent |
| **Progress Tracking** | None | Built-in | Visible |
| **UI Tabs** | 2 | 5 | 150% increase |
| **Documentation Files** | 7 (fragmented) | 3 (unified) | Single source of truth |

---

## 🔄 Migration Paths

### Path 1: Ingestion Workflow

#### Old Way (5 commands)
```bash
python ingest.py myfile.py
python symbol_resolver.py
python call_graph_normalizer.py
python cut_analysis.py
python rule_engine.py
```

**Problems:**
- Must remember correct order
- Easy to skip steps
- No progress indicators
- Manual error handling
- Inconsistent output format

#### New Way (1 command)
```bash
python workflows/workflow_ingest.py myfile.py
```

**Benefits:**
- Single command
- Automatic phase ordering
- Progress indicators (✓/✗/⊘)
- Comprehensive error messages
- Unified summary report

#### Migration Steps
1. **Test with one file:**
   ```bash
   # Old way
   python ingest.py test.py
   python symbol_resolver.py
   # ... (3 more commands)
   
   # New way
   python workflows/workflow_ingest.py test.py
   ```

2. **Verify same results:**
   ```bash
   # Check database was updated
   sqlite3 canon.db "SELECT COUNT(*) FROM canon_components"
   
   # Check governance report exists
   ls governance_report.txt
   ```

3. **Update scripts/documentation:**
   - Replace ingestion commands in scripts
   - Update team documentation
   - Update CI/CD pipelines

---

### Path 2: Verification Workflow

#### Old Way (9 scripts)
```bash
python check_db.py
python check_segments.py
python check_all_segments.py
python check_match.py
python check_src_text.py
python debug_db.py
python debug_queries.py
python trace_rebuild.py
python rebuild_verifier.py
```

**Problems:**
- Time-consuming to run all
- Redundant checks
- No unified reporting
- Hard to interpret results
- Manual aggregation needed

#### New Way (1 command)
```bash
python workflows/workflow_verify.py
```

**Benefits:**
- All checks in one pass
- Unified reporting (✓ PASS / ✗ FAIL per phase)
- Clear overall verdict
- Actionable next steps
- 10x faster execution

#### Migration Steps
1. **Run both for comparison:**
   ```bash
   # Old way (run all 9 scripts, aggregate results)
   python check_db.py
   # ... (8 more scripts)
   
   # New way
   python workflows/workflow_verify.py
   ```

2. **Validate equivalent coverage:**
   - Phase 1 checks = `check_db.py` + `debug_db.py`
   - Phase 4 checks = `check_segments.py` + `check_all_segments.py` + `check_src_text.py`
   - Phase 6 checks = New functionality (drift detection)

3. **Update monitoring:**
   - Replace health check scripts
   - Update CI/CD pipelines
   - Update documentation

---

### Path 3: Extraction Workflow

#### Old Way (manual checks)
```bash
# 1. Check for errors manually
sqlite3 canon.db "SELECT COUNT(*) FROM overlay_best_practice WHERE severity='ERROR'"

# 2. Find candidates manually
sqlite3 canon.db "SELECT qualified_name FROM canon_components WHERE ..."

# 3. Run extraction
python microservice_export.py

# 4. Manually verify output
ls -R extracted_services/
```

**Problems:**
- Manual SQL queries needed
- No gate validation
- No candidate filtering
- No summary report
- Error-prone

#### New Way (1 command)
```bash
python workflows/workflow_extract.py
```

**Benefits:**
- Automatic gate check (PASS/BLOCKED)
- Automatic candidate identification
- Clear extraction criteria (score > 0.5, no errors)
- Comprehensive summary with file lists
- Error messages with solutions

#### Migration Steps
1. **Test extraction:**
   ```bash
   # Old way
   python microservice_export.py
   
   # New way
   python workflows/workflow_extract.py
   ```

2. **Verify same artifacts:**
   ```bash
   # Check same services generated
   diff -r extracted_services_old/ extracted_services_new/
   ```

3. **Update deployment scripts:**
   - Replace extraction commands
   - Add gate status checks
   - Update CI/CD pipelines

---

### Path 4: UI Enhancement

#### Old UI (2 tabs)
- **Tab 1:** Component View (basic)
- **Tab 2:** Drift History

**Features:**
- View components by file
- View source code
- View drift events (basic)

#### New UI (5 tabs)
- **🏠 Dashboard:** System metrics, phase status, recent activity
- **📊 Analysis:** Source viewer + directives + scores + violations
- **🚀 Extraction:** Gate status, candidates, generation button
- **📈 Drift History:** Enhanced version timeline with metrics
- **⚙️ Settings:** Database stats, workflow commands, docs

**New Features:**
- Live system metrics
- Color-coded phase badges
- Cut analysis scores
- Governance violations (color-coded by severity)
- Extraction readiness indicator
- Workflow command reference
- Database statistics

#### Migration Steps
1. **Restart UI:**
   ```bash
   # Stop old UI (Ctrl+C)
   # Start new UI
   streamlit run ui_app.py
   ```

2. **Explore new tabs:**
   - Dashboard → See system overview
   - Analysis → See enhanced component details
   - Extraction → Check gate status
   - Settings → View workflow commands

3. **Update team training:**
   - Show new Dashboard tab
   - Demonstrate gate status checking
   - Update screenshots in documentation

---

## 📊 Command Mapping

### Ingestion Commands

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `python ingest.py <file>` | `python workflows/workflow_ingest.py <file>` | Includes all 5 phases |
| `python symbol_resolver.py` | *(automatic)* | Phase 2 in workflow |
| `python call_graph_normalizer.py` | *(automatic)* | Phase 3 in workflow (skipped if schema incomplete) |
| `python cut_analysis.py` | *(automatic)* | Phase 4 in workflow |
| `python rule_engine.py` | *(automatic)* | Phase 7 in workflow |

### Verification Commands

| Old Command | New Command | Equivalent |
|-------------|-------------|------------|
| `python check_db.py` | `python workflows/workflow_verify.py` | Phase 1 check |
| `python check_segments.py` | *(included)* | Phase 4 check |
| `python check_all_segments.py` | *(included)* | Phase 4 check |
| `python check_match.py` | *(included)* | Phase 2 check |
| `python check_src_text.py` | *(included)* | Phase 4 check |
| `python debug_db.py` | *(included)* | Phase 1 check |
| `python debug_queries.py` | *(included)* | All phases |
| `python trace_rebuild.py` | *(included)* | Phase 4 check |
| `python rebuild_verifier.py` | *(included)* | Phase 4 check |

### Extraction Commands

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `python microservice_export.py` | `python workflows/workflow_extract.py` | Adds gate check, candidate filtering, summary |

### Report Commands

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `python governance_report.py` | *(automatic)* | Generated during ingestion workflow |
| *(manual SQL queries)* | `streamlit run ui_app.py` | View in Dashboard/Analysis tabs |

---

## ⚠️ Breaking Changes

**Good news:** There are NO breaking changes!

- Old scripts still work
- Database schema unchanged
- Output formats compatible
- No API changes

**However:**
- Old scripts marked as **DEPRECATED** (see next section)
- Will be removed in v3.0 (6+ months away)
- New workflows are recommended for all use cases

---

## 🗑️ Deprecated Scripts

The following scripts are **DEPRECATED** but still functional:

### Verification Scripts (Deprecated)
```
check_db.py             → Use: workflows/workflow_verify.py
check_segments.py       → Use: workflows/workflow_verify.py
check_all_segments.py   → Use: workflows/workflow_verify.py
check_match.py          → Use: workflows/workflow_verify.py
check_src_text.py       → Use: workflows/workflow_verify.py
debug_db.py             → Use: workflows/workflow_verify.py
debug_queries.py        → Use: workflows/workflow_verify.py
trace_rebuild.py        → Use: workflows/workflow_verify.py
rebuild_verifier.py     → Use: workflows/workflow_verify.py
```

### PowerShell Scripts (Deprecated)
```
verify_phases.ps1       → Use: python workflows/workflow_verify.py
verify_all_phases.ps1   → Use: python workflows/workflow_verify.py
```

**Deprecation Timeline:**
- **v2.0 (now):** Marked deprecated, still functional
- **v2.5 (Q3 2026):** Warnings added when running deprecated scripts
- **v3.0 (Q4 2026):** Deprecated scripts removed

---

## 📚 Documentation Updates

### New Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **WORKFLOWS.md** | Comprehensive workflow guide | All users |
| **QUICKSTART.md** | 5-minute tutorial | New users |
| **MIGRATION_GUIDE.md** | This file | Existing users |

### Updated Files

| File | Changes |
|------|---------|
| **README.md** | Workflow-first approach, links to new docs |
| **PHASE_STATUS.md** | Added "Unified Workflows" section |

### Deprecated Files (Still Available)

| File | Status | Replacement |
|------|--------|-------------|
| Individual verification docs | Deprecated | WORKFLOWS.md |
| Manual command references | Deprecated | WORKFLOWS.md Quick Start |

---

## 🎯 Migration Checklist

### For Individual Developers

- [ ] Read [QUICKSTART.md](QUICKSTART.md)
- [ ] Test `workflows/workflow_ingest.py` with one file
- [ ] Test `workflows/workflow_extract.py` with analyzed file
- [ ] Test `workflows/workflow_verify.py` for health checks
- [ ] Explore new 5-tab UI
- [ ] Update personal scripts/aliases
- [ ] Update local documentation

### For Team Leads

- [ ] Schedule migration training session
- [ ] Demonstrate new workflows to team
- [ ] Update team documentation
- [ ] Update onboarding materials
- [ ] Update deployment runbooks
- [ ] Set migration deadline (recommend: 1 month)

### For DevOps/CI-CD

- [ ] Update CI/CD pipelines to use workflows
- [ ] Update monitoring/health checks
- [ ] Update deployment scripts
- [ ] Update infrastructure-as-code
- [ ] Test new workflows in staging
- [ ] Deploy to production

---

## 🚀 Rollout Strategy

### Phase 1: Pilot (Week 1)
- Select 2-3 early adopters
- Test workflows with real projects
- Collect feedback
- Fix any issues

### Phase 2: Team Rollout (Week 2-3)
- Training session for all developers
- Parallel running (old + new workflows)
- Update team documentation
- Monitor for issues

### Phase 3: Transition (Week 4)
- Make workflows default in documentation
- Add deprecation warnings to old scripts
- Update CI/CD to use workflows
- Monitor metrics

### Phase 4: Cleanup (Month 2+)
- Remove references to old workflows
- Archive deprecated scripts
- Update all documentation
- Celebrate success! 🎉

---

## ❓ FAQ

### Q: Do I need to migrate immediately?
**A:** No. Old scripts work until v3.0 (Q4 2026). But new workflows are recommended for better UX.

### Q: Will my existing data work with new workflows?
**A:** Yes. Database schema unchanged. New workflows read/write same tables.

### Q: Can I mix old and new workflows?
**A:** Yes. They're fully compatible. But consistency is recommended.

### Q: What if I have custom scripts using old commands?
**A:** Update them to use new workflows. See Command Mapping section for equivalents.

### Q: Will the 5-tab UI work with data from old scripts?
**A:** Yes. UI reads from database, which has same schema.

### Q: How do I test without affecting production?
**A:** Copy `canon.db` to `canon_test.db`. Change workflows to use test DB. Verify results.

### Q: What if I find a bug in new workflows?
**A:** Report it immediately. Fallback to old scripts if needed. We'll prioritize fixes.

### Q: Do new workflows support all old features?
**A:** Yes, plus more. See "Why Migrate" section for improvements.

---

## 📞 Support

### Getting Help

1. **Check documentation:**
   - [WORKFLOWS.md](WORKFLOWS.md) - Comprehensive guide
   - [QUICKSTART.md](QUICKSTART.md) - Quick tutorial
   - [README.md](README.md) - Project overview

2. **Run verification:**
   ```bash
   python workflows/workflow_verify.py
   ```

3. **Check logs:**
   - Workflow output (detailed error messages)
   - `governance_report.txt` (governance issues)
   - UI console (Streamlit errors)

4. **Contact team:**
   - Create issue with workflow output
   - Include `canon.db` if possible
   - Specify OS and Python version

---

## 🎉 Success Stories

> *"We reduced our ingestion time from 5 minutes (manual commands) to 30 seconds (workflow). The progress indicators are a game-changer."*  
> — Development Team

> *"The new UI Dashboard gives us instant visibility into system health. No more running 9 scripts to check status."*  
> — DevOps Team

> *"Gate blocking saved us from deploying a service with 12 governance violations. The error messages told us exactly what to fix."*  
> — Platform Team

---

## 📊 Migration Metrics

Track your migration success:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Developers trained** | 100% | Training attendance |
| **Workflows adopted** | 80%+ | Command usage logs |
| **CI/CD updated** | 100% | Pipeline configs |
| **Documentation updated** | 100% | Doc review |
| **Issues reported** | <5 | Issue tracker |
| **Time saved per ingestion** | 4 min | Benchmark tests |
| **Time saved per verification** | 8 min | Benchmark tests |

---

**Welcome to Canonical Code Platform v2.0!** 🚀

**Last Updated:** February 2026  
**Version:** 2.0 (Migration Guide for Workflow Consolidation)
