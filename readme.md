## deployed on render
it will redeploy on every push to main branch

## run locally
1. clone the repo
2. create a virtual environment
```bash
python3 -m venv venv
```
3. activate the virtual environment
```bash
source venv/bin/activate
```
4. install the requirements
```bash
pip install -r requirements.txt
```
5. run the app
```bash
gunicorn main:app
```

or 
```bash
python main.py
```

## ran tests

## Reference

- [MyGo Line bot project](https://hackmd.io/@StevenShih-0402/mygorobot)