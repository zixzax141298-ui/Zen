from __future__ import annotations

import hashlib
import json
from dataclasses import is_dataclass
from typing import Any

def _canonicalize(node: Any) -> Any:
    """Ubah AST menjadi format JSON yang kanonik (mengabaikan span/source_id)."""
    if node is None or isinstance(node, (str, int, float, bool)):
        return node
    if isinstance(node, (list, tuple)):
        return [_canonicalize(item) for item in node]
    if isinstance(node, dict):
        return {str(k): _canonicalize(v) for k, v in node.items() if k not in ("span", "source_id")}
    
    # Jika node adalah dataclass (seperti Program, VarDecl, dll)
    if is_dataclass(node) and not isinstance(node, type):
        out: dict[str, Any] = {"__type__": type(node).__name__}
        for field_name in node.__dataclass_fields__:
            # Abaikan span dan source_id agar murni struktural
            if field_name in ("span", "source_id"):
                continue
            out[field_name] = _canonicalize(getattr(node, field_name))
        return out
        
    if hasattr(node, "__dict__"):
        out = {"__type__": type(node).__name__}
        for k, v in vars(node).items():
            if not k.startswith("_") and k not in ("span", "source_id"):
                out[k] = _canonicalize(v)
        return out
    return repr(node)

def generate_fingerprint(ast: Any) -> str:
    """Menghasilkan hash SHA-256 dari AST yang sudah dikanonikalisasi."""
    canonical_data = _canonicalize(ast)
    # sort_keys=True sangat penting agar urutan dictionary tidak mengubah hash
    json_str = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
    hash_hex = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
    
    # Format ZIIF: "z1-" diikuti 32 karakter pertama (cukup unik dan mudah dibaca)
    return f"z1-{hash_hex[:32]}"
