package library;

import java.util.Objects;

public final class LoanReceipt {
    public String format(String title) {
        Objects.requireNonNull(title, "Title is required");
        return "Borrowed: " + title;
    }
}
