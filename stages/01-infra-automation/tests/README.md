# Tests

From the stage root, install `requirements.txt` and run `python -m unittest discover -s tests -v`. The ten tests cover validation and CLI success/failure paths. Service failures use a replacement script, so the tests do not install Nginx.
