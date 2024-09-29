from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response=client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message":"Welcome to root page!"}

def test_run():
    #define the request body
    item_data = {
        "language": "cpp",
        "code": "#include<bits/stdc++.h>\nusing namespace std;\nclass Solution {\npublic:\n    bool isValid(string s) {\n        if(s.length()==0)\n            return true;\n        if(s.length()==1)\n            return false;\n        stack<char>s1;\n        int i=0;\n        while(i<s.length())\n        {\n            char c = s[i];\n            if(c==')'||c=='}'||c==']')\n            {\n                if(s1.size()==0)\n                    return 0;\n                if(c==')'&& s1.top()!='(') return false;\n                if(c=='}'&& s1.top()!='{') return false;\n                if(c==']'&&s1.top()!='[') return false;\n                s1.pop();\n            }\n            else\n                s1.push(c);\n            i++;\n        }\n        if(s1.size()==0)\n            return true;\n        return false;\n    }\n};\nint main()\n{\n  Solution s;\n  string str;\n  cin>>str;\n  cout<<s.isValid(str)<<endl;\n  return 0;\n}",
        "input": "(())["
    }

    headers = {
        "Content-Type": "application/json"
    }
    response=client.post("/api/run",json=item_data, headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['output'] == "0\n"

def test_submit():
    item_data = {
        "language": "py",
        "code": "def palindrome() -> bool:\n    y = input()\n    x = int(y)\n    if x < 0 or (x > 0 and x % 10 == 0):\n        return int(False)\n    sum = 0\n    while x > sum:\n        sum = (sum * 10) + x % 10\n        x = x // 10\n    \n    return int((sum // 10 == x or sum == x))\n\nresult = palindrome()\nprint(result)\n",
        "id": 0
    }

    # return int((sum // 10 == x or sum == x)) : here we have modified this to test wrong code
    item_data1 = {
        "language": "py",
        "code": "def palindrome() -> bool:\n    y = input()\n    x = int(y)\n    if x < 0 or (x > 0 and x % 10 == 0):\n        return int(False)\n    sum = 0\n    while x > sum:\n        sum = (sum * 10) + x % 10\n        x = x // 10\n    \n    return int((sum == x))\n\nresult = palindrome()\nprint(result)\n",
        "id": 0
    }

    item_data2 = {
        "language": "cpp",
        "code": "#include<bits/stdc++.h>\nusing namespace std;\nclass Solution {\npublic:\n    bool isPalindrome(int x) {\n       if(x<0 || (x>0 && x%10 ==0))\n            return false;\n        int n=0;\n        while(x>n)\n        {\n            n=n*10+x%10;\n            x/=10;\n        }\n        return (x==n || n/10==x);\n    }\n};\n\nint main()\n{\n  Solution s;\n  int str;\n  cin>>str;\n  cout<<s.isPalindrome(str)<<endl;\n  return 0;\n}",
        "id": 0
    }

    # return (x==n || n/10==x);\n  : here we have modified this to test wrong code
    item_data3 = {
        "language": "py",
        "code": "#include<bits/stdc++.h>\nusing namespace std;\nclass Solution {\npublic:\n    bool isPalindrome(int x) {\n       if(x<0 || (x>0 && x%10 ==0))\n            return false;\n        int n=0;\n        while(x>n)\n        {\n            n=n*10+x%10;\n            x/=10;\n        }\n        return (x==n);\n    }\n};\n\nint main()\n{\n  Solution s;\n  int str;\n  cin>>str;\n  cout<<s.isPalindrome(str)<<endl;\n  return 0;\n}",
        "id": 0
    }

    headers = {
        "Content-Type": "application/json"
    }
    response=client.post("/api/submit",json=item_data, headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['status'] == "Success"

    response=client.post("/api/submit",json=item_data1, headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['status'] == "Failed"

    response=client.post("/api/submit",json=item_data2, headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['status'] == "Success"

    response=client.post("/api/submit",json=item_data3, headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['status'] == "Failed"
