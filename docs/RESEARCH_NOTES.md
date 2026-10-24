# GODZIP Research Notes & Experimental Subsystems

## 1. Investigation of Reference Projects

### 1.1 Nacrith (GPU-Accelerated Neural Lossless Compression)
- **Repository**: `https://github.com/robtacconelli/Nacrith-GPU`
- **Architecture**: Deep autoregressive neural network modeling character/byte probability distributions, coupled with an asymmetric numeral systems (rANS) entropy coder.
- **Analysis**:
  - *Strengths*: Highly effective on natural language, source code, and structured logs with predictable semantic relationships.
  - *Challenges*: High inference latency, requires CUDA hardware and substantial GPU VRAM (~2–8 GB). Model weights (~10–50 MB) must be distributed alongside the archive or pre-installed on the decompression target. If model weights are counted against a small file's archive size, net compression is negative.
  - *GODZIP Role*: Optional research backend behind a feature flag, with model-size accounting included.

### 1.2 CMIX (Context Mixing Lossless Compressor)
- **Repository**: `https://github.com/byronknoll/cmix`
- **Architecture**: Ensemble context mixing combining multiple independent statistical models (dictionary, word, PPM, PAQ-style byte contexts) mixed through neural perceptron layers.
- **Analysis**:
  - *Strengths*: World-record compression ratios on the Silesia and enwik8 benchmarks.
  - *Challenges*: Extremely compute-intensive (hours of CPU time for moderate-sized inputs, gigabytes of RAM). Not practical for general-purpose interactive desktop usage.
  - *GODZIP Role*: Benchmark baseline and research comparison candidate.

### 1.3 OmniZip (Multimodal Lossless Compression Research)
- **Paper**: Zhao et al., *OmniZip: Learning a Unified and Lightweight Lossless Compressor for Multi-Modal Data*, CVPR 2026.
- **Analysis**:
  - Unifies multi-modal tokens (text, image patches, audio tokens) under a shared compact latent space for entropy estimation.
  - *GODZIP Role*: Theoretical foundation for cross-modality classification in the Content Analyzer.

---

## 2. GODZIP Adaptive Search

### 2.1 Problem Formulation
Conventional archivers apply a single fixed algorithm (e.g. 7-Zip LZMA2 or zip Deflate) across all files, or test all codecs blindly (brute force $O(K)$ trial search).
GODZIP Adaptive Search implements an empirical predictor:
1. Extract fast statistical features $f(x)$ from the data block:
   - Shannon entropy $H(x)$
   - Byte distribution standard deviation and zero-byte frequency
   - 2-gram transition entropy
   - Magic file signature identification
2. Score candidate codecs:
   - For high-entropy pre-compressed files ($H > 7.95$, JPEG/PNG/MP4 magic): early-exit to `STORE` or light `ZSTD-1`.
   - For structured text/code ($H \in [3.5, 5.5]$, high printable ASCII): shortlist `ZSTD-19`, `LZMA2-9`, `BROTLI-11`.
   - For repetitive binary ($H < 3.0$): shortlist `LZ4`, `ZSTD-3`.
3. In `MAXIMUM` mode, run trial compression on candidate samples, compare actual serialized bytes (including container metadata), select the winner, and record empirical performance.
