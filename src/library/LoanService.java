package library;

import java.time.Clock;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/** A small in-memory service; each book ID represents one physical copy. */
public final class LoanService {
    private final Catalog catalog;
    private final LoanPolicy policy;
    private final Clock clock;
    private final Map<String, Member> members = new LinkedHashMap<>();
    private final Map<String, Loan> activeLoans = new LinkedHashMap<>();

    public LoanService(Catalog catalog, LoanPolicy policy, Clock clock) {
        this.catalog = Objects.requireNonNull(catalog);
        this.policy = Objects.requireNonNull(policy);
        this.clock = Objects.requireNonNull(clock);
    }

    public void registerMember(Member member) {
        Objects.requireNonNull(member, "Member is required");
        if (members.putIfAbsent(member.id(), member) != null) {
            throw new IllegalArgumentException("Duplicate member: " + member.id());
        }
    }

    public Loan borrow(String bookId, String memberId) {
        catalog.book(bookId);
        Member member = member(memberId);
        if (activeLoans.containsKey(bookId)) {
            throw new IllegalStateException("Book is already on loan: " + bookId);
        }
        if (loansFor(memberId).size() >= policy.maxBooks(member.type())) {
            throw new IllegalStateException("Loan limit reached for " + memberId);
        }
        LocalDate today = LocalDate.now(clock);
        Loan loan = new Loan(bookId, memberId, today, today.plusDays(policy.loanDays()));
        activeLoans.put(bookId, loan);
        return loan;
    }

    /** Returns the fee in whole currency units and makes the copy available again. */
    public int returnBook(String bookId, String memberId) {
        catalog.book(bookId);
        member(memberId);
        Loan loan = activeLoans.get(bookId);
        if (loan == null) {
            throw new IllegalStateException("Book is not on loan: " + bookId);
        }
        if (!loan.memberId().equals(memberId)) {
            throw new IllegalStateException("Book was borrowed by a different member");
        }
        int daysLate = Math.toIntExact(ChronoUnit.DAYS.between(loan.dueOn(), LocalDate.now(clock)));
        int fee = policy.overdueFee(daysLate);
        activeLoans.remove(bookId);
        return fee;
    }

    public List<Loan> loansFor(String memberId) {
        member(memberId);
        return activeLoans.values().stream()
                .filter(loan -> loan.memberId().equals(memberId))
                .toList();
    }

    public List<Loan> activeLoans() {
        return List.copyOf(activeLoans.values());
    }

    private Member member(String id) {
        Member member = members.get(id);
        if (member == null) {
            throw new IllegalArgumentException("Unknown member: " + id);
        }
        return member;
    }
}
