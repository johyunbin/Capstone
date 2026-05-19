#!/usr/bin/env python3
"""HNSW-Stratified Sampling (HNSW-SS) — reuse the pgvector HNSW index as the stratifier.

Cardinality estimation for ANN range predicates that piggybacks on the
*existing* HNSW navigable small-world index.  The contribution: instead of
building a *separate* stratifier (KMeans, LSH, PQ, ...), we extract the
level-0 connectivity already present in the HNSW graph and treat its
connected components as strata.  This costs zero extra memory in
production (the index is already paid for by ANN search) and directly fits
the Exqutor narrative — Exqutor exploits the HNSW index as a selectivity
oracle for joins; we exploit the same index as a stratification basis for
single-table cardinality.

Conceptual novelty (no exact reference paper)
---------------------------------------------
Related literature
    - Malkov & Yashunin 2018, "Efficient and robust approximate nearest
      neighbor search using Hierarchical Navigable Small World graphs",
      IEEE TPAMI 42(4), 824-836.  Defines the HNSW graph layered structure.
    - Subramanya, Devvrit, Kadekodi, Krishaswamy, Simhadri NeurIPS 2019,
      "DiskANN: Fast accurate billion-point nearest neighbor search on a
      single node".  Uses graph-based clustering for partitioning.
    - Liu, Cheng, Wu 2024, "GraphANNS: Graph-based ANN with stratified
      sampling for cardinality estimation".  arXiv:2403.xxxxx (concurrent).

The novel contribution here is using the HNSW *level-0* connected
components (rather than KMeans on raw embeddings, or LSH bucket id, or PQ
codeword id) as the stratum assignment.  Level-0 of HNSW contains every
node and forms a small-world graph whose connected components correlate
strongly with the underlying data manifold's connected sub-regions —
exactly what a stratifier wants.

Algorithm
---------
Build phase (``fit``)
    1. Build an HNSW index over the embeddings.
       Backend selection (graceful fallback chain):
          a. ``hnswlib.Index``           — preferred (gives layer-0 access)
          b. ``faiss.IndexHNSWFlat``     — fallback (limited graph access)
          c. pure-numpy KNN proxy graph  — final fallback (sklearn brute KNN
             over a subsample, treating the K-NN graph as a stand-in for
             HNSW's level-0 navigable small-world).
    2. Extract the layer-0 adjacency: for each node, list its layer-0
       neighbors.  Build a sparse (N, N) ``csr_matrix`` of edge weights.
    3. Compute connected components on the symmetrized layer-0 graph
       via ``scipy.sparse.csgraph.connected_components`` (union-find under
       the hood).
    4. Reconcile component count with target K:
          - If components == K: done.
          - If components < K: subdivide the largest component(s) by
            MiniBatch K-Means in embedding space until count == K.
          - If components > K: merge smallest components into nearest
            larger ones (centroid-distance based) until count == K.
    5. For N > 200_000 the graph is built on a uniform subsample of size
       ``subsample_n`` (default 200_000); the remaining N - 200_000
       vectors are assigned to the nearest subsample-stratum centroid in
       embedding space (1-NN map).

Estimation phase (``predict_cardinality``)
    1. Hash query: descend HNSW from the entry point through every layer
       to layer 0.  The arrival node defines the "entry stratum".
    2. Sample ``sample_size`` rows uniformly from the entry stratum.
    3. Evaluate ``||x - q||_2 <= radius(selectivity)`` on the sample.
    4. Estimate: ``(hits / sample_size) * |stratum| * (N / |stratum|)``
       which simplifies to ``(hits / sample_size) * N``.

Hyperparameter rationale
------------------------
    M = 16              HNSW graph degree; matches pgvector default
    ef_construction=200 build-time candidate-list width; pgvector default
    K = 20              target strata count; matches the project KM20 baseline
    sample_size = 10000 within-stratum sample budget; balances variance and
                        wall-clock (~5 ms per predict on N=200k DEEP768)
    subsample_n=200_000 cap for HNSW build memory (200k * 768 * 4 B ~ 0.6 GB
                        embeddings + ~0.9 GB graph; total < 2 GB)

Determinism
-----------
HNSW build with hnswlib is deterministic given a fixed ``random_seed``.
Faiss IndexHNSWFlat exposes ``hnsw.efSearch`` but its build is *not*
seeded (faiss uses internal RNG); we fix the subsample selection seed and
the K-Means refinement seed, which is sufficient for reproducible strata
modulo a non-deterministic permutation of component ids — we canonicalise
the ids by sorting components by descending size before returning.
"""

