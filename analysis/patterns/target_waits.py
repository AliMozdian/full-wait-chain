# Target-wait pattern database
from ..rule import ClassificationRule, StackPattern


TARGET_WAIT_RULES = [

    ClassificationRule(
        id="FUTEX_WAIT",
        category="futex",
        description="Target was blocked waiting on a futex.",
        priority=800,
        pattern=StackPattern(
            required=frozenset({
                "futex_wait_queue",
                "__futex_wait",
                "futex_wait",
            }),
        ),
        tags=("futex", "userspace_sync"),
    ),

    ClassificationRule(
        id="NANOSLEEP",
        category="nanosleep",
        description="Target was sleeping using nanosleep.",
        priority=750,
        pattern=StackPattern(
            required=frozenset({
                "do_nanosleep",
                "hrtimer_nanosleep",
            }),
        ),
        tags=("timer", "sleep"),
    ),

    ClassificationRule(
        id="EPOLL_WAIT",
        category="epoll",
        description="Target was blocked waiting in epoll.",
        priority=700,
        pattern=StackPattern(
            required=frozenset({
                "ep_poll",
                "do_epoll_wait",
            }),
        ),
        tags=("io", "epoll"),
    ),

    ClassificationRule(
        id="EPOLL_PWAIT",
        category="epoll",
        description="Target was blocked waiting in epoll_pwait.",
        priority=690,
        pattern=StackPattern(
            required=frozenset({
                "ep_poll",
                "do_epoll_pwait.part.0",
            }),
        ),
        tags=("io", "epoll"),
    ),

    ClassificationRule(
        id="SCHEDULE_TIMEOUT",
        category="schedule_timeout",
        description="Target was blocked using schedule_timeout.",
        priority=600,
        pattern=StackPattern(
            required=frozenset({
                "schedule_timeout",
            }),
        ),
        tags=("timer", "sleep"),
    ),

    ClassificationRule(
        id="WAIT_FOR_COMPLETION",
        category="completion",
        description="Target was waiting for a kernel completion.",
        priority=550,
        pattern=StackPattern(
            required=frozenset({
                "wait_for_completion",
            }),
        ),
        tags=("synchronization", "completion"),
    ),

    ClassificationRule(
        id="WAIT_FOR_COMPLETION_TIMEOUT",
        category="completion_timeout",
        description="Target was waiting for a completion with a timeout.",
        priority=560,
        pattern=StackPattern(
            required=frozenset({
                "wait_for_completion_timeout",
            }),
        ),
        tags=("synchronization", "completion"),
    ),

    ClassificationRule(
        id="WORKER_THREAD",
        category="workqueue",
        description="Target was a kernel worker waiting for work.",
        priority=400,
        pattern=StackPattern(
            required=frozenset({
                "worker_thread",
            }),
        ),
        tags=("kernel_thread", "workqueue"),
    ),

    ClassificationRule(
        id="RCU_GP_THREAD",
        category="rcu_kernel_thread",
        description="Target was the RCU grace-period kernel thread.",
        priority=500,
        pattern=StackPattern(
            required=frozenset({
                "rcu_gp_kthread",
            }),
        ),
        tags=("rcu", "kernel_thread"),
    ),

    ClassificationRule(
        id="MIGRATION_THREAD",
        category="cpu_migration",
        description="Target was a CPU migration kernel thread.",
        priority=500,
        pattern=StackPattern(
            required=frozenset({
                "smpboot_thread_fn",
            }),
        ),
        tags=("scheduler", "migration"),
    ),

    ClassificationRule(
        id="IRQ_THREAD",
        category="threaded_irq",
        description="Target was a threaded interrupt handler.",
        priority=500,
        pattern=StackPattern(
            required=frozenset({
                "irq_thread",
            }),
        ),
        tags=("irq", "kernel_thread"),
    ),

    ClassificationRule(
        id="KTHREAD_SLEEP",
        category="kernel_thread_sleep",
        description="Target was blocked in a kernel thread.",
        priority=100,
        pattern=StackPattern(
            required=frozenset({
                "kthread",
            }),
        ),
        confidence="low",
        tags=("kernel_thread",),
    ),
]
