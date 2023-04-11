#include <iostream>
#include <exception>
using namespace std;

struct MyException : public exception
{
  const char * what () const throw ()
  {
    return "C++ Exception";
  }
};

int main()
{

   int i;
   throw exception();
  try
  {
    throw MyException();
  }

  catch(MyException& e)
  {
    std::cout << "MyException caught" << std::endl;
    std::cout << e.what() << std::endl;
  }

}

// 第一种
//stateDiagram-v2
//state "function foo()" as 0{
//state "try-begin" as 16
//state "throw Expection()" as 17
//state "try-end" as 16end
//
//state "catch Expection & e" as 18
//state "catch expection & anotherE" as 19
//
//16-->17
//17-->16end
//16end-->18
//16end-->19
//
//
//}
//state "foo()" as 348
//0-->348
//[*]-->0
//348-->[*]


// 第二种
