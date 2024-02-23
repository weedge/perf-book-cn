#!/bin/bash

find ./zh/chapters/* -type f -name "*.md" -exec rename 's/ /_/g' {} \;
