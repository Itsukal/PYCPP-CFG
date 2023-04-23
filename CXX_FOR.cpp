# include "iostream"
using namespace std;
int main()
{
    int a[5] = {1,2,3,4,5};
    for (auto f:a)
    {
        cout<<f<<endl;
        break;
    }

    bool flag = 3>5?true:false;
    if(flag)
    {
        cout<<flag<<endl;
        return;
    }
    else
    {
        cout<<flag<<endl;
    }
    return 0;
}