import signal
import os
import asyncio
import multiprocessing

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

WORKERS = ThreadPoolExecutor(max_workers=2, thread_name_prefix="workers")
HELPERS = {"pool": None, "ready": False}


def IgnoreCtrlC():
    """Initializer function for background worker processes that ignores
    interrupt signals (SIGINT), ensuring that keyboard interrupts (Ctrl+C)
    are handled exclusively by the main process without crashing worker pools.

    Passed as an initializer when instantiating a ProcessPoolExecutor:
    pool = ProcessPoolExecutor(max_workers=4, initializer=ignoreCtrlC)
    """
    # Ignore SIGINT in child processes so only the main event loop intercepts Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def HelperReady(future):
    """A completion callback for worker pool initialization tasks that marks
    the helper system as ready once a worker successfully responds.

    Args:
        future (Future): The concurrent future object representing the startup task.

    Attached as a callback to a background initialization submit:
    pool.submit(os.getpid).add_done_callback(helperReady)
    """
    # Ensure the worker startup task completed successfully without cancellation or errors
    if not future.cancelled() and future.exception() is None:
        HELPERS["ready"] = True


def StartHelpers():
    """Initializes a multi-process worker pool for background CPU-bound tasks,
    using a safe spawn context and validating worker readiness via asynchronous callbacks.
    Falls back gracefully if process creation is restricted in the current environment.

    Starts the helper process pool (up to 4 workers) to offload heavy parsing:
    """
    count = min(os.cpu_count() or 1, 4)
    if count < 2:
        return

    try:
        # Enforce 'spawn' context for safe process creation and isolated execution
        pool = ProcessPoolExecutor(max_workers=count, mp_context=multiprocessing.get_context("spawn"),
                                   initializer=IgnoreCtrlC)

        # Warm up workers with a lightweight task and attach a readiness callback
        for _ in range(count):
            pool.submit(os.getpid).add_done_callback(HelperReady)

        HELPERS["pool"] = pool
    except Exception:
        # Fall back to single-process execution if sandboxed or restricted environments block process pools
        HELPERS["pool"] = None


def StopHelpers(cancelQueued=True):
    """Terminates and shuts down the primary helper execution pool,
    resetting global helper availability flags to prevent further faulty dispatches.

    Args:
        cancelQueued (bool): If True, cancels any pending futures queued in the pool
                             upon shutdown. Defaults to True.

    Shuts down the primary helper pool and abandons any queued tasks:
    StopHelpers(cancelQueued=True)

    Shuts down the pool while allowing already running tasks to finish:
    StopHelpers(cancelQueued=False)
    """
    # Atomically extract and clear the pool reference while flipping the ready flag to False
    pool, HELPERS["pool"], HELPERS["ready"] = HELPERS["pool"], None, False

    if pool is not None:
        # Shutdown non-blockingly (wait=False) to avoid freezing the event loop
        pool.shutdown(wait=False, cancel_futures=cancelQueued)


async def ParallelDispatch(function, *args):
    """Dispatches a callback to be executed asynchronously in a background executor pool
    (process or thread pool) to prevent blocking the main event loop.

    Args:
        function (callable): The synchronous function to execute in the executor.
        *args: Variable length argument list to pass directly to the target function.

    Returns:
        Any: The result returned by the executed function.


    Runs a heavy CPU-bound parsing function in a background worker pool:
    result = await Analyse(extractProductPage, html_content, url, json_data)

    If the primary helpers pool fails, it catches the exception,
    switches to the fallback WORKERS pool, and terminates helpers.
    """
    loop = asyncio.get_running_loop()
    pool = HELPERS["pool"]

    # Attempt execution in the primary helper pool if available and marked ready
    if pool is not None and HELPERS["ready"]:
        try:
            return await loop.run_in_executor(pool, function, *args)
        except Exception:
            # Fallback to the dedicated workers pool if the primary helpers fail
            result = await loop.run_in_executor(WORKERS, function, *args)

            # Shut down broken helper pools and continue execution without them
            StopHelpers(cancelQueued=False)
            return result

    # Default path: run in the standard workers executor pool
    return await loop.run_in_executor(WORKERS, function, *args)