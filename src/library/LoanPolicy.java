package library;

public class LoanPolicy {
    public int maxBooks(MemberType type) { return type == MemberType.STUDENT ? 3 : 5; }
    public int loanDays() { return 14; }
    public int overdueFee(int daysLate) { return Math.max(0, daysLate) * 100; }
}
