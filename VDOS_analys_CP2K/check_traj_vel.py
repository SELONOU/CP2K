from ase.io import read

clean_xyz = "mobley_6091882-vel-1.xyz"  # original file

# Clean it with the function from previous script or manually clean file

images = read(clean_xyz, index=":")

print(f"Total frames: {len(images)}")

for i, img in enumerate(images[:5]):
    print(f"Frame {i}:")
    v = img.get_velocities()
    if v is None:
        print("No velocities!")
    else:
        print(f"Velocities shape: {v.shape}")

