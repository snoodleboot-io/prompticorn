# Load Testing (Minimal)

## Purpose
Find where a system's latency curve bends, and why, rather than proving it passed
a number someone invented in a planning meeting.

## Core Techniques

### 1. Pick the Test Shape That Finds Your Failure
| Shape | Profile | What it finds |
|---|---|---|
| Load | Expected peak, held 15–30 min | Whether normal traffic meets the SLO |
| Stress | Ramp past peak until it breaks | The knee, and the failure mode past it |
| Soak | 60–80% of peak for 4–24 h | Leaks: heap, file descriptors, pools, disk |
| Spike | 10× in seconds, then drop | Cold starts, autoscale lag, thundering herd |

A soak is the only shape that finds a leak, because a leak needs time. A spike is
the only shape that finds autoscale lag, because a gentle ramp gives the scaler
warning it will not get in production. Running one shape and calling it "load
testing" leaves three failure classes untested.

### 2. Drive Load Open-Loop
```python
from locust import HttpUser, task, constant_throughput

class Checkout(HttpUser):
    # Each user targets 2 req/s regardless of how slow responses get
    wait_time = constant_throughput(2)

    @task(4)
    def browse(self):
        # name= groups dynamic URLs into one stat line
        self.client.get("/api/products?page=1", name="/api/products")

    @task(1)
    def add_to_cart(self):
        self.client.post("/api/cart", json={"sku": "A-1042", "qty": 1})
```
A closed model — N virtual users that each wait for a response before sending
again — throttles itself the instant the server slows. Offered load falls as
latency rises, queues never build, and the system looks stable right up to the
point where it isn't. Real users and upstream callers do not wait politely; they
retry. Holding arrival rate constant is what exposes queue collapse.

### 3. Report Percentiles, Never the Mean
A mean of 120 ms hides a p99 of 4 s. At 40 backend calls per page render, a p99
of 4 s means roughly a third of page loads contain a four-second call. Report
p50, p95, p99, and max; set thresholds on p95/p99. Averaging per-minute p95s
across a run is also wrong — aggregate from the underlying histograms. See
`slo-sli-definition` for turning these into targets.

### 4. Warm Before You Measure
Discard the first 2–5 minutes. Cold JIT, empty caches, unfilled connection pools,
and lazily-initialised classes make the opening minute of every run look awful,
and folding it in makes a healthy build read as a regression. Warm deliberately,
then open the measurement window.

### 5. Test Against Production-Scale Data
A query that uses an index on 10k rows can flip to a sequential scan at 10M when
the planner's cardinality estimate changes. Cache hit rates collapse once the
working set outgrows memory. Load testing against a seeded dev database measures
a system you do not operate. Match row counts, key distribution (Zipfian, not
uniform), and index state.

### 6. Find the Knee, Not a Verdict
Ramp arrival rate in steps and plot throughput and p99 against offered load.
Below the knee, throughput rises and latency stays flat. At the knee, throughput
flattens while p99 climbs steeply. Past it, throughput *falls* as retries and
timeouts eat capacity. "Knee at 3,200 req/s; p99 crosses 800 ms at 2,900;
bottleneck is the 20-connection DB pool" is an engineering result. "PASS" is not.

## Warning Signs

- Only one test shape ever runs, usually a ten-minute load test
- Results reported as an average response time
- Fixed virtual-user count with a think-time sleep, described as an open model
- The load generator saturating its own CPU or ephemeral ports, unmeasured
- A few thousand rows of test data against a production table of millions
- Every request hitting the same hot key, so caches look perfect
- The first minute of the run included in the reported numbers
- No resource telemetry beside the latency graph, so the bottleneck is a guess
- Tests run against a shared environment with other traffic on it
