ubuntu@ip-172-30-2-118:/etc/nginx/sites-available$ lsa -ltr
Command 'lsa' not found, but there are 20 similar ones.
ubuntu@ip-172-30-2-118:/etc/nginx/sites-available$ ls -ltr
total 16
-rw-r--r-- 1 root root 1092 Jul 18 17:17 auto-manual-search
-rw-r--r-- 1 root root 1111 Jul 31 11:03 faiss-rag
-rw-r--r-- 1 root root 1079 Aug 25 15:26 ocr
-rw-r--r-- 1 root root 1181 Aug 27 19:36 asr
ubuntu@ip-172-30-2-118:/etc/nginx/sites-available$ vi ocr 
ubuntu@ip-172-30-2-118:/etc/nginx/sites-available$ vi asr 
ubuntu@ip-172-30-2-118:/etc/nginx/sites-available$ sudo vi asr 
ubuntu@ip-172-30-2-118:/etc/nginx/sites-available$ sudo nginx -t && sudo systemctl reload nginx
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
ubuntu@ip-172-30-2-118:/etc/nginx/sites-available$ cd ~/nvidia_parakeet/
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./stop_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./start_parakeet.sh 
Requirement already satisfied: pip in ./venv/lib/python3.12/site-packages (25.2)
Requirement already satisfied: streamlit==1.48.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 5)) (1.48.1)
Requirement already satisfied: torch==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 8)) (2.8.0)
Requirement already satisfied: torchaudio==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 9)) (2.8.0)
Requirement already satisfied: transformers==4.55.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 12)) (4.55.4)
Requirement already satisfied: huggingface_hub==0.34.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 13)) (0.34.4)
Requirement already satisfied: safetensors==0.6.2 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 14)) (0.6.2)
Requirement already satisfied: sentencepiece==0.2.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 15)) (0.2.0)
Requirement already satisfied: numpy==1.26.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 18)) (1.26.4)
Requirement already satisfied: soundfile==0.13.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 19)) (0.13.1)
Requirement already satisfied: librosa==0.10.2.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 20)) (0.10.2.post1)
Requirement already satisfied: soxr==0.5.0.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 21)) (0.5.0.post1)
Requirement already satisfied: pyctcdecode==0.5.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 24)) (0.5.0)
Requirement already satisfied: streamlit-webrtc==0.47.6 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 27)) (0.47.6)
Requirement already satisfied: av==14.0.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 28)) (14.0.1)
Requirement already satisfied: einops==0.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 31)) (0.8.0)
Requirement already satisfied: altair!=5.4.0,!=5.4.1,<6,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.5.0)
Requirement already satisfied: blinker<2,>=1.5.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (1.9.0)
Requirement already satisfied: cachetools<7,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.2.0)
Requirement already satisfied: click<9,>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (8.2.1)
Requirement already satisfied: packaging<26,>=20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (24.2)
Requirement already satisfied: pandas<3,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.3.2)
Requirement already satisfied: pillow<12,>=7.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (11.3.0)
Requirement already satisfied: protobuf<7,>=3.20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.29.5)
Requirement already satisfied: pyarrow>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (21.0.0)
Requirement already satisfied: requests<3,>=2.27 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.32.5)
Requirement already satisfied: tenacity<10,>=8.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (9.1.2)
Requirement already satisfied: toml<2,>=0.10.1 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.10.2)
Requirement already satisfied: typing-extensions<5,>=4.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (4.15.0)
Requirement already satisfied: watchdog<7,>=2.1.5 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.0.0)
Requirement already satisfied: gitpython!=3.1.19,<4,>=3.0.7 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (3.1.45)
Requirement already satisfied: pydeck<1,>=0.8.0b4 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.9.1)
Requirement already satisfied: tornado!=6.5.0,<7,>=6.0.3 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.5.2)
Requirement already satisfied: filelock in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.19.1)
Requirement already satisfied: setuptools in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (80.9.0)
Requirement already satisfied: sympy>=1.13.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.14.0)
Requirement already satisfied: networkx in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.5)
Requirement already satisfied: jinja2 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.1.6)
Requirement already satisfied: fsspec in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2024.12.0)
Requirement already satisfied: nvidia-cuda-nvrtc-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cuda-runtime-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cuda-cupti-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cudnn-cu12==9.10.2.21 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (9.10.2.21)
Requirement already satisfied: nvidia-cublas-cu12==12.8.4.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.4.1)
Requirement already satisfied: nvidia-cufft-cu12==11.3.3.83 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.3.3.83)
Requirement already satisfied: nvidia-curand-cu12==10.3.9.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (10.3.9.90)
Requirement already satisfied: nvidia-cusolver-cu12==11.7.3.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.7.3.90)
Requirement already satisfied: nvidia-cusparse-cu12==12.5.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.5.8.93)
Requirement already satisfied: nvidia-cusparselt-cu12==0.7.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (0.7.1)
Requirement already satisfied: nvidia-nccl-cu12==2.27.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2.27.3)
Requirement already satisfied: nvidia-nvtx-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-nvjitlink-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cufile-cu12==1.13.1.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.13.1.3)
Requirement already satisfied: triton==3.4.0 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.4.0)
Requirement already satisfied: pyyaml>=5.1 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (6.0.2)
Requirement already satisfied: regex!=2019.12.17 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (2025.7.34)
Requirement already satisfied: tokenizers<0.22,>=0.21 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (0.21.4)
Requirement already satisfied: tqdm>=4.27 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (4.67.1)
Requirement already satisfied: hf-xet<2.0.0,>=1.1.3 in ./venv/lib/python3.12/site-packages (from huggingface_hub==0.34.4->-r requirements.txt (line 13)) (1.1.8)
Requirement already satisfied: cffi>=1.0 in ./venv/lib/python3.12/site-packages (from soundfile==0.13.1->-r requirements.txt (line 19)) (1.17.1)
Requirement already satisfied: audioread>=2.1.9 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.0.1)
Requirement already satisfied: scipy>=1.2.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.16.1)
Requirement already satisfied: scikit-learn>=0.20.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.7.1)
Requirement already satisfied: joblib>=0.14 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.5.1)
Requirement already satisfied: decorator>=4.3.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (5.2.1)
Requirement already satisfied: numba>=0.51.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.61.2)
Requirement already satisfied: pooch>=1.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.8.2)
Requirement already satisfied: lazy-loader>=0.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.4)
Requirement already satisfied: msgpack>=1.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.1.1)
Requirement already satisfied: pygtrie<3.0,>=2.1 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.5.0)
Requirement already satisfied: hypothesis<7,>=6.14 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (6.138.3)
Requirement already satisfied: aiortc<2.0.0,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.13.0)
Requirement already satisfied: aioice<1.0.0,>=0.10.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.10.1)
Requirement already satisfied: cryptography>=44.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (45.0.6)
Requirement already satisfied: google-crc32c>=1.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.7.1)
Requirement already satisfied: pyee>=13.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (13.0.0)
Requirement already satisfied: pylibsrtp>=0.10.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.12.0)
Requirement already satisfied: pyopenssl>=25.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (25.1.0)
Requirement already satisfied: dnspython>=2.0.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (2.7.0)
Requirement already satisfied: ifaddr>=0.2.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.2.0)
Requirement already satisfied: jsonschema>=3.0 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (4.25.1)
Requirement already satisfied: narwhals>=1.14.2 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.2.0)
Requirement already satisfied: gitdb<5,>=4.0.1 in ./venv/lib/python3.12/site-packages (from gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (4.0.12)
Requirement already satisfied: smmap<6,>=3.0.1 in ./venv/lib/python3.12/site-packages (from gitdb<5,>=4.0.1->gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (5.0.2)
Requirement already satisfied: attrs>=22.2.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (25.3.0)
Requirement already satisfied: sortedcontainers<3.0.0,>=2.1.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.4.0)
Requirement already satisfied: python-dateutil>=2.8.2 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: tzdata>=2022.7 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: charset_normalizer<4,>=2 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.4.3)
Requirement already satisfied: idna<4,>=2.5 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2.5.0)
Requirement already satisfied: certifi>=2017.4.17 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.8.3)
Requirement already satisfied: pycparser in ./venv/lib/python3.12/site-packages (from cffi>=1.0->soundfile==0.13.1->-r requirements.txt (line 19)) (2.22)
Requirement already satisfied: MarkupSafe>=2.0 in ./venv/lib/python3.12/site-packages (from jinja2->torch==2.8.0->-r requirements.txt (line 8)) (3.0.2)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.4.1)
Requirement already satisfied: referencing>=0.28.4 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.36.2)
Requirement already satisfied: rpds-py>=0.7.1 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.27.0)
Requirement already satisfied: llvmlite<0.45,>=0.44.0dev0 in ./venv/lib/python3.12/site-packages (from numba>=0.51.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.44.0)
Requirement already satisfied: platformdirs>=2.5.0 in ./venv/lib/python3.12/site-packages (from pooch>=1.1->librosa==0.10.2.post1->-r requirements.txt (line 20)) (4.4.0)
Requirement already satisfied: six>=1.5 in ./venv/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (1.17.0)
Requirement already satisfied: threadpoolctl>=3.1.0 in ./venv/lib/python3.12/site-packages (from scikit-learn>=0.20.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.6.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./venv/lib/python3.12/site-packages (from sympy>=1.13.3->torch==2.8.0->-r requirements.txt (line 8)) (1.3.0)
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ vi test.py
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./stop_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ vi start_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./stop_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./start_parakeet.sh 
Requirement already satisfied: pip in ./venv/lib/python3.12/site-packages (25.2)
Requirement already satisfied: streamlit==1.48.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 5)) (1.48.1)
Requirement already satisfied: torch==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 8)) (2.8.0)
Requirement already satisfied: torchaudio==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 9)) (2.8.0)
Requirement already satisfied: transformers==4.55.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 12)) (4.55.4)
Requirement already satisfied: huggingface_hub==0.34.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 13)) (0.34.4)
Requirement already satisfied: safetensors==0.6.2 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 14)) (0.6.2)
Requirement already satisfied: sentencepiece==0.2.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 15)) (0.2.0)
Requirement already satisfied: numpy==1.26.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 18)) (1.26.4)
Requirement already satisfied: soundfile==0.13.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 19)) (0.13.1)
Requirement already satisfied: librosa==0.10.2.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 20)) (0.10.2.post1)
Requirement already satisfied: soxr==0.5.0.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 21)) (0.5.0.post1)
Requirement already satisfied: pyctcdecode==0.5.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 24)) (0.5.0)
Requirement already satisfied: streamlit-webrtc==0.47.6 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 27)) (0.47.6)
Requirement already satisfied: av==14.0.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 28)) (14.0.1)
Requirement already satisfied: einops==0.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 31)) (0.8.0)
Requirement already satisfied: altair!=5.4.0,!=5.4.1,<6,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.5.0)
Requirement already satisfied: blinker<2,>=1.5.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (1.9.0)
Requirement already satisfied: cachetools<7,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.2.0)
Requirement already satisfied: click<9,>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (8.2.1)
Requirement already satisfied: packaging<26,>=20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (24.2)
Requirement already satisfied: pandas<3,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.3.2)
Requirement already satisfied: pillow<12,>=7.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (11.3.0)
Requirement already satisfied: protobuf<7,>=3.20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.29.5)
Requirement already satisfied: pyarrow>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (21.0.0)
Requirement already satisfied: requests<3,>=2.27 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.32.5)
Requirement already satisfied: tenacity<10,>=8.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (9.1.2)
Requirement already satisfied: toml<2,>=0.10.1 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.10.2)
Requirement already satisfied: typing-extensions<5,>=4.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (4.15.0)
Requirement already satisfied: watchdog<7,>=2.1.5 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.0.0)
Requirement already satisfied: gitpython!=3.1.19,<4,>=3.0.7 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (3.1.45)
Requirement already satisfied: pydeck<1,>=0.8.0b4 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.9.1)
Requirement already satisfied: tornado!=6.5.0,<7,>=6.0.3 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.5.2)
Requirement already satisfied: filelock in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.19.1)
Requirement already satisfied: setuptools in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (80.9.0)
Requirement already satisfied: sympy>=1.13.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.14.0)
Requirement already satisfied: networkx in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.5)
Requirement already satisfied: jinja2 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.1.6)
Requirement already satisfied: fsspec in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2024.12.0)
Requirement already satisfied: nvidia-cuda-nvrtc-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cuda-runtime-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cuda-cupti-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cudnn-cu12==9.10.2.21 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (9.10.2.21)
Requirement already satisfied: nvidia-cublas-cu12==12.8.4.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.4.1)
Requirement already satisfied: nvidia-cufft-cu12==11.3.3.83 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.3.3.83)
Requirement already satisfied: nvidia-curand-cu12==10.3.9.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (10.3.9.90)
Requirement already satisfied: nvidia-cusolver-cu12==11.7.3.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.7.3.90)
Requirement already satisfied: nvidia-cusparse-cu12==12.5.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.5.8.93)
Requirement already satisfied: nvidia-cusparselt-cu12==0.7.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (0.7.1)
Requirement already satisfied: nvidia-nccl-cu12==2.27.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2.27.3)
Requirement already satisfied: nvidia-nvtx-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-nvjitlink-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cufile-cu12==1.13.1.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.13.1.3)
Requirement already satisfied: triton==3.4.0 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.4.0)
Requirement already satisfied: pyyaml>=5.1 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (6.0.2)
Requirement already satisfied: regex!=2019.12.17 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (2025.7.34)
Requirement already satisfied: tokenizers<0.22,>=0.21 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (0.21.4)
Requirement already satisfied: tqdm>=4.27 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (4.67.1)
Requirement already satisfied: hf-xet<2.0.0,>=1.1.3 in ./venv/lib/python3.12/site-packages (from huggingface_hub==0.34.4->-r requirements.txt (line 13)) (1.1.8)
Requirement already satisfied: cffi>=1.0 in ./venv/lib/python3.12/site-packages (from soundfile==0.13.1->-r requirements.txt (line 19)) (1.17.1)
Requirement already satisfied: audioread>=2.1.9 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.0.1)
Requirement already satisfied: scipy>=1.2.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.16.1)
Requirement already satisfied: scikit-learn>=0.20.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.7.1)
Requirement already satisfied: joblib>=0.14 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.5.1)
Requirement already satisfied: decorator>=4.3.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (5.2.1)
Requirement already satisfied: numba>=0.51.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.61.2)
Requirement already satisfied: pooch>=1.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.8.2)
Requirement already satisfied: lazy-loader>=0.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.4)
Requirement already satisfied: msgpack>=1.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.1.1)
Requirement already satisfied: pygtrie<3.0,>=2.1 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.5.0)
Requirement already satisfied: hypothesis<7,>=6.14 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (6.138.3)
Requirement already satisfied: aiortc<2.0.0,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.13.0)
Requirement already satisfied: aioice<1.0.0,>=0.10.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.10.1)
Requirement already satisfied: cryptography>=44.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (45.0.6)
Requirement already satisfied: google-crc32c>=1.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.7.1)
Requirement already satisfied: pyee>=13.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (13.0.0)
Requirement already satisfied: pylibsrtp>=0.10.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.12.0)
Requirement already satisfied: pyopenssl>=25.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (25.1.0)
Requirement already satisfied: dnspython>=2.0.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (2.7.0)
Requirement already satisfied: ifaddr>=0.2.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.2.0)
Requirement already satisfied: jsonschema>=3.0 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (4.25.1)
Requirement already satisfied: narwhals>=1.14.2 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.2.0)
Requirement already satisfied: gitdb<5,>=4.0.1 in ./venv/lib/python3.12/site-packages (from gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (4.0.12)
Requirement already satisfied: smmap<6,>=3.0.1 in ./venv/lib/python3.12/site-packages (from gitdb<5,>=4.0.1->gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (5.0.2)
Requirement already satisfied: attrs>=22.2.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (25.3.0)
Requirement already satisfied: sortedcontainers<3.0.0,>=2.1.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.4.0)
Requirement already satisfied: python-dateutil>=2.8.2 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: tzdata>=2022.7 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: charset_normalizer<4,>=2 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.4.3)
Requirement already satisfied: idna<4,>=2.5 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2.5.0)
Requirement already satisfied: certifi>=2017.4.17 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.8.3)
Requirement already satisfied: pycparser in ./venv/lib/python3.12/site-packages (from cffi>=1.0->soundfile==0.13.1->-r requirements.txt (line 19)) (2.22)
Requirement already satisfied: MarkupSafe>=2.0 in ./venv/lib/python3.12/site-packages (from jinja2->torch==2.8.0->-r requirements.txt (line 8)) (3.0.2)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.4.1)
Requirement already satisfied: referencing>=0.28.4 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.36.2)
Requirement already satisfied: rpds-py>=0.7.1 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.27.0)
Requirement already satisfied: llvmlite<0.45,>=0.44.0dev0 in ./venv/lib/python3.12/site-packages (from numba>=0.51.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.44.0)
Requirement already satisfied: platformdirs>=2.5.0 in ./venv/lib/python3.12/site-packages (from pooch>=1.1->librosa==0.10.2.post1->-r requirements.txt (line 20)) (4.4.0)
Requirement already satisfied: six>=1.5 in ./venv/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (1.17.0)
Requirement already satisfied: threadpoolctl>=3.1.0 in ./venv/lib/python3.12/site-packages (from scikit-learn>=0.20.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.6.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./venv/lib/python3.12/site-packages (from sympy>=1.13.3->torch==2.8.0->-r requirements.txt (line 8)) (1.3.0)
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ vi test.py 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./stop_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./start_parakeet.sh 
Requirement already satisfied: pip in ./venv/lib/python3.12/site-packages (25.2)
Requirement already satisfied: streamlit==1.48.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 5)) (1.48.1)
Requirement already satisfied: torch==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 8)) (2.8.0)
Requirement already satisfied: torchaudio==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 9)) (2.8.0)
Requirement already satisfied: transformers==4.55.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 12)) (4.55.4)
Requirement already satisfied: huggingface_hub==0.34.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 13)) (0.34.4)
Requirement already satisfied: safetensors==0.6.2 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 14)) (0.6.2)
Requirement already satisfied: sentencepiece==0.2.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 15)) (0.2.0)
Requirement already satisfied: numpy==1.26.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 18)) (1.26.4)
Requirement already satisfied: soundfile==0.13.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 19)) (0.13.1)
Requirement already satisfied: librosa==0.10.2.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 20)) (0.10.2.post1)
Requirement already satisfied: soxr==0.5.0.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 21)) (0.5.0.post1)
Requirement already satisfied: pyctcdecode==0.5.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 24)) (0.5.0)
Requirement already satisfied: streamlit-webrtc==0.47.6 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 27)) (0.47.6)
Requirement already satisfied: av==14.0.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 28)) (14.0.1)
Requirement already satisfied: einops==0.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 31)) (0.8.0)
Requirement already satisfied: altair!=5.4.0,!=5.4.1,<6,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.5.0)
Requirement already satisfied: blinker<2,>=1.5.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (1.9.0)
Requirement already satisfied: cachetools<7,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.2.0)
Requirement already satisfied: click<9,>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (8.2.1)
Requirement already satisfied: packaging<26,>=20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (24.2)
Requirement already satisfied: pandas<3,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.3.2)
Requirement already satisfied: pillow<12,>=7.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (11.3.0)
Requirement already satisfied: protobuf<7,>=3.20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.29.5)
Requirement already satisfied: pyarrow>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (21.0.0)
Requirement already satisfied: requests<3,>=2.27 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.32.5)
Requirement already satisfied: tenacity<10,>=8.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (9.1.2)
Requirement already satisfied: toml<2,>=0.10.1 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.10.2)
Requirement already satisfied: typing-extensions<5,>=4.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (4.15.0)
Requirement already satisfied: watchdog<7,>=2.1.5 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.0.0)
Requirement already satisfied: gitpython!=3.1.19,<4,>=3.0.7 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (3.1.45)
Requirement already satisfied: pydeck<1,>=0.8.0b4 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.9.1)
Requirement already satisfied: tornado!=6.5.0,<7,>=6.0.3 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.5.2)
Requirement already satisfied: filelock in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.19.1)
Requirement already satisfied: setuptools in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (80.9.0)
Requirement already satisfied: sympy>=1.13.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.14.0)
Requirement already satisfied: networkx in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.5)
Requirement already satisfied: jinja2 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.1.6)
Requirement already satisfied: fsspec in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2024.12.0)
Requirement already satisfied: nvidia-cuda-nvrtc-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cuda-runtime-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cuda-cupti-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cudnn-cu12==9.10.2.21 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (9.10.2.21)
Requirement already satisfied: nvidia-cublas-cu12==12.8.4.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.4.1)
Requirement already satisfied: nvidia-cufft-cu12==11.3.3.83 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.3.3.83)
Requirement already satisfied: nvidia-curand-cu12==10.3.9.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (10.3.9.90)
Requirement already satisfied: nvidia-cusolver-cu12==11.7.3.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.7.3.90)
Requirement already satisfied: nvidia-cusparse-cu12==12.5.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.5.8.93)
Requirement already satisfied: nvidia-cusparselt-cu12==0.7.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (0.7.1)
Requirement already satisfied: nvidia-nccl-cu12==2.27.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2.27.3)
Requirement already satisfied: nvidia-nvtx-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-nvjitlink-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cufile-cu12==1.13.1.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.13.1.3)
Requirement already satisfied: triton==3.4.0 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.4.0)
Requirement already satisfied: pyyaml>=5.1 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (6.0.2)
Requirement already satisfied: regex!=2019.12.17 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (2025.7.34)
Requirement already satisfied: tokenizers<0.22,>=0.21 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (0.21.4)
Requirement already satisfied: tqdm>=4.27 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (4.67.1)
Requirement already satisfied: hf-xet<2.0.0,>=1.1.3 in ./venv/lib/python3.12/site-packages (from huggingface_hub==0.34.4->-r requirements.txt (line 13)) (1.1.8)
Requirement already satisfied: cffi>=1.0 in ./venv/lib/python3.12/site-packages (from soundfile==0.13.1->-r requirements.txt (line 19)) (1.17.1)
Requirement already satisfied: audioread>=2.1.9 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.0.1)
Requirement already satisfied: scipy>=1.2.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.16.1)
Requirement already satisfied: scikit-learn>=0.20.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.7.1)
Requirement already satisfied: joblib>=0.14 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.5.1)
Requirement already satisfied: decorator>=4.3.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (5.2.1)
Requirement already satisfied: numba>=0.51.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.61.2)
Requirement already satisfied: pooch>=1.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.8.2)
Requirement already satisfied: lazy-loader>=0.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.4)
Requirement already satisfied: msgpack>=1.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.1.1)
Requirement already satisfied: pygtrie<3.0,>=2.1 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.5.0)
Requirement already satisfied: hypothesis<7,>=6.14 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (6.138.3)
Requirement already satisfied: aiortc<2.0.0,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.13.0)
Requirement already satisfied: aioice<1.0.0,>=0.10.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.10.1)
Requirement already satisfied: cryptography>=44.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (45.0.6)
Requirement already satisfied: google-crc32c>=1.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.7.1)
Requirement already satisfied: pyee>=13.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (13.0.0)
Requirement already satisfied: pylibsrtp>=0.10.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.12.0)
Requirement already satisfied: pyopenssl>=25.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (25.1.0)
Requirement already satisfied: dnspython>=2.0.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (2.7.0)
Requirement already satisfied: ifaddr>=0.2.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.2.0)
Requirement already satisfied: jsonschema>=3.0 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (4.25.1)
Requirement already satisfied: narwhals>=1.14.2 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.2.0)
Requirement already satisfied: gitdb<5,>=4.0.1 in ./venv/lib/python3.12/site-packages (from gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (4.0.12)
Requirement already satisfied: smmap<6,>=3.0.1 in ./venv/lib/python3.12/site-packages (from gitdb<5,>=4.0.1->gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (5.0.2)
Requirement already satisfied: attrs>=22.2.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (25.3.0)
Requirement already satisfied: sortedcontainers<3.0.0,>=2.1.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.4.0)
Requirement already satisfied: python-dateutil>=2.8.2 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: tzdata>=2022.7 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: charset_normalizer<4,>=2 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.4.3)
Requirement already satisfied: idna<4,>=2.5 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2.5.0)
Requirement already satisfied: certifi>=2017.4.17 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.8.3)
Requirement already satisfied: pycparser in ./venv/lib/python3.12/site-packages (from cffi>=1.0->soundfile==0.13.1->-r requirements.txt (line 19)) (2.22)
Requirement already satisfied: MarkupSafe>=2.0 in ./venv/lib/python3.12/site-packages (from jinja2->torch==2.8.0->-r requirements.txt (line 8)) (3.0.2)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.4.1)
Requirement already satisfied: referencing>=0.28.4 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.36.2)
Requirement already satisfied: rpds-py>=0.7.1 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.27.0)
Requirement already satisfied: llvmlite<0.45,>=0.44.0dev0 in ./venv/lib/python3.12/site-packages (from numba>=0.51.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.44.0)
Requirement already satisfied: platformdirs>=2.5.0 in ./venv/lib/python3.12/site-packages (from pooch>=1.1->librosa==0.10.2.post1->-r requirements.txt (line 20)) (4.4.0)
Requirement already satisfied: six>=1.5 in ./venv/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (1.17.0)
Requirement already satisfied: threadpoolctl>=3.1.0 in ./venv/lib/python3.12/site-packages (from scikit-learn>=0.20.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.6.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./venv/lib/python3.12/site-packages (from sympy>=1.13.3->torch==2.8.0->-r requirements.txt (line 8)) (1.3.0)
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ vi test.py 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./stop_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./start_parakeet.sh 
Requirement already satisfied: pip in ./venv/lib/python3.12/site-packages (25.2)
Requirement already satisfied: streamlit==1.48.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 5)) (1.48.1)
Requirement already satisfied: torch==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 8)) (2.8.0)
Requirement already satisfied: torchaudio==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 9)) (2.8.0)
Requirement already satisfied: transformers==4.55.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 12)) (4.55.4)
Requirement already satisfied: huggingface_hub==0.34.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 13)) (0.34.4)
Requirement already satisfied: safetensors==0.6.2 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 14)) (0.6.2)
Requirement already satisfied: sentencepiece==0.2.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 15)) (0.2.0)
Requirement already satisfied: numpy==1.26.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 18)) (1.26.4)
Requirement already satisfied: soundfile==0.13.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 19)) (0.13.1)
Requirement already satisfied: librosa==0.10.2.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 20)) (0.10.2.post1)
Requirement already satisfied: soxr==0.5.0.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 21)) (0.5.0.post1)
Requirement already satisfied: pyctcdecode==0.5.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 24)) (0.5.0)
Requirement already satisfied: streamlit-webrtc==0.47.6 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 27)) (0.47.6)
Requirement already satisfied: av==14.0.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 28)) (14.0.1)
Requirement already satisfied: einops==0.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 31)) (0.8.0)
Requirement already satisfied: altair!=5.4.0,!=5.4.1,<6,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.5.0)
Requirement already satisfied: blinker<2,>=1.5.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (1.9.0)
Requirement already satisfied: cachetools<7,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.2.0)
Requirement already satisfied: click<9,>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (8.2.1)
Requirement already satisfied: packaging<26,>=20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (24.2)
Requirement already satisfied: pandas<3,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.3.2)
Requirement already satisfied: pillow<12,>=7.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (11.3.0)
Requirement already satisfied: protobuf<7,>=3.20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.29.5)
Requirement already satisfied: pyarrow>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (21.0.0)
Requirement already satisfied: requests<3,>=2.27 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.32.5)
Requirement already satisfied: tenacity<10,>=8.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (9.1.2)
Requirement already satisfied: toml<2,>=0.10.1 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.10.2)
Requirement already satisfied: typing-extensions<5,>=4.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (4.15.0)
Requirement already satisfied: watchdog<7,>=2.1.5 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.0.0)
Requirement already satisfied: gitpython!=3.1.19,<4,>=3.0.7 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (3.1.45)
Requirement already satisfied: pydeck<1,>=0.8.0b4 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.9.1)
Requirement already satisfied: tornado!=6.5.0,<7,>=6.0.3 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.5.2)
Requirement already satisfied: filelock in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.19.1)
Requirement already satisfied: setuptools in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (80.9.0)
Requirement already satisfied: sympy>=1.13.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.14.0)
Requirement already satisfied: networkx in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.5)
Requirement already satisfied: jinja2 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.1.6)
Requirement already satisfied: fsspec in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2024.12.0)
Requirement already satisfied: nvidia-cuda-nvrtc-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cuda-runtime-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cuda-cupti-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cudnn-cu12==9.10.2.21 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (9.10.2.21)
Requirement already satisfied: nvidia-cublas-cu12==12.8.4.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.4.1)
Requirement already satisfied: nvidia-cufft-cu12==11.3.3.83 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.3.3.83)
Requirement already satisfied: nvidia-curand-cu12==10.3.9.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (10.3.9.90)
Requirement already satisfied: nvidia-cusolver-cu12==11.7.3.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.7.3.90)
Requirement already satisfied: nvidia-cusparse-cu12==12.5.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.5.8.93)
Requirement already satisfied: nvidia-cusparselt-cu12==0.7.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (0.7.1)
Requirement already satisfied: nvidia-nccl-cu12==2.27.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2.27.3)
Requirement already satisfied: nvidia-nvtx-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-nvjitlink-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cufile-cu12==1.13.1.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.13.1.3)
Requirement already satisfied: triton==3.4.0 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.4.0)
Requirement already satisfied: pyyaml>=5.1 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (6.0.2)
Requirement already satisfied: regex!=2019.12.17 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (2025.7.34)
Requirement already satisfied: tokenizers<0.22,>=0.21 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (0.21.4)
Requirement already satisfied: tqdm>=4.27 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (4.67.1)
Requirement already satisfied: hf-xet<2.0.0,>=1.1.3 in ./venv/lib/python3.12/site-packages (from huggingface_hub==0.34.4->-r requirements.txt (line 13)) (1.1.8)
Requirement already satisfied: cffi>=1.0 in ./venv/lib/python3.12/site-packages (from soundfile==0.13.1->-r requirements.txt (line 19)) (1.17.1)
Requirement already satisfied: audioread>=2.1.9 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.0.1)
Requirement already satisfied: scipy>=1.2.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.16.1)
Requirement already satisfied: scikit-learn>=0.20.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.7.1)
Requirement already satisfied: joblib>=0.14 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.5.1)
Requirement already satisfied: decorator>=4.3.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (5.2.1)
Requirement already satisfied: numba>=0.51.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.61.2)
Requirement already satisfied: pooch>=1.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.8.2)
Requirement already satisfied: lazy-loader>=0.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.4)
Requirement already satisfied: msgpack>=1.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.1.1)
Requirement already satisfied: pygtrie<3.0,>=2.1 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.5.0)
Requirement already satisfied: hypothesis<7,>=6.14 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (6.138.3)
Requirement already satisfied: aiortc<2.0.0,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.13.0)
Requirement already satisfied: aioice<1.0.0,>=0.10.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.10.1)
Requirement already satisfied: cryptography>=44.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (45.0.6)
Requirement already satisfied: google-crc32c>=1.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.7.1)
Requirement already satisfied: pyee>=13.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (13.0.0)
Requirement already satisfied: pylibsrtp>=0.10.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.12.0)
Requirement already satisfied: pyopenssl>=25.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (25.1.0)
Requirement already satisfied: dnspython>=2.0.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (2.7.0)
Requirement already satisfied: ifaddr>=0.2.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.2.0)
Requirement already satisfied: jsonschema>=3.0 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (4.25.1)
Requirement already satisfied: narwhals>=1.14.2 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.2.0)
Requirement already satisfied: gitdb<5,>=4.0.1 in ./venv/lib/python3.12/site-packages (from gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (4.0.12)
Requirement already satisfied: smmap<6,>=3.0.1 in ./venv/lib/python3.12/site-packages (from gitdb<5,>=4.0.1->gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (5.0.2)
Requirement already satisfied: attrs>=22.2.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (25.3.0)
Requirement already satisfied: sortedcontainers<3.0.0,>=2.1.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.4.0)
Requirement already satisfied: python-dateutil>=2.8.2 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: tzdata>=2022.7 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: charset_normalizer<4,>=2 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.4.3)
Requirement already satisfied: idna<4,>=2.5 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2.5.0)
Requirement already satisfied: certifi>=2017.4.17 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.8.3)
Requirement already satisfied: pycparser in ./venv/lib/python3.12/site-packages (from cffi>=1.0->soundfile==0.13.1->-r requirements.txt (line 19)) (2.22)
Requirement already satisfied: MarkupSafe>=2.0 in ./venv/lib/python3.12/site-packages (from jinja2->torch==2.8.0->-r requirements.txt (line 8)) (3.0.2)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.4.1)
Requirement already satisfied: referencing>=0.28.4 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.36.2)
Requirement already satisfied: rpds-py>=0.7.1 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.27.0)
Requirement already satisfied: llvmlite<0.45,>=0.44.0dev0 in ./venv/lib/python3.12/site-packages (from numba>=0.51.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.44.0)
Requirement already satisfied: platformdirs>=2.5.0 in ./venv/lib/python3.12/site-packages (from pooch>=1.1->librosa==0.10.2.post1->-r requirements.txt (line 20)) (4.4.0)
Requirement already satisfied: six>=1.5 in ./venv/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (1.17.0)
Requirement already satisfied: threadpoolctl>=3.1.0 in ./venv/lib/python3.12/site-packages (from scikit-learn>=0.20.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.6.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./venv/lib/python3.12/site-packages (from sympy>=1.13.3->torch==2.8.0->-r requirements.txt (line 8)) (1.3.0)
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ vi test.py 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./stop_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./start_parakeet.sh 
Requirement already satisfied: pip in ./venv/lib/python3.12/site-packages (25.2)
Requirement already satisfied: streamlit==1.48.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 5)) (1.48.1)
Requirement already satisfied: torch==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 8)) (2.8.0)
Requirement already satisfied: torchaudio==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 9)) (2.8.0)
Requirement already satisfied: transformers==4.55.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 12)) (4.55.4)
Requirement already satisfied: huggingface_hub==0.34.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 13)) (0.34.4)
Requirement already satisfied: safetensors==0.6.2 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 14)) (0.6.2)
Requirement already satisfied: sentencepiece==0.2.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 15)) (0.2.0)
Requirement already satisfied: numpy==1.26.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 18)) (1.26.4)
Requirement already satisfied: soundfile==0.13.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 19)) (0.13.1)
Requirement already satisfied: librosa==0.10.2.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 20)) (0.10.2.post1)
Requirement already satisfied: soxr==0.5.0.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 21)) (0.5.0.post1)
Requirement already satisfied: pyctcdecode==0.5.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 24)) (0.5.0)
Requirement already satisfied: streamlit-webrtc==0.47.6 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 27)) (0.47.6)
Requirement already satisfied: av==14.0.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 28)) (14.0.1)
Requirement already satisfied: einops==0.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 31)) (0.8.0)
Requirement already satisfied: altair!=5.4.0,!=5.4.1,<6,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.5.0)
Requirement already satisfied: blinker<2,>=1.5.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (1.9.0)
Requirement already satisfied: cachetools<7,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.2.0)
Requirement already satisfied: click<9,>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (8.2.1)
Requirement already satisfied: packaging<26,>=20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (24.2)
Requirement already satisfied: pandas<3,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.3.2)
Requirement already satisfied: pillow<12,>=7.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (11.3.0)
Requirement already satisfied: protobuf<7,>=3.20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.29.5)
Requirement already satisfied: pyarrow>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (21.0.0)
Requirement already satisfied: requests<3,>=2.27 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.32.5)
Requirement already satisfied: tenacity<10,>=8.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (9.1.2)
Requirement already satisfied: toml<2,>=0.10.1 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.10.2)
Requirement already satisfied: typing-extensions<5,>=4.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (4.15.0)
Requirement already satisfied: watchdog<7,>=2.1.5 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.0.0)
Requirement already satisfied: gitpython!=3.1.19,<4,>=3.0.7 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (3.1.45)
Requirement already satisfied: pydeck<1,>=0.8.0b4 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.9.1)
Requirement already satisfied: tornado!=6.5.0,<7,>=6.0.3 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.5.2)
Requirement already satisfied: filelock in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.19.1)
Requirement already satisfied: setuptools in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (80.9.0)
Requirement already satisfied: sympy>=1.13.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.14.0)
Requirement already satisfied: networkx in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.5)
Requirement already satisfied: jinja2 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.1.6)
Requirement already satisfied: fsspec in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2024.12.0)
Requirement already satisfied: nvidia-cuda-nvrtc-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cuda-runtime-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cuda-cupti-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cudnn-cu12==9.10.2.21 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (9.10.2.21)
Requirement already satisfied: nvidia-cublas-cu12==12.8.4.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.4.1)
Requirement already satisfied: nvidia-cufft-cu12==11.3.3.83 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.3.3.83)
Requirement already satisfied: nvidia-curand-cu12==10.3.9.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (10.3.9.90)
Requirement already satisfied: nvidia-cusolver-cu12==11.7.3.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.7.3.90)
Requirement already satisfied: nvidia-cusparse-cu12==12.5.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.5.8.93)
Requirement already satisfied: nvidia-cusparselt-cu12==0.7.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (0.7.1)
Requirement already satisfied: nvidia-nccl-cu12==2.27.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2.27.3)
Requirement already satisfied: nvidia-nvtx-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-nvjitlink-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cufile-cu12==1.13.1.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.13.1.3)
Requirement already satisfied: triton==3.4.0 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.4.0)
Requirement already satisfied: pyyaml>=5.1 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (6.0.2)
Requirement already satisfied: regex!=2019.12.17 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (2025.7.34)
Requirement already satisfied: tokenizers<0.22,>=0.21 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (0.21.4)
Requirement already satisfied: tqdm>=4.27 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (4.67.1)
Requirement already satisfied: hf-xet<2.0.0,>=1.1.3 in ./venv/lib/python3.12/site-packages (from huggingface_hub==0.34.4->-r requirements.txt (line 13)) (1.1.8)
Requirement already satisfied: cffi>=1.0 in ./venv/lib/python3.12/site-packages (from soundfile==0.13.1->-r requirements.txt (line 19)) (1.17.1)
Requirement already satisfied: audioread>=2.1.9 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.0.1)
Requirement already satisfied: scipy>=1.2.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.16.1)
Requirement already satisfied: scikit-learn>=0.20.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.7.1)
Requirement already satisfied: joblib>=0.14 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.5.1)
Requirement already satisfied: decorator>=4.3.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (5.2.1)
Requirement already satisfied: numba>=0.51.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.61.2)
Requirement already satisfied: pooch>=1.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.8.2)
Requirement already satisfied: lazy-loader>=0.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.4)
Requirement already satisfied: msgpack>=1.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.1.1)
Requirement already satisfied: pygtrie<3.0,>=2.1 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.5.0)
Requirement already satisfied: hypothesis<7,>=6.14 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (6.138.3)
Requirement already satisfied: aiortc<2.0.0,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.13.0)
Requirement already satisfied: aioice<1.0.0,>=0.10.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.10.1)
Requirement already satisfied: cryptography>=44.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (45.0.6)
Requirement already satisfied: google-crc32c>=1.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.7.1)
Requirement already satisfied: pyee>=13.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (13.0.0)
Requirement already satisfied: pylibsrtp>=0.10.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.12.0)
Requirement already satisfied: pyopenssl>=25.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (25.1.0)
Requirement already satisfied: dnspython>=2.0.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (2.7.0)
Requirement already satisfied: ifaddr>=0.2.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.2.0)
Requirement already satisfied: jsonschema>=3.0 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (4.25.1)
Requirement already satisfied: narwhals>=1.14.2 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.2.0)
Requirement already satisfied: gitdb<5,>=4.0.1 in ./venv/lib/python3.12/site-packages (from gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (4.0.12)
Requirement already satisfied: smmap<6,>=3.0.1 in ./venv/lib/python3.12/site-packages (from gitdb<5,>=4.0.1->gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (5.0.2)
Requirement already satisfied: attrs>=22.2.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (25.3.0)
Requirement already satisfied: sortedcontainers<3.0.0,>=2.1.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.4.0)
Requirement already satisfied: python-dateutil>=2.8.2 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: tzdata>=2022.7 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: charset_normalizer<4,>=2 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.4.3)
Requirement already satisfied: idna<4,>=2.5 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2.5.0)
Requirement already satisfied: certifi>=2017.4.17 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.8.3)
Requirement already satisfied: pycparser in ./venv/lib/python3.12/site-packages (from cffi>=1.0->soundfile==0.13.1->-r requirements.txt (line 19)) (2.22)
Requirement already satisfied: MarkupSafe>=2.0 in ./venv/lib/python3.12/site-packages (from jinja2->torch==2.8.0->-r requirements.txt (line 8)) (3.0.2)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.4.1)
Requirement already satisfied: referencing>=0.28.4 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.36.2)
Requirement already satisfied: rpds-py>=0.7.1 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.27.0)
Requirement already satisfied: llvmlite<0.45,>=0.44.0dev0 in ./venv/lib/python3.12/site-packages (from numba>=0.51.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.44.0)
Requirement already satisfied: platformdirs>=2.5.0 in ./venv/lib/python3.12/site-packages (from pooch>=1.1->librosa==0.10.2.post1->-r requirements.txt (line 20)) (4.4.0)
Requirement already satisfied: six>=1.5 in ./venv/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (1.17.0)
Requirement already satisfied: threadpoolctl>=3.1.0 in ./venv/lib/python3.12/site-packages (from scikit-learn>=0.20.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.6.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./venv/lib/python3.12/site-packages (from sympy>=1.13.3->torch==2.8.0->-r requirements.txt (line 8)) (1.3.0)
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ Read from remote host 52.20.229.144: Connection reset by peer
Connection to 52.20.229.144 closed.
client_loop: send disconnect: Broken pipe
sobhan@Sobhans-MacBook-Air Downloads % ssh -i vedant-25m-key.pem ubuntu@52.20.229.144
Welcome to Ubuntu 24.04.2 LTS (GNU/Linux 6.14.0-1011-aws x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Thu Aug 28 12:46:18 UTC 2025

  System load:    0.2                Temperature:           -273.1 C
  Usage of /home: 52.5% of 97.87GB   Processes:             122
  Memory usage:   58%                Users logged in:       0
  Swap usage:     0%                 IPv4 address for enX0: 172.30.2.118

  => / is using 92.9% of 28.02GB

 * Ubuntu Pro delivers the most comprehensive open source security and
   compliance features.

   https://ubuntu.com/aws/pro

Expanded Security Maintenance for Applications is not enabled.

22 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


Last login: Wed Aug 27 18:53:04 2025 from 216.195.13.185
ubuntu@ip-172-30-2-118:~$ ls -ltr
total 64956
drwxrwxr-x   4 ubuntu ubuntu     4096 Jun 19 22:33 airflow
drwxrwxr-x   3 ubuntu ubuntu     4096 Jul 18 17:24 vedant
drwxr-xr-x   3 ubuntu ubuntu     4096 Jul 18 18:14 aws
-rw-rw-r--   1 ubuntu ubuntu 66440050 Jul 21 14:17 awscliv2.zip
drwxrwxr-x   2 ubuntu ubuntu     4096 Jul 21 15:07 bkup_processing
-rwxr-xr-x   1 ubuntu ubuntu      618 Jul 21 15:12 bkup_search_manual.sh
drwxrwxr-x   4 ubuntu ubuntu     4096 Jul 21 16:18 video_transcribe
drwx------   3 ubuntu ubuntu     4096 Jul 29 12:54 snap
drwxrwxr-x   2 ubuntu ubuntu     4096 Jul 29 13:09 dremio
drwxrwxr-x   8 ubuntu ubuntu     4096 Jul 30 13:52 colbert_doc_retrieval
drwxrwxr-x   8 ubuntu ubuntu     4096 Aug  4 16:28 search_manual
drwxrwxr-x   5 ubuntu ubuntu     4096 Aug 24 16:01 nemotron_vlm
drwxrwxr-x   4 ubuntu ubuntu     4096 Aug 24 20:41 RAG_bot
drwxrwxr-x   5 ubuntu ubuntu     4096 Aug 26 20:22 pip-cache
drwxrwxrwt 192 root   root      16384 Aug 27 21:22 tmp
drwxrwxr-x   4 ubuntu ubuntu     4096 Aug 27 21:36 nvidia_parakeet
ubuntu@ip-172-30-2-118:~$ cd nvidia_parakeet/
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ls -ltr
total 52
-rwxr-xr-x 1 ubuntu ubuntu    58 Aug 26 13:14 stop_parakeet.sh
drwxrwxr-x 7 ubuntu ubuntu  4096 Aug 26 19:43 venv
drwxrwxr-x 2 ubuntu ubuntu  4096 Aug 26 19:43 logs
-rw-rw-r-- 1 ubuntu ubuntu   754 Aug 26 20:19 requirements.txt
-rw-rw-r-- 1 ubuntu ubuntu 24131 Aug 27 19:04 nvidia_parakeet.py
-rwxr-xr-x 1 ubuntu ubuntu   891 Aug 27 21:29 start_parakeet.sh
-rw-rw-r-- 1 ubuntu ubuntu  5976 Aug 27 21:36 test.py
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ rm -rf test.py 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ls -ltr
total 44
-rwxr-xr-x 1 ubuntu ubuntu    58 Aug 26 13:14 stop_parakeet.sh
drwxrwxr-x 7 ubuntu ubuntu  4096 Aug 26 19:43 venv
drwxrwxr-x 2 ubuntu ubuntu  4096 Aug 26 19:43 logs
-rw-rw-r-- 1 ubuntu ubuntu   754 Aug 26 20:19 requirements.txt
-rw-rw-r-- 1 ubuntu ubuntu 24131 Aug 27 19:04 nvidia_parakeet.py
-rwxr-xr-x 1 ubuntu ubuntu   891 Aug 27 21:29 start_parakeet.sh
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ vi start_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./stop_parakeet.sh 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ./start_parakeet.sh 
Requirement already satisfied: pip in ./venv/lib/python3.12/site-packages (25.2)
Requirement already satisfied: streamlit==1.48.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 5)) (1.48.1)
Requirement already satisfied: torch==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 8)) (2.8.0)
Requirement already satisfied: torchaudio==2.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 9)) (2.8.0)
Requirement already satisfied: transformers==4.55.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 12)) (4.55.4)
Requirement already satisfied: huggingface_hub==0.34.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 13)) (0.34.4)
Requirement already satisfied: safetensors==0.6.2 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 14)) (0.6.2)
Requirement already satisfied: sentencepiece==0.2.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 15)) (0.2.0)
Requirement already satisfied: numpy==1.26.4 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 18)) (1.26.4)
Requirement already satisfied: soundfile==0.13.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 19)) (0.13.1)
Requirement already satisfied: librosa==0.10.2.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 20)) (0.10.2.post1)
Requirement already satisfied: soxr==0.5.0.post1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 21)) (0.5.0.post1)
Requirement already satisfied: pyctcdecode==0.5.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 24)) (0.5.0)
Requirement already satisfied: streamlit-webrtc==0.47.6 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 27)) (0.47.6)
Requirement already satisfied: av==14.0.1 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 28)) (14.0.1)
Requirement already satisfied: einops==0.8.0 in ./venv/lib/python3.12/site-packages (from -r requirements.txt (line 31)) (0.8.0)
Requirement already satisfied: altair!=5.4.0,!=5.4.1,<6,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.5.0)
Requirement already satisfied: blinker<2,>=1.5.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (1.9.0)
Requirement already satisfied: cachetools<7,>=4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.2.0)
Requirement already satisfied: click<9,>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (8.2.1)
Requirement already satisfied: packaging<26,>=20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (24.2)
Requirement already satisfied: pandas<3,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.3.2)
Requirement already satisfied: pillow<12,>=7.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (11.3.0)
Requirement already satisfied: protobuf<7,>=3.20 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (5.29.5)
Requirement already satisfied: pyarrow>=7.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (21.0.0)
Requirement already satisfied: requests<3,>=2.27 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (2.32.5)
Requirement already satisfied: tenacity<10,>=8.1.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (9.1.2)
Requirement already satisfied: toml<2,>=0.10.1 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.10.2)
Requirement already satisfied: typing-extensions<5,>=4.4.0 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (4.15.0)
Requirement already satisfied: watchdog<7,>=2.1.5 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.0.0)
Requirement already satisfied: gitpython!=3.1.19,<4,>=3.0.7 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (3.1.45)
Requirement already satisfied: pydeck<1,>=0.8.0b4 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (0.9.1)
Requirement already satisfied: tornado!=6.5.0,<7,>=6.0.3 in ./venv/lib/python3.12/site-packages (from streamlit==1.48.1->-r requirements.txt (line 5)) (6.5.2)
Requirement already satisfied: filelock in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.19.1)
Requirement already satisfied: setuptools in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (80.9.0)
Requirement already satisfied: sympy>=1.13.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.14.0)
Requirement already satisfied: networkx in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.5)
Requirement already satisfied: jinja2 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.1.6)
Requirement already satisfied: fsspec in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2024.12.0)
Requirement already satisfied: nvidia-cuda-nvrtc-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cuda-runtime-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cuda-cupti-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-cudnn-cu12==9.10.2.21 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (9.10.2.21)
Requirement already satisfied: nvidia-cublas-cu12==12.8.4.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.4.1)
Requirement already satisfied: nvidia-cufft-cu12==11.3.3.83 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.3.3.83)
Requirement already satisfied: nvidia-curand-cu12==10.3.9.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (10.3.9.90)
Requirement already satisfied: nvidia-cusolver-cu12==11.7.3.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (11.7.3.90)
Requirement already satisfied: nvidia-cusparse-cu12==12.5.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.5.8.93)
Requirement already satisfied: nvidia-cusparselt-cu12==0.7.1 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (0.7.1)
Requirement already satisfied: nvidia-nccl-cu12==2.27.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (2.27.3)
Requirement already satisfied: nvidia-nvtx-cu12==12.8.90 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.90)
Requirement already satisfied: nvidia-nvjitlink-cu12==12.8.93 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (12.8.93)
Requirement already satisfied: nvidia-cufile-cu12==1.13.1.3 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (1.13.1.3)
Requirement already satisfied: triton==3.4.0 in ./venv/lib/python3.12/site-packages (from torch==2.8.0->-r requirements.txt (line 8)) (3.4.0)
Requirement already satisfied: pyyaml>=5.1 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (6.0.2)
Requirement already satisfied: regex!=2019.12.17 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (2025.7.34)
Requirement already satisfied: tokenizers<0.22,>=0.21 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (0.21.4)
Requirement already satisfied: tqdm>=4.27 in ./venv/lib/python3.12/site-packages (from transformers==4.55.4->-r requirements.txt (line 12)) (4.67.1)
Requirement already satisfied: hf-xet<2.0.0,>=1.1.3 in ./venv/lib/python3.12/site-packages (from huggingface_hub==0.34.4->-r requirements.txt (line 13)) (1.1.8)
Requirement already satisfied: cffi>=1.0 in ./venv/lib/python3.12/site-packages (from soundfile==0.13.1->-r requirements.txt (line 19)) (1.17.1)
Requirement already satisfied: audioread>=2.1.9 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.0.1)
Requirement already satisfied: scipy>=1.2.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.16.1)
Requirement already satisfied: scikit-learn>=0.20.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.7.1)
Requirement already satisfied: joblib>=0.14 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.5.1)
Requirement already satisfied: decorator>=4.3.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (5.2.1)
Requirement already satisfied: numba>=0.51.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.61.2)
Requirement already satisfied: pooch>=1.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.8.2)
Requirement already satisfied: lazy-loader>=0.1 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.4)
Requirement already satisfied: msgpack>=1.0 in ./venv/lib/python3.12/site-packages (from librosa==0.10.2.post1->-r requirements.txt (line 20)) (1.1.1)
Requirement already satisfied: pygtrie<3.0,>=2.1 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.5.0)
Requirement already satisfied: hypothesis<7,>=6.14 in ./venv/lib/python3.12/site-packages (from pyctcdecode==0.5.0->-r requirements.txt (line 24)) (6.138.3)
Requirement already satisfied: aiortc<2.0.0,>=1.4.0 in ./venv/lib/python3.12/site-packages (from streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.13.0)
Requirement already satisfied: aioice<1.0.0,>=0.10.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.10.1)
Requirement already satisfied: cryptography>=44.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (45.0.6)
Requirement already satisfied: google-crc32c>=1.1 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (1.7.1)
Requirement already satisfied: pyee>=13.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (13.0.0)
Requirement already satisfied: pylibsrtp>=0.10.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.12.0)
Requirement already satisfied: pyopenssl>=25.0.0 in ./venv/lib/python3.12/site-packages (from aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (25.1.0)
Requirement already satisfied: dnspython>=2.0.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (2.7.0)
Requirement already satisfied: ifaddr>=0.2.0 in ./venv/lib/python3.12/site-packages (from aioice<1.0.0,>=0.10.1->aiortc<2.0.0,>=1.4.0->streamlit-webrtc==0.47.6->-r requirements.txt (line 27)) (0.2.0)
Requirement already satisfied: jsonschema>=3.0 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (4.25.1)
Requirement already satisfied: narwhals>=1.14.2 in ./venv/lib/python3.12/site-packages (from altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.2.0)
Requirement already satisfied: gitdb<5,>=4.0.1 in ./venv/lib/python3.12/site-packages (from gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (4.0.12)
Requirement already satisfied: smmap<6,>=3.0.1 in ./venv/lib/python3.12/site-packages (from gitdb<5,>=4.0.1->gitpython!=3.1.19,<4,>=3.0.7->streamlit==1.48.1->-r requirements.txt (line 5)) (5.0.2)
Requirement already satisfied: attrs>=22.2.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (25.3.0)
Requirement already satisfied: sortedcontainers<3.0.0,>=2.1.0 in ./venv/lib/python3.12/site-packages (from hypothesis<7,>=6.14->pyctcdecode==0.5.0->-r requirements.txt (line 24)) (2.4.0)
Requirement already satisfied: python-dateutil>=2.8.2 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: tzdata>=2022.7 in ./venv/lib/python3.12/site-packages (from pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.2)
Requirement already satisfied: charset_normalizer<4,>=2 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.4.3)
Requirement already satisfied: idna<4,>=2.5 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2.5.0)
Requirement already satisfied: certifi>=2017.4.17 in ./venv/lib/python3.12/site-packages (from requests<3,>=2.27->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.8.3)
Requirement already satisfied: pycparser in ./venv/lib/python3.12/site-packages (from cffi>=1.0->soundfile==0.13.1->-r requirements.txt (line 19)) (2.22)
Requirement already satisfied: MarkupSafe>=2.0 in ./venv/lib/python3.12/site-packages (from jinja2->torch==2.8.0->-r requirements.txt (line 8)) (3.0.2)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (2025.4.1)
Requirement already satisfied: referencing>=0.28.4 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.36.2)
Requirement already satisfied: rpds-py>=0.7.1 in ./venv/lib/python3.12/site-packages (from jsonschema>=3.0->altair!=5.4.0,!=5.4.1,<6,>=4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (0.27.0)
Requirement already satisfied: llvmlite<0.45,>=0.44.0dev0 in ./venv/lib/python3.12/site-packages (from numba>=0.51.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (0.44.0)
Requirement already satisfied: platformdirs>=2.5.0 in ./venv/lib/python3.12/site-packages (from pooch>=1.1->librosa==0.10.2.post1->-r requirements.txt (line 20)) (4.4.0)
Requirement already satisfied: six>=1.5 in ./venv/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas<3,>=1.4.0->streamlit==1.48.1->-r requirements.txt (line 5)) (1.17.0)
Requirement already satisfied: threadpoolctl>=3.1.0 in ./venv/lib/python3.12/site-packages (from scikit-learn>=0.20.0->librosa==0.10.2.post1->-r requirements.txt (line 20)) (3.6.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./venv/lib/python3.12/site-packages (from sympy>=1.13.3->torch==2.8.0->-r requirements.txt (line 8)) (1.3.0)
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ ls -ltr
total 44
-rwxr-xr-x 1 ubuntu ubuntu    58 Aug 26 13:14 stop_parakeet.sh
drwxrwxr-x 7 ubuntu ubuntu  4096 Aug 26 19:43 venv
drwxrwxr-x 2 ubuntu ubuntu  4096 Aug 26 19:43 logs
-rw-rw-r-- 1 ubuntu ubuntu   754 Aug 26 20:19 requirements.txt
-rw-rw-r-- 1 ubuntu ubuntu 24131 Aug 27 19:04 nvidia_parakeet.py
-rwxr-xr-x 1 ubuntu ubuntu   810 Aug 28 12:46 start_parakeet.sh
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ vi nvidia_parakeet.py 
ubuntu@ip-172-30-2-118:~/nvidia_parakeet$ vi nvidia_parakeet.py 

            beam_decoder=beam_decoder if use_beam else None,
            use_beam=use_beam,
            normalize_opts=normalize_opts,
            emit_partial=live_emit_partial
        )

    transcriber = st.session_state["live_transcriber"]
    RTC_CFG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

    def audio_frame_callback(frame):
        pcm = frame.to_ndarray()
        if pcm.ndim > 1:
            pcm = pcm.mean(axis=0)
        if pcm.dtype == np.int16:
            pcm = pcm.astype(np.float32) / 32768.0
        elif pcm.dtype != np.float32:
            pcm = pcm.astype(np.float32)
        transcriber.add_audio(pcm, frame.sample_rate)
        return frame

    webrtc_streamer(
        key="live-ctc",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=256,
        media_stream_constraints={"audio": True, "video": False},
        audio_frame_callback=audio_frame_callback,
        rtc_configuration=RTC_CFG,
        async_processing=True
    )

    st.text_area("Partial Transcript", st.session_state["live_partial"], height=180)

    if st.button("Finalize Live Session"):
        final_text = transcriber.final()
        st.text_area("Final Transcript", final_text, height=250)
        if offer_download and final_text:
            st.download_button(
                "Download Live Transcript",
                final_text.encode("utf-8"),
                file_name="live_session_transcript.txt",
                mime="text/plain"
            )
        st.session_state["live_transcriber"] = None
        st.session_state["live_partial"] = ""

# ---------------------------------------------------------------
# Footer / Guidance
# ---------------------------------------------------------------
st.markdown("---")
st.caption(
    "Provide MODEL_LOCAL_DIR (env or secrets.local_model_dir) to run offline. "
    "Set MODEL_SNAPSHOT_DIR to auto-create a minimal snapshot. "
    "Set DISABLE_NETWORK=1 to enforce offline-only behavior."
)
"nvidia_parakeet.py" 636L, 24131B                                                                                                                                                                                         636,1         Bot
