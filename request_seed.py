import requests
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
STUDENT_ID = "23A91A05A7"
GITHUB_REPO_URL = "https://github.com/Tanoosree2006/securepki"
pub = open("student_public.pem","r",encoding="utf-8").read()
r = requests.post(API_URL, json={"student_id":STUDENT_ID,"github_repo_url":GITHUB_REPO_URL,"public_key":pub}, timeout=20)
print("HTTP", r.status_code); print(r.text)
if r.ok:
    open("encrypted_seed.txt","w",encoding="utf-8").write(r.json()["encrypted_seed"])
    print("Saved encrypted_seed.txt")
