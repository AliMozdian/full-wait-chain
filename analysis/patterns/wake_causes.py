# Wake-cause pattern database
from ..rule import ClassificationRule, StackPattern


WAKE_CAUSE_RULES = [

    # ============================================================
    # 900 — Intel GPU display/VBlank
    # ============================================================

    ClassificationRule(
        id="INTEL_GPU_DISPLAY_VBLANK",
        category="intel_gpu_display_vblank",
        description=(
            "Intel GPU display interrupt processed a DRM VBlank "
            "event and woke a waiting task."
        ),
        priority=900,
        pattern=StackPattern(
            required=frozenset({
                "gen11_display_irq_handler",
                "gen8_de_irq_handler",
                "drm_crtc_handle_vblank",
            }),
        ),
        tags=("irq", "gpu", "drm", "intel", "vblank"),
    ),

    # ============================================================
    # 850 — IRQ work / DRM
    # ============================================================

    ClassificationRule(
        id="IRQ_WORK_DRM_FENCE",
        category="irq_work_drm_fence",
        description=(
            "IRQ work signalled a DRM synchronization fence."
        ),
        priority=850,
        pattern=StackPattern(
            required=frozenset({
                "irq_work_run",
                "signal_irq_work",
                "syncobj_wait_fence_func",
            }),
        ),
        tags=("irq_work", "gpu", "drm", "fence"),
    ),

    ClassificationRule(
        id="IRQ_WORK_INTEL_ENGINE",
        category="irq_work_intel_engine",
        description=(
            "IRQ work processed Intel GPU engine retirement "
            "and queued kernel work."
        ),
        priority=840,
        pattern=StackPattern(
            required=frozenset({
                "irq_work_run",
                "signal_irq_work",
                "intel_engine_add_retire",
                "queue_work_on",
            }),
        ),
        tags=("irq_work", "gpu", "intel", "workqueue"),
    ),

    # ============================================================
    # 820 — NVIDIA modeset timer
    # ============================================================

    ClassificationRule(
        id="NVIDIA_MODESET_TIMER",
        category="nvidia_modeset_timer",
        description=(
            "A kernel timer invoked an NVIDIA modeset timer callback "
            "which woke the NVIDIA modeset thread."
        ),
        priority=820,
        pattern=StackPattern(
            required=frozenset({
                "nvkms_timer_callback_typed_data",
                "nv_kthread_q_schedule_q_item",
            }),
        ),
        tags=("timer", "nvidia", "gpu"),
    ),

    # ============================================================
    # 810 — RAPL / SMP cross CPU
    # ============================================================

    ClassificationRule(
        id="SMP_CROSS_CPU_RAPL",
        category="smp_cross_cpu_rapl",
        description=(
            "An SMP cross-CPU call performed an MSR read associated "
            "with RAPL energy-counter access."
        ),
        priority=810,
        pattern=StackPattern(
            required=frozenset({
                "flush_smp_call_function_queue",
                "__rdmsr_safe_on_cpu",
            }),
        ),
        tags=("smp", "rapl", "power"),
    ),

    # ============================================================
    # 800 — Threaded IRQ
    # ============================================================

    ClassificationRule(
        id="THREADED_HARDWARE_IRQ",
        category="threaded_hardware_irq",
        description=(
            "A hardware interrupt woke its associated threaded IRQ "
            "handler."
        ),
        priority=800,
        pattern=StackPattern(
            required=frozenset({
                "handle_irq_event",
                "__irq_wake_thread",
            }),
        ),
        tags=("irq", "threaded_irq"),
    ),

    # ============================================================
    # 700 — High-resolution timer
    # ============================================================

    ClassificationRule(
        id="HIGH_RESOLUTION_TIMER",
        category="high_resolution_timer",
        description=(
            "Expiration of a high-resolution timer woke the target."
        ),
        priority=700,
        pattern=StackPattern(
            required=frozenset({
                "hrtimer_interrupt",
                "__hrtimer_run_queues",
                "hrtimer_wakeup",
            }),
        ),
        tags=("timer", "hrtimer"),
    ),

    # ============================================================
    # 650 — RCU
    # ============================================================

    ClassificationRule(
        id="RCU_WAKEUP",
        category="rcu",
        description=(
            "RCU processing caused the RCU grace-period kernel "
            "thread to be woken."
        ),
        priority=650,
        pattern=StackPattern(
            required=frozenset({
                "rcu_core",
                "rcu_gp_kthread_wake",
                "swake_up_one_online",
            }),
        ),
        tags=("rcu", "kernel_thread"),
    ),

    # ============================================================
    # 640 — Delayed work
    # ============================================================

    ClassificationRule(
        id="DELAYED_WORK_TIMER",
        category="delayed_work_timer",
        description=(
            "A kernel timer expired and queued delayed work "
            "on a workqueue."
        ),
        priority=640,
        pattern=StackPattern(
            required=frozenset({
                "run_timer_softirq",
                "__run_timers",
                "delayed_work_timer_fn",
                "__queue_work.part.0",
                "kick_pool",
            }),
        ),
        tags=("timer", "workqueue", "delayed_work"),
    ),

    # ============================================================
    # 600 — process_timeout
    # ============================================================

    ClassificationRule(
        id="PROCESS_TIMEOUT",
        category="timer_process_timeout",
        description=(
            "A kernel timer expired and process_timeout() "
            "caused the target to become runnable."
        ),
        priority=600,
        pattern=StackPattern(
            required=frozenset({
                "run_timer_softirq",
                "__run_timers",
                "process_timeout",
            }),
        ),
        tags=("timer", "timeout"),
    ),

    # ============================================================
    # 300 — Generic timer softirq
    # ============================================================

    ClassificationRule(
        id="GENERIC_TIMER_SOFTIRQ",
        category="timer_softirq",
        description=(
            "An APIC timer interrupt entered the timer subsystem, "
            "but the specific timer callback could not be identified."
        ),
        priority=300,
        pattern=StackPattern(
            required=frozenset({
                "run_timer_softirq",
                "__run_timers",
            }),
        ),
        confidence="medium",
        tags=("timer",),
    ),

    # ============================================================
    # 250 — Generic call-function IPI
    # ============================================================

    ClassificationRule(
        id="SMP_CALL_FUNCTION",
        category="smp_call_function",
        description=(
            "A CPU call-function IPI caused kernel work to execute "
            "while the CPU was idle."
        ),
        priority=250,
        pattern=StackPattern(
            any_of=(
                frozenset({
                    "asm_sysvec_call_function_single",
                    "sysvec_call_function_single",
                }),
            ),
        ),
        confidence="medium",
        tags=("smp", "ipi"),
    ),

    # ============================================================
    # 200 — Generic hardware IRQ
    # ============================================================

    ClassificationRule(
        id="GENERIC_HARDWARE_IRQ",
        category="hardware_interrupt",
        description=(
            "A hardware interrupt interrupted the idle CPU, but "
            "the specific device could not be identified."
        ),
        priority=200,
        pattern=StackPattern(
            any_of=(
                frozenset({
                    "asm_common_interrupt",
                    "common_interrupt",
                    "handle_edge_irq",
                }),
            ),
        ),
        confidence="medium",
        tags=("irq",),
    ),

    # ============================================================
    # 100 — Generic APIC timer
    # ============================================================

    ClassificationRule(
        id="GENERIC_APIC_TIMER",
        category="apic_timer_unknown",
        description=(
            "An APIC timer interrupt occurred while the CPU was "
            "idle, but the specific timer activity was unknown."
        ),
        priority=100,
        pattern=StackPattern(
            any_of=(
                frozenset({
                    "asm_sysvec_apic_timer_interrupt",
                    "sysvec_apic_timer_interrupt",
                }),
            ),
        ),
        confidence="low",
        tags=("timer",),
    ),
]
