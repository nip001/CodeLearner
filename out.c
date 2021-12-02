#include <stdio.h>
int main(void){
float nums;
float a;
float b;
float c;
nums = 5;
printf("What is the Fibonacci of 5?\n");
a = 0;
b = 1;
while(nums>1){
c = a+b;
a = b;
b = c;
nums = nums-1;
}
printf("%.2f\n",(float)(c));
return 0;
}
