#include <iostream>
#include <string>
#include <map>
using namespace std;

// ─────────────────────────────────────────────────────────────
// FORWARD DECLARATIONS
// ─────────────────────────────────────────────────────────────
class Passenger;
class Flight;
class Booking;
class Airline;

void printHeader(string title);
void printSeparator();

// ─────────────────────────────────────────────────────────────
// ERROR 1: Missing Semicolon (after int flightNumber)
// ERROR 2: Missing #include <vector>
// ─────────────────────────────────────────────────────────────
class Flight {
private:
    int flightNumber
    string origin;
    string destination;
    string departureTime;
    int totalSeats;
    int availableSeats;
    double ticketPrice;
    vector<int> bookedSeatNumbers;

public:
    Flight(int num, string org, string dest, string time, int total, double price) {
        flightNumber = num;
        origin = org;
        destination = dest;
        departureTime = time;
        totalSeats = total;
        availableSeats = total;
        ticketPrice = price;
    }

    int getFlightNumber() const { return flightNumber; }
    string getOrigin() const { return origin; }
    string getDestination() const { return destination; }
    string getDepartureTime() const { return departureTime; }
    int getAvailableSeats() const { return availableSeats; }
    double getTicketPrice() const { return ticketPrice; }

    bool bookSeat(int seatNumber) {
        if (availableSeats <= 0) {
            cout << "Flight " << flightNumber << " is full." << endl;
            return false;
        }
        bookedSeatNumbers.push_back(seatNumber);
        availableSeats--;
        cout << "Seat " << seatNumber << " booked on flight " << flightNumber << endl;
        return true;
    }

    void cancelSeat(int seatNumber) {
        availableSeats++;
        cout << "Seat " << seatNumber << " canceled on flight " << flightNumber << endl;
    }

    void printFlightDetails() const {
        cout << "Flight #: " << flightNumber 
             << " | From: " << origin 
             << " | To: " << destination 
             << " | Time: " << departureTime 
             << " | Seats: " << availableSeats << "/" << totalSeats 
             << " | Price: $" << ticketPrice << endl;
    }
};

// ─────────────────────────────────────────────────────────────
// PASSENGER CLASS
// ─────────────────────────────────────────────────────────────
class Passenger {
private:
    int passengerId;
    string firstName;
    string lastName;
    string passportNumber;
    string email;
    vector<Booking> bookings;

public:
    Passenger(int id, string fname, string lname, string passport, string mail) {
        passengerId = id;
        firstName = fname;
        lastName = lname;
        passportNumber = passport;
        email = mail;
    }

    int getPassengerId() const { return passengerId; }
    string getFullName() const { return firstName + " " + lastName; }
    string getPassportNumber() const { return passportNumber; }
    string getEmail() const { return email; }

    void printPassengerDetails() const {
        cout << "Passenger ID: " << passengerId 
             << " | Name: " << getFullName() 
             << " | Passport: " << passportNumber 
             << " | Email: " << email << endl;
    }
};

// ─────────────────────────────────────────────────────────────
// BOOKING CLASS
// ─────────────────────────────────────────────────────────────
class Booking {
private:
    int bookingId;
    int passengerId;
    int flightNumber;
    int seatNumber;
    double amountPaid;
    string bookingStatus;

public:
    Booking(int bId, int pId, int fNum, int seat, double amount, string status) {
        bookingId = bId;
        passengerId = pId;
        flightNumber = fNum;
        seatNumber = seat;
        amountPaid = amount;
        bookingStatus = status;
    }

    int getBookingId() const { return bookingId; }
    int getPassengerId() const { return passengerId; }
    int getFlightNumber() const { return flightNumber; }
    int getSeatNumber() const { return seatNumber; }
    double getAmountPaid() const { return amountPaid; }
    string getBookingStatus() const { return bookingStatus; }

    void printBooking() const {
        cout << "Booking #: " << bookingId 
             << " | Passenger: " << passengerId 
             << " | Flight: " << flightNumber 
             << " | Seat: " << seatNumber 
             << " | Paid: $" << amountPaid 
             << " | Status: " << bookingStatus << endl;
    }
};

