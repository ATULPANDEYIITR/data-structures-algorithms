import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.PriorityQueue;

/*
 * Enterprise service-desk escalation and processing scheduler.
 *
 * Compile and run:
 *   javac PriorityQueueDemo.java
 *   java PriorityQueueDemo
 *
 * Java 17 or later; no third-party dependencies.
 */
public class PriorityQueueDemo {

    enum Severity {
        LOW(20),
        NORMAL(40),
        HIGH(70),
        CRITICAL(100);

        private final int score;

        Severity(int score) {
            this.score = score;
        }

        int score() {
            return score;
        }
    }

    enum TicketState {
        QUEUED,
        ASSIGNED,
        RESOLVED,
        CANCELLED
    }

    record TicketSnapshot(
            String id,
            String service,
            String summary,
            Severity severity,
            int escalationLevel,
            long arrivalSequence,
            TicketState state
    ) {}

    static final class Ticket {
        private final String id;
        private final String service;
        private final String summary;
        private final long arrivalSequence;

        private Severity severity;
        private int escalationLevel;
        private TicketState state;

        Ticket(String id, String service, String summary,
               Severity severity, long arrivalSequence) {
            this.id = requireText(id, "Ticket ID");
            this.service = requireText(service, "Service");
            this.summary = requireText(summary, "Summary");
            this.severity = Objects.requireNonNull(severity, "Severity");
            this.arrivalSequence = arrivalSequence;
            this.escalationLevel = 0;
            this.state = TicketState.QUEUED;
        }

        private static String requireText(String value, String field) {
            if (value == null || value.isBlank()) {
                throw new IllegalArgumentException(field + " cannot be blank");
            }
            return value;
        }

        int effectivePriority() {
            return Math.min(100, severity.score() + escalationLevel * 10);
        }

        TicketSnapshot snapshot() {
            return new TicketSnapshot(
                    id, service, summary, severity, escalationLevel,
                    arrivalSequence, state
            );
        }
    }

    record QueueEntry(
            String ticketId,
            long version,
            int effectivePriority,
            long insertionSequence
    ) {}

    static final class TicketScheduler {
        private final Map<String, Ticket> tickets = new HashMap<>();
        private final Map<String, Long> currentVersions = new HashMap<>();
        private final PriorityQueue<QueueEntry> queue =
                new PriorityQueue<>(
                        Comparator.comparingInt(QueueEntry::effectivePriority)
                                .reversed()
                                .thenComparingLong(QueueEntry::insertionSequence)
                );

        private long nextArrivalSequence = 0;
        private long nextQueueSequence = 0;
        private long nextVersion = 0;

        public TicketSnapshot submit(
                String id, String service, String summary, Severity severity) {
            if (tickets.containsKey(id)) {
                throw new IllegalArgumentException("Duplicate ticket: " + id);
            }

            Ticket ticket = new Ticket(
                    id, service, summary, severity, nextArrivalSequence++
            );
            tickets.put(ticket.id, ticket);
            enqueue(ticket);
            return ticket.snapshot();
        }

        private void enqueue(Ticket ticket) {
            long version = ++nextVersion;
            currentVersions.put(ticket.id, version);
            queue.add(new QueueEntry(
                    ticket.id,
                    version,
                    ticket.effectivePriority(),
                    nextQueueSequence++
            ));
        }

        public void escalate(String id, int levels) {
            if (levels < 1 || levels > 10) {
                throw new IllegalArgumentException(
                        "Escalation must be between 1 and 10 levels"
                );
            }

            Ticket ticket = requireQueued(id);
            ticket.escalationLevel = Math.min(
                    10, ticket.escalationLevel + levels
            );
            enqueue(ticket);
        }

        public void changeSeverity(String id, Severity severity) {
            Ticket ticket = requireQueued(id);
            ticket.severity = Objects.requireNonNull(severity, "Severity");
            enqueue(ticket);
        }

        public void cancel(String id) {
            Ticket ticket = requireQueued(id);
            ticket.state = TicketState.CANCELLED;
            currentVersions.remove(id);
        }

