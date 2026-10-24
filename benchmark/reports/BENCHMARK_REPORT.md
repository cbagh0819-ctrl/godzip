# GODZIP Benchmark Report

| Category | Compressor | Mode / Level | Orig (bytes) | Arch (bytes) | Ratio | Red % | Comp (s) | Comp (MB/s) | Decomp (s) | Verified |
|---|---|---|---|---|---|---|---|---|---|---|
| text_logs | GODZIP | FAST | 515,690 | 41,766 | 12.35x | 91.9% | 0.063 | 7.8 | 0.023 | True |
| text_logs | GODZIP | BALANCED | 515,690 | 29,274 | 17.62x | 94.3% | 0.070 | 7.1 | 0.021 | True |
| text_logs | GODZIP | MAX | 515,690 | 16,529 | 31.20x | 96.8% | 2.867 | 0.2 | 0.021 | True |
| text_logs | Zstandard | Level 19 | 515,690 | 30,426 | 16.95x | 94.1% | 0.757 | 0.7 | 0.001 | True |
| text_logs | 7-Zip (py7zr) | LZMA2 | 515,690 | 23,000 | 22.42x | 95.5% | 0.409 | 1.2 | 0.033 | True |
| source_code | GODZIP | FAST | 5,556 | 666 | 8.34x | 88.0% | 0.035 | 0.1 | 0.018 | True |
| source_code | GODZIP | BALANCED | 5,556 | 630 | 8.82x | 88.7% | 0.008 | 0.7 | 0.018 | True |
| source_code | GODZIP | MAX | 5,556 | 646 | 8.60x | 88.4% | 0.048 | 0.1 | 0.016 | True |
| source_code | 7-Zip (py7zr) | LZMA2 | 5,556 | 506 | 10.98x | 90.9% | 0.023 | 0.2 | 0.024 | True |
| json_csv | GODZIP | FAST | 237,042 | 8,099 | 29.27x | 96.6% | 0.055 | 4.1 | 0.019 | True |
| json_csv | GODZIP | BALANCED | 237,042 | 8,094 | 29.29x | 96.6% | 0.049 | 4.7 | 0.016 | True |
| json_csv | GODZIP | MAX | 237,042 | 5,726 | 41.40x | 97.6% | 1.726 | 0.1 | 0.020 | True |
| json_csv | Zstandard | Level 19 | 237,042 | 6,632 | 35.74x | 97.2% | 0.814 | 0.3 | 0.000 | True |
| json_csv | 7-Zip (py7zr) | LZMA2 | 237,042 | 5,621 | 42.17x | 97.6% | 0.156 | 1.4 | 0.023 | True |
| xml_html | GODZIP | FAST | 248,367 | 3,995 | 62.17x | 98.4% | 0.060 | 3.9 | 0.018 | True |
| xml_html | GODZIP | BALANCED | 248,367 | 3,701 | 67.11x | 98.5% | 0.053 | 4.5 | 0.018 | True |
| xml_html | GODZIP | MAX | 248,367 | 3,418 | 72.66x | 98.6% | 2.072 | 0.1 | 0.020 | True |
| xml_html | Zstandard | Level 19 | 248,367 | 4,109 | 60.44x | 98.3% | 0.753 | 0.3 | 0.000 | True |
| xml_html | 7-Zip (py7zr) | LZMA2 | 248,367 | 3,316 | 74.90x | 98.7% | 0.087 | 2.7 | 0.023 | True |
| documents_pdf | GODZIP | FAST | 64,737 | 2,097 | 30.87x | 96.8% | 0.045 | 1.4 | 0.016 | True |
| documents_pdf | GODZIP | BALANCED | 64,737 | 2,018 | 32.08x | 96.9% | 0.023 | 2.6 | 0.033 | True |
| documents_pdf | GODZIP | MAX | 64,737 | 1,825 | 35.47x | 97.2% | 0.380 | 0.2 | 0.056 | True |
| documents_pdf | Zstandard | Level 19 | 64,737 | 1,646 | 39.33x | 97.5% | 0.109 | 0.6 | 0.000 | True |
| documents_pdf | 7-Zip (py7zr) | LZMA2 | 64,737 | 1,720 | 37.64x | 97.3% | 0.042 | 1.5 | 0.021 | True |
| uncompressed_bmp | GODZIP | FAST | 196,662 | 196,864 | 1.00x | -0.1% | 0.049 | 3.9 | 0.018 | True |
| uncompressed_bmp | GODZIP | BALANCED | 196,662 | 85,358 | 2.30x | 56.6% | 0.116 | 1.6 | 0.031 | True |
| uncompressed_bmp | GODZIP | MAX | 196,662 | 87,098 | 2.26x | 55.7% | 0.208 | 0.9 | 0.029 | True |
| uncompressed_bmp | Zstandard | Level 19 | 196,662 | 196,677 | 1.00x | -0.0% | 0.027 | 6.9 | 0.000 | True |
| uncompressed_bmp | 7-Zip (py7zr) | LZMA2 | 196,662 | 90,036 | 2.18x | 54.2% | 0.117 | 1.6 | 0.033 | True |
| compressed_image | GODZIP | FAST | 13,400 | 13,607 | 0.98x | -1.5% | 0.020 | 0.7 | 0.021 | True |
| compressed_image | GODZIP | BALANCED | 13,400 | 288 | 46.53x | 97.8% | 0.006 | 2.2 | 0.017 | True |
| compressed_image | GODZIP | MAX | 13,400 | 288 | 46.53x | 97.8% | 0.007 | 1.9 | 0.005 | True |
| compressed_image | Zstandard | Level 19 | 13,400 | 81 | 165.43x | 99.4% | 0.000 | 55.1 | 0.000 | True |
| compressed_image | 7-Zip (py7zr) | LZMA2 | 13,400 | 271 | 49.45x | 98.0% | 0.022 | 0.6 | 0.019 | True |
| compressed_video | GODZIP | FAST | 16,024 | 16,226 | 0.99x | -1.3% | 0.062 | 0.2 | 0.015 | True |
| compressed_video | GODZIP | BALANCED | 16,024 | 16,226 | 0.99x | -1.3% | 0.012 | 1.2 | 0.021 | True |
| compressed_video | GODZIP | MAX | 16,024 | 16,226 | 0.99x | -1.3% | 0.008 | 2.0 | 0.019 | True |
| compressed_video | Zstandard | Level 19 | 16,024 | 16,034 | 1.00x | -0.1% | 0.002 | 7.1 | 0.000 | True |
| compressed_video | 7-Zip (py7zr) | LZMA2 | 16,024 | 16,186 | 0.99x | -1.0% | 0.029 | 0.5 | 0.022 | True |
| audio_wav | GODZIP | FAST | 32,044 | 666 | 48.11x | 97.9% | 0.030 | 1.0 | 0.025 | True |
| audio_wav | GODZIP | BALANCED | 32,044 | 666 | 48.11x | 97.9% | 0.023 | 1.4 | 0.018 | True |
| audio_wav | GODZIP | MAX | 32,044 | 665 | 48.19x | 97.9% | 0.042 | 0.7 | 0.054 | True |
| audio_wav | Zstandard | Level 19 | 32,044 | 463 | 69.21x | 98.6% | 0.000 | 76.3 | 0.000 | True |
| audio_wav | 7-Zip (py7zr) | LZMA2 | 32,044 | 652 | 49.15x | 98.0% | 0.025 | 1.2 | 0.023 | True |
| mesh_3d | GODZIP | FAST | 74,233 | 18,411 | 4.03x | 75.2% | 0.051 | 1.4 | 0.017 | True |
| mesh_3d | GODZIP | BALANCED | 74,233 | 11,520 | 6.44x | 84.5% | 0.034 | 2.1 | 0.016 | True |
| mesh_3d | GODZIP | MAX | 74,233 | 8,915 | 8.33x | 88.0% | 0.380 | 0.2 | 0.017 | True |
| mesh_3d | Zstandard | Level 19 | 74,233 | 10,826 | 6.86x | 85.4% | 0.056 | 1.3 | 0.000 | True |
| mesh_3d | 7-Zip (py7zr) | LZMA2 | 74,233 | 9,187 | 8.08x | 87.6% | 0.051 | 1.4 | 0.020 | True |
| software_pkg | GODZIP | FAST | 141,279 | 3,263 | 43.30x | 97.7% | 0.062 | 2.2 | 0.018 | True |
| software_pkg | GODZIP | BALANCED | 141,279 | 904 | 156.28x | 99.4% | 0.043 | 3.1 | 0.019 | True |
| software_pkg | GODZIP | MAX | 141,279 | 329 | 429.42x | 99.8% | 0.072 | 1.9 | 0.015 | True |
| software_pkg | Zstandard | Level 19 | 141,279 | 126 | 1121.26x | 99.9% | 0.003 | 50.8 | 0.000 | True |
| software_pkg | 7-Zip (py7zr) | LZMA2 | 141,279 | 740 | 190.92x | 99.5% | 0.068 | 2.0 | 0.021 | True |
| random_binary | GODZIP | FAST | 32,000 | 32,203 | 0.99x | -0.6% | 0.044 | 0.7 | 0.018 | True |
| random_binary | GODZIP | BALANCED | 32,000 | 32,203 | 0.99x | -0.6% | 0.012 | 2.5 | 0.028 | True |
| random_binary | GODZIP | MAX | 32,000 | 32,203 | 0.99x | -0.6% | 0.012 | 2.5 | 0.027 | True |
| random_binary | Zstandard | Level 19 | 32,000 | 32,010 | 1.00x | -0.0% | 0.004 | 7.3 | 0.000 | True |
| random_binary | 7-Zip (py7zr) | LZMA2 | 32,000 | 32,163 | 0.99x | -0.5% | 0.033 | 0.9 | 0.024 | True |
| encrypted_sample | GODZIP | FAST | 16,000 | 16,206 | 0.99x | -1.3% | 0.021 | 0.7 | 0.017 | True |
| encrypted_sample | GODZIP | BALANCED | 16,000 | 16,206 | 0.99x | -1.3% | 0.008 | 1.9 | 0.018 | True |
| encrypted_sample | GODZIP | MAX | 16,000 | 16,206 | 0.99x | -1.3% | 0.009 | 1.8 | 0.016 | True |
| encrypted_sample | Zstandard | Level 19 | 16,000 | 16,010 | 1.00x | -0.1% | 0.002 | 7.9 | 0.000 | True |
| encrypted_sample | 7-Zip (py7zr) | LZMA2 | 16,000 | 16,165 | 0.99x | -1.0% | 0.029 | 0.5 | 0.020 | True |
| dedup_snapshots | GODZIP | FAST | 103,400 | 556 | 185.97x | 99.5% | 0.082 | 1.2 | 0.060 | True |
| dedup_snapshots | GODZIP | BALANCED | 103,400 | 530 | 195.09x | 99.5% | 0.035 | 2.8 | 0.020 | True |
| dedup_snapshots | GODZIP | MAX | 103,400 | 522 | 198.08x | 99.5% | 0.087 | 1.1 | 0.020 | True |
| dedup_snapshots | 7-Zip (py7zr) | LZMA2 | 103,400 | 384 | 269.27x | 99.6% | 0.028 | 3.5 | 0.060 | True |
