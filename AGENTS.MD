You are an autonomous engineering agent running in Codex CLI on a Windows PC with WSL2 available. Your job is to reproduce, as closely as public artifacts allow, the full embodied fruit-fly simulation stack associated with the public Eon fly-brain demo context, on this exact machine:

HARDWARE TARGET
- Host OS: Windows 11
- WSL2 available and preferred
- GPUs: dual NVIDIA RTX 5060 Ti 16 GB
- System RAM: 192 GB
- Goal is to use local compute only unless a public dependency must be downloaded
- Assume no prior project context beyond this prompt

Eon Demo:
https://x.com/alexwg/status/2030217301929132323

PRIMARY OBJECTIVE
Build a runnable, tested, task-tracked local system that reproduces the open full-stack embodied fly simulation as closely as possible to the public Eon-style demo:
1. whole-brain fly neural simulation
2. embodied musculoskeletal / physics fly simulation
3. realistic vision enabled, not toy vision
4. closed-loop online control, not disconnected offline batch scripts
5. observable parity outputs approximating the public demo behavior
6. benchmarked sim-speed versus wall-time on this machine
7. final reproducible repo with one-command setup, tests, benchmarks, and demo runs

NON-NEGOTIABLE DELIVERY REQUIREMENTS
- You must maintain an explicit task tracker in the repo root and update it continuously.
- You must maintain a lab notebook / progress log with dated entries.
- You must create runnable tests and benchmark scripts before claiming progress.
- You must produce observable artifacts: videos, plots, logs, CSV benchmarks, screenshots, and summary markdown.
- You must not declare success unless the final observable outputs run locally and match the stated acceptance criteria.
- You must never hand-wave missing glue code. If public repos do not provide a closed-loop bridge, you must implement it.
- You must assume the public Eon demo may include unpublished glue. You must reproduce the public-equivalent stack and explicitly document any unreplicable private gaps. Do not use private or paid APIs.
- You must optimize for this exact machine, including evaluating single-GPU vs dual-GPU usage where relevant.
- You must keep everything reproducible and scripted.

HONESTY REQUIREMENT
Do not pretend that exact parity with any unpublished private system is already achieved. Instead:
- reproduce the public-equivalent stack,
- define parity metrics against publicly observable demo behavior,
- meet those parity metrics as closely as possible,
- document residual gaps precisely.

PROJECT CONTEXT YOU MUST INTERNALIZE
Public components likely involved:
1. Eon public fly-brain benchmark repo
   - public repo: eonsystemspbc/fly-brain
   - includes backends such as Brian2 CPU, Brian2CUDA, PyTorch CUDA, NEST GPU
   - tested publicly on Ubuntu 22.04 under WSL2 on Windows with NVIDIA GPU
2. Philip Shiu Drosophila whole-brain model
   - public repo: philshiu/Drosophila_brain_model
   - Brian2-based
   - public code is batch-experiment oriented, not obviously a persistent online controller
3. FlyGym / NeuroMechFly v2 embodied simulation stack
   - MuJoCo-based fly body / environment simulation
   - realistic embodiment and controller tutorial ecosystem
4. Realistic vision
   - use FlyGym’s realistic vision path and associated fly visual system model
   - do not substitute a trivial camera-only pipeline unless used as a baseline
5. Advanced olfaction / plume optional as stretch goal, but realistic vision is mandatory

CORE ENGINEERING CHALLENGE
The public pieces are not guaranteed to already form one turnkey persistent closed-loop online controller. Therefore you must:
- inspect each public repo
- install each component
- benchmark each component independently
- design and implement the online bridge layer that converts body observations into brain inputs and brain outputs into body control
- preserve time consistency across modules
- create a persistent simulation loop

MANDATORY SUCCESS CRITERIA
A. Environment and install
- one bootstrap script for WSL2
- one bootstrap script for Python / conda / uv environment creation
- documented CUDA checks
- documented MuJoCo setup
- documented repo checkout and patching
- no manual hidden steps

B. Independent module validation
- brain-only benchmark runs on this PC
- body-only / FlyGym benchmark runs on this PC
- realistic vision module runs on this PC
- all benchmark results saved as CSV and summarized in markdown

C. Closed-loop integration
- persistent online control loop exists
- body state feeds neural model every simulation step or at a documented coarser synchronization cadence
- neural outputs drive body actuators / descending commands every control step
- system runs for fixed-duration demos without crashing

