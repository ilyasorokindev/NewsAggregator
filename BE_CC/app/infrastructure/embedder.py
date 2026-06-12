from sentence_transformers import SentenceTransformer

from app.config import settings

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    vectors = model.encode(texts, batch_size=32, show_progress_bar=False)
    return [v.tolist() for v in vectors]