        public Optional<TicketSnapshot> assignNext() {
            while (!queue.isEmpty()) {
                QueueEntry entry = queue.remove();
                Long currentVersion = currentVersions.get(entry.ticketId());

                // Old heap entries are discarded after escalation, severity
                // changes, cancellation, or other invalidating transitions.
                if (currentVersion == null ||
                        currentVersion.longValue() != entry.version()) {
                    continue;
                }

                Ticket ticket = tickets.get(entry.ticketId());
                if (ticket == null || ticket.state != TicketState.QUEUED) {
                    continue;
                }

                ticket.state = TicketState.ASSIGNED;
                currentVersions.remove(ticket.id);
                return Optional.of(ticket.snapshot());
            }
            return Optional.empty();
        }

        public void resolve(String id) {
            Ticket ticket = tickets.get(id);
            if (ticket == null || ticket.state != TicketState.ASSIGNED) {
                throw new IllegalStateException(
                        "Only assigned tickets can be resolved: " + id
                );
            }
            ticket.state = TicketState.RESOLVED;
        }

        public List<TicketSnapshot> queuedTickets() {
            return tickets.values().stream()
                    .filter(ticket -> ticket.state == TicketState.QUEUED)
                    .sorted(
                            Comparator.comparingInt(Ticket::effectivePriority)
                                    .reversed()
                                    .thenComparingLong(ticket ->
                                            ticket.arrivalSequence)
                    )
                    .map(Ticket::snapshot)
                    .toList();
        }

        public int physicalQueueSize() {
            return queue.size();
        }

        public void compactQueue() {
            // Rebuild the heap from authoritative queued tickets to reclaim
            // memory when repeated escalations create many stale entries.
            queue.clear();
            for (Ticket ticket : tickets.values()) {
                if (ticket.state == TicketState.QUEUED) {
                    enqueue(ticket);
                }
            }
        }

        private Ticket requireQueued(String id) {
            Ticket ticket = tickets.get(id);
            if (ticket == null || ticket.state != TicketState.QUEUED) {
                throw new IllegalStateException(
                        "Ticket is not queued: " + id
                );
            }
            return ticket;
        }
    }

    private static void printTickets(
            String heading, List<TicketSnapshot> tickets) {
        System.out.println(heading);
        for (TicketSnapshot ticket : tickets) {
            int priority = Math.min(
                    100, ticket.severity().score()
                            + ticket.escalationLevel() * 10
            );
            System.out.printf(
                    "%s | service=%s | priority=%d | severity=%s | %s%n",
                    ticket.id(), ticket.service(), priority,
                    ticket.severity(), ticket.summary()
            );
        }
    }

    public static void main(String[] args) {
        TicketScheduler scheduler = new TicketScheduler();

        scheduler.submit(
                "INC-801", "payments", "Payment authorization failures",
                Severity.CRITICAL
        );
        scheduler.submit(
                "INC-802", "identity", "Elevated login latency",
                Severity.HIGH
        );
        scheduler.submit(
                "REQ-803", "analytics", "Create a scheduled report",
                Severity.LOW
        );
        scheduler.submit(
                "INC-804", "network", "Intermittent service connectivity",
                Severity.NORMAL
        );

        scheduler.escalate("INC-804", 2);
        scheduler.changeSeverity("INC-802", Severity.CRITICAL);
        scheduler.cancel("REQ-803");

        printTickets("Current dispatch order:", scheduler.queuedTickets());

        System.out.println("\nAssignment:");
        Optional<TicketSnapshot> assigned = scheduler.assignNext();
        assigned.ifPresent(ticket -> {
            System.out.println("Assigned " + ticket.id());
            scheduler.resolve(ticket.id());
        });

        System.out.println("\nRemaining queue:");
        printTickets("Queued tickets:", scheduler.queuedTickets());

        System.out.println(
                "Physical heap entries before compaction: "
                        + scheduler.physicalQueueSize()
        );
        scheduler.compactQueue();
        System.out.println(
                "Physical heap entries after compaction: "
                        + scheduler.physicalQueueSize()
        );

        try {
            scheduler.resolve("INC-804");
        } catch (IllegalStateException error) {
            System.out.println("Invalid transition rejected: " + error.getMessage());
        }

        try {
            scheduler.escalate("INC-801", 0);
        } catch (IllegalArgumentException error) {
            System.out.println("Invalid escalation rejected: " + error.getMessage());
        }
    }
}
