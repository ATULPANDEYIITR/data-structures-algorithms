import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;
import java.util.List;
import java.util.Random;

public class AdvancedLinkedListProblems {

    static final class ListNode {
        final int value;
        ListNode next;

        ListNode(int value) {
            this.value = value;
        }
    }

    static final class RandomNode {
        final int value;
        RandomNode next;
        RandomNode random;

        RandomNode(int value) {
            this.value = value;
        }
    }

    static final class MultiNode {
        final int value;
        MultiNode prev;
        MultiNode next;
        MultiNode child;

        MultiNode(int value) {
            this.value = value;
        }
    }

    /*
     * The service class contains algorithms that mutate links in place.
     * Returning the new head is essential for operations such as reversal,
     * merge sort, partitioning, and k-group reversal because the original
     * head may no longer be the first node.
     */
    static final class LinkedListAlgorithms {

        private LinkedListAlgorithms() {
        }

        static ListNode build(List<Integer> values) {
            ListNode head = null;
            ListNode tail = null;

            for (int value : values) {
                ListNode node = new ListNode(value);

                if (head == null) {
                    head = node;
                } else {
                    tail.next = node;
                }

                tail = node;
            }

            return head;
        }

        static List<Integer> values(ListNode head) {
            List<Integer> result = new ArrayList<>();
            ListNode current = head;

            while (current != null) {
                result.add(current.value);
                current = current.next;
            }

            return result;
        }

        static ListNode reverse(ListNode head) {
            ListNode previous = null;
            ListNode current = head;

            while (current != null) {
                ListNode next = current.next;
                current.next = previous;
                previous = current;
                current = next;
            }

            return previous;
        }

        /*
         * Intersection is an identity problem. Java's == compares references,
         * so it correctly answers whether two traversal paths reach the same
         * physical ListNode.
         */
        static ListNode intersection(ListNode first, ListNode second) {
            ListNode a = first;
            ListNode b = second;

            while (a != b) {
                a = (a == null) ? second : a.next;
                b = (b == null) ? first : b.next;
            }

            return a;
        }

        static ListNode mergeSorted(ListNode first, ListNode second) {
            ListNode dummy = new ListNode(0);
            ListNode tail = dummy;

            while (first != null && second != null) {
                if (first.value <= second.value) {
                    tail.next = first;
                    first = first.next;
                } else {
                    tail.next = second;
                    second = second.next;
                }

                tail = tail.next;
            }

            tail.next = first != null ? first : second;
            return dummy.next;
        }

        static ListNode mergeSort(ListNode head) {
            if (head == null || head.next == null) {
                return head;
            }

            ListNode slow = head;
            ListNode fast = head.next;

            while (fast != null && fast.next != null) {
                slow = slow.next;
                fast = fast.next.next;
            }

            ListNode right = slow.next;
            slow.next = null;

            ListNode leftSorted = mergeSort(head);
            ListNode rightSorted = mergeSort(right);

            return mergeSorted(leftSorted, rightSorted);
        }

        static ListNode stablePartition(ListNode head, int pivot) {
            ListNode lessDummy = new ListNode(0);
            ListNode greaterDummy = new ListNode(0);

            ListNode lessTail = lessDummy;
            ListNode greaterTail = greaterDummy;

            ListNode current = head;

            while (current != null) {
                ListNode next = current.next;
                current.next = null;

                if (current.value < pivot) {
                    lessTail.next = current;
                    lessTail = current;
                } else {
                    greaterTail.next = current;
                    greaterTail = current;
                }

                current = next;
            }

            lessTail.next = greaterDummy.next;
            return lessDummy.next;
        }

        static ListNode reverseKGroup(ListNode head, int k) {
            if (k <= 1 || head == null) {
                return head;
            }

            ListNode dummy = new ListNode(0);
            dummy.next = head;

            ListNode groupPrevious = dummy;

            while (true) {
                ListNode kth = groupPrevious;

                for (int i = 0; i < k; i++) {
                    kth = kth.next;

                    if (kth == null) {
                        return dummy.next;
                    }
                }

                ListNode groupNext = kth.next;
                ListNode previous = groupNext;
                ListNode current = groupPrevious.next;

                while (current != groupNext) {
                    ListNode next = current.next;
                    current.next = previous;
                    previous = current;
                    current = next;
                }

                ListNode oldGroupHead = groupPrevious.next;
                groupPrevious.next = kth;
                groupPrevious = oldGroupHead;
            }
        }

        static ListNode detectCycleEntry(ListNode head) {
            ListNode slow = head;
            ListNode fast = head;

            while (fast != null && fast.next != null) {
                slow = slow.next;
                fast = fast.next.next;

                if (slow == fast) {
                    slow = head;

                    while (slow != fast) {
                        slow = slow.next;
                        fast = fast.next;
                    }

                    return slow;
                }
            }

            return null;
        }

