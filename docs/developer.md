# Developer

To trigger a production release:

```bash
$ git tag -a vN -m "Version N on YYYY-MM-DD HH:MMa ZZZ"
```

Example:
```bash
$ git tag -a v1.0 -m "Version 1.0 on 2024-02-22 10:32am PST"
```

## Notes

- The PyPI publisher `environment` must be the same value for the `environment` within the `publish.yml` file for the respective job. e.g. In `publish.yml` the `environment` for `publish-to-testpypi` is `testpypi`. Therefore, the `environment` for the publisher on the test PyPI website must also be `testpypi`.
