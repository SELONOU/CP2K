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

# Run RDF calculations for selected pairs

echo "Calculating RDFs..."

# C - H
gmx rdf -f $TRRFILE -s $TPRFILE -n $NDXFILE -ref C_atoms -sel H_atoms -o rdf_C-H.xvg

# C - C
gmx rdf -f $TRRFILE -s $TPRFILE -n $NDXFILE -ref C_atoms -sel C_atoms -o rdf_C-C.xvg

# H - H
gmx rdf -f $TRRFILE -s $TPRFILE -n $NDXFILE -ref H_atoms -sel H_atoms -o rdf_H-H.xvg

echo "RDF calculations finished. Output files:"
echo " rdf_C-H.xvg"
echo " rdf_C-C.xvg"
echo " rdf_H-H.xvg"

