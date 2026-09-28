package library;

import java.util.Objects;

public record Member(String id, String name, MemberType type) {
    public Member {
        Objects.requireNonNull(id, "Member ID is required");
        Objects.requireNonNull(name, "Member name is required");
        Objects.requireNonNull(type, "Member type is required");
        if (id.isBlank() || name.isBlank()) {
            throw new IllegalArgumentException("Member ID and name must not be blank");
        }
    }
}
