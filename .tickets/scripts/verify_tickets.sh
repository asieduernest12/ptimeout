#!/bin/bash
grep -rEc '\\[[x-]\\]' .tickets/*/prd.md | sort
