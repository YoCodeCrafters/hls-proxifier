# HLS-Proxifier <img src="https://img.shields.io/badge/version-1.0-blue">

**HLS-Proxifier** is a script designed to bypass header protection of an HLS stream or make a local stream accessible worldwide.

## Requirements
- Python 3.6+

## Getting started

1. Clone the project using git:

```bash
git clone https://github.com/SabBits/hls-proxifier.git
```

2. Go inside of the directory:
```bash
cd hls-proxifier 
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Run the WSGI Server:
```bash
python hls-proxifier.py
```

## Usage

**HLS-Proxifier** should be reachable at ```localhost:5000``` when started by following the steps mentioned above.

- To use without headers, use this URL format:
    ```
    http://localhost:5000/proxify?url=https://cph-msl.akamaized.net/hls/live/2000341/test/master.m3u8
    ```

- To use with headers, use this URL format:
    ```
    http://localhost:5000/proxify?url=https://nl-nb.score806.cc/live/uk_bts1/playlist.m3u8&headers={"Referer": "https://aesport.tv/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}
    ```

For optimal usage, consider converting the script to a `blueprint` and passing the link and headers from an external view.

## TODO

- [ ] Add a `quality` argument to specify a specific quality for master HLS.
- [ ] Add more user-friendly interfaces for passing headers.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

This project is licensed under the [**Apache License**](http://www.apache.org/licenses/LICENSE-2.0).