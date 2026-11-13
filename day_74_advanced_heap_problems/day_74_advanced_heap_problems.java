import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

/*
 * Advanced Heap Problems
 *
 * Enterprise-oriented Java 17 implementation.
 *
 * Components:
 * 1. Streaming median service
 * 2. Priority-based job scheduling
 * 3. K-way sorted data merging
 * 4. Capital allocation
 * 5. Fuel optimization
 * 6. Deadline-based profit optimization
 *
 * No third-party dependencies.
 */

public class AdvancedHeapProblems {

    // ========================================================
    // 1. DOMAIN EXCEPTIONS
    // ========================================================

    static class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    static class SchedulingException extends DomainException {
        SchedulingException(String message) {
            super(message);
        }
    }


    // ========================================================
    // 2. STREAMING MEDIAN SERVICE
    // ========================================================

    static final class MedianService {

        private final PriorityQueue<Long> lower =
            new PriorityQueue<>(Comparator.reverseOrder());

        private final PriorityQueue<Long> upper =
            new PriorityQueue<>();

        public synchronized void add(long value) {

            lower.offer(value);

            if (
                !upper.isEmpty() &&
                lower.peek() > upper.peek()
            ) {
                upper.offer(lower.poll());
            }

            if (lower.size() > upper.size() + 1) {
                upper.offer(lower.poll());
            } else if (upper.size() > lower.size()) {
                lower.offer(upper.poll());
            }
        }

        public synchronized double median() {

            if (lower.isEmpty()) {
                throw new DomainException(
                    "Cannot calculate an empty stream median"
                );
            }

            if (lower.size() > upper.size()) {
                return lower.peek().doubleValue();
            }

            // Avoid long overflow during addition.
            return lower.peek() / 2.0 + upper.peek() / 2.0;
        }

        public synchronized int size() {
            return lower.size() + upper.size();
        }
    }


    // ========================================================
    // 3. ENTERPRISE JOB DOMAIN
    // ========================================================

    enum JobStatus {
        QUEUED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    record Job(
        String id,
        int priority,
        long duration,
        long sequence
    ) {
        Job {
            if (id == null || id.isBlank()) {
                throw new DomainException("Job ID is required");
            }

            if (priority < 0 || duration <= 0) {
                throw new DomainException("Invalid job properties");
            }
        }
    }

    record JobResult(
        String jobId,
        JobStatus status,
        String message
    ) {}


    interface JobExecutor {
        String execute(Job job) throws Exception;
    }


    static final class JobSchedulingService {

        private final PriorityQueue<Job> queue =
            new PriorityQueue<>(
                Comparator.comparingInt(Job::priority)
                    .thenComparingLong(Job::sequence)
            );

        private final Set<String> identifiers = new HashSet<>();

        private final Map<String, JobResult> results =
            new LinkedHashMap<>();

        private final AtomicLong sequence = new AtomicLong();

        public synchronized void submit(
            String id,
            int priority,
            long duration
        ) {
            Job job = new Job(
                id,
                priority,
                duration,
                sequence.getAndIncrement()
            );

            if (!identifiers.add(id)) {
                throw new SchedulingException(
                    "Duplicate job: " + id
                );
            }

            queue.offer(job);
        }

        public synchronized Optional<Job> nextJob() {
            return Optional.ofNullable(queue.poll());
        }

        public void executeAll(JobExecutor executor) {

            Objects.requireNonNull(executor);

            while (true) {

                Job job;

                synchronized (this) {
                    job = queue.poll();
                }

                if (job == null) {
                    break;
                }

                synchronized (this) {
                    results.put(
                        job.id(),
                        new JobResult(
                            job.id(),
                            JobStatus.RUNNING,
                            "Execution started"
                        )
                    );
                }

                try {
                    String output = executor.execute(job);

                    synchronized (this) {
                        results.put(
                            job.id(),
                            new JobResult(
                                job.id(),
                                JobStatus.COMPLETED,
                                output
                            )
                        );
                    }

                } catch (Exception exception) {

                    synchronized (this) {
                        results.put(
                            job.id(),
                            new JobResult(
                                job.id(),
                                JobStatus.FAILED,
                                exception.getMessage()
                            )
                        );
                    }
                }
            }
        }

