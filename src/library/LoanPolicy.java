package library;

public class LoanPolicy {
    public int maxBooks(MemberType type) { return type == MemberType.STUDENT ? 2 : 5; }
    public int loanDays() { return 14; }
    public int overdueFee(int daysLate) { return daysLate * 100; }
}
