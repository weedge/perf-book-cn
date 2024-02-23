#!/bin/bash

# gitbook build

git checkout gh-pages
cp -rf _book/* ./ 
git add -u
git commit -m "Publish book"
git push origin gh-pages

