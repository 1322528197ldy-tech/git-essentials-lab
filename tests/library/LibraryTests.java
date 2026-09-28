package library;

import java.time.Clock;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Locale;
import java.util.Objects;

/** Behavioral checks without JUnit or network dependencies. */
public final class LibraryTests {
    private static final LocalDate TODAY = LocalDate.of(2026, 9, 1);
    private static int assertions;
    private static int failures;
    private static int student = 2;
    private static int faculty = 2;
    private static int days = 14;
    private static int fee = 100;
    private static boolean sensitive = true;

    private LibraryTests() { }

    public static void main(String[] args) {
        parse(args);
        run("policy", LibraryTests::policy);
        run("catalog and search", LibraryTests::catalog);
        run("student loan limit", () -> limit(MemberType.STUDENT, student));
        run("faculty loan limit", () -> limit(MemberType.FACULTY, faculty));
        run("borrow validation and state", LibraryTests::borrowValidation);
        run("return lifecycle and fees", LibraryTests::returns);
        run("receipt", LibraryTests::receipt);
        System.out.println("RESULT: " + (failures == 0 ? "PASS" : "FAIL")
                + " (" + assertions + " assertions, " + failures + " failed groups)");
        if (failures != 0) {
            System.exit(1);
        }
    }

    private static void parse(String[] args) {
        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--student" -> student = Integer.parseInt(args[++i]);
                case "--faculty" -> faculty = Integer.parseInt(args[++i]);
                case "--days" -> days = Integer.parseInt(args[++i]);
                case "--fee" -> fee = Integer.parseInt(args[++i]);
                case "--search-sensitive" -> sensitive = true;
                case "--search-insensitive" -> sensitive = false;
                default -> throw new IllegalArgumentException("Unknown test argument: " + args[i]);
            }
        }
    }

    private static void run(String name, Runnable test) {
        try {
            test.run();
            System.out.println("PASS " + name);
        } catch (AssertionError | RuntimeException error) {
            failures++;
            System.err.println("FAIL " + name + ": " + error.getMessage());
        }
    }

    private static void policy() {
        LoanPolicy policy = new LoanPolicy();
        equal(student, policy.maxBooks(MemberType.STUDENT), "student cap");
        equal(faculty, policy.maxBooks(MemberType.FACULTY), "faculty cap");
        equal(days, policy.loanDays(), "loan days");
        equal(0, policy.overdueFee(-1), "negative late days clamp");
        equal(0, policy.overdueFee(-30), "early return clamp");
        equal(0, policy.overdueFee(0), "on-time fee");
        equal(fee, policy.overdueFee(1), "one-day fee");
        equal(fee * 3, policy.overdueFee(3), "multi-day fee");
    }

    private static void catalog() {
        Catalog catalog = new Catalog();
        Book git = new Book("git", "Git Essentials");
        Book java = new Book("java", "Practical Java");
        catalog.add(git);
        catalog.add(java);
        equal(git, catalog.book("git"), "lookup book");
        equal(List.of(git, java), catalog.books(), "insertion order");
        equal(List.of(git), catalog.search("Git"), "exact-case search");
        equal(sensitive ? List.of() : List.of(git), catalog.search("git"), "lower-case search");
        equal(sensitive ? List.of() : List.of(git), catalog.search("GIT"), "upper-case search");
        equal(List.of(), catalog.search("No such title"), "missing search");
        equal(2, catalog.search("").size(), "empty query matches all");
        expect(IllegalArgumentException.class, () -> catalog.book("missing"), "unknown book");
        expect(IllegalArgumentException.class, () -> catalog.add(new Book("git", "Replacement")),
                "duplicate book ID");
        equal(git, catalog.book("git"), "duplicate does not overwrite");
        expect(UnsupportedOperationException.class, () -> catalog.books().clear(), "catalog snapshot");
        expect(NullPointerException.class, () -> catalog.search(null), "null search");
        expect(IllegalArgumentException.class, () -> new Book("", "Title"), "blank book ID");
        if (!sensitive) {
            Locale previous = Locale.getDefault();
            try {
                Locale.setDefault(Locale.forLanguageTag("tr-TR"));
                equal(List.of(git), catalog.search("GIT"), "search is independent of default locale");
            } finally {
                Locale.setDefault(previous);
            }
        }
    }

    private static void limit(MemberType type, int cap) {
        Catalog catalog = new Catalog();
        for (int i = 0; i <= cap; i++) {
            catalog.add(new Book("b" + i, "Book " + i));
        }
        LoanService service = new LoanService(catalog, new LoanPolicy(), new TestClock());
        service.registerMember(new Member("m", "Member", type));
        service.registerMember(new Member("other", "Other", type));
        for (int i = 0; i < cap; i++) {
            Loan loan = service.borrow("b" + i, "m");
            equal(TODAY, loan.borrowedOn(), "injected borrow date");
            equal(TODAY.plusDays(days), loan.dueOn(), "policy due date");
        }
        equal(cap, service.loansFor("m").size(), "exact cap can be borrowed");
        expect(IllegalStateException.class, () -> service.borrow("b" + cap, "m"), "cap + 1 rejected");
        equal(cap, service.activeLoans().size(), "rejected borrow leaves state unchanged");
        if (cap > 0) {
            service.borrow("b" + cap, "other");
            equal(1, service.loansFor("other").size(), "caps are per member");
            service.returnBook("b0", "m");
            service.borrow("b0", "m");
            equal(cap, service.loansFor("m").size(), "return frees a loan slot");
        }
    }

    private static LoanPolicy lifecyclePolicy() {
        // Lifecycle checks remain useful even when an exercise changes a borrowing cap.
        return new LoanPolicy() {
            @Override public int maxBooks(MemberType type) { return 10; }
        };
    }

    private static LoanService service(TestClock clock) {
        Catalog catalog = new Catalog();
        catalog.add(new Book("git", "Git Essentials"));
        catalog.add(new Book("java", "Practical Java"));
        LoanService service = new LoanService(catalog, lifecyclePolicy(), clock);
        service.registerMember(new Member("s", "Student", MemberType.STUDENT));
        service.registerMember(new Member("f", "Faculty", MemberType.FACULTY));
        return service;
    }

    private static void borrowValidation() {
        LoanService service = service(new TestClock());
        expect(IllegalArgumentException.class, () -> service.borrow("unknown", "s"), "unknown book borrow");
        expect(IllegalArgumentException.class, () -> service.borrow("git", "unknown"), "unknown member borrow");
        expect(IllegalArgumentException.class,
                () -> service.registerMember(new Member("s", "Replacement", MemberType.FACULTY)),
                "duplicate member ID");
        equal(0, service.activeLoans().size(), "invalid requests create no loans");
        Loan original = service.borrow("git", "s");
        expect(IllegalStateException.class, () -> service.borrow("git", "s"), "same member duplicate loan");
        expect(IllegalStateException.class, () -> service.borrow("git", "f"), "different member duplicate loan");
        equal(List.of(original), service.loansFor("s"), "existing loan retained");
        equal(List.of(), service.loansFor("f"), "second member has no loan");
        expect(UnsupportedOperationException.class, () -> service.activeLoans().clear(), "loan snapshot");
        expect(IllegalArgumentException.class, () -> service.loansFor("unknown"), "unknown member query");
    }

    private static void returns() {
        TestClock clock = new TestClock();
        LoanService service = service(clock);
        Loan first = service.borrow("git", "s");
        expect(IllegalStateException.class, () -> service.returnBook("git", "f"), "wrong member return");
        expect(IllegalArgumentException.class, () -> service.returnBook("missing", "s"), "unknown book return");
        expect(IllegalArgumentException.class, () -> service.returnBook("git", "missing"), "unknown member return");
        equal(List.of(first), service.activeLoans(), "failed returns retain existing loan");
        clock.set(first.dueOn());
        equal(0, service.returnBook("git", "s"), "due-date return is free");
        equal(0, service.activeLoans().size(), "returned loan removed");
        expect(IllegalStateException.class, () -> service.returnBook("git", "s"), "duplicate return rejected");

        Loan next = service.borrow("git", "f");
        clock.set(next.dueOn().plusDays(3));
        equal(fee * 3, service.returnBook("git", "f"), "three-day late fee");
        equal(List.of(), service.loansFor("f"), "late returned loan removed");

        Loan early = service.borrow("java", "s");
        clock.set(early.dueOn().minusDays(1));
        equal(0, service.returnBook("java", "s"), "early return cannot create a negative fee");
    }

    private static void receipt() {
        String title = "Git Essentials";
        String text = new LoanReceipt().format(title);
        equal(true, text != null && !text.isBlank() && text.contains(title), "receipt contains title");
    }

    private static void equal(Object expected, Object actual, String description) {
        assertions++;
        if (!Objects.equals(expected, actual)) {
            throw new AssertionError(description + ": expected " + expected + ", got " + actual);
        }
    }

    private static void expect(Class<? extends Throwable> type, Runnable action, String description) {
        assertions++;
        try {
            action.run();
        } catch (Throwable error) {
            if (type.isInstance(error)) {
                return;
            }
            throw new AssertionError(description + ": expected " + type.getSimpleName()
                    + ", got " + error.getClass().getSimpleName());
        }
        throw new AssertionError(description + ": expected " + type.getSimpleName());
    }

    private static final class TestClock extends Clock {
        private LocalDate date = TODAY;

        void set(LocalDate date) { this.date = date; }
        @Override public ZoneId getZone() { return ZoneOffset.UTC; }
        @Override public Clock withZone(ZoneId zone) { return Clock.fixed(instant(), zone); }
        @Override public Instant instant() { return date.atStartOfDay(ZoneOffset.UTC).toInstant(); }
    }
}
