#!/bin/bash

GROFILE="nvt.gro"
TPRFILE="nvt.tpr"
TRRFILE="nvt.trr"
NDXFILE="index.ndx"

# Create index groups
gmx make_ndx -f $GROFILE -o $NDXFILE << EOF
a C | a C1
name 3 C_atoms
a H | a H1 | a H2 | a H3 | a H4 | a H5
name 4 H_atoms
q
EOF

# Calculate distances between groups
echo "Calculating distances..."

# C - H distance (group-to-group COM distance)
gmx distance -f $TRRFILE -s $TPRFILE -n $NDXFILE -select 'com of group "C_atoms" plus com of group "H_atoms"' -oall dist_C-H.xvg

# C - C distance (in this case between C and C1 COMs)
gmx distance -f $TRRFILE -s $TPRFILE -n $NDXFILE -select 'com of group "C_atoms" plus com of group "C_atoms"' -oall dist_C-C.xvg

# H - H distance (COM distance between all H atoms)
gmx distance -f $TRRFILE -s $TPRFILE -n $NDXFILE -select 'com of group "H_atoms" plus com of group "H_atoms"' -oall dist_H-H.xvg

echo "Distance calculations finished. Output files:"
echo " dist_C-H.xvg"
echo " dist_C-C.xvg"
echo " dist_H-H.xvg"

