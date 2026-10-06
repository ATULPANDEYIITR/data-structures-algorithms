import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;

public class FastSlowPointers {

    static final class Node<T> {
        private final T value;
        private Node<T> next;

        Node(T value) {
            this.value = Objects.requireNonNull(value);
        }

        T value() {
            return value;
        }

        Node<T> next() {
            return next;
        }

        void next(Node<T> next) {
            this.next = next;
        }
    }

    enum CycleState {
        ACYCLIC,
        CYCLIC
    }

    record CycleReport<T>(
            CycleState state,
            Node<T> meetingNode,
            Node<T> entryNode,
            int distanceToEntry,
            int cycleLength
    ) {
        static <T> CycleReport<T> acyclic() {
            return new CycleReport<>(
                    CycleState.ACYCLIC,
                    null,
                    null,
                    -1,
                    0
            );
        }
    }

    static final class LinkedList<T> {
        private final List<Node<T>> ownedNodes = new ArrayList<>();
        private Node<T> head;

        void add(T value) {
            Node<T> node = new Node<>(value);
            ownedNodes.add(node);

            if (head == null) {
                head = node;
                return;
            }

            Node<T> current = head;

            while (current.next() != null) {
                current = current.next();
            }

            current.next(node);
        }

        Node<T> head() {
            return head;
        }

        Node<T> nodeAt(int index) {
            if (index < 0) {
                throw new IllegalArgumentException("index cannot be negative");
            }

            Node<T> current = head;

            for (int i = 0; current != null && i < index; i++) {
                current = current.next();
            }

            return current;
        }

        void createCycle(int entryIndex) {
            Node<T> entry = nodeAt(entryIndex);

            if (entry == null) {
                throw new IllegalArgumentException(
                        "entryIndex must identify an existing node"
                );
            }

            Node<T> tail = head;

            if (tail == null) {
                throw new IllegalStateException(
                        "Cannot create a cycle in an empty list"
                );
            }

            while (tail.next() != null) {
                tail = tail.next();
            }

            tail.next(entry);
        }

        String representation(int maximumNodes) {
            StringBuilder result = new StringBuilder();
            List<Node<T>> visited = new ArrayList<>();

            Node<T> current = head;

            while (current != null && visited.size() < maximumNodes) {
                if (visited.contains(current)) {
                    result.append("cycle->").append(current.value());
                    break;
                }

                if (!visited.isEmpty()) {
                    result.append(" -> ");
                }

                visited.add(current);
                result.append(current.value());
                current = current.next();
            }

            if (current != null && visited.size() == maximumNodes) {
                result.append(" -> ...");
            }

            return result.toString();
        }
    }

    static <T> Node<T> middleNode(Node<T> head) {
        Node<T> slow = head;
        Node<T> fast = head;

        while (fast != null && fast.next() != null) {
            slow = slow.next();
            fast = fast.next().next();
        }

        return slow;
    }

    static <T> Node<T> firstMiddleNode(Node<T> head) {
        if (head == null) {
            return null;
        }

        Node<T> slow = head;
        Node<T> fast = head.next();

        while (fast != null && fast.next() != null) {
            slow = slow.next();
            fast = fast.next().next();
        }

        return slow;
    }

    static <T> Node<T> findMeetingNode(Node<T> head) {
        Node<T> slow = head;
        Node<T> fast = head;

        while (fast != null && fast.next() != null) {
            slow = slow.next();
            fast = fast.next().next();

            if (slow == fast) {
                return slow;
            }
        }

        return null;
    }

    static <T> Node<T> findCycleEntry(Node<T> head) {
        Node<T> meeting = findMeetingNode(head);

        if (meeting == null) {
            return null;
        }

        Node<T> fromHead = head;
        Node<T> fromMeeting = meeting;

        while (fromHead != fromMeeting) {
            fromHead = fromHead.next();
            fromMeeting = fromMeeting.next();
        }

        return fromHead;
    }

    static <T> CycleReport<T> analyzeCycle(Node<T> head) {
        Node<T> meeting = findMeetingNode(head);

        if (meeting == null) {
            return CycleReport.acyclic();
        }

        Node<T> entry = findCycleEntry(head);

        int distance = 0;
        Node<T> current = head;

        while (current != entry) {
            distance++;
            current = current.next();
        }

        int length = 1;
        current = entry.next();

        while (current != entry) {
            length++;
            current = current.next();
        }

        return new CycleReport<>(
                CycleState.CYCLIC,
                meeting,
                entry,
                distance,
                length
        );
    }

