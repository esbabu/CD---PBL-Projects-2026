# OptAgent Native (C11 / C++17) Sandbox Image
# Includes clang/llvm + sanitizers + llvm-cov, gcc/g++, libc++, valgrind,
# cppcheck, clang-tidy, cbmc, and vendored cJSON + nlohmann/json.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    clang \
    llvm \
    lld \
    gcc \
    g++ \
    libc++-dev \
    libc++abi-dev \
    valgrind \
    cppcheck \
    clang-tidy \
    cbmc \
    libcjson-dev \
    nlohmann-json3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV CC=clang
ENV CXX=clang++
WORKDIR /tmp