        /*
         * Interleaving creates copied nodes without a Map.
         *
         * This is a useful example of an algorithm whose correctness depends
         * on temporarily changing the data structure and then restoring it.
         */
        static RandomNode copyRandomList(RandomNode head) {
            if (head == null) {
                return null;
            }

            RandomNode current = head;

            while (current != null) {
                RandomNode copy = new RandomNode(current.value);
                copy.next = current.next;
                current.next = copy;
                current = copy.next;
            }

            current = head;

            while (current != null) {
                RandomNode copy = current.next;

                if (current.random != null) {
                    copy.random = current.random.next;
                }

                current = copy.next;
            }

            RandomNode copiedHead = head.next;
            current = head;

            while (current != null) {
                RandomNode copy = current.next;
                RandomNode originalNext = copy.next;

                current.next = originalNext;
                copy.next =
                        originalNext == null ? null : originalNext.next;

                current = originalNext;
            }

            return copiedHead;
        }

        /*
         * Flattening uses an explicit stack instead of recursion. This keeps
         * deeply nested structures from consuming the Java call stack.
         */
        static MultiNode flatten(MultiNode head) {
            if (head == null) {
                return null;
            }

            Deque<MultiNode> stack = new ArrayDeque<>();
            stack.push(head);

            MultiNode previous = null;

            while (!stack.isEmpty()) {
                MultiNode current = stack.pop();

                if (previous != null) {
                    previous.next = current;
                    current.prev = previous;
                }

                if (current.next != null) {
                    stack.push(current.next);
                }

                if (current.child != null) {
                    stack.push(current.child);
                    current.child = null;
                }

                previous = current;
            }

            if (previous != null) {
                previous.next = null;
            }

            return head;
        }
    }

    /*
     * Enterprise-style validation service. It does not alter the list, which
     * separates structural validation from pointer-mutating algorithms.
     */
    static final class ListValidator {

        private ListValidator() {
        }

        static void requireValidGroupSize(int k) {
            if (k < 1) {
                throw new IllegalArgumentException(
                        "Group size must be at least 1.");
            }
        }

        static void requireAcyclic(ListNode head) {
            if (LinkedListAlgorithms.detectCycleEntry(head) != null) {
                throw new IllegalStateException(
                        "Operation requires an acyclic linked list.");
            }
        }
    }

    static RandomNode buildRandomExample() {
        RandomNode[] nodes = {
                new RandomNode(7),
                new RandomNode(13),
                new RandomNode(11),
                new RandomNode(10),
                new RandomNode(1)
        };

        for (int i = 0; i < nodes.length - 1; i++) {
            nodes[i].next = nodes[i + 1];
        }

        nodes[1].random = nodes[0];
        nodes[2].random = nodes[4];
        nodes[3].random = nodes[2];
        nodes[4].random = nodes[4];

        return nodes[0];
    }

    static String randomDescription(RandomNode head) {
        StringBuilder result = new StringBuilder();
        RandomNode current = head;

        while (current != null) {
            if (result.length() > 0) {
                result.append(" -> ");
            }

            result.append("(")
                    .append(current.value)
                    .append(", random=")
                    .append(current.random == null
                            ? "null"
                            : current.random.value)
                    .append(")");

            current = current.next;
        }

        return result.toString();
    }

    static MultiNode buildMultilevelExample() {
        MultiNode[] nodes = new MultiNode[7];

        for (int i = 0; i < nodes.length; i++) {
            nodes[i] = new MultiNode(i + 1);
        }

        nodes[0].next = nodes[1];
        nodes[1].prev = nodes[0];

        nodes[1].next = nodes[2];
        nodes[2].prev = nodes[1];

        nodes[2].next = nodes[3];
        nodes[3].prev = nodes[2];

        nodes[1].child = nodes[4];

        nodes[4].next = nodes[5];
        nodes[5].prev = nodes[4];

        nodes[5].child = nodes[6];

        return nodes[0];
    }

    static List<Integer> multiValues(MultiNode head) {
        List<Integer> result = new ArrayList<>();

        while (head != null) {
            result.add(head.value);
            head = head.next;
        }

        return result;
    }

    static void demonstrateIntersection() {
        ListNode shared = LinkedListAlgorithms.build(
                Arrays.asList(8, 10, 12));

        ListNode first = LinkedListAlgorithms.build(
                Arrays.asList(3, 7));

        ListNode firstTail = first;
        while (firstTail.next != null) {
            firstTail = firstTail.next;
        }
        firstTail.next = shared;

        ListNode second = LinkedListAlgorithms.build(
                Arrays.asList(99, 1, 5));

        ListNode secondTail = second;
        while (secondTail.next != null) {
            secondTail = secondTail.next;
        }
        secondTail.next = shared;

        ListNode result =
                LinkedListAlgorithms.intersection(first, second);

        System.out.println("Intersection:");
        System.out.println("  value = " +
                (result == null ? "null" : result.value));
        System.out.println("  same reference = " + (result == shared));
    }