D. Observable parity targets
Produce side-by-side output artifacts for:
- walking / locomotion behavior
- turning / orientation behavior
- reaction to visual stimuli with realistic vision enabled
- stable video capture of the embodied fly
- logs showing neural backend, control frequency, physics step frequency, wall time, sim time
Define and compute parity metrics such as:
- completed simulated duration
- stability without divergence
- average forward speed
- turn response latency
- trajectory smoothness
- qualitative similarity to the public demo clips or descriptions
You must provide a final parity report with pass / partial / fail for each metric.

E. Speed and performance
- benchmark sim-speed vs wall-time for:
  1. brain-only
  2. body-only
  3. body + realistic vision
  4. full closed-loop stack
- benchmark at least two neural backends if feasible on this machine
- identify bottlenecks with profiler evidence
- provide best achievable local speed on this machine
- provide recommendations for additional speedups that remain within this PC

F. Testing
You must create:
- unit tests for adapter / bridge logic
- smoke tests for install and imports
- integration tests for short closed-loop runs
- regression tests for benchmark output format
- acceptance tests that verify videos / logs / metrics are generated

REPO STRUCTURE TO CREATE
Create a clean project repo with at least:
- README.md
- TASKS.md
- PROGRESS_LOG.md
- ASSUMPTIONS_AND_GAPS.md
- REPRO_PARITY_REPORT.md
- environment/
- scripts/
- configs/
- src/
- tests/
- benchmarks/
- outputs/
- docs/
- patches/
Use sane structure under src/, e.g.:
- src/brain/
- src/body/
- src/vision/
- src/bridge/
- src/runtime/
- src/metrics/

OPERATING PROCEDURE
Follow this exact phased workflow.

PHASE 0: INITIAL SCOUTING
- clone / inspect the candidate public repos
- determine exact dependency requirements
- determine OS / CUDA / compiler constraints
- determine whether NEST GPU is realistically buildable in this environment
- determine what each repo already does versus what must be added
Outputs required:
- TASKS.md initialized
- PROGRESS_LOG.md first entry
- docs/architecture_scout.md
- docs/dependency_matrix.md
- docs/repo_gap_analysis.md

PHASE 1: ENVIRONMENT + MODULE INSTALL
- create WSL2-first environment plan
- install all independent modules
- verify imports
- verify minimal example execution
Outputs required:
- scripts/bootstrap_wsl.sh
- scripts/bootstrap_env.sh
- scripts/check_cuda.sh
- scripts/check_mujoco.sh
- tests/test_imports.py
- docs/install_report.md