    static <T> boolean removeCycle(Node<T> head) {
        Node<T> entry = findCycleEntry(head);

        if (entry == null) {
            return false;
        }

        Node<T> cycleTail = entry;

        while (cycleTail.next() != entry) {
            cycleTail = cycleTail.next();
        }

        cycleTail.next(null);
        return true;
    }

    static <T> Node<T> nthFromEnd(Node<T> head, int n) {
        if (n <= 0) {
            throw new IllegalArgumentException("n must be positive");
        }

        Node<T> fast = head;

        for (int i = 0; i < n; i++) {
            if (fast == null) {
                return null;
            }

            fast = fast.next();
        }

        Node<T> slow = head;

        while (fast != null) {
            slow = slow.next();
            fast = fast.next();
        }

        return slow;
    }

    static <T> Node<T> reverse(Node<T> head) {
        Node<T> previous = null;
        Node<T> current = head;

        while (current != null) {
            Node<T> following = current.next();
            current.next(previous);
            previous = current;
            current = following;
        }

        return previous;
    }

    static <T> boolean isPalindrome(Node<T> head) {
        if (head == null || head.next() == null) {
            return true;
        }

        Node<T> slow = head;
        Node<T> fast = head;

        while (fast != null && fast.next() != null) {
            slow = slow.next();
            fast = fast.next().next();
        }

        Node<T> reversedSecondHalf = reverse(slow);
        Node<T> left = head;
        Node<T> right = reversedSecondHalf;

        boolean result = true;

        while (right != null) {
            if (!Objects.equals(left.value(), right.value())) {
                result = false;
                break;
            }

            left = left.next();
            right = right.next();
        }

        reverse(reversedSecondHalf);
        return result;
    }

    static <T> Node<T> intersectionNode(Node<T> headA, Node<T> headB) {
        Node<T> a = headA;
        Node<T> b = headB;

        while (a != b) {
            a = a == null ? headB : a.next();
            b = b == null ? headA : b.next();
        }

        return a;
    }

    static int findDuplicateFloyd(int[] values) {
        if (values.length < 2) {
            throw new IllegalArgumentException(
                    "At least two values are required"
            );
        }

        int n = values.length - 1;

        for (int value : values) {
            if (value < 1 || value > n) {
                throw new IllegalArgumentException(
                        "Every value must be between 1 and n"
                );
            }
        }

        /*
         * The integer values are interpreted as next-pointer destinations.
         * This creates the same functional-graph structure that Floyd's
         * cycle algorithm expects.
         */
        int slow = values[0];
        int fast = values[values[0]];

        while (slow != fast) {
            slow = values[slow];
            fast = values[values[fast]];
        }

        int finder = 0;

        while (finder != slow) {
            finder = values[finder];
            slow = values[slow];
        }

        return finder;
    }

    static <T> void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    static void demonstrateEnterpriseQueue() {
        /*
         * Enterprise scenario:
         *
         * A processing queue is represented as linked event records. A bad
         * routing update can accidentally make a record point backward into
         * an earlier record. The governance service needs to detect the loop,
         * identify its entry point, and repair the terminal link.
         *
         * The domain behavior is modeled explicitly instead of relying on a
         * visited set, which keeps auxiliary memory constant.
         */
        LinkedList<String> queue = new LinkedList<>();

        queue.add("ORDER_CREATED");
        queue.add("PAYMENT_AUTHORIZED");
        queue.add("INVENTORY_RESERVED");
        queue.add("SHIPMENT_CREATED");
        queue.add("AUDIT_RECORDED");
        queue.add("NOTIFICATION_SENT");

        queue.createCycle(2);

        CycleReport<String> report = analyzeCycle(queue.head());

        System.out.println("\nENTERPRISE EVENT QUEUE");
        System.out.println("State: " + report.state());
        System.out.println("Meeting record: " + report.meetingNode().value());
        System.out.println("Cycle entry: " + report.entryNode().value());
        System.out.println("Prefix length: " + report.distanceToEntry());
        System.out.println("Cycle length: " + report.cycleLength());

        boolean repaired = removeCycle(queue.head());

        System.out.println("Cycle repaired: " + repaired);
        System.out.println("Queue: " + queue.representation(20));
    }

    static void demonstrateGenericMiddleFinding() {
        LinkedList<String> events = new LinkedList<>();

        events.add("CREATED");
        events.add("VALIDATED");
        events.add("AUTHORIZED");
        events.add("PROCESSED");
        events.add("ARCHIVED");

        Node<String> middle = middleNode(events.head());

        System.out.println("\nGENERIC MIDDLE-NODE SEARCH");
        System.out.println("Middle event: " + middle.value());
    }

