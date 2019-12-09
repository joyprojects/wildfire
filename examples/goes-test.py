import xarray as xr
import glob
import dask as da


def zarr_training_examples(files, to_zarr_directory,
                           tile_size=128, max_hpa=1000, min_hpa=0,
                           timesteps=2, time_stride=2):
    ds = xr.open_mfdataset(files)
    ds = ds.sel(lev=slice(max_hpa, min_hpa))
    ds['QV'] = ds['QV'].fillna(0.0)

    C = ds.lev.shape[0]
    print('levels: {}'.format(ds.lev))
    T = ds['time'].size

    # Split dask.array into blocks with overlap
    def block_array(arr, axis, size=128, stride=128):
        arr = da.array.swapaxes(arr, axis, 0)
        n = arr.shape[0]
        stack = []
        for j in range(0, n, stride):
            j = min(j, n - size)
            stack.append(arr[j:j + size])
        stack = da.array.stack(stack)
        stack = da.array.swapaxes(stack, axis + 1, 1)
        return stack

    # spatial split
    QV_blocks = block_array(ds.QV.data, 3, size=tile_size, stride=tile_size - 20)  # lon
    QV_blocks = block_array(QV_blocks, 3, size=tile_size, stride=tile_size - 20)  # lat
    QV_blocks = QV_blocks.reshape((-1, T, C, tile_size, tile_size))
    # temporal split
    QV_blocks = block_array(QV_blocks, 1, size=timesteps, stride=time_stride)  # time
    QV_blocks = QV_blocks.reshape((-1, timesteps, C, tile_size, tile_size))
    QV_blocks = QV_blocks.rechunk((1, -1, -1, -1, -1))
    # cache examples on disk
    QV_blocks.to_zarr(to_zarr_directory, overwrite=True)
    return QV_blocks


if __name__ == "__main__":
    data_directory = '/nex/datapool/goes/ABI-L1b-RadC/'
    zarr_directory = './data/test'
    tile_size = 140
    data_files = sorted(glob.glob('{}/*/*/*.nc'.format(data_directory)))
    data_files = data_files
    zarr_training_examples(data_files, zarr_directory, tile_size=tile_size,
                           max_hpa=800, min_hpa=300, timesteps=9,
                           time_stride=7)