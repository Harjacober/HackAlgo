import java.util.Scanner;

class Solution {

    public static void main(String[] args) {
        Scanner myObj = new Scanner(System.in); 
        int n = myObj.nextInt();
        for(int i=0;i<n;i++){
            int a=myObj.nextInt();
            int b=myObj.nextInt();
            System.out.println(a+b);
        }
        
    }

}