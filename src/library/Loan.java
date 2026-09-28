package library;

import java.time.LocalDate;
import java.util.Objects;

public record Loan(String bookId, String memberId, LocalDate borrowedOn, LocalDate dueOn) {
    public Loan {
        Objects.requireNonNull(bookId, "Book ID is required");
        Objects.requireNonNull(memberId, "Member ID is required");
        Objects.requireNonNull(borrowedOn, "Borrow date is required");
        Objects.requireNonNull(dueOn, "Due date is required");
        if (bookId.isBlank() || memberId.isBlank() || dueOn.isBefore(borrowedOn)) {
            throw new IllegalArgumentException("Invalid loan details");
        }
    }
}
