#include <iostream>
class Base { public: virtual int f(){ return 1; } };
class Derived : public Base { public: int f() override { return 2; } };
int main(){ int x=0; if (x) { std::cout << x; } return 0; }