PHASE 2: STANDALONE BENCHMARKS
Run and record:
1. brain-only benchmarks across available backends
2. body-only benchmarks
3. realistic-vision-only benchmark or representative body+vision workload
Outputs required:
- benchmarks/run_brain_benchmarks.py
- benchmarks/run_body_benchmarks.py
- benchmarks/run_vision_benchmarks.py
- outputs/benchmarks/*.csv
- outputs/plots/*.png
- docs/benchmark_summary.md
All benchmark scripts must report:
- wall time
- simulated time
- real-time factor
- GPU / CPU usage if obtainable
- configuration used

PHASE 3: ARCHITECTURE DESIGN FOR CLOSED LOOP
Design a clean adapter architecture for:
- sensory encoding: body -> brain
- motor decoding: brain -> body
- scheduler / synchronization
- configurable time step ratios
- logging / metrics collection
Produce:
- docs/system_architecture.md
- docs/timing_model.md
- docs/sensory_motor_mapping.md
- config files for timing and backend selection

PHASE 4: IMPLEMENT THE BRIDGE
Implement the bridge in code.
Requirements:
- persistent brain state
- persistent body sim state
- explicit sync loop
- clear interfaces
- no monolithic script spaghetti
- baseline toy visual path allowed only as an intermediate debug mode
- realistic vision path mandatory as production path
Outputs required:
- src/bridge/*.py
- src/runtime/*.py
- configs/*.yaml
- tests/test_bridge_unit.py
- tests/test_closed_loop_smoke.py

PHASE 5: REALISTIC VISION INTEGRATION
This phase is mandatory.
- enable the realistic vision pipeline, not just rendered RGB frames
- connect the realistic vision outputs into the brain input pathway
- create a baseline comparison between toy camera input and realistic vision
- demonstrate that the full production run uses realistic vision
Outputs required:
- docs/realistic_vision_integration.md
- benchmarks/run_fullstack_with_realistic_vision.py
- tests/test_realistic_vision_path.py

PHASE 6: OPTIMIZATION FOR THIS PC
You must profile and optimize specifically for:
- dual RTX 5060 Ti 16 GB
- 192 GB RAM
Tasks:
- test which backend gives best speed on this machine
- test CPU parallelism settings where relevant
- test WSL2 performance-sensitive settings
- test whether second GPU can be used meaningfully for concurrent workloads, e.g. neural backend on one GPU and vision or another module on the other, if practical
- if multi-GPU is not practical, document exactly why
Outputs required:
- docs/perf_tuning.md
- docs/multi_gpu_evaluation.md
- outputs/profiling/*
- updated benchmark CSVs and plots

PHASE 7: PARITY DEMO RUNS
Produce final demo artifacts with:
- full closed-loop run
- realistic vision enabled
- video output
- trajectory plots
- timing logs
- parity metrics
At minimum produce:
- short demo run
- medium demo run
- longest stable demo run achievable
Outputs required:
- outputs/demos/*.mp4
- outputs/logs/*.jsonl
- outputs/metrics/*.csv
- REPRO_PARITY_REPORT.md

PHASE 8: FINAL HARDENING
- README must allow a new user to reproduce
- tests must pass
- benchmark scripts must run
- demo command must be documented
- all assumptions / gaps / TODOs documented
Outputs required:
- final README.md
- final TASKS.md with statuses
- final PROGRESS_LOG.md
- final ASSUMPTIONS_AND_GAPS.md

TASK TRACKING RULES
Maintain TASKS.md with these columns:
- ID
- Task
- Status [todo|doing|blocked|done]
- Owner
- Depends On
- Evidence
- Notes
Every meaningful step must update TASKS.md.
Never silently skip blocked tasks. Mark them blocked with evidence and immediately work a fallback path.

TESTING RULES
Before claiming any subsystem works, write or update the relevant test.
At minimum use pytest.
Every integration milestone must have:
- a smoke test
- a metric-producing run
- saved output artifacts
If a subsystem is too expensive for full CI-style testing, create a short deterministic smoke configuration.

BENCHMARKING RULES
Always compute and store:
- wall_seconds
- sim_seconds
- real_time_factor = sim_seconds / wall_seconds
- backend
- device
- config
- commit hash if possible
Always compare at least:
- best CPU path
- best single-GPU path
- full realistic-vision closed loop path

PARITY RULES
“Parity” does not mean pretending unpublished internal implementation was cloned. It means:
- observable behavior is reproduced as closely as possible from public artifacts
- architecture is functionally analogous where exact internals are unavailable
- residual differences are documented explicitly
Create parity criteria from public observables and then measure against them.
Do not claim stronger parity than evidence supports.

REQUIRED FILE CONTENTS
README.md must include:
- purpose
- hardware used
- quick start
- environment creation
- benchmark commands
- demo commands
- known limitations

ASSUMPTIONS_AND_GAPS.md must include:
- public vs inferred pieces
- any unpublished or inaccessible components
- any places where an engineering substitute was required
- confidence level per subsystem

REPRO_PARITY_REPORT.md must include:
- target public behavior summary
- reproduced behavior summary
- table of parity metrics
- video links / file paths
- unresolved deviations
- final verdict: pass / partial / fail with explanation

ENGINEERING PREFERENCES
- Prefer Python where practical for orchestration.
- Use compiled acceleration only where needed and justified.
- Prefer clean interfaces and explicit configs.
- Avoid hidden notebook-only code.
- All main workflows must be runnable from CLI scripts.
- Use logging, not print spam.
- Save outputs deterministically with timestamped directories.

RESEARCH AND IMPLEMENTATION RULES
- Search public docs / repos as needed.
- Validate claims against actual code where possible.
- Do not rely on vague blog claims without code verification.
- When a repo README conflicts with real code, trust the real code and document the conflict.

FAILURE HANDLING
If an installation path fails:
- capture logs
- isolate cause
- propose and execute the best fallback
- update TASKS.md and PROGRESS_LOG.md
If an exact module cannot be made to work:
- produce the closest functional substitute consistent with public artifacts
- measure it
- document the gap
Do not stop at the first obstacle.

COMMAND DISCIPLINE
At every major milestone, emit:
1. what you attempted
2. what succeeded
3. what failed
4. evidence paths
5. next actions
Keep these in PROGRESS_LOG.md and concise terminal summaries.

FINAL ACCEPTANCE GATE
You are not done until all of the following exist:
- runnable repo on this PC
- passing smoke tests
- benchmark CSVs and plots
- realistic-vision-enabled closed-loop demo
- sim-speed vs wall-time results for full stack
- parity report with evidence
- assumptions / gaps report
- updated task tracker showing all completed or explicitly blocked tasks

START NOW
Begin with Phase 0.
First inspect the public repos and dependency requirements, then create:
- TASKS.md
- PROGRESS_LOG.md
- docs/architecture_scout.md
- docs/dependency_matrix.md
- docs/repo_gap_analysis.md

Then proceed phase by phase without waiting for further instruction.