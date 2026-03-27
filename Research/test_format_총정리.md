# Test Document Title

> **범위**: This is a quote with **bold** text inside

---

### [1] Test Paper Section One

This is a paragraph with **bold text** and *italic text* and `inline code`.

**Standalone bold line:**

핵심 기술:
1. **PROMPT 토큰**: SQL 내에서 LLM 을 직접 호출
2. **SEM_MATCH 토큰**: 선언적 시맨틱 유사도 매칭

- Regular bullet with **bold** inside
  - Sub-bullet with `code` inside
- Another bullet

```python
client.search(
    collection_name="products",
    query_vector=[0.1, 0.2, ...],
    limit=10
)
```

**시나리오 1:** 벡터 조건의 실제 선택도 = 0.1%
**시나리오 2:** 벡터 조건의 실제 선택도 = 90%

---

### [2] Test Paper Section Two

This section should start on a new page.

```sql
SELECT * FROM items
WHERE embedding <=> query_vector < 0.1
ORDER BY price;
```
