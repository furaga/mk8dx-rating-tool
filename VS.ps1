Get-Job | Remove-Job

$job = Start-Job {
Set-Location "C:\Users\furag\Documents\prog\python\mk8dx-rating-tool"
Get-Location
venv\Scripts\python.exe plot_result.py
}

Set-Location "C:\Users\furag\Documents\prog\python\mk8dx-rating-tool"
venv\Scripts\python.exe .\run.py --obs_pass "GKzsYMK574JexVLr" --out_csv_path out.csv