// ─────────────────────────────────────────────────────────────
// ERROR 3: Misspelled keyword (retrun)
// ─────────────────────────────────────────────────────────────
double calculateDiscount(double amount, double discountPercent) {
    double discount = amount * (discountPercent / 100.0);
    retrun discount;
}

// ─────────────────────────────────────────────────────────────
// ERROR 4: Missing Semicolon (after int count)
// ─────────────────────────────────────────────────────────────
void processBookings(vector<Booking>& bookings) {
    int count
    for (const auto& b : bookings) {
        b.printBooking();
        count++;
    }
    cout << "Total bookings processed: " << count << endl;
}

// ─────────────────────────────────────────────────────────────
// ERROR 5: Stream operator flip (cout >>)
// ─────────────────────────────────────────────────────────────
void displayMenu() {
    int choice;
    cout >> "1. Book Flight" >> endl;
    cout >> "2. Cancel Booking" >> endl;
    cout >> "3. View Flights" >> endl;
    cout >> "4. Exit" >> endl;
    cout << "Enter your choice: ";
    cin >> choice;
    
    switch (choice) {
        case 1:
            cout << "Booking flight..." << endl;
            break;
        case 2:
            cout << "Canceling booking..." << endl;
            break;
        case 3:
            cout << "Viewing flights..." << endl;
            break;
        case 4:
            cout << "Exiting..." << endl;
            break;
        default:
            cout << "Invalid choice." << endl;
    }
}

// ─────────────────────────────────────────────────────────────
// UTILITIES
// ─────────────────────────────────────────────────────────────
void printHeader(string title) {
    cout << "\n========================================" << endl;
    cout << "  " << title << endl;
    cout << "========================================" << endl;
}

void printSeparator() {
    cout << "----------------------------------------" << endl;
}

int calculatePower(int base, int exp) {
    if (exp == 0) return 1;
    return base * calculatePower(base, exp - 1);
}

void testRecursion() {
    printHeader("Recursion Tests");
    cout << "2^10 = " << calculatePower(2, 10) << endl;
}

// ─────────────────────────────────────────────────────────────
// MAIN FUNCTION
// ─────────────────────────────────────────────────────────────
int main() {
    printHeader("Airline Management System");

    // 1. Create Flights
    Flight f1(101, "New York", "London", "08:00 AM", 200, 500.00);
    Flight f2(102, "London", "Paris", "12:00 PM", 150, 250.00);
    Flight f3(103, "Paris", "Berlin", "04:00 PM", 100, 150.00);

    // 2. Create Passengers
    Passenger p1(1, "Alice", "Johnson", "AB123456", "alice@example.com");
    Passenger p2(2, "Bob", "Williams", "CD789012", "bob@example.com");

    // 3. List Flights
    printHeader("Available Flights");
    f1.printFlightDetails();
    f2.printFlightDetails();
    f3.printFlightDetails();

    // 4. List Passengers
    printHeader("Registered Passengers");
    p1.printPassengerDetails();
    p2.printPassengerDetails();

    // 5. Book Seats
    printHeader("Booking Seats");
    f1.bookSeat(1);
    f1.bookSeat(2);
    f2.bookSeat(10);
    f3.bookSeat(5);

    // 6. Create Bookings
    vector<Booking> bookings;
    bookings.push_back(Booking(1001, 1, 101, 1, 500.00, "Confirmed"));
    bookings.push_back(Booking(1002, 2, 101, 2, 500.00, "Confirmed"));
    bookings.push_back(Booking(1003, 1, 102, 10, 250.00, "Confirmed"));
    bookings.push_back(Booking(1004, 2, 103, 5, 150.00, "Confirmed"));

    // 7. Process Bookings (Triggers Error 4)
    printHeader("Processing Bookings");
    processBookings(bookings);

    // 8. Calculate Discounts (Triggers Error 3)
    printHeader("Calculating Discounts");
    double discount = calculateDiscount(500.00, 10);
    cout << "Discount: $" << discount << endl;

    // 9. Display Menu (Triggers Error 5)
    printHeader("Menu");
    displayMenu();

    // 10. Test Recursion
    testRecursion();

    printHeader("End of Airline System");
    return 0;
}

// ─────────────────────────────────────────────────────────────
// ERROR 6: Missing closing brace at the end of the file
