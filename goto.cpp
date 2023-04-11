#include <iostream>
using namespace std;

int main() {
   int i, j;

   goto endloop;
    cout<<"no"<<endl;
   endloop:
   cout << "Jumped out of loop at i = " << i << ", j = " << j << endl;
   goto test;
   fun:
   cout << "fun" << j << endl;

   test:
   cout<<"test"<<endl;
   return 0;
}