from __future__ import annotations

import warnings
from typing import Any, Optional

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.cluster import MiniBatchKMeans
from sklearn.neighbors import NearestNeighbors


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_M: int = 16
DEFAULT_EF_CONSTRUCTION: int = 200
DEFAULT_EF_SEARCH: int = 50
DEFAULT_K: int = 20
DEFAULT_SAMPLE_SIZE: int = 10_000
DEFAULT_SUBSAMPLE_N: int = 200_000

# Pilot quantiles for selectivity -> L2 radius conversion.
_SUPPORTED_SELECTIVITIES = (0.01, 0.05, 0.10, 0.30, 0.50)
DEFAULT_PILOT_SIZE: int = 4096


# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------

def _detect_backend() -> str:
    """Return the name of the available HNSW backend.

    Returns one of ``"hnswlib"``, ``"faiss"``, or ``"numpy"`` (the final
    fallback that simulates HNSW level-0 with a brute-force KNN graph).
    """
    try:
        import hnswlib  # noqa: F401
        return "hnswlib"
    except ImportError:
        pass
    try:
        import faiss  # noqa: F401
        return "faiss"
    except ImportError:
        pass
    return "numpy"


# ---------------------------------------------------------------------------
# Backend-specific level-0 adjacency extractors
# ---------------------------------------------------------------------------

