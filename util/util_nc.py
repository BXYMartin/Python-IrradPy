import netCDF4 as nc

if __name__ == '__main__':
    f = nc.Dataset(input())
    print(f)
    print(f.variables.keys())
    print("---- Shapes ----")
    for key in f.variables.keys():
        print(f.variables[key].long_name)
        print(f.variables[key].shape)
