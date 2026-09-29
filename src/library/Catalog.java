package library;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;

public final class Catalog {
    private final Map<String, Book> books = new LinkedHashMap<>();

    public void add(Book book) {
        Objects.requireNonNull(book, "Book is required");
        if (books.putIfAbsent(book.id(), book) != null) {
            throw new IllegalArgumentException("Duplicate book: " + book.id());
        }
    }

    public Book book(String id) {
        Book book = books.get(id);
        if (book == null) {
            throw new IllegalArgumentException("Unknown book: " + id);
        }
        return book;
    }

    public List<Book> books() {
        return List.copyOf(books.values());
    }

    public List<Book> search(String query) {
        Objects.requireNonNull(query, "Search query is required");
        return books.values().stream()
                .filter(book -> book.title().toLowerCase(Locale.ROOT).contains(query.toLowerCase(Locale.ROOT)))
                .toList();
    }
}
