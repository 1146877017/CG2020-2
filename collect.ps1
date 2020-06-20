$target = ".\submit\***REMOVED***_4\"
$target.Replace("`"", "")
$zip = ".\submit\***REMOVED***_4.7z"
$zip.Replace("`"", "")


Remove-Item -Recurse -ErrorAction Ignore submit
New-Item -ItemType Directory -Force -Path $target
Copy-Item -Recurse .\source $target
Copy-Item -Recurse .\test $target
Copy-Item ".\***REMOVED***_报告.pdf" $target
Copy-Item ".\***REMOVED***_说明书.pdf" $target

Get-ChildItem -Path $target -Include __pycache__ -Recurse | Remove-Item -Recurse
7z a -t7z $zip $target
