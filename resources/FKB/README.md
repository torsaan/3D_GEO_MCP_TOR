# FKB Documentation Resources

Comprehensive FKB (Felles Kartgrunnlag) documentation for Norwegian geomatics standards.

## 📚 Available Resources

### Core Reference Documents

#### [FKB-RULES-CONSOLIDATED.md](FKB-RULES-CONSOLIDATED.md) (33KB)
**THE master reference document** consolidating all 400+ FKB rules from 15 specifications.

**Contents:**
- Complete object catalog (164 types)
- All geometric and topology rules
- Complete accuracy tables (FKB-A/B/C/D)
- KVALITET metadata requirements
- SOSI file format specification
- Validation procedures
- Quick reference tables

**Use this when:** You need authoritative, comprehensive FKB rules in one place.

---

#### [09-VALIDATION-CHECKLIST.md](09-VALIDATION-CHECKLIST.md) (32KB)
**Production-ready validation workflow** with priority-based checks.

**Contents:**
- 10 validation sections with checkboxes
- Priority levels (🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🟢 LOW)
- Code examples (Python, SQL, Bash)
- Validation report template
- Top 5 critical checks that catch 80% of issues
- Time estimates for different dataset sizes

**Use this when:** Performing quality control or building validation tools.

---

#### [00-DOCUMENT-INDEX.md](00-DOCUMENT-INDEX.md) (44KB)
**Complete inventory** of all 15 FKB 5.1 specification documents.

**Contents:**
- Document metadata and versions
- Object type counts per specification
- File sizes and structure
- Source locations

**Use this when:** You need to reference original specifications or understand document structure.

---

### Special Cases & Edge Cases

#### [06-SPECIAL-CASES.md](06-SPECIAL-CASES.md) (24KB)
**Exceptional rules and conditional requirements.**

**Contents:**
- Conditional mandatory attributes
- Fictional boundary usage rules
- Historical/legacy data handling
- Multi-representation objects
- Medium attribute special cases
- Coordinate system edge cases

**Use this when:** Dealing with unusual data or edge cases.

---

#### [07-CONFLICTS-AMBIGUITIES.md](07-CONFLICTS-AMBIGUITIES.md) (25KB)
**Known issues and clarifications needed.**

**Contents:**
- 5 documented ambiguities
- 3 information gaps
- 2 version-specific issues
- Overall assessment: FKB 5.1 is internally consistent

**Use this when:** Interpreting unclear rules or reporting specification issues.

---

### Quick Reference

#### [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (7KB)
**Fast lookup tables** for common values and codes.

**Contents:**
- DATAFANGSTMETODE codes (byg, ukj, pla, sat, gen, fot, dig, lan)
- SYNBARHET codes (0-3)
- MEDIUM codes (T/U/B/L)
- Common accuracy values
- Coordinate systems (22/23/24/25/32/33)

**Use this when:** You need quick lookup of valid code values.

---

#### [fkb_rules.md](fkb_rules.md) (16KB)
**Original FKB rules summary** (legacy).

**Contents:**
- Basic FKB concepts
- Common object types
- Geometry rules overview

**Use this when:** You need a quick introduction to FKB concepts.

---

## 🎯 Which Document Should I Use?

### I'm building a validator
→ **FKB-RULES-CONSOLIDATED.md** (complete rules)
→ **09-VALIDATION-CHECKLIST.md** (workflow and priorities)

### I'm performing quality control
→ **09-VALIDATION-CHECKLIST.md** (step-by-step checklist)
→ **FKB-RULES-CONSOLIDATED.md** (reference for specific rules)

### I need to look up a code value
→ **QUICK_REFERENCE.md** (fast lookup)
→ **FKB-RULES-CONSOLIDATED.md** (complete code lists)

### I'm dealing with unusual data
→ **06-SPECIAL-CASES.md** (exceptions and edge cases)
→ **07-CONFLICTS-AMBIGUITIES.md** (known issues)

### I want to understand FKB structure
→ **00-DOCUMENT-INDEX.md** (specification overview)
→ **fkb_rules.md** (quick introduction)

### I need to cite a source
→ **00-DOCUMENT-INDEX.md** (original spec locations)
→ **FKB-RULES-CONSOLIDATED.md** (extracted with source references)

---

## 📖 Access via MCP

All these resources are available via the MCP server:

```python
# In Claude Desktop or MCP clients
file://fkb_rules_consolidated
file://fkb_validation_checklist
file://fkb_document_index
file://fkb_special_cases
file://fkb_conflicts
file://fkb_quick_reference
file://fkb_rules_legacy
```

---

## 🔄 Updates

**Last Updated:** 2025-11-04
**FKB Version:** 5.1
**Source:** 15 FKB specifications (1.4MB analyzed)

---

## 📁 Related Resources

### Validation Tools
- Python validation module: `FKB/validation/`
- Extracted structured rules: `FKB/extracted/`

### Original Specifications
- Source PDFs: `FKB/Spesifications/`

### Other Resources (in parent folder)
- `accuracy_metrics.md` - Surveying accuracy concepts
- `surveying_rules.md` - Norwegian surveying principles
- `topology_math.md` - Advanced topology mathematics
- `statistical_tests.md` - Statistical testing methods

---

## 💡 Tips

1. **Most Critical Rule:** TOPO-CRITICAL-001
   - Type 2 flater: `område = union(avgrensningsobjekter)`
   - Applies to 15+ major object types

2. **Top 5 Validation Checks** (catch 80% of issues):
   - Mandatory attributes present
   - Geometry valid (no self-intersections)
   - KVALITET block complete
   - Accuracy within standards
   - Type 2 flater topology correct

3. **FKB Standards Quick Reference:**
   - **FKB-A:** 3-30 cm (high precision)
   - **FKB-B:** 6-60 cm (standard)
   - **FKB-C:** 15-150 cm (overview)
   - **FKB-D:** 30-300 cm (background)

---

**Need Help?**
- Validation issues: See `09-VALIDATION-CHECKLIST.md`
- Rule interpretation: See `FKB-RULES-CONSOLIDATED.md`
- Edge cases: See `06-SPECIAL-CASES.md`
- Specification bugs: See `07-CONFLICTS-AMBIGUITIES.md`
