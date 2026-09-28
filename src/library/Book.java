package library;

import java.util.Objects;

public record Book(String id, String title) {
    public Book {
        Objects.requireNonNull(id, "Book ID is required");
        Objects.requireNonNull(title, "Book title is required");
        if (id.isBlank() || title.isBlank()) {
            throw new IllegalArgumentException("Book ID and title must not be blank");
        }
    }
}