        public synchronized List<JobResult> getResults() {
            return List.copyOf(results.values());
        }
    }


    // ========================================================
    // 4. K-WAY MERGE SERVICE
    // ========================================================

    record MergeNode(
        int value,
        int listIndex,
        int elementIndex
    ) {}

    static List<Integer> mergeKSortedLists(
        List<List<Integer>> lists
    ) {

        Comparator<MergeNode> comparator =
            Comparator.comparingInt(MergeNode::value)
                .thenComparingInt(MergeNode::listIndex);

        PriorityQueue<MergeNode> heap =
            new PriorityQueue<>(comparator);

        long totalElements = 0;

        for (int i = 0; i < lists.size(); i++) {

            List<Integer> list = lists.get(i);

            for (int j = 1; j < list.size(); j++) {
                if (list.get(j - 1) > list.get(j)) {
                    throw new DomainException(
                        "Input sequence is not sorted"
                    );
                }
            }

            totalElements += list.size();

            if (!list.isEmpty()) {
                heap.offer(
                    new MergeNode(
                        list.get(0),
                        i,
                        0
                    )
                );
            }
        }

        if (totalElements > Integer.MAX_VALUE) {
            throw new DomainException(
                "Result exceeds Java List capacity"
            );
        }

        List<Integer> result =
            new ArrayList<>((int) totalElements);

        while (!heap.isEmpty()) {

            MergeNode current = heap.poll();

            result.add(current.value());

            int nextIndex = current.elementIndex() + 1;

            List<Integer> source =
                lists.get(current.listIndex());

            if (nextIndex < source.size()) {
                heap.offer(
                    new MergeNode(
                        source.get(nextIndex),
                        current.listIndex(),
                        nextIndex
                    )
                );
            }
        }

        return List.copyOf(result);
    }


    // ========================================================
    // 5. CAPITAL ALLOCATION POLICY
    // ========================================================

    record Project(
        String id,
        long requiredCapital,
        long profit
    ) {
        Project {
            if (
                id == null ||
                id.isBlank() ||
                requiredCapital < 0 ||
                profit < 0
            ) {
                throw new DomainException(
                    "Invalid project"
                );
            }
        }
    }

    record CapitalDecision(
        long initialCapital,
        long finalCapital,
        List<String> selectedProjects
    ) {}


    static final class CapitalAllocationService {

        public CapitalDecision allocate(
            long initialCapital,
            List<Project> projects,
            int maximumProjects
        ) {
            if (initialCapital < 0 || maximumProjects < 0) {
                throw new DomainException(
                    "Invalid allocation parameters"
                );
            }

            Set<String> ids = new HashSet<>();

            for (Project project : projects) {
                if (!ids.add(project.id())) {
                    throw new DomainException(
                        "Duplicate project ID"
                    );
                }
            }

            List<Project> sorted =
                new ArrayList<>(projects);

            sorted.sort(
                Comparator.comparingLong(Project::requiredCapital)
            );

            PriorityQueue<Project> affordable =
                new PriorityQueue<>(
                    Comparator.comparingLong(Project::profit)
                        .reversed()
                        .thenComparing(Project::id)
                );

            long capital = initialCapital;
            int index = 0;

            List<String> selected = new ArrayList<>();

            for (int i = 0; i < maximumProjects; i++) {

                while (
                    index < sorted.size() &&
                    sorted.get(index).requiredCapital() <= capital
                ) {
                    affordable.offer(sorted.get(index));
                    index++;
                }

                if (
                    affordable.isEmpty() ||
                    affordable.peek().profit() == 0
                ) {
                    break;
                }

                Project project = affordable.poll();

                try {
                    capital = Math.addExact(
                        capital,
                        project.profit()
                    );
                } catch (ArithmeticException exception) {
                    throw new DomainException(
                        "Capital overflow"
                    );
                }

                selected.add(project.id());
            }

            return new CapitalDecision(
                initialCapital,
                capital,
                List.copyOf(selected)
            );
        }
    }


