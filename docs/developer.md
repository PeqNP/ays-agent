# Developer

## Release to Production

To trigger a production release:

```bash
$ git tag -a vN -m "Version N on YYYY-MM-DD HH:MMa ZZZ"
```

Example:
```bash
$ git tag -a v1.0 -m "Version 1.0 on 2024-02-22 10:32am PST"
```

## Testing

To test running the `ays-agent`, it is best to do it on a fresh instance of a VM or a Python virtual environment. This ensures that package installation can be tested.

I use [multipass](https://multipass.run/install) for this scenario.

Then run the command, within the VM, to test the installation:

```bash
$ python3 -m pip install --no-cache-dir --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ays-agent
```

This fails 100% of the time as `fastapi` has a broken developer dependency `test.pypi.org`. Using the `extra-index-url` does not pull modules exclusively from PyPI. This would solve the problem. YOLO to prod LOL!

You may need to install `pip` first:

```bash
$ sudo apt-get install python3-pip
```

Make sure you are using Python 3.8+. Execute `python3 --version` to get version.

## Notes

- The PyPI publisher `environment` must be the same value for the `environment` within the `publish.yml` file for the respective job. e.g. In `publish.yml` the `environment` for `publish-to-testpypi` is `testpypi`. Therefore, the `environment` for the publisher on the test PyPI website must also be `testpypi`.