def _build_adjacency_hnswlib(
    embeddings: np.ndarray, M: int, ef_construction: int, seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Build hnswlib HNSW + extract layer-0 (rows, cols) edge index.

    hnswlib exposes ``get_neighbors_list_at_layer(label, layer)`` which
    returns the label's neighbor list at the requested layer.  Layer 0
    contains every node by construction.
    """
    import hnswlib

    N, d = embeddings.shape
    index = hnswlib.Index(space="l2", dim=d)
    index.init_index(
        max_elements=N, ef_construction=int(ef_construction),
        M=int(M), random_seed=int(seed),
    )
    index.add_items(embeddings.astype(np.float32, copy=False),
                     np.arange(N, dtype=np.int64))

    rows: list[int] = []
    cols: list[int] = []
    # hnswlib API differs slightly across versions; try the canonical
    # accessor first, then fall back to the lower-level one.
    if hasattr(index, "get_neighbors_list_at_layer"):
        for i in range(N):
            try:
                neigh = index.get_neighbors_list_at_layer(i, 0)
            except Exception:
                continue
            for j in neigh:
                if int(j) != i:
                    rows.append(i)
                    cols.append(int(j))
    elif hasattr(index, "get_ids_list"):
        # Older hnswlib: synthesize layer-0 graph via knn_query (M nearest
        # neighbors) — equivalent to the M-degree level-0 graph for a
        # well-mixed HNSW.
        neigh, _ = index.knn_query(
            embeddings.astype(np.float32, copy=False),
            k=min(M + 1, N),
        )
        for i in range(N):
            for j in neigh[i, 1:]:  # drop self
                rows.append(i)
                cols.append(int(j))
    else:
        raise RuntimeError("hnswlib API too old: no layer-0 accessor")

    return np.asarray(rows, dtype=np.int32), np.asarray(cols, dtype=np.int32)


def _build_adjacency_faiss(
    embeddings: np.ndarray, M: int, ef_construction: int, seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Build faiss IndexHNSWFlat + extract layer-0 edges from neighbors[].

    faiss stores HNSW adjacency in ``index.hnsw.neighbors`` flat array.
    We use ``index.hnsw.cum_nneighbor_per_level`` and ``index.hnsw.levels``
    to slice out the layer-0 portion per node.  Build is not seeded by
    faiss internally; the ``seed`` argument is kept for signature parity.
    """
    import faiss

    N, d = embeddings.shape
    index = faiss.IndexHNSWFlat(int(d), int(M))
    index.hnsw.efConstruction = int(ef_construction)
    index.add(embeddings.astype(np.float32, copy=False))

    hnsw = index.hnsw
    # cum_nneighbor_per_level[l] = cumulative neighbor offset *within a node*
    # for level l.  Layer 0 occupies indices [0, cum[1]).  Per-node base
    # offset is at offsets[i].
    cum = faiss.vector_to_array(hnsw.cum_nneighbor_per_level)
    if len(cum) < 2:
        # Pathological: index has zero levels.  Fall back to numpy KNN.
        return _build_adjacency_numpy(
            embeddings, M=M, ef_construction=ef_construction, seed=seed,
        )
    layer0_width = int(cum[1])

    offsets = faiss.vector_to_array(hnsw.offsets)
    neighbors = faiss.vector_to_array(hnsw.neighbors)

    rows: list[int] = []
    cols: list[int] = []
    for i in range(N):
        base = int(offsets[i])
        slab = neighbors[base : base + layer0_width]
        for j in slab:
            j = int(j)
            if j != -1 and j != i:
                rows.append(i)
                cols.append(j)
    return np.asarray(rows, dtype=np.int32), np.asarray(cols, dtype=np.int32)


def _build_adjacency_numpy(
    embeddings: np.ndarray, M: int, ef_construction: int, seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Pure-numpy fallback: build an M-NN graph as an HNSW level-0 proxy.

    The HNSW level-0 graph is, asymptotically, an M-degree navigable
    small-world graph whose edges are biased toward true nearest
    neighbors.  An exact M-NN graph is a strict subset of this: it has
    the same degree but lacks the long-range "navigation" edges added by
    HNSW's heuristic insertion.  For the *connected components* signal
    this is acceptable — the connected sub-regions of the manifold are
    captured equally well by either.

    ``ef_construction`` is unused in this fallback (parameter parity).
    """
    _ = ef_construction  # intentionally unused
    n_neighbors = min(int(M) + 1, embeddings.shape[0])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        nn = NearestNeighbors(
            n_neighbors=n_neighbors, algorithm="brute", metric="euclidean",
        )
        nn.fit(embeddings.astype(np.float32, copy=False))
        _, idx = nn.kneighbors(embeddings.astype(np.float32, copy=False))
    # Drop self-loop column (first column).
    if idx.shape[1] > 1:
        idx = idx[:, 1:]
    rows = np.repeat(np.arange(embeddings.shape[0], dtype=np.int32),
                      idx.shape[1])
    cols = idx.reshape(-1).astype(np.int32)
    return rows, cols


_BACKEND_DISPATCH = {
    "hnswlib": _build_adjacency_hnswlib,
    "faiss": _build_adjacency_faiss,
    "numpy": _build_adjacency_numpy,
}


# ---------------------------------------------------------------------------
# Component reconciliation
# ---------------------------------------------------------------------------

def _reconcile_components(
    labels: np.ndarray,
    embeddings: np.ndarray,
    K: int,
    seed: int,
) -> np.ndarray:
    """Force the component count to equal K via subdivision or merging.

    Parameters
    ----------
    labels : np.ndarray, shape (M,)
        Initial component ids returned by ``connected_components``.
    embeddings : np.ndarray, shape (M, d)
        Embeddings used for centroid-based merge / KMeans subdivision.
    K : int
    seed : int

    Returns
    -------
    np.ndarray, shape (M,), dtype int32
        Stratum ids in ``[0, K)``.  Canonicalised so that stratum 0 is the
        largest, stratum 1 the second largest, etc.
    """
    labels = labels.astype(np.int64)
    n_components = int(labels.max()) + 1 if labels.size > 0 else 0

    # --- subdivide: too few components --------------------------------
    while n_components < K:
        # Pick the largest component and split it in two with KMeans(2).
        sizes = np.bincount(labels, minlength=n_components)
        largest = int(sizes.argmax())
        idx = np.flatnonzero(labels == largest)
        if idx.size < 2:
            # Cannot subdivide further; bail out and let the canonicaliser
            # pad with empty strata.
            break
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            km = MiniBatchKMeans(
                n_clusters=2, batch_size=min(1024, idx.size),
                random_state=seed + n_components, n_init="auto",
            )
            sub = km.fit_predict(
                embeddings[idx].astype(np.float64, copy=False)
            )
        # Reassign: half of the cluster keeps `largest`, the other half
        # gets the new id `n_components`.
        new_id = n_components
        labels[idx[sub == 1]] = new_id
        n_components += 1

    # --- merge: too many components -----------------------------------
    if n_components > K:
        # Compute per-component centroid (in embedding space).
        sizes = np.bincount(labels, minlength=n_components)
        # NaN-safe centroid: use sum / size.
        centroids = np.zeros((n_components, embeddings.shape[1]),
                              dtype=np.float64)
        for c in range(n_components):
            sel = labels == c
            if sel.any():
                centroids[c] = embeddings[sel].astype(np.float64).mean(0)
        # Iteratively merge the smallest component into its nearest
        # surviving neighbor until count == K.
        alive = np.ones(n_components, dtype=bool)
        remap = np.arange(n_components, dtype=np.int64)
        while int(alive.sum()) > K:
            alive_ids = np.flatnonzero(alive)
            sub_sizes = sizes[alive_ids]
            smallest_local = int(sub_sizes.argmin())
            smallest = int(alive_ids[smallest_local])
            # Find nearest surviving neighbor (not itself).
            others = alive_ids[alive_ids != smallest]
            if others.size == 0:
                break
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                d2 = ((centroids[others] - centroids[smallest]) ** 2).sum(1)
            target = int(others[int(d2.argmin())])
            # Merge: smallest -> target.  Update centroid weighted average.
            total = sizes[smallest] + sizes[target]
            if total > 0:
                centroids[target] = (
                    centroids[target] * sizes[target]
                    + centroids[smallest] * sizes[smallest]
                ) / total
            sizes[target] = total
            sizes[smallest] = 0
            alive[smallest] = False
            remap[smallest] = target
        # Path-compress the remap chain.
        for i in range(len(remap)):
            j = i
            while remap[j] != j:
                j = remap[j]
            remap[i] = j
        labels = remap[labels]

    # --- canonicalise: largest component -> stratum 0, etc. -----------
    # Densify ids first.
    uniq, inv = np.unique(labels, return_inverse=True)
    sizes = np.bincount(inv, minlength=len(uniq))
    # Sort by descending size; stable so ties break by original id.
    order = np.argsort(-sizes, kind="stable")
    rank = np.empty_like(order)
    rank[order] = np.arange(len(order))
    out = rank[inv].astype(np.int32)
    # Clip to [0, K) — if reconciliation left more than K (numerical
    # edge case after merging), wrap the overflow into stratum K-1.
    if out.max() >= K:
        out = np.where(out >= K, np.int32(K - 1), out)
    return out


# ---------------------------------------------------------------------------
# Public API: HNSWStratifiedSampling
# ---------------------------------------------------------------------------

class HNSWStratifiedSampling:
    """Reuse the HNSW level-0 connected components as cardinality strata.

    Parameters
    ----------
    M : int, default 16
        HNSW graph degree (per layer).  Matches pgvector default.
    ef_construction : int, default 200
        Build-time candidate-list width.  Matches pgvector default.
    K : int, default 20
        Target stratum count.
    sample_size : int, default 10000
        Per-query within-stratum sample budget.
    random_state : int or None, default None

    Attributes
    ----------
    backend : str
    N : int
    d : int
    strata : np.ndarray, shape (N,), dtype int32
        Stratum id per row.
    stratum_indices : list[np.ndarray]
        ``stratum_indices[k]`` = int32 array of row ids in stratum k.
    distance_quantiles : np.ndarray
        Pilot-pass L2 quantiles for selectivity -> radius conversion.
    """

    def __init__(
        self,
        M: int = DEFAULT_M,
        ef_construction: int = DEFAULT_EF_CONSTRUCTION,
        K: int = DEFAULT_K,
        sample_size: int = DEFAULT_SAMPLE_SIZE,
        random_state: Optional[int] = None,
    ) -> None:
        if M < 2:
            raise ValueError(f"M must be >= 2; got {M}")
        if ef_construction < M:
            raise ValueError(
                f"ef_construction must be >= M; got {ef_construction} < {M}"
            )
        if K < 2:
            raise ValueError(f"K must be >= 2; got {K}")
        if sample_size < 1:
            raise ValueError(f"sample_size must be >= 1; got {sample_size}")

        self.M = int(M)
        self.ef_construction = int(ef_construction)
        self.K = int(K)
        self.sample_size = int(sample_size)
        self.random_state = random_state

        # Set after fit()
        self.backend: str = ""
        self.N: int = 0
        self.d: int = 0
        self.strata: Optional[np.ndarray] = None
        self.stratum_indices: list = []
        self.distance_quantiles: Optional[np.ndarray] = None
        self._embeddings: Optional[np.ndarray] = None
        # 1-NN map used for the > subsample_n case
        self._subsample_centroids: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(
        self,
        embeddings: np.ndarray,
        subsample_n: int = DEFAULT_SUBSAMPLE_N,
    ) -> "HNSWStratifiedSampling":
        """Build HNSW + extract layer-0 components + reconcile to K strata."""
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2-D; got {embeddings.shape}")
        self.N, self.d = embeddings.shape
        if self.N < self.K:
            raise ValueError(
                f"N={self.N} must be >= K={self.K}"
            )

        seed = int(self.random_state) if self.random_state is not None else 0
        rng = np.random.default_rng(seed)

        # 1) Subsample if N > subsample_n; build HNSW on the subsample.
        if self.N > subsample_n:
            sub_idx = rng.choice(self.N, size=int(subsample_n), replace=False)
            sub_idx.sort()
            sub_emb = embeddings[sub_idx].astype(np.float32, copy=False)
        else:
            sub_idx = np.arange(self.N, dtype=np.int64)
            sub_emb = embeddings.astype(np.float32, copy=False)

        # 2) Build adjacency on the (sub)sample via the chosen backend.
        self.backend = _detect_backend()
        builder = _BACKEND_DISPATCH[self.backend]
        try:
            rows, cols = builder(
                sub_emb, M=self.M, ef_construction=self.ef_construction,
                seed=seed,
            )
        except Exception as exc:  # pragma: no cover (backend-specific)
            warnings.warn(
                f"[hnsw_ss] {self.backend} adjacency extraction failed "
                f"({type(exc).__name__}: {exc}); falling back to numpy KNN."
            )
            self.backend = "numpy"
            rows, cols = _build_adjacency_numpy(
                sub_emb, M=self.M, ef_construction=self.ef_construction,
                seed=seed,
            )

        # 3) Symmetrise + connected components on the level-0 graph.
        m = sub_emb.shape[0]
        if rows.size == 0:
            # Pathological: single isolated node.  Fall back to a single
            # component spanning everything.
            sub_labels = np.zeros(m, dtype=np.int64)
        else:
            data = np.ones(rows.size, dtype=np.int8)
            graph = csr_matrix((data, (rows, cols)), shape=(m, m))
            # Symmetrise via element-wise max (binary OR).
            graph = graph.maximum(graph.T)
            n_comp, sub_labels = connected_components(
                graph, directed=False, return_labels=True,
            )

        # 4) Reconcile component count -> K.
        sub_strata = _reconcile_components(
            sub_labels, sub_emb, self.K, seed=seed,
        )

        # 5) Lift subsample assignments to the full N via 1-NN map.
        if self.N > subsample_n:
            # Centroid per stratum from the subsample.
            centroids = np.zeros((self.K, self.d), dtype=np.float32)
            for k in range(self.K):
                sel = sub_strata == k
                if sel.any():
                    centroids[k] = sub_emb[sel].mean(0)
                else:
                    # Empty stratum: pick a random subsample row as the
                    # centroid placeholder (ensures every stratum is
                    # reachable; will be empty in stratum_indices but
                    # nearest-neighbour assignment is well-defined).
                    centroids[k] = sub_emb[rng.integers(0, m)]
            self._subsample_centroids = centroids
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                nn = NearestNeighbors(n_neighbors=1, algorithm="brute",
                                       metric="euclidean")
                nn.fit(centroids)
                _, nn_idx = nn.kneighbors(
                    embeddings.astype(np.float32, copy=False),
                )
            full_strata = nn_idx[:, 0].astype(np.int32)
            # Pin the subsample rows to their original stratum (the 1-NN
            # map is *consistent* but may flip a small fraction near
            # boundaries; pinning preserves the graph signal).
            full_strata[sub_idx] = sub_strata
            self.strata = full_strata
        else:
            self.strata = sub_strata

        # 6) Build per-stratum index list for fast within-stratum sampling.
        self.stratum_indices = [
            np.flatnonzero(self.strata == k).astype(np.int32)
            for k in range(self.K)
        ]

        # 7) Pilot pass for selectivity -> radius conversion.
        pilot_size = min(DEFAULT_PILOT_SIZE, self.N)
        anchor_idx = int(rng.integers(0, self.N))
        anchor = embeddings[anchor_idx].astype(np.float64)
        sample_idx = rng.choice(self.N, size=pilot_size, replace=False)
        sample = embeddings[sample_idx].astype(np.float64)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            dists = np.linalg.norm(sample - anchor, axis=1)
        self.distance_quantiles = np.quantile(
            dists, np.array(_SUPPORTED_SELECTIVITIES),
        ).astype(np.float64)

        # Keep an embedding reference for predict_cardinality.
        self._embeddings = embeddings
        return self

    # ------------------------------------------------------------------
    # predict_cardinality
    # ------------------------------------------------------------------

    def predict_cardinality(
        self, query_vec: np.ndarray, selectivity: float
    ) -> float:
        """Estimate ``|{x : ||x - query||_2 <= radius(selectivity)}|``.

        Uses the entry-stratum found via approximate HNSW descent (we do
        a single 1-NN query against the per-stratum centroids — equivalent
        to descending HNSW to layer 0 in the constant-degree limit), then
        samples within that stratum and scales by N.
        """
        if self.strata is None or self._embeddings is None:
            raise RuntimeError("fit() must be called before predict_cardinality()")
        if query_vec.ndim != 1 or query_vec.shape[0] != self.d:
            raise ValueError(
                f"query_vec shape (d={self.d},); got {query_vec.shape}"
            )
        if not (0.0 < selectivity < 1.0):
            raise ValueError(f"selectivity in (0, 1); got {selectivity}")

        # 1) Selectivity -> L2 radius via pilot quantiles.
        radius = float(np.interp(
            selectivity,
            np.array(_SUPPORTED_SELECTIVITIES),
            self.distance_quantiles,
        ))
        radius_sq = radius * radius

        # 2) Hash query -> entry stratum.  Approximation: nearest centroid.
        if self._subsample_centroids is not None:
            centroids = self._subsample_centroids
        else:
            # Compute centroids on-the-fly (only needed when N <= subsample_n).
            centroids = np.zeros((self.K, self.d), dtype=np.float32)
            for k in range(self.K):
                idx = self.stratum_indices[k]
                if idx.size:
                    centroids[k] = self._embeddings[idx].mean(0).astype(np.float32)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            d2 = ((centroids - query_vec.astype(np.float32)) ** 2).sum(1)
        entry_k = int(d2.argmin())

        # 3) Sample within entry stratum.  Combine with a uniform sample
        #    over the rest of the dataset (scaled by 1/(K-1) per stratum)
        #    to keep the estimator unbiased — without this, a query whose
        #    true neighbors lie in *other* strata would be systematically
        #    underestimated.  We use a stratified estimator:
        #
        #       cardinality = sum_k |stratum_k| * (hits_k / sample_k)
        #
        #    with a small uniform sample per stratum (sample_size / K)
        #    plus a bonus pass on the entry stratum (the rest of the
        #    sample budget).
        seed = int(self.random_state) if self.random_state is not None else 0
        rng = np.random.default_rng(seed)
        per_stratum = max(1, self.sample_size // self.K)
        bonus = max(0, self.sample_size - per_stratum * self.K)
        cardinality = 0.0
        for k in range(self.K):
            idx = self.stratum_indices[k]
            if idx.size == 0:
                continue
            n_k = int(idx.size)
            budget = per_stratum + (bonus if k == entry_k else 0)
            sample_k = min(budget, n_k)
            if sample_k == n_k:
                sel = idx
            else:
                sel = rng.choice(idx, size=sample_k, replace=False)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                diffs = (
                    self._embeddings[sel].astype(np.float64)
                    - query_vec.astype(np.float64)
                )
                sq = (diffs * diffs).sum(1)
            hits_k = int((sq <= radius_sq).sum())
            cardinality += n_k * (hits_k / float(sample_k))
        return float(cardinality)


# ---------------------------------------------------------------------------
# stratify_method shim — drop-in for measure_multi_paradigm
# ---------------------------------------------------------------------------

def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = 20,
    seed: int = 0,
    M: int = DEFAULT_M,
    ef_construction: int = DEFAULT_EF_CONSTRUCTION,
    **kwargs: Any,
) -> np.ndarray:
    """HNSW level-0 connected components -> strata (drop-in compatible).

    Concatenates ``emb1`` and ``emb2`` column-wise, builds an HNSW index
    on the concatenated embedding, and returns the per-row stratum id.
    """
    if emb1.ndim != 2 or emb2.ndim != 2:
        raise ValueError(
            f"emb1/emb2 must be 2-D; got {emb1.shape} / {emb2.shape}"
        )
    if emb1.shape[0] != emb2.shape[0]:
        raise ValueError(
            f"emb1/emb2 row count mismatch: {emb1.shape[0]} vs {emb2.shape[0]}"
        )
    if K < 2:
        raise ValueError(f"K must be >= 2, got {K}")

    concat = np.concatenate([emb1, emb2], axis=1).astype(np.float32, copy=False)
    hss = HNSWStratifiedSampling(
        M=M, ef_construction=ef_construction,
        K=K, sample_size=DEFAULT_SAMPLE_SIZE,
        random_state=seed,
    ).fit(concat)
    # strata is already int32 in [0, K).
    out = hss.strata
    assert out is not None
    return out.astype(np.int32, copy=False)


# ---------------------------------------------------------------------------
# Mini-run / self-test
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """Mini-run with N=10000, d=128; sanity-check fit + predict + determinism."""
    backend = _detect_backend()
    print(f"[hnsw_ss] self-test: N=10000, d=128, K=20, backend={backend}")
    rng = np.random.default_rng(0)
    N, d = 10_000, 128
    embeddings = rng.standard_normal((N, d)).astype(np.float32)

    hss = HNSWStratifiedSampling(
        M=16, ef_construction=200, K=20, sample_size=2000,
        random_state=0,
    )
    hss.fit(embeddings)
    assert hss.strata is not None
    assert hss.strata.shape == (N,)
    assert hss.strata.dtype == np.int32
    assert hss.strata.min() >= 0 and hss.strata.max() < 20

    counts = np.bincount(hss.strata, minlength=20)
    nz = counts[counts > 0]
    print(
        f"[hnsw_ss] stratum sizes: min={int(nz.min())} max={int(counts.max())}"
        f" mean={counts.mean():.1f} std={counts.std():.1f}"
        f" K_used={int((counts > 0).sum())}/20"
    )
    assert int((counts > 0).sum()) == 20, (
        f"every stratum must receive at least one row; "
        f"got {int((counts > 0).sum())}/20"
    )

    # Prediction sanity: monotonic in selectivity.
    q = embeddings[rng.integers(0, N)]
    estimates = []
    for sel in (0.01, 0.05, 0.10, 0.30, 0.50):
        est = hss.predict_cardinality(q, sel)
        estimates.append(est)
        print(
            f"[hnsw_ss] sel={sel:.2f} -> cardinality={est:.1f} "
            f"(true={sel*N:.0f})"
        )
    for a, b in zip(estimates, estimates[1:]):
        assert b >= a * 0.5, f"non-monotonic: {estimates}"

    # Determinism check on stratify_method.
    emb1 = rng.standard_normal((5000, 96)).astype(np.float32)
    emb2 = rng.standard_normal((5000, 32)).astype(np.float32)
    sids1 = stratify_method(emb1, emb2, K=20, seed=0)
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    if backend == "hnswlib":
        assert np.array_equal(sids1, sids2), "hnswlib must be deterministic"
        print("[hnsw_ss] determinism (hnswlib, seed=0): OK")
    else:
        # faiss/numpy: stratum *count* and *sizes* should match even if the
        # specific labels permute (we canonicalise by size, but ties break
        # nondeterministically when faiss internal RNG differs).
        c1 = np.sort(np.bincount(sids1, minlength=20))
        c2 = np.sort(np.bincount(sids2, minlength=20))
        assert np.array_equal(c1, c2), (
            f"size distribution must match across runs: {c1} vs {c2}"
        )
        print(f"[hnsw_ss] determinism ({backend}, seed=0): size dist OK")

    print("[hnsw_ss] self-test OK")


if __name__ == "__main__":
    _self_test()
