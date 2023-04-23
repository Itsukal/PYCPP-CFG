#include <iostream>

//int addNumbers(int a, int b);

int main()
{
//   for(int i=0;i<4;i++)
//   {
//       std::cout<<i<<std::endl;
//   }

//    int i = 0;
//    do
//    {
//        i++;
//    }while(i < 4);

      int  i = 0;
      for(int j = 0; j < 4; j++)
      {
           switch(i)
          {
    //        if(i==3)
    //        {
    //            std::cout<<"0"<<std::endl;
    //        }
            case 1:
                std::cout<<"1"<<std::endl;
                break;
            case 2:
                std::cout<<"2"<<std::endl;
                return;
            case 4:
                std::cout<<"4"<<std::endl;
                continue;
                std::
            case 3:
                std::cout<<"3"<<std::endl;
                break;
            default:
                std::cout<<"other"<<std::endl;
          }
      }

//      int a[5];
//      for(int i = 0; i<5;i++)
//      {
//        a[i]= i;
//      }
//
//      for(item:a)
//      {
//        std::cout<<"num is "<<item<<std::endl;
//      }



//    std::cout<<"start"<<std::endl;
//    auto test = [](int x, int y){ return x < y ; };
//    test(10,20);
//    int ans[20] = {0,};
//
//    if(ans[1]== 0)
//    std::cout<<"good"<<std::endl;
//
//    if(ans[2]==0);
//    int *p = new int(3);
//    if(*p == 3)
//    {
//        std::cout<<"is 3"<<std::endl;
//    }
//
//    if(p)
//    {
//        std::cout<<"exist"<<std::endl;
//    }
//    int flag = 0;
//            while(flag < 4)
//            {
//                flag++;
//                if(flag == 3)
//                {
//                    break;
//                }
//                else
//                std::cout<<"error"<<std::endl;
//                std::cout<<"error"<<std::endl;
//            }
//
//            do
//            {
//                flag--;
//                continue;
//            }while(flag>0);
//    for(int i = 0; i < 4;i++)
//    {
//        for(int j = 0; j < 5;j++)
//        {
//            std::cout<<i<<j<<std::endl;
//
//            int flag = 0;
//            while(flag < 4)
//            {
//                flag++;
//            }
//
//            do
//            {
//                flag--;
//            }while(flag>0)
//        }
//    }
  return 0;
}

//int addNumbers(int a,int b)
//{
//    int result;
//    result = a+b;
//    return result;
//}