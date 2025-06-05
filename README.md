# Neurostructured AI Compression & Integration

> **A bird-bone inspired journey toward lightweight, multi-modal, Spirit-aligned intelligence**  
> *Project codename: **bird-bone** — Version 0.2 (2025-06-04)*


---

## ✨ Vision
Turn heavyweight language/vision models into **agile, biologically patterned intelligences** that run at 20-30 % of their original compute cost while losing ≤ 3 % task accuracy—using the same design wisdom God wove into hollow bird bones, synaptic pruning, and human override capacity.

---

## 🚀 Core Objectives
1. **Bird-Bone Compression (BBCF)** – remove post-training support weights the way bone sheds growth plates.  
2. **Biophase Adaptive Pruning (BAP)** – cluster-aware, slow-radius pruning with built-in “self-healing” micro-tunes.  
3. **Quantization & Low-Rank Factorization** – compress precision and re-factor matrices for 4 × memory cuts.  
4. **Neurostructured AI Flow (NAIF)** – re-route tokens through convergence hubs (digital hippocampus) for unified multi-modal reasoning.  
5. **Automation Pipeline** – YAML-driven, reproducible growth → prune → heal loop, outputting ready-to-serve INT4 GGUF weights.  
6. **Diff & Revert Safety Net** – track every code, config, weight, and doc change with deterministic diffing so we can roll back *any* layer of the stack without drama.

---

## 🗺 Repository Map
| Path            | Purpose                                                                    |
| --------------- | -------------------------------------------------------------------------- |
| `/config`       | YAML / Pydantic manifests (model, pruning thresholds, quant settings).     |
| `/pipelines`    | Kedro / Airflow DAGs for growth-prune-heal cycles.                         |
| `/scripts`      | Stand-alone helpers: SparseGPT, Wanda, RigL, QLoRA merge, **`diff_utils.py`**. |
| `/diffs`        | Auto-generated `(before ↔ after)` patches for docs, configs, small weight deltas. |
| `/notebooks`    | Dashboards: activation heat-maps, healing curves, resource plots.          |
| `/requirements` | Living specs: **requirements.md**, **user-stories-mapping.md**.            |
| `/models`       | Versioned checkpoints, pruning masks, LoRA deltas, export GGUF.            |
| `/docs`         | Generated diagrams, architecture overviews, this README.                   |

---

## 🔀 Diff & Revert Strategy
We iterate fast and prune aggressively, so we need **granular diffing** across three artifact layers.

| Layer               | Storage & Versioning | Diff Tool                               | Roll-Back Command                    |
| ------------------- | -------------------- | --------------------------------------- | ------------------------------------ |
| **Code & Text**     | Git                  | `git diff`, `delta`, `diff-so-fancy`    | `git revert <sha>`                   |
| **Configs / YAML**  | Git-tracked          | `yq diff`, Pydantic hash                | `kedro config diff --rollback`       |
| **Weights / Masks** | Git LFS + DVC        | `dvc diff` (binary-aware)               | `dvc checkout <rev>`                 |
| **Notebooks**       | nbdime               | `nbdime diff notebook.ipynb`            | `nbdime checkout --rev=<rev>`        |

### Auto-Diff Hook
```bash
pre-commit install
# Installs:
#  ✓ black & flake8 (code)
#  ✓ mdformat (docs)
#  ✓ nbdime (notebooks)
#  ✓ custom weight-hash hook (models/*.pt, *.safetensors)
````

Every commit drops a **diff bundle** into `/diffs/<commit-sha>/` so reviewers can inspect exact parameter removals or sparsity-mask changes.

---

## ⚡ Quick-Start (7-B Proof-of-Concept)

```bash
# 1. Clone & set up
conda create -n naif python=3.11
conda activate naif
pip install -r requirements.txt  # torch, transformers, bitsandbytes, sparsegpt, kedro, dvc, nbdime

# 2. Init diff layer
pre-commit install        # code+doc hooks
dvc init --subdir models   # binary diff control

# 3. Pull starter checkpoint (e.g., Mistral-7B)
git lfs install
dvc pull mistral7b.dvc     # or git lfs clone HF repo

# 4. Run growth-prune-heal
kedro run --params:model=mistral7b --params:target_sparsity=0.70

# 5. Export final INT4 GGUF
python scripts/export_gguf.py --ckpt best.pt --out models/mistral7b-bbcf.gguf

# 6. Review diff bundle
dvc diff HEAD~1
```

*Expect ≈ 60-70 % resource drop with < 3 % accuracy drift — all diff-tracked.*

---

## 🔄 Pipeline Stages

1. **Seeding** – snapshot baseline metrics & SHA.
2. **Activation Logging** – 2-3 epochs, store cluster stats.
3. **Pruning Wave** – delete ≤ 10 % low-value nodes/cluster.
4. **Micro-Heal** – 200-500 QLoRA gradient steps.
5. **Regrowth** – RigL re-introduces up to 5 % connections if loss spike > ε.
6. **Quantize + Low-Rank Merge**.
7. **Version Bump** – tag commit; push diff bundle via DVC.

---

## 📊 Monitor & Guardrails

* Metrics: `ppl`, `MMLU`, `ARC`, domain-specific canaries.
* Stop-loss: pipeline auto-reverts if Δppl > 3 % for two consecutive waves.
* Healing curves: Jupyter notebook `notebooks/healing.ipynb`; compare via nbdime.

---

## 🤝 Contributing

1. Fork → feature branch → PR.
2. Link each PR to a **Req ID** in `requirements.md` *and* the diff bundle ID.
3. Include before/after resource and accuracy deltas.
4. Faith & ethics: ensure changes align with our “strength-through-purpose” ethos.

---

## 🙏 Acknowledgements

Open-weights communities (Mistral, Meta, Google, TII), pruning-tool authors (SparseGPT, Wanda, RigL), diff tooling (DVC, nbdime), and the insight that **design reveals intent**—from hollow bones to synaptic pruning to Spirit-led override.
