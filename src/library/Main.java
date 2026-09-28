package library;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;

public final class Main {
    private Main() { }

    public static void main(String[] args) {
        Catalog catalog = new Catalog();
        catalog.add(new Book("git", "Git Essentials"));
        catalog.add(new Book("java", "Practical Java"));
        catalog.add(new Book("design", "Software Design"));
        LoanPolicy policy = new LoanPolicy();
        // A fixed date keeps the classroom demonstration reproducible.
        Clock clock = Clock.fixed(Instant.parse("2026-09-01T09:00:00Z"), ZoneOffset.UTC);
        LoanService service = new LoanService(catalog, policy, clock);
        service.registerMember(new Member("s1", "Alex", MemberType.STUDENT));
        service.registerMember(new Member("f1", "Dr. Lee", MemberType.FACULTY));

        System.out.println("Library loan demo (fixed date: 2026-09-01)");
        System.out.println("Student limit: " + policy.maxBooks(MemberType.STUDENT));
        System.out.println("Faculty limit: " + policy.maxBooks(MemberType.FACULTY));
        System.out.println("Search for 'git': " + catalog.search("git"));
        Loan loan = service.borrow("git", "s1");
        System.out.println(new LoanReceipt().format(catalog.book(loan.bookId()).title()));
        System.out.println("Borrowed by: Alex; due: " + loan.dueOn());
        System.out.println("Return fee: " + service.returnBook("git", "s1"));
        System.out.println("Active loans after return: " + service.activeLoans().size());
    }
}
