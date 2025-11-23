#!/usr/bin/env python3
"""
MatVerse Dual-Brain Watcher
Monitora TeraBox + Google Drive → Cria embeddings únicos → Upsert Qdrant
"""

import os
import time
import hashlib
import json
import requests
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DualBrainWatcher(FileSystemEventHandler):
    """
    Monitora TeraBox + GDrive → Cria embeddings únicos → Upsert Qdrant
    Hash MD5 por path = zero duplicatas
    """

    ROOTS = ["/mnt/terabox", "/mnt/gdrive"]
    QDRANT = "http://localhost:6333"
    COLLECTION = "dual_brain"
    EXTENSIONS = (".txt", ".md", ".py", ".js", ".sol", ".yaml", ".json", ".rs", ".go")
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        self.seen_hashes = set()
        self.qdrant_init()

    def qdrant_init(self):
        """Cria collection se não existir"""
        try:
            requests.put(
                f"{self.QDRANT}/collections/{self.COLLECTION}",
                json={
                    "vectors": {
                        "size": 1536,  # text-embedding-3-small
                        "distance": "Cosine"
                    }
                }
            )
            print(f"✓ Qdrant collection '{self.COLLECTION}' pronta")
        except Exception as e:
            print(f"⚠️ Qdrant init error (collection pode já existir): {e}")

    def get_file_hash(self, path):
        """Hash único por path (não por conteúdo) = renomear não duplica"""
        return hashlib.md5(str(path).encode()).hexdigest()

    def embed(self, text):
        """
        Gera embedding usando modelo local (Ollama) ou OpenAI
        Fallback para embeddings simples se APIs não disponíveis
        """
        # Tenta Ollama primeiro (zero-cost)
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": text[:8000]
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["embedding"]
        except:
            pass

        # Fallback: embedding sintético (count-based)
        # Em produção, usar OpenAI ou modelo dedicado
        words = text.lower().split()[:1536]
        vector = [0.0] * 1536
        for i, word in enumerate(words):
            if i < 1536:
                vector[i] = hash(word) % 100 / 100.0
        return vector

    def upsert_file(self, path):
        """Le arquivo → embedding → upsert Qdrant"""
        try:
            # Verificar tamanho
            if os.path.getsize(path) > self.MAX_FILE_SIZE:
                print(f"⚠️ Arquivo muito grande, ignorando: {path}")
                return

            # 1. Hash do path
            file_id = self.get_file_hash(path)

            if file_id in self.seen_hashes:
                return  # já indexado

            # 2. Le conteúdo
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return  # arquivo vazio

            # 3. Embedding
            vector = self.embed(content)

            # 4. Upsert
            requests.put(
                f"{self.QDRANT}/collections/{self.COLLECTION}/points",
                json={
                    "points": [{
                        "id": file_id,
                        "vector": vector,
                        "payload": {
                            "path": str(path),
                            "source": "terabox" if "terabox" in str(path) else "gdrive",
                            "content": content[:1000],  # preview
                            "indexed_at": time.time(),
                            "size": len(content),
                            "extension": Path(path).suffix
                        }
                    }]
                }
            )

            self.seen_hashes.add(file_id)
            print(f"✓ Indexed: {Path(path).name} ({len(content)} bytes)")

        except Exception as e:
            print(f"✗ Error indexing {path}: {e}")

    def on_created(self, event):
        """Novo arquivo detectado"""
        if not event.is_directory and event.src_path.endswith(self.EXTENSIONS):
            print(f"📄 Novo arquivo: {event.src_path}")
            self.upsert_file(event.src_path)

    def on_modified(self, event):
        """Arquivo modificado"""
        if not event.is_directory and event.src_path.endswith(self.EXTENSIONS):
            # Remove hash antigo para forçar re-index
            file_id = self.get_file_hash(event.src_path)
            self.seen_hashes.discard(file_id)
            print(f"✏️ Modificado: {event.src_path}")
            self.upsert_file(event.src_path)

    def initial_scan(self):
        """Scan inicial das duas clouds"""
        print("🔍 Scanning inicial...")
        total_files = 0

        for root in self.ROOTS:
            if not os.path.exists(root):
                print(f"⚠️ Path não existe: {root}")
                continue

            print(f"📁 Scanning: {root}")
            for path in Path(root).rglob("*"):
                if path.is_file() and str(path).endswith(self.EXTENSIONS):
                    self.upsert_file(path)
                    total_files += 1

                    # Progress indicator
                    if total_files % 100 == 0:
                        print(f"  ... {total_files} arquivos processados")

        print(f"✓ Scan completo: {len(self.seen_hashes)} arquivos indexados")

def query_dual_brain(question, top_k=5):
    """
    API de busca unificada
    """
    # 1. Embedding da pergunta (simplificado)
    words = question.lower().split()[:1536]
    vec = [0.0] * 1536
    for i, word in enumerate(words):
        if i < 1536:
            vec[i] = hash(word) % 100 / 100.0

    # 2. Search Qdrant
    try:
        response = requests.post(
            "http://localhost:6333/collections/dual_brain/points/search",
            json={
                "vector": vec,
                "limit": top_k,
                "with_payload": True
            }
        )

        results = response.json()["result"]

        # 3. Retorna contexto unificado
        contexts = []
        for hit in results:
            contexts.append({
                "text": hit["payload"]["content"],
                "source": hit["payload"]["source"],
                "path": hit["payload"]["path"],
                "score": hit["score"]
            })

        return contexts
    except Exception as e:
        print(f"✗ Query error: {e}")
        return []

def main():
    """Main entry point"""
    print("🍒 MatVerse Dual-Brain Watcher")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    watcher = DualBrainWatcher()
    watcher.initial_scan()

    # Inicia watchdog
    observer = Observer()
    for root in DualBrainWatcher.ROOTS:
        if os.path.exists(root):
            observer.schedule(watcher, root, recursive=True)
            print(f"👁️ Watching: {root}")

    observer.start()
    print("✓ Monitoring ativo (Ctrl+C para parar)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n✓ Watcher parado")
    observer.join()

if __name__ == "__main__":
    main()
