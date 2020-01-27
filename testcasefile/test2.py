def passPhrase(string):
    arr = string.split()
    if len(arr) < 1 or not arr:
        return "n/a" 
    Set = set()
    for each in arr:
        if each in Set:
            return "Weak"
        Set.add(each) 

    return "Strong"    
print(passPhrase(input()))
