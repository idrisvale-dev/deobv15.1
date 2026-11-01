FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN cp vendor/luraph_v151/bin/luau-ast vendor/luraph_v15zip/Deobfuscator/deobf/bin/luau-ast || true && \
    cp vendor/luraph_v151/bin/luau     vendor/luraph_v15zip/Deobfuscator/deobf/bin/luau     || true && \
    cp vendor/luraph_v151/bin/luau-ast vendor/luraph_v15zip/Deobfuscator/deobf/obfuscators/luraph_v15/luau-ast || true

RUN find vendor/luraph_v151/bin -type f ! -name "*.exe" ! -name "*.txt" -exec chmod +x {} \; && \
    find vendor/luraph_v15zip/Deobfuscator/deobf/bin -type f ! -name "*.exe" ! -name "*.txt" -exec chmod +x {} \; || true

RUN cd vendor/prometheus    && npm install --silent 2>/dev/null || true
RUN cd vendor/clyde         && npm install --silent 2>/dev/null || true
RUN cd vendor/luaobfuscator && npm install --silent 2>/dev/null || true
RUN cd vendor/ironveil/deobfuscator && npm install --silent 2>/dev/null || true
RUN cd vendor/luraph_v151   && npm install --silent 2>/dev/null || true

CMD ["python", "main.py"]