    // ========================================================
    // 6. REFUELING OPTIMIZATION
    // ========================================================

    record Station(
        long position,
        long fuel
    ) {}

    record RefuelingDecision(
        int minimumStops,
        List<Integer> stationIndices
    ) {}


    static RefuelingDecision minimumRefuelingStops(
        long target,
        long initialFuel,
        List<Station> stations
    ) {
        if (target < 0 || initialFuel < 0) {
            throw new DomainException(
                "Invalid journey parameters"
            );
        }

        record IndexedStation(
            Station station,
            int index
        ) {}

        List<IndexedStation> sorted = new ArrayList<>();

        for (int i = 0; i < stations.size(); i++) {

            Station station = stations.get(i);

            if (
                station.position() < 0 ||
                station.position() > target ||
                station.fuel() < 0
            ) {
                throw new DomainException(
                    "Invalid fuel station"
                );
            }

            sorted.add(new IndexedStation(station, i));
        }

        sorted.sort(
            Comparator.comparingLong(
                item -> item.station().position()
            )
        );

        for (int i = 1; i < sorted.size(); i++) {
            if (
                sorted.get(i - 1).station().position() ==
                sorted.get(i).station().position()
            ) {
                throw new DomainException(
                    "Duplicate station position"
                );
            }
        }

        PriorityQueue<IndexedStation> heap =
            new PriorityQueue<>(
                Comparator.comparingLong(
                    (IndexedStation item) ->
                        item.station().fuel()
                ).reversed()
            );

        long reachable = initialFuel;

        List<Integer> selected = new ArrayList<>();

        for (IndexedStation current : sorted) {

            while (reachable < current.station().position()) {

                if (heap.isEmpty()) {
                    return new RefuelingDecision(-1, List.of());
                }

                IndexedStation best = heap.poll();

                try {
                    reachable = Math.addExact(
                        reachable,
                        best.station().fuel()
                    );
                } catch (ArithmeticException exception) {
                    throw new DomainException("Fuel overflow");
                }

                selected.add(best.index());
            }

            heap.offer(current);
        }

        while (reachable < target) {

            if (heap.isEmpty()) {
                return new RefuelingDecision(-1, List.of());
            }

            IndexedStation best = heap.poll();

            try {
                reachable = Math.addExact(
                    reachable,
                    best.station().fuel()
                );
            } catch (ArithmeticException exception) {
                throw new DomainException("Fuel overflow");
            }

            selected.add(best.index());
        }

        return new RefuelingDecision(
            selected.size(),
            List.copyOf(selected)
        );
    }


    // ========================================================
    // 7. DEADLINE-BASED PROFIT OPTIMIZATION
    // ========================================================

    record DeadlineTask(
        String id,
        int deadline,
        long profit
    ) {
        DeadlineTask {
            if (
                id == null ||
                id.isBlank() ||
                deadline <= 0 ||
                profit < 0
            ) {
                throw new DomainException(
                    "Invalid deadline task"
                );
            }
        }
    }

    record DeadlineDecision(
        long maximumProfit,
        List<String> selectedTasks
    ) {}