    static void demonstrateSortingAndMerging() {
        ListNode input = LinkedListAlgorithms.build(
                Arrays.asList(7, 2, 9, 1, 5, 2, 8, 3));

        System.out.println("Before merge sort: " +
                LinkedListAlgorithms.values(input));

        input = LinkedListAlgorithms.mergeSort(input);

        System.out.println("After merge sort: " +
                LinkedListAlgorithms.values(input));

        ListNode left = LinkedListAlgorithms.build(
                Arrays.asList(1, 4, 7, 10));

        ListNode right = LinkedListAlgorithms.build(
                Arrays.asList(2, 3, 8, 9));

        ListNode merged =
                LinkedListAlgorithms.mergeSorted(left, right);

        System.out.println("Merged lists: " +
                LinkedListAlgorithms.values(merged));
    }

    static void demonstratePartition() {
        ListNode input = LinkedListAlgorithms.build(
                Arrays.asList(1, 4, 3, 2, 5, 2));

        ListNode result =
                LinkedListAlgorithms.stablePartition(input, 3);

        System.out.println("Stable partition around 3: " +
                LinkedListAlgorithms.values(result));
    }

    static void demonstrateRandomCopy() {
        RandomNode original = buildRandomExample();
        RandomNode copy =
                LinkedListAlgorithms.copyRandomList(original);

        System.out.println("Original random list:");
        System.out.println("  " + randomDescription(original));

        System.out.println("Copied random list:");
        System.out.println("  " + randomDescription(copy));

        if (original == copy) {
            throw new AssertionError("Copy reused original head.");
        }
    }

    static void demonstrateFlattening() {
        MultiNode multilevel = buildMultilevelExample();

        MultiNode flattened =
                LinkedListAlgorithms.flatten(multilevel);

        System.out.println("Flattened multilevel list: " +
                multiValues(flattened));
    }

    static void demonstrateCycleDetection() {
        ListNode cyclic =
                LinkedListAlgorithms.build(
                        Arrays.asList(1, 2, 3, 4, 5));

        ListNode entry = cyclic.next.next;
        ListNode tail = cyclic;

        while (tail.next != null) {
            tail = tail.next;
        }

        tail.next = entry;

        ListNode detected =
                LinkedListAlgorithms.detectCycleEntry(cyclic);

        System.out.println("Cycle entry: " +
                (detected == null ? "none" : detected.value));
    }

    static void randomizedSortVerification() {
        Random random = new Random(42);

        for (int trial = 0; trial < 100; trial++) {
            int size = random.nextInt(21);
            List<Integer> expected = new ArrayList<>();

            for (int i = 0; i < size; i++) {
                expected.add(random.nextInt(41) - 20);
            }

            List<Integer> expectedSorted =
                    new ArrayList<>(expected);

            Collections.sort(expectedSorted);

            ListNode input =
                    LinkedListAlgorithms.build(expected);

            ListNode sorted =
                    LinkedListAlgorithms.mergeSort(input);

            List<Integer> actual =
                    LinkedListAlgorithms.values(sorted);

            if (!actual.equals(expectedSorted)) {
                throw new AssertionError(
                        "Merge sort mismatch: expected "
                                + expectedSorted
                                + ", actual "
                                + actual);
            }
        }

        System.out.println(
                "Randomized merge-sort verification passed.");
    }

    public static void main(String[] args) {
        System.out.println("=== Advanced Linked List Problems ===");
        System.out.println();

        demonstrateIntersection();
        System.out.println();

        demonstrateSortingAndMerging();
        System.out.println();

        demonstratePartition();
        System.out.println();

        demonstrateRandomCopy();
        System.out.println();

        demonstrateFlattening();
        System.out.println();

        demonstrateCycleDetection();
        System.out.println();

        ListNode grouped =
                LinkedListAlgorithms.reverseKGroup(
                        LinkedListAlgorithms.build(
                                Arrays.asList(1, 2, 3, 4, 5, 6, 7)),
                        3);

        System.out.println("Reverse every group of three: " +
                LinkedListAlgorithms.values(grouped));

        System.out.println();

        randomizedSortVerification();

        ListNode single =
                LinkedListAlgorithms.build(
                        List.of(42));

        ListValidator.requireAcyclic(single);
        ListValidator.requireValidGroupSize(3);

        System.out.println();
        System.out.println("All demonstrations completed successfully.");
    }
}
