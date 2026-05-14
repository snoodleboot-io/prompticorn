#!/bin/bash
git fetch origin
git merge origin/main
if git status --porcelain | grep -q "UU logo.png"; then
  git checkout --ours logo.png
  git add logo.png
fi
git commit -m "Merge origin/main into feat/github-page"
git push origin feat/github-page