    static DeadlineDecision maximizeDeadlineProfit(
        List<DeadlineTask> tasks
    ) {
        Set<String> ids = new HashSet<>();

        for (DeadlineTask task : tasks) {
            if (!ids.add(task.id())) {
                throw new DomainException(
                    "Duplicate deadline task"
                );
            }
        }

        List<DeadlineTask> sorted =
            new ArrayList<>(tasks);

        sorted.sort(
            Comparator.comparingInt(DeadlineTask::deadline)
                .thenComparing(DeadlineTask::id)
        );

        PriorityQueue<DeadlineTask> selected =
            new PriorityQueue<>(
                Comparator.comparingLong(DeadlineTask::profit)
                    .thenComparing(DeadlineTask::id)
            );

        long totalProfit = 0;

        for (DeadlineTask task : sorted) {

            try {
                totalProfit = Math.addExact(
                    totalProfit,
                    task.profit()
                );
            } catch (ArithmeticException exception) {
                throw new DomainException("Profit overflow");
            }

            selected.offer(task);

            if (selected.size() > task.deadline()) {
                totalProfit -= selected.poll().profit();
            }
        }

        List<String> idsSelected =
            selected.stream()
                .map(DeadlineTask::id)
                .sorted()
                .toList();

        return new DeadlineDecision(
            totalProfit,
            idsSelected
        );
    }


    // ========================================================
    // 8. INTEGRATION TESTS
    // ========================================================

    public static void main(String[] args) {

        System.out.println("\nADVANCED HEAP PROBLEMS");
        System.out.println("=".repeat(55));

        // Streaming median
        System.out.println("\n1. Streaming Median");

        MedianService median = new MedianService();

        for (long value : List.of(12L, 4L, 5L, 3L, 8L, 7L)) {
            median.add(value);
            System.out.println(
                value + " => " + median.median()
            );
        }

        assert median.median() == 6.0;

        // Job scheduling
        System.out.println("\n2. Enterprise Job Scheduling");

        JobSchedulingService service =
            new JobSchedulingService();

        service.submit("Backup", 3, 20);
        service.submit("Security", 1, 10);
        service.submit("Analytics", 2, 15);

        service.executeAll(
            job -> "Executed " + job.id()
        );

        service.getResults().forEach(System.out::println);

        assert service.getResults().size() == 3;

        // K-way merge
        System.out.println("\n3. Merge K Sorted Lists");

        List<Integer> merged = mergeKSortedLists(
            List.of(
                List.of(1, 4, 7),
                List.of(2, 5, 8),
                List.of(3, 6, 9)
            )
        );

        System.out.println(merged);

        assert merged.equals(
            List.of(1, 2, 3, 4, 5, 6, 7, 8, 9)
        );

        // Capital optimization
        System.out.println("\n4. Capital Allocation");

        CapitalDecision capital =
            new CapitalAllocationService().allocate(
                1,
                List.of(
                    new Project("Infrastructure", 0, 2),
                    new Project("Analytics", 1, 5),
                    new Project("Security", 2, 8),
                    new Project("Cloud", 5, 10)
                ),
                3
            );

        System.out.println(capital);

        assert capital.finalCapital() == 16;

        // Refueling
        System.out.println("\n5. Refueling Optimization");

        RefuelingDecision refueling =
            minimumRefuelingStops(
                100,
                10,
                List.of(
                    new Station(10, 60),
                    new Station(20, 30),
                    new Station(30, 30),
                    new Station(60, 40)
                )
            );

        System.out.println(refueling);

        assert refueling.minimumStops() == 2;

        // Deadline optimization
        System.out.println("\n6. Deadline Profit Optimization");

        DeadlineDecision deadline =
            maximizeDeadlineProfit(
                List.of(
                    new DeadlineTask("A", 2, 100),
                    new DeadlineTask("B", 1, 19),
                    new DeadlineTask("C", 2, 27),
                    new DeadlineTask("D", 1, 25),
                    new DeadlineTask("E", 3, 15)
                )
            );

        System.out.println(deadline);

        assert deadline.maximumProfit() == 142;

        // Failure handling
        System.out.println("\n7. Validation");

        try {
            median = new MedianService();
            median.median();

            throw new AssertionError(
                "Empty median should have failed"
            );

        } catch (DomainException expected) {
            System.out.println(
                "Empty stream correctly rejected"
            );
        }

        RefuelingDecision unreachable =
            minimumRefuelingStops(100, 10, List.of());

        assert unreachable.minimumStops() == -1;

        System.out.println("All validations passed.");
    }
}