    static void demonstrateApprovalHistory() {
        /*
         * This is deliberately a pointer algorithm example, not a generic
         * list traversal. A singly linked audit history can be checked for
         * symmetry without allocating a second collection.
         */
        LinkedList<String> history = new LinkedList<>();

        history.add("REQUESTED");
        history.add("REVIEWED");
        history.add("APPROVED");
        history.add("REVIEWED");
        history.add("REQUESTED");

        System.out.println("\nSYMMETRIC HISTORY");
        System.out.println(
                "Palindrome history: " + isPalindrome(history.head())
        );
    }

    static void demonstrateDuplicateStateDetection() {
        int[][] examples = {
                {1, 3, 4, 2, 2},
                {3, 1, 3, 4, 2},
                {1, 1},
                {2, 2, 2, 2, 2}
        };

        System.out.println("\nDUPLICATE STATE DETECTION");

        for (int[] example : examples) {
            System.out.print("Duplicate: ");
            System.out.println(findDuplicateFloyd(example));
        }
    }

    static void runTests() {
        LinkedList<Integer> empty = new LinkedList<>();

        require(middleNode(empty.head()) == null, "empty middle");
        require(
                analyzeCycle(empty.head()).state() == CycleState.ACYCLIC,
                "empty list must be acyclic"
        );

        LinkedList<Integer> list = new LinkedList<>();
        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);

        require(middleNode(list.head()).value() == 3, "second middle");
        require(firstMiddleNode(list.head()).value() == 2, "first middle");
        require(nthFromEnd(list.head(), 1).value() == 4, "last node");
        require(nthFromEnd(list.head(), 4).value() == 1, "first node");
        require(nthFromEnd(list.head(), 5) == null, "too-large n");

        LinkedList<Integer> cyclic = new LinkedList<>();
        cyclic.add(10);
        cyclic.add(20);
        cyclic.add(30);
        cyclic.add(40);
        cyclic.add(50);
        cyclic.createCycle(2);

        CycleReport<Integer> report = analyzeCycle(cyclic.head());

        require(report.state() == CycleState.CYCLIC, "cycle state");
        require(report.entryNode().value() == 30, "cycle entry");
        require(report.distanceToEntry() == 2, "cycle prefix");
        require(report.cycleLength() == 3, "cycle length");

        require(removeCycle(cyclic.head()), "cycle should be removed");
        require(
                analyzeCycle(cyclic.head()).state() == CycleState.ACYCLIC,
                "cycle must be gone"
        );

        LinkedList<Integer> palindrome = new LinkedList<>();
        palindrome.add(1);
        palindrome.add(2);
        palindrome.add(3);
        palindrome.add(2);
        palindrome.add(1);

        require(isPalindrome(palindrome.head()), "palindrome");

        LinkedList<Integer> nonPalindrome = new LinkedList<>();
        nonPalindrome.add(1);
        nonPalindrome.add(2);
        nonPalindrome.add(3);

        require(!isPalindrome(nonPalindrome.head()), "non-palindrome");

        require(
                findDuplicateFloyd(new int[]{1, 3, 4, 2, 2}) == 2,
                "duplicate 2"
        );

        require(
                findDuplicateFloyd(new int[]{3, 1, 3, 4, 2}) == 3,
                "duplicate 3"
        );

        System.out.println("\nALL JAVA TESTS PASSED");
    }

    public static void main(String[] args) {
        try {
            System.out.println("FAST AND SLOW POINTER TECHNIQUE");
            System.out.println("========================================");

            demonstrateEnterpriseQueue();
            demonstrateGenericMiddleFinding();
            demonstrateApprovalHistory();
            demonstrateDuplicateStateDetection();
            runTests();

            System.out.println("\nCOMPLEXITY");
            System.out.println(
                    "Middle node: O(n) time, O(1) auxiliary space"
            );
            System.out.println(
                    "Cycle detection: O(n) time, O(1) auxiliary space"
            );
            System.out.println(
                    "Cycle entry: O(n) time, O(1) auxiliary space"
            );
            System.out.println(
                    "Cycle removal: O(n) time, O(1) auxiliary space"
            );
            System.out.println(
                    "Nth from end: O(n) time, O(1) auxiliary space"
            );
            System.out.println(
                    "Palindrome: O(n) time, O(1) auxiliary space"
            );
            System.out.println(
                    "Duplicate detection: O(n) time, O(1) auxiliary space"
            );
        } catch (RuntimeException error) {
            System.err.println("Execution failed: " + error.getMessage());
            System.exit(1);
        }
    }
}